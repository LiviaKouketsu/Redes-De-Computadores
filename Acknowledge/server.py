import socket

def ackUDP(server):
    while True:
        msg, addr = server.recvfrom(50)
        msg = int(msg.decode())
        if msg:
            server.sendto("ACK".encode(), addr)
        else:
            return


def ackTCP(client):
    while True:
        msg = int(client.recv(50).decode())
        if msg:
            client.send("ACK".encode())
        else: 
            return


# MAIN ---------------------------------------------------------------------------
PORT = int(input("Digite a Porta a ser usada: "))
PROTOCOL = input("Selecione o Protocolo (TCP / UDP): ")

if PROTOCOL == "TCP":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(("0.0.0.0", PORT))
    server.listen()
    client, addr = server.accept()

    ackTCP(client)
elif PROTOCOL == "UDP":
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('', PORT))

    ackUDP(server)
else:
    print(f"Protocolo invalido: {PROTOCOL}")
    exit

server.close()