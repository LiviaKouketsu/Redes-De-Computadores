import socket
import time


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