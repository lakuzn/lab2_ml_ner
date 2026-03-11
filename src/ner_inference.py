import joblib
import re

class NERPipeline:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def tokenize(self, text):
        return re.findall(r'(?:[A-Z]\.)+|[A-Za-z0-9_]+|[^\w\s]', text)

    def word2features(self, sent, i):
        word = str(sent[i])
        is_title = word[0].isupper() if len(word) > 0 else False
        
        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word[-3:]': word[-3:],
            'word[-2:]': word[-2:], 
            'word[:2]': word[:2],  
            'word[:3]': word[:3],   
            'word.length': len(word),
            'word.isupper()': word.isupper(),
            'word.istitle()': is_title,
            'word.isdigit()': word.isdigit(),
        }
        if i > 0:
            word1 = str(sent[i-1])
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1[0].isupper() if len(word1) > 0 else False,
                '-1:word.isupper()': word1.isupper(),
            })
        else:
            features['BOS'] = True

        if i < len(sent)-1:
            word1 = str(sent[i+1])
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1[0].isupper() if len(word1) > 0 else False,
                '+1:word.isupper()': word1.isupper(),
            })
        else:
            features['EOS'] = True
            
        return features

    def predict(self, text):
        tokens = self.tokenize(text)
        features = [self.word2features(tokens, i) for i in range(len(tokens))]
        # Превращаем результат обратно в список, чтобы можно было его изменять
        predictions = list(self.model.predict([features])[0])
        
        # post proccessing
        for i in range(len(predictions)):
            word = tokens[i]
            
            if word.lower() == "and" and predictions[i] != '0':
                predictions[i] = '0' # Обнуляем and, чтобы сборщик начал новую сущность
                
            if predictions[i] in ['15', '7', '1', '3']: 
                idx = i - 1
                while idx >= 0 and predictions[idx] == '0' and tokens[idx][0].isupper() and tokens[idx].lower() not in ['the', 'a', 'an']:
                    base_tag = int(predictions[i]) if int(predictions[i]) % 2 != 0 else int(predictions[i]) - 1
                    i_tag = str(base_tag + 1) # Тег продолжения
                    
                    predictions[idx] = str(base_tag)   # Предыдущее слово становится началом
                    predictions[idx+1] = str(i_tag)    # Текущее сдвигается в продолжение
                    idx -= 1

        # Сборщик
        entities = []
        current_entity_words = []
        current_tag = None
        
        for word, tag in zip(tokens, predictions):
            tag_num = int(tag)
            
            if tag_num == 0:
                if current_entity_words:
                    entities.append({'word': " ".join(current_entity_words), 'tag_id': str(current_tag)})
                    current_entity_words = []
                    current_tag = None
                    
            elif tag_num % 2 != 0: # B-tag (Начало)
                if current_entity_words:
                    entities.append({'word': " ".join(current_entity_words), 'tag_id': str(current_tag)})
                current_entity_words = [word]
                current_tag = tag_num
                
            else: # I-tag (Продолжение)
                if current_entity_words and (current_tag == tag_num - 1 or current_tag == tag_num):
                    current_entity_words.append(word)
                else:
                    # Если I оторвался от начала
                    if current_entity_words:
                        entities.append({'word': " ".join(current_entity_words), 'tag_id': str(current_tag)})
                    current_entity_words = [word]
                    current_tag = tag_num - 1 # Восстанавливаем родительский B-тег
                    
        if current_entity_words:
            entities.append({'word': " ".join(current_entity_words), 'tag_id': str(current_tag)})
                
        return entities