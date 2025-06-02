import socket
import threading
import time

PYTHONHASHSEED = 7

separator = "<>"

def recvPckt(number_pckt, size_pckt):
    id_pckts = []

    numPkgRecv = 0
    numPkglost = 0
    numOutOrdr = 0
    numPkgCorr = 0

    for i in range(number_pckt):
        data, addr = sock.recvfrom(size_pckt)

        print(data.decode())

        packat = data.decode()

        if packat == "0":
            print("Finalizando recebimento de pacotes.")
            break

        header, payload, checksum = packat.split(separator)

        id_pckts.append(int(header))

        checkHash = hash(f"{header}{separator}{payload}")

        if checkHash != int(checksum):
            numPkgCorr += 1
            continue

    numPkgRecv = len(id_pckts)
    numPkglost = number_pckt - numPkgRecv
    numOutOrdr = sum(1 for i in range(1, len(id_pckts)) if id_pckts[i] < id_pckts[i - 1])

    printData(number_pckt, numPkgRecv, numPkglost, numOutOrdr, numPkgCorr)


def printData(number_pckt, numPkgRecv, numPkglost, numOutOrdr, numPkgCorr):
    print(f"Número de pacotes enviados: {number_pckt}")
    print(f"Número de pacotes recebidos: {numPkgRecv}")
    print(f"Número de pacotes perdidos: {numPkglost}")
    print(f"Número de pacotes recebidos na ordem errada: {numOutOrdr}")
    print(f"Número de pacotes corrompidos: {numPkgCorr}\n")


def sendPckt(number_pckt, size_pckt, default_msg, addr):
    number_sendPckt = 0
    
    separator = "<>"
    payload = default_msg 


    i = 0
    while (i < number_pckt):

        packet = f"{i}{separator}{payload}"
        checksum = hash(packet)
        packet = f"{packet}{separator}{checksum}"
        binary_packet = packet.encode()


        sock.sendto(binary_packet, addr)
        number_sendPckt += 1
        
        i+=1


HOST = input("Digite o IP a ser conectado: ")
PORT = int(input("Digite a Porta a ser usada: "))

addr = (HOST, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
# sock.settimeout(1)

default_msg = "#! Redes de Computadores UEL 2025 *#!"

thread = threading.Thread(target=recvPckt, args=(100, 500))
thread.start()
sendPckt(100, 500, default_msg, addr)
sock.sendto("0".encode(), addr)
thread.join()