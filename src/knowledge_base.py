import json
import os
from wiki_parser import WikiParser 

class KnowledgeBase:
    def __init__(self, storage_file='./data/knowledge_base.json'):
        self.storage_file = storage_file
        self.db = {}
        self.wiki = WikiParser()  # Инициализируем парсер Википедии
        
        # Маппинг цифровых тегов Kaggle в нормалльные названия категорий
        self.tag_mapping = {
            '1': 'Person', '2': 'Person',
            '7': 'Location', '8': 'Location',
            '15': 'Organization', '16': 'Organization',
            '3': 'GPE', '4': 'GPE',
            '13': 'Time', '14': 'Time',
        }
        
        self.load_db()

    def load_db(self):
        # Загружает базу из файла, если он существует
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.db = json.load(f)

    def save_db(self):
        # Сохраняет текущее состояние базы в json
        dir_name = os.path.dirname(self.storage_file)
        if dir_name: 
            os.makedirs(dir_name, exist_ok=True)
            
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=4, ensure_ascii=False)

    def clear_db(self):
        # Для удобства добавил еще функцию чистки базы знаний
        self.db = {}
        self.save_db()
        return True

    def add_entity(self, word, tag_id, text_context=None):
        # Добавление новой сущности. Если её нет, подтягиваем википедию.
        category = self.tag_mapping.get(str(tag_id), 'Other')
        
        # Если слова еще нет в базе, создаем для него запись и ищем справку
        if word not in self.db:
            print(f"[{word}] Новая сущность! Ищу справку в Википедии...")
            explanation = self.wiki.get_explanation(word)
            
            self.db[word] = {
                "category": category,
                "explanation": explanation,
                "texts": []
            }
            
        # Добавляем предложение, в котором встретилось слово (если его там еще нет)
        if text_context and text_context not in self.db[word]["texts"]:
            self.db[word]["texts"].append(text_context)
            
        self.save_db()
        return True

    def delete_entity(self, word):
        # Удаление сущности из базы
        if word in self.db:
            del self.db[word]
            self.save_db()
            return True
        return False

    def get_texts_for_entity(self, word):
        # Возвращает все тексты для конкретной сущности
        return self.db.get(word, {}).get("texts", [])

    def add_new_category(self, new_category, words_to_reassign):
        # Добавление новой категории и переназначение старых слов
        for word in words_to_reassign:
            if word in self.db:
                self.db[word]["category"] = new_category
        self.save_db()
        return True

# Проверкa
if __name__ == "__main__":
    kb = KnowledgeBase(storage_file='test_kb.json')
    
    test_text = "Vladimir Putin visited Moscow to meet with Apple representatives."
    print("Обрабатываем текст и добавляем сущности...\n")
    
    # передаем сущности, которые нашла наша модель
    kb.add_entity("Vladimir Putin", "1", test_text)
    kb.add_entity("Apple", "15", test_text)
    kb.add_entity("Moscow", "7", test_text)
    
    print("\n Содержимое базы для Apple:")
    print(json.dumps(kb.db["Apple"], indent=2, ensure_ascii=False))