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

    completion = openai.Completion.create(
        model="model-identifier",
        prompt=f"{user_name}: {user_message}\nAI:",
        temperature=0.7,
        max_tokens=50  # Adjust this value to control the length of the response
    )

    response_message = completion.choices[0].text.strip().split('\n')[0]  # Get the first line of the response
    return jsonify({"message": response_message})

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

    # Call the chatbot API
    completion = openai.Completion.create(
        model="model-identifier",
        prompt=f"{name}: {message}\nAI:",
        temperature=0.7,
        max_tokens=50  # Adjust this value to control the length of the response
    )

    response_message = completion.choices[0].text.strip().split('\n')[0]  # Get the first line of the response

    # Broadcast the AI's response
    ai_response = {'name': 'AI', 'message': response_message}
    emit('message', ai_response, broadcast=True)

# Start the server
if __name__ == '__main__':
    socketio.run(app, port=port, debug=True)
