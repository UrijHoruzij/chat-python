import http.server
import socketserver
from io import BytesIO
import random
import json
import hashlib
from pathlib import Path

read_file = open("database.json", "r+", encoding="utf-8")
database = json.load(read_file)
message_history = []
tokens = {}

def send(this,requestJson):
    token = requestJson["token"]
    if token in tokens:
        if tokens[token] in database:
            data = {
                "nick": database[tokens[token]]["name"],
                "text": requestJson["message"],
                "image": requestJson["image"],
                "id-user": requestJson["id-user"]
            }
            message = json.dumps(data)
            message_history.append(message)
            this.send_response(200, "OK")
            this.send_header("Access-Control-Allow-Origin", "*")
            this.send_header("Access-Control-Allow-Headers", "Content-Type")
            this.end_headers()
            response = BytesIO()
            answer = json.dumps({"answer": "ok"})
            this.wfile.write(answer.encode("utf_8"))

def get(this,requestJson):
    if requestJson["id"] == "":
        answer = json.dumps({"id": len(message_history), "messages": message_history})
        print(answer)
        this.wfile.write(answer.encode("utf_8"))
    else:
        last_message_id = requestJson["id"]
        answer = json.dumps({"id": len(message_history), "messages": message_history[last_message_id:]}) 
        print(answer)
        this.wfile.write(answer.encode("utf_8"))

def auth(this, requestJson):
    login = requestJson["login"]
    password = requestJson["password"]
    if login in database:
       if password == database[login]["password"]:
           token = tokenGenerate();
           answer = json.dumps({"token": token, "id-user": database[login]["id"]})
           this.wfile.write(answer.encode("utf_8"))
           tokens[token]=login
           print(tokens)

def registration(this, requestJson):
    login = requestJson["login"]
    password = requestJson["password"]
    hashPassword = hashlib.sha256()
    hashPassword.update(password.encode('utf-8'))
    if login in database:
        print(login)
    else:
        data = {
                "id": str(len(database)+1),
                "name": requestJson["nameUser"],
                "login": login,
                "password": hashPassword.hexdigest()
        }
        with open('database.json', 'a+') as f:
            database[login] = data
            json.dump(database, f)
        if hashPassword.hexdigest() == database[login]["password"]:
            token = tokenGenerate()
            answer = json.dumps({"token": token, "id-user": database[login]["id"]})
            this.wfile.write(answer.encode("utf_8"))
            tokens[token]=login
            print(tokens)

def tokenGenerate():
    token = ""
    for i in range(0, 16):
        token += str(random.randint(0,9))
    return token

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200, "OK")
        self.end_headers()
        response = BytesIO()
        response.write(b"Hello world!")
        self.wfile.write(response.getvalue())

    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        content_length = int(self.headers["Content-length"])
        body = self.rfile.read(content_length)

        requestJson = json.loads(body.decode("utf_8"))
        if requestJson["command"] == "Send":
            send(self,requestJson)
        if requestJson["command"] == "Get":
            get(self,requestJson)
        if requestJson["command"] == "Auth":
            auth(self,requestJson)
        if requestJson["command"] == "Registration":
            registration(self,requestJson)

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    PORT = 8080
    Handler = MyHandler
    httpd = socketserver.TCPServer(("localhost", PORT), Handler)
    print("Start server at port : ", PORT)
    httpd.serve_forever()