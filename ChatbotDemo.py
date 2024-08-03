# Jan-Daryl Bantug

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit
import json
import openai

port = 3000
app = Flask(__name__, static_folder='public')
socketio = SocketIO(app)

# Configure OpenAI client to point to your local LM Studio server
openai.api_key = "lm-studio"
openai.api_base = "http://localhost:1234/v1"

@app.route('/')
def index():
    return send_from_directory('public', 'chat-demo.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_name = data['name']
    user_message = data['message']

    # Initialize conversation between two bots
    bot1_message = initiate_chat(user_name, user_message)
    bot2_message = chat_between_bots(bot1_message)

    return jsonify({"message": bot2_message})

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    data = json.loads(msg)
    name = data['name']
    message = data['message']

    # Broadcast the user's message
    user_response = {'name': name, 'message': message}
    emit('message', user_response, broadcast=True)

    # Initialize conversation between two bots
    bot1_message = initiate_chat(name, message)
    bot2_message = chat_between_bots(bot1_message)

    # Broadcast the AI's response
    ai_response = {'name': 'AI Bot 2', 'message': bot2_message}
    emit('message', ai_response, broadcast=True)

def initiate_chat(name, message):
    # Call the chatbot API for the first bot
    completion = openai.Completion.create(
        model="model-identifier",
        prompt=f"{name}: {message}\nAI Bot 1:",
        temperature=0.7,
        max_tokens=50
    )

    # Get the response from the first bot
    bot1_response = completion.choices[0].text.strip().split('\n')[0]
    return bot1_response

def chat_between_bots(bot1_message):
    # Call the chatbot API for the second bot
    completion = openai.Completion.create(
        model="model-identifier",
        prompt=f"AI Bot 1: {bot1_message}\nAI Bot 2:",
        temperature=0.7,
        max_tokens=50
    )

    # Get the response from the second bot
    bot2_response = completion.choices[0].text.strip().split('\n')[0]
    return bot2_response

# Start the server
if __name__ == '__main__':
    socketio.run(app, port=port, debug=True)
