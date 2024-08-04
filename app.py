import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info={
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modelling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing and Modelling.'),
    },
    host=LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

def text_cleansing(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    text = re.sub(r'(user|rt|retweet|\\t|\\r)', '', text)
    text = re.sub(r"\s+", " ", text)
    text = text.lstrip().rstrip() 
    text = re.sub(r'(https|https:|url)', '', text)
    text = re.sub(r'#([^\s]+)', '', text)
    text = re.sub(r'@[^\s]+', '', text)
    text = re.sub(r'\\[a-z0-9]{1,5}', '', text)
    text = re.sub(r'[^\x00-\x7f]', '', text)
    text = re.sub(r'(\\u[0-9A-Fa-f]+)', '', text)
    text = re.sub(r'\b\w{1,3}\b', '', text)
    
    return text

@swag_from('docs/text_processing.yml', methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO text (before, after)
                      VALUES (?, ?)''', (text, text_cleansing(text)))
    conn.commit()
    conn.close()
        
    json_response = {
        'status': 200,
        'description': 'Teks yang sudah diproses',
        'before': text,
        'after': text_cleansing(text),
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from('docs/text_processing_file.yml', methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    file = request.files.getlist('file')[0]
    df = pd.read_csv(file)
    text = df.iloc[:, 0].tolist()
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cleaned_text = []
    for t in text:
        cleaned_text.append(text_cleansing(t))
        cursor.execute('''INSERT INTO text (before, after)
                      VALUES (?, ?)''', (t, text_cleansing(t)))

    conn.commit()
    conn.close()

    json_response = {
        'status': 200,
        'description': 'Teks yang sudah diproses',
        'before': text,
        'after': cleaned_text,
    }

    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run()