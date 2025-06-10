import threading
import socket

PORT = int(input("Digite a Porta a ser usada: "))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", PORT))
server.listen()
client, addr = server.accept()

print("[---------------Chat Conectado---------------]")
def receiveMsg():
    while True:
        msg = client.recv(1024).decode()
        print("\t\t\t\t\t" + msg)
        if msg == '': 
            return
    

thread = threading.Thread(target=receiveMsg, daemon=True)
thread.start()

while True:
    msgInp = input()
    client.send(msgInp.encode("utf-8"))
    if msgInp == '':
        break

server.close()