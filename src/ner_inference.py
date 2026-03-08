import joblib
import re

class NERPipeline:
    def __init__(self, model_path):
        # Загружает сохраненную модель при инициализации класса
        print(f"Загрузка модели из {model_path}...")
        self.model = joblib.load(model_path)
        print("Модель успешно загружена!")

    def tokenize(self, text):
        # Разбивает сплошной текст на слова и знаки препинания.
        return re.findall(r'\w+|[^\w\s]', text)

    def word2features(self, sent, i):
        # копия функции извлечения признаков из нашего ноутбука
        word = str(sent[i])
        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word[-3:]': word[-3:],
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
        }
        if i > 0:
            word1 = str(sent[i-1])
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
                '-1:word.isupper()': word1.isupper(),
            })
        else:
            features['BOS'] = True

        if i < len(sent)-1:
            word1 = str(sent[i+1])
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
                '+1:word.isupper()': word1.isupper(),
            })
        else:
            features['EOS'] = True
            
        return features

    def predict(self, text):
        # Основной метод который принимает текст и отдает найденные сущности
        tokens = self.tokenize(text)

        features = [self.word2features(tokens, i) for i in range(len(tokens))]

        predictions = self.model.predict([features])[0]
        
        # Собираем результаты в удобный формат
        entities = []
        for word, tag in zip(tokens, predictions):
            if tag != '0': 
                entities.append({
                    'word': word,
                    'tag_id': tag
                })
                
        return entities

# Блок для проверки работоспособности скрипта
if __name__ == "__main__":
    pipeline = NERPipeline('./models/crf_model.joblib') 

    test_text = "Vladimir Putin visited Moscow to meet with Apple representatives."
    print(f"\nАнализируем текст: '{test_text}'")
    
    results = pipeline.predict(test_text)
    
    print("\nНайденные сущности:")
    for res in results:
        print(f"Слово: {res['word']:<10} | Тег: {res['tag_id']}")