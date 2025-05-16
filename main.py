from flask import Flask, render_template, jsonify, request, url_for
from flask_pymongo import PyMongo
import openai
import os
from dotenv import load_dotenv
load_dotenv()  # Add this at the top

# Securely fetch environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='static')
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    myChats = [chat for chat in chats]
    print(myChats)
    return render_template("index.html", myChats=myChats)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        print(request.json)
        question = request.json.get("question")
        chat = mongo.db.chats.find_one({"question": question})
        print(chat)
        if chat:
            data = {"question": question, "answer": f"{chat['answer']}"}
            return jsonify(data)
        else:
            # Updated to use the current OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=256
            )
            print(response)
            answer = response.choices[0].message.content.strip()
            mongo.db.chats.insert_one({"question": question, "answer": answer})
            return jsonify({"question": question, "answer": answer})
    return jsonify({
        "result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss?"
    })

# Prevent auto-run when using Gunicorn
if __name__ == "__main__":
    app.run(debug=True, port=5001)