import openai
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from openai.error import OpenAIError

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Custom log format
log_format = '[%(levelname)s] - Client IP: %(client_ip)s - Request Info - %s %s'


load_dotenv() 
openai.api_key = os.getenv("MY_API_KEY")

def process_message(chat_history):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=chat_history  
        )
        ai_message = {"role": "assistant", "content": response['choices'][0]['message']['content']}
        return ai_message
    except OpenAIError as e:
        return {"error": str(e)}

# Custom log format
log_format = (
    '%(asctime)s [%(levelname)s] - ' 
    'Client IP: %(client_ip)s - ' 
    '%(message)s'
)

with app.app_context():
    # Remove the default handler
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    # Create a new handler with the custom format
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)  # Ensure our logger captures INFO level logs
    # Optionally, if you want to suppress the default Werkzeug logs:
    logging.getLogger('werkzeug').setLevel(logging.ERROR) 

# Update the logger to include client_ip
@app.before_request
def before_request():
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    request._client_ip = client_ip  # Attach IP to the request object

# Inject client_ip into the logger's extra parameter
def log_request_info(response):
    app.logger.info('Request Info - %s %s', request.method, request.url, extra={'client_ip': request._client_ip})
    return response

app.after_request(log_request_info)

@app.route('/')
def index():
    #client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['user_message']
    bot_message = process_message(user_message)
    return jsonify({ 'bot_message': bot_message })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 
    #app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem')) 