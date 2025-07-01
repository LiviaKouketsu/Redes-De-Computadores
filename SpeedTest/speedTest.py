import socket
import time

def downloadTCP(sock):
   
    bytes_recv = 0
    pckt_recv = 0
    lost_pckt = 0

    data, addr = sock.recvfrom(500)

    start_time = time.time()
    duracao = time.time() - start_time
    bytes_recv += len(data)
    pckt_recv += 1

    while duracao < 20:
        data, addr = sock.recvfrom(500)

        bytes_recv += len(data)
        pckt_recv += 1
        duracao = time.time() - start_time

    sock.sendto("Qual a quantidade de pacotes?")
    send_pckt, addr = sock.recvfrom(500)

    lost_pckt = send_pckt - pckt_recv

    printData(bytes_recv, pckt_recv, duracao, lost_pckt)

def downloadUDP(sock):
   
    bytes_recv = 0
    pckt_recv = 0
    lost_pckt = 0

    data, addr = sock.recv(500)

    start_time = time.time()
    duracao = time.time() - start_time
    bytes_recv += len(data)
    pckt_recv += 1

    while duracao < 20:
        data, addr = sock.recv(500)

        bytes_recv += len(data)
        pckt_recv += 1
        duracao = time.time() - start_time

    sock.sendto("Qual a quantidade de pacotes?")
    send_pckt, addr = sock.recv(500)
     
    lost_pckt = send_pckt - pckt_recv

    printData(bytes_recv, pckt_recv, duracao, lost_pckt)

def printData(bytes_recv, pckt_recv, duracao, lost_pckt):
    print(f"Total de bytes recebidos: {bytes_recv}")
    print(f"Total de pacotes recebidos: {pckt_recv}")
    print(f"Total de bytes enviados por segundo: {bytes_recv/duracao}")
    print(f"Total de pacotes enviados por segundo: {pckt_recv/duracao}")
    print(f"Total de pacotes perdidos: {lost_pckt}")


# Function to perform a TCP speed test
def speedTestUDP(host, port, execType):

    print(f"Connected to {host}:{port}")

    if execType == 'upload':
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("Iniciando teste de upload...")
        
        uploadUDP(sock)
        
        sock.close()
        
    elif execType == 'download':
        # Create a TCP socket        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.bind(('0.0.0.0', port))
        
        print("Iniciando teste de download...")

        downloadUDP(sock)
        
        sock.close()
    
    else:
        print("tipo de execução inválido.")
        sock.close()
        return


# Function to perform a TCP speed test
def speedTestTCP(host, port, execType):

    print(f"Connected to {host}:{port}")

    if execType == 'upload':
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.connect((host, port))

        print("Iniciando teste de upload...")
        
        uploadTCP(sock)
        
        sock.close()
        
    elif execType == 'download':
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        sock, addr = sock.accept()
        
        print("Iniciando teste de download...")
        
        downloadTCP(sock)
        
        sock.close()
    else:
        print("tipo de execução inválido.")


type = input("UDP ou TCP: ").lower()
addr = input("Entre com o endereço a ser conectado: ")
port = int(input("Digite a porta a ser utilizada: "))
mode = input("Modo de execução (upload, download): ")

if   type.lower() == 'udp':
    speedTestUDP(addr, port, mode)
elif type.lower() == 'tcp':
    speedTestTCP(addr, port, mode)
else:print("Tipo de conexão inválido.")