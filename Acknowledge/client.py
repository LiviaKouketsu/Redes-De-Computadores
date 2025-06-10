import socket
import time

def printData(packagesLost, packagesSent, ACKRecv, inicioTimer, fimTimer):
    print(f"Pacotes Perdidos: {packagesLost}")
    print(f"Pacotes Enviados: {packagesSent}")
    print(f"ACKs Recebidos  : {ACKRecv}")
    print(f"Foram Foram levados {fimTimer - inicioTimer} segundos")
    print(60 * "-" + f"\n\n")

# Função para enviar pacotes UDP
def sendPackUDP(client, addr, numPackages):
    inicioTimer = time.time()

    packagesLost = 0
    packagesSent = 0
    ACKRecv = 0         
    for i in range(1, numPackages + 1):
        msg = (50 - len(str(i))) * '0' + str(i)
        while True:    
            client.sendto(msg.encode(), addr)
            packagesSent += 1
            try:
                client.recvfrom(50)
                ACKRecv += 1    
                break
            except socket.timeout:
                packagesLost += 1

    fimTimer = time.time()

    print(f"UDP - {numPkg} pacotes".ljust(60, "-"))
    printData(packagesLost, packagesSent, ACKRecv, inicioTimer, fimTimer)


# Função para enviar pacotes TCP
def sendPackTCP(client, numPackages):
    inicioTimer = time.time()

    packagesLost = 0
    packagesSent = 0
    ACKRecv = 0
    for i in range(1, numPackages + 1):
        msg = (50 - len(str(i))) * '0' + str(i)
        while True:
            client.send(msg.encode())
            packagesSent += 1
            try:
                client.recv(50)
                ACKRecv += 1
                break
            except socket.timeout:
                packagesLost += 1
    
    fimTimer = time.time()
    
    print(f"TCP - {numPkg} pacotes".ljust(60, "-"))
    printData(packagesLost, packagesSent, ACKRecv, inicioTimer, fimTimer)


# MAIN --------------------------------------------------------------------------------
HOST = input("Digite o IP a ser conectado: ")
PORT = int(input("Digite a Porta a ser usada: "))
PROTOCOL = input("Selecione o Protocolo (TCP / UDP): ")
numPkg = int(input("\nNumero de Pacotes a serem enviados: "))

addr = (HOST, PORT)

if PROTOCOL == "TCP":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(addr)
    
    client.settimeout(1)

    while numPkg > 0:
        sendPackTCP(client, numPkg)
        numPkg = int(input("Numero de Pacotes a serem enviados(0 para encerrar): "))

    client.send("0".encode())
elif PROTOCOL == "UDP":
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(1)

    while numPkg > 0:
        sendPackUDP(client, addr, numPkg)
        numPkg = int(input("Numero de Pacotes a serem enviados(0 para encerrar): "))
    
    client.sendto("0".encode(), addr)
else:
    print(f"Protocolo invalido: {PROTOCOL}")
    exit

client.close()