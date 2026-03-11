import wikipedia

class WikiParser:
    def __init__(self, lang="en"):
        wikipedia.set_lang(lang)

    def get_explanation(self, entity_name, sentences=2):
        try:
            # Сначала делаем поиск
            search_results = wikipedia.search(entity_name)
            
            if not search_results:
                return "Explanation not found on Wikipedia."
            
            # Берем самый релевантный результат поиска
            best_match = search_results[0]
            
            # Запрашиваем текст именно для этого названия, отключая автоисправление
            summary = wikipedia.summary(best_match, sentences=sentences, auto_suggest=False)
            return summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Если даже поиск выдал многозначность, берем первый адекватный вариант
            try:
                # фильтруем от мусора, если нужно, или просто берем первый
                return wikipedia.summary(e.options[0], sentences=sentences, auto_suggest=False)
            except:
                return "Explanation not found due to ambiguity."
                
        except wikipedia.exceptions.PageError:
            return "Explanation not found on Wikipedia."
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

# Блок для проверки
if __name__ == "__main__":
    parser = WikiParser()
    
    print("Ищем 'Vladimir Putin':")
    print(parser.get_explanation("Vladimir Putin"))
    print("-" * 50)
    
    print("Ищем 'Apple' (проверка многозначности):")
    print(parser.get_explanation("Apple"))
    print("-" * 50)
    
    print("Проверка на поиск чего-то несуществующего 'Qwerty12345':")
    print(parser.get_explanation("Qwertyuiop12345"))