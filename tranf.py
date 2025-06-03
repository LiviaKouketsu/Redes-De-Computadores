import socket
import threading
import time
import locale

# Define o locale para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

PYTHONHASHSEED = 7

separator = "<>"

def recvPckt(number_pckt, size_pckt):
    id_pckts = []

    numPkgRecv = 0
    numPkglost = 0
    numOutOrdr = 0
    numPkgCorr = 0

    for i in range(number_pckt):
        try:
            data, addr = sock.recvfrom(2000)
        except socket.timeout:
            numPkglost += 1
            print("Tempo limite de recebimento de pacotes excedido.")
            continue

        packat = data.decode()


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
    print(f"Numero de pacotes enviados:", locale.format_string('%.2f', number_pckt, grouping=True))
    print(f"Numero de pacotes recebidos:", locale.format_string('%.2f', numPkgRecv, grouping=True))
    print(f"Numero de pacotes perdidos:", locale.format_string('%.2f', numPkglost, grouping=True))
    print(f"Numero de pacotes recebidos na ordem errada:", locale.format_string('%.2f', numOutOrdr, grouping=True))
    print(f"Numero de pacotes corrompidos:", locale.format_string('%.2f', numPkgCorr, grouping=True))


def sendPckt(number_pckt, size_pckt, default_msg, addr):
    number_sendPckt = 0
    
    # payload = default_msg * size_pckt//(len(default_msg) + 1)
    payload = default_msg

    print(f"Enviando {number_pckt} pacotes de {size_pckt} bytes...")

    i = 0
    while (i < number_pckt):

        packet = f"{i}{separator}{payload}".ljust(size_pckt)
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

sock.sendto("SYN".encode(), addr)
data, add = sock.recvfrom(1024)
if data.decode() == "SYN" and add == addr: sock.sendto("ACK".encode(), addr)

sock.settimeout(0.1)

default_msg = "#! Redes de Computadores UEL 2025 *#!"

thread = threading.Thread(target=recvPckt, args=(1000, 500))
thread.start()
sendPckt(1000, 500, default_msg, addr)
thread.join()