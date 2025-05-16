from flask import Flask, render_template, jsonify, request, url_for
from flask_pymongo import PyMongo
import openai
import os
from dotenv import load_dotenv
load_dotenv()

# Debug print to check if we have a MONGO_URI (don't print the full string for security)
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    print(f"MONGO_URI found with length: {len(mongo_uri)}, starts with: {mongo_uri[:15]}...")
else:
    print("WARNING: MONGO_URI environment variable is not set!")

# Securely fetch environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("WARNING: OPENAI_API_KEY environment variable is not set!")

app = Flask(__name__, static_folder='static')

# Set up MongoDB connection (if possible)
if mongo_uri:
    app.config["MONGO_URI"] = mongo_uri
    try:
        mongo = PyMongo(app)
        # Test the connection
        mongo.db.command('ping')
        print("MongoDB connection successful!")
        db_connected = True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        mongo = None
        db_connected = False
else:
    print("No MongoDB URI provided, running in no-database mode")
    mongo = None
    db_connected = False

@app.route("/")
def home():
    myChats = []
    try:
        if db_connected:
            chats = mongo.db.chats.find({})
            myChats = [chat for chat in chats]
            print(f"Found {len(myChats)} chats in database")
    except Exception as e:
        print(f"Error retrieving chats: {e}")
    
    return render_template("index.html", myChats=myChats)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        question = request.json.get("question")
        print(f"Received question: {question}")
        
        # Try to find existing answer in MongoDB
        answer = None
        if db_connected:
            try:
                chat = mongo.db.chats.find_one({"question": question})
                if chat:
                    answer = chat['answer']
                    print("Found existing answer in database")
            except Exception as e:
                print(f"Error querying database: {e}")
        
        # If no existing answer, ask OpenAI
        if not answer:
            try:
                # Check if we have an API key
                if not openai.api_key:
                    return jsonify({"question": question, 
                                    "answer": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."})
                
                print("Requesting answer from OpenAI")
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.7,
                    max_tokens=256
                )
                answer = response.choices[0].message.content.strip()
                
                # Save to database if connected
                if db_connected:
                    try:
                        mongo.db.chats.insert_one({"question": question, "answer": answer})
                        print("Saved new answer to database")
                    except Exception as e:
                        print(f"Error saving to database: {e}")
                        
            except Exception as e:
                print(f"Error from OpenAI API: {e}")
                return jsonify({"question": question, "answer": f"Error: {str(e)}"})
        
        # Return the answer
        return jsonify({"question": question, "answer": answer})
    
    return jsonify({
        "result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss?"
    })

# Adding a simple route to check database status
@app.route("/status")
def status():
    return jsonify({
        "database_connected": db_connected,
        "openai_api_configured": bool(openai.api_key)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
