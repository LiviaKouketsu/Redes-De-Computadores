import threading
import socket

HOST = input("Digite o IP a ser conectado: ")
PORT = int(input("Digite a Porta a ser usada: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

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

client.close()