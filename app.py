from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
from flask_pymongo import PyMongo
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Database setup
mongo_uri = os.getenv("MONGO_URI")
openai.api_key = os.getenv("OPENAI_API_KEY")
db_connected = False

if mongo_uri:
    app.config["MONGO_URI"] = mongo_uri
    try:
        mongo = PyMongo(app)
        mongo.db.command('ping')
        db_connected = True
    except Exception as e:
        print(f"MongoDB error: {str(e)}")
        mongo = None

@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.route("/")
def home():
    chats = []
    if db_connected:
        try:
            chats = list(mongo.db.chats.find({}))
        except Exception as e:
            print(f"DB error: {str(e)}")
    return render_template("index.html", myChats=chats)

@app.route("/api", methods=["POST"])
def qa():
    data = request.json
    question = data.get("question", "")
    
    if db_connected:
        existing = mongo.db.chats.find_one({"question": question})
        if existing:
            return jsonify(existing)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            temperature=0.7,
            max_tokens=256
        )
        answer = response.choices[0].message.content
        
        if db_connected:
            mongo.db.chats.insert_one({"question": question, "answer": answer})
            
        return jsonify({"question": question, "answer": answer})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
