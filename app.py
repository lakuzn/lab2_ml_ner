import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import sys
import os

# Добавляем папку src в пути, чтобы импорты работали корректно
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ner_inference import NERPipeline
from src.knowledge_base import KnowledgeBase

st.set_page_config(page_title="NER Pipeline & Knowledge Base", layout="wide")

# Загружаем модель и базу только один раз (кешируем)
@st.cache_resource
def load_model():
    return NERPipeline('models/crf_model.joblib')

@st.cache_resource
def load_kb():
    return KnowledgeBase('data/knowledge_base.json')

try:
    pipeline = load_model()
    kb = load_kb()
except Exception as e:
    st.error(f"Ошибка загрузки: убедитесь, что модель crf_model.joblib существует. Ошибка: {e}")
    st.stop()

st.title("Лабораторная II: NER")

# Разделим интерфейс на две вкладки
tab1, tab2 = st.tabs(["Ввод текста и инференс", "База знаний и визуализация"])

with tab1:
    st.header("Анализ текста")
    user_text = st.text_area("Введите текст на английском:", 
                             value="Vladimir Putin and Steve Jobs visited Moscow to buy Apple computers.")
    
    if st.button("Проанализировать текст"):
        with st.spinner("Модель анализирует текст..."):
            # 1. Получаем предсказания от модели
            entities = pipeline.predict(user_text)
            
            # 2. Подсветка текста
            highlighted_text = user_text
            for ent in entities:
                word = ent['word']
                # Сохраняем в базу
                kb.add_entity(word, ent['tag_id'], user_text)
                
                # Простая подсветка
                color = "#ffd700" if ent['tag_id'] in ['1', '2'] else "#87cefa" if ent['tag_id'] in ['7', '8'] else "#98fb98"
                html_tag = f'<mark style="background-color: {color}; padding: 2px; border-radius: 3px;"><b>{word}</b></mark>'
                highlighted_text = highlighted_text.replace(word, html_tag)
                
            st.markdown("### Результат:")
            st.markdown(highlighted_text, unsafe_allow_html=True)
            
            st.success(f"Найдено сущностей: {len(entities)}. База знаний обновлена!")

with tab2:
    st.header("Управление базой знаний")

    # Кнопка очистки
    if st.button("Очистить всю базу знаний", type="primary"):
        kb.clear_db()
        st.success("База знаний и история запросов успешно очищены!")
        st.rerun()
    
    # Облако слов 
    st.subheader("Облако слов по категориям")
    categories = list(set([data["category"] for data in kb.db.values()]))
    
    if categories:
        selected_cat = st.selectbox("Выберите категорию для облака слов:", categories)
        words_in_cat = [word for word, data in kb.db.items() if data["category"] == selected_cat]
        
        if words_in_cat:
            word_string = " ".join(words_in_cat)
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(word_string)
            
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
    else:
        st.info("База пуста. Проанализируйте текст во вкладке 'Ввод текста'.")

    st.subheader("Сохраненные сущности")
    if kb.db:
        selected_word = st.selectbox("Выберите сущность, чтобы узнать больше:", list(kb.db.keys()))
        if selected_word:
            st.write(f"**Категория:** {kb.db[selected_word]['category']}")
            st.write(f"**Описание:** {kb.db[selected_word].get('explanation', 'Нет данных')}")
            st.write("**Где встречается:**")
            for text in kb.db[selected_word]['texts']:
                st.info(text)