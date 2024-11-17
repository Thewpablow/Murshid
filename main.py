import requests
import json
import time
import os
import http.server
import socketserver
import threading
import logging

# AKATSUKI logo
logo = """
   _____   ____  __.  _____________________________ ___ ____  __.___ 
  /  _  \ |    |/ _| /  _  \__    ___/   _____/    |   \    |/ _|   |
 /  /_\  \|      <  /  /_\  \|    |  \_____  \|    |   /      < |   |
/    |    \    |  \/    |    \    |  /        \    |  /|    |  \|   |
\____|__  /____|__ \____|__  /____| /_______  /______/ |____|__ \___|
        \/        \/       \/               \/                 \/    
"""

print(logo)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("script.log"),
        logging.StreamHandler()
    ]
)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Mentawl King")

def execute_server():
    PORT = int(os.environ.get('PORT', 4010))
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        logging.info(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []

def send_message(chat_id, message, access_token):
    url = f"https://graph.facebook.com/v17.0/t_{chat_id}"
    parameters = {'access_token': access_token, 'message': message}
    headers = {
        'User-Agent': 'PythonScript/1.0',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, data=json.dumps(parameters), headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            logging.info(f"Message sent to {chat_id}: {message}")
        else:
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            logging.warning(f"Failed to send message to {chat_id}: {error_message}")
            
            # If token is invalid, stop further usage of this token
            if "Invalid OAuth access token" in error_message or "expired" in error_message:
                return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while sending message: {e}")
    
    return True

def process_messages(time_interval):
    access_tokens = read_file("d3")
    messages = read_file("messages.txt")
    chat_ids = read_file("chat_ids.txt")

    if not access_tokens or not messages or not chat_ids:
        logging.error("Missing essential input data. Check your files.")
        return

    token_index = 0

    while True:
        for message in messages:
            if token_index >= len(access_tokens):
                logging.error("All tokens have been exhausted or invalidated.")
                return

            current_token = access_tokens[token_index]

            for chat_id in chat_ids:
                success = send_message(chat_id, message, current_token)
                if not success:
                    logging.warning(f"Token {current_token} invalid. Skipping.")
                    token_index += 1
                    if token_index >= len(access_tokens):
                        logging.error("No more valid tokens. Exiting.")
                        return
                time.sleep(time_interval)

def main():
    settings = read_file('settings.txt')
    time_interval = int(settings.get('TIME_INTERVAL', 2)) if settings else 2

    # Start server in a separate thread
    server_thread = threading.Thread(target=execute_server, daemon=True)
    server_thread.start()

    process_messages(time_interval)

if __name__ == '__main__':
    main()
