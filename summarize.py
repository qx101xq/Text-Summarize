import requests
import json
import re
import nltk
import yaml
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
stop_words = set(stopwords.words('russian'))  # Замените 'english' на нужный язык, например, 'russian'
lemmatizer = WordNetLemmatizer()


class LLMSummarize:
    def __init__(self, url, model):
        self.url = url
        self.model = model
        
    def form_prompt(self, comp_force): # формируем промпт из .yaml файла в зависимости от силы сжатия
        with open('prompt.yaml', 'r', encoding='utf-8') as file:
            system = yaml.safe_load(file)['summarization_task']

        summary_type = system['options'][comp_force]['description']

        end_prompt = [
            system['description'],
            '\n'.join(system['requirements']),  # Объединяем требования в одну строку
            summary_type,
            system['end']
        ]

        return ' '.join(end_prompt)
        

    def preprocess(self, text): # делаем препроцессинг подаваемого на вход текста
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^A-Za-z0-9а-яА-ЯёЁ\s]', '', text)
        text = text.lower()
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        processed_text = ' '.join(tokens)
    
        return processed_text


    def compress(self, text, comp_force): # суммаризируем текст в зависимости от силы
        prompt = self.form_prompt(comp_force) + self.preprocess(text)

        js = {
            'model': self.model, 
            'options': {"seed": 123, "temperature": 0},
            'prompt': prompt,
            'stream': True
        }

        with requests.post(url=self.url, json=js, stream=True) as result:
            if result.status_code == 200:
                for line in result.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        response_text = data.get('response', '')
                        yield response_text
            else:
                return f"Something went wrong. Status code: {result.status_code}."