from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = openai(api_key=os.getenv("OPENAI_API_KEY"))

def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                role TEXT,
                content TEXT
              )
              ''')
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", 
              (role, content))
    conn.commit()
    conn.close()

def get_chat_history():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history")
    chat_history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return chat_history

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        
        save_message('user', question)
        
        chat_history = get_chat_history()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_history
        )
        
        result = response.choices[0].message.content
        save_message('assistant', result)
        
        return jsonify({'response': result})

    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
