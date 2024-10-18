import requests
import json
import time
import os
import http.server
import socketserver
import threading

# Fancy AKATSUKI logo
logo = """
   _____   ____  __.  _____________________________ ___ ____  __.___ 
  /  _  \ |    |/ _| /  _  \__    ___/   _____/    |   \    |/ _|   |
 /  /_\  \|      <  /  /_\  \|    |  \_____  \|    |   /      < |   |
/    |    \    |  \/    |    \    |  /        \    |  /|    |  \|   |
\____|__  /____|__ \____|__  /____| /_______  /______/ |____|__ \___|
        \/        \/       \/               \/                 \/    
"""

print(logo)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Mentawl King")

def execute_server():
    PORT = int(os.environ.get('PORT', 4010))

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Server running at http://localhost:{}".format(PORT))
        httpd.serve_forever()

def read_access_tokens(file_path):
    with open(file_path, 'r') as file:
        access_tokens = file.readlines()
    access_tokens = [token.strip() for token in access_tokens]
    return access_tokens

def read_messages(file_path):
    with open(file_path, 'r') as file:
        messages = file.readlines()
    messages = [message.strip() for message in messages]
    return messages

def read_chat_ids(file_path):
    with open(file_path, 'r') as file:
        chat_ids = file.readlines()
    chat_ids = [chat_id.strip() for chat_id in chat_ids]
    return chat_ids

def read_settings(file_path):
    with open(file_path, 'r') as file:
        settings = file.readlines()
    settings = [setting.strip() for setting in settings if '=' in setting]
    settings_dict = {setting.split('=')[0]: setting.split('=')[1] for setting in settings}
    return settings_dict

requests.packages.urllib3.disable_warnings()

def send_message(chat_id, message, access_token):
    try:
        url = f"https://graph.facebook.com/v17.0/{'t_' + chat_id}"
        parameters = {'access_token': access_token, 'message': message}
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Referer': 'http://www.google.com'
        }
        s = requests.post(url, data=parameters, headers=headers)
        s.raise_for_status()

        tt = time.strftime("%Y-%m-%d %I:%M:%S %p")
        print(f"[{tt}] Message sent to {chat_id}: {message}")

    except requests.exceptions.RequestException as e:
        print("[!] Failed to send message:", e)

def deta(time_interval):
    access_token_file = "d3"
    messages_file = "messages.txt"
    chat_ids_file = "chat_ids.txt"

    access_tokens = read_access_tokens(access_token_file)
    messages = read_messages(messages_file)
    chat_ids = read_chat_ids(chat_ids_file)

    token_index = 0

    while True:
        for message in messages:
            access_token = access_tokens[token_index % len(access_tokens)]

            for chat_id in chat_ids:
                try:
                    send_message(chat_id, message, access_token)
                    token_index += 1
                    time.sleep(time_interval)

                except requests.exceptions.RequestException as e:
                    print("[!] Internet error:", e)
                    continue

def main():
    settings = read_settings('settings.txt')
    time_interval = int(settings.get('TIME_INTERVAL', 2))  # Default to 2 seconds if not specified

    server_thread = threading.Thread(target=execute_server)
    server_thread.start()
    deta(time_interval)

if __name__ == '__main__':
    main()
        
