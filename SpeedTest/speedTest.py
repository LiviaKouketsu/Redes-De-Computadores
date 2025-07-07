import socket
import time
import locale
import threading

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


payload = "teste de rede *2025*"
content = (payload * (498 // len(payload))).encode() + payload[:18].encode() + b"--"

exec_time = 20

def timer():
    for i in range(1, exec_time):
        time.sleep(1)
        print(i)

t1 = threading.Thread(target=timer)





def printDataUpload(packet_sent, bytes_sent):
    print(f"Numero total de bytes: ", locale.format_string('%.2f', bytes_sent, grouping=True))
    print(f"Numero total de bits enviados por segundo: ", locale.format_string('%.2f', (8*bytes_sent)/exec_time, grouping=True))
    print(f"Numero total de pacotes enviados: ", locale.format_string('%.2f', packet_sent, grouping=True))
    print(f"Numero total de pacotes enviados por segundo: ", locale.format_string('%.2f', packet_sent/exec_time, grouping=True))





def printDataDownload(bytes_recv, pckt_recv, lost_pckt):
    print(f"Numero total de bytes recebidos:", locale.format_string('%d', bytes_recv, grouping=True))
    print(f"Numero total de bits recebidos por segundo:", locale.format_string('%.2f', (8*bytes_recv)/exec_time, grouping=True))
    print(f"Numero total de pacotes recebidos:", locale.format_string('%d', pckt_recv, grouping=True))
    print(f"Numero total de pacotes recebidos por segundo:", locale.format_string('%.2f', pckt_recv / exec_time, grouping=True))
    print(f"Numero total de pacotes perdidos:", locale.format_string('%d', lost_pckt, grouping=True))





def uploadUDP(sock, addr):
    
    packet_sent = 0
    bytes_sent = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    tempo = exec_time + inicio
    t1.start()
    while(time.monotonic() < tempo):
        bytes_sent += sock.sendto(content, addr)
        packet_sent += 1
    
    sock.recvfrom(500)
    sock.sendto(f"{packet_sent}".encode(), addr)

    printDataUpload(packet_sent, bytes_sent)
    




def uploadTCP(sock):
    
    packet_sent = 0
    bytes_sent = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    tempo = exec_time + inicio
    t1.start()
    while(time.monotonic() < tempo):
        bytes_sent += sock.send(content)             
        packet_sent += 1

    sock.recvfrom(500)
    sock.send(f"{packet_sent}".encode())

    printDataUpload(packet_sent, bytes_sent)
    




def downloadUDP(sock):
    # Pacote Inicial do "fluxo"
    data, addr = sock.recvfrom(500)
    v = [data]

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(0.1)
    
    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    tempo = exec_time + inicio
    t1.start()
    while(time.monotonic() < tempo):
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: 
            data, addr = sock.recvfrom(500)
            v.append(data)
        except socket.timeout: continue

    buffer = ""
    bytes_recv = 0
    pckt_recv2 = 0
    for data in v:
        bytes_recv += len(data)

        buffer += data.decode()
        while "--" in buffer:
            pacote, buffer = buffer.split("--", 1)
            pckt_recv2 += 1

    pckt_recv = len(v)
    
    # Desabilita o timeout e envia o pedido pelo numero de pacotes enviados
    sock.settimeout(None)
    sock.sendto("GET".encode(), addr)

    # Espera receber o pacote com o numero de pacotes, desconsiderando os pacotes de teste de rede (que dão exception pq são diferentes de um inteiro)
    # Repete o processo em caso de erro para tentar encontrar o pacote com o numero de pacotes
    pckt_sent = 0
    msg, _ = sock.recvfrom(500)
    while not pckt_sent:
        try: pckt_sent = int(msg.decode())
        except ValueError: msg, _ = sock.recvfrom(500)

    lost_pckt = pckt_sent - pckt_recv2

    printDataDownload(bytes_recv, pckt_recv, lost_pckt)





def downloadTCP(sock):

    # Pacote Inicial do "fluxo"
    data = sock.recv(500)
    v = [data]

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(0.1)
    
    #Contagem de 20 segundos de envio 
    inicio = time.monotonic()
    tempo = exec_time + inicio
    t1.start()
    while(time.monotonic() < tempo):
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: 
            data = sock.recv(500)
            v.append(data)
        except socket.timeout: continue

    buffer = ""
    bytes_recv = 0
    pckt_recv2 = 0
    for data in v:
        bytes_recv += len(data)

        buffer += data.decode()
        while "--" in buffer:
            pacote, buffer = buffer.split("--", 1)
            pckt_recv2 += 1

    pckt_recv = len(v)

    # Desabilita o timeout e envia o pedido pelo numero de pacotes enviados
    sock.settimeout(None)
    sock.send("GET".encode())

    # Espera receber o pacote com o numero de pacotes, desconsiderando os pacotes de teste de rede (que dão exception pq são diferentes de um inteiro)
    # Repete o processo em caso de erro para tentar encontrar o pacote com o numero de pacotes
    pckt_sent = 0
    msg = sock.recv(500)
    while not pckt_sent:
        try: pckt_sent = int(msg.decode())
        except ValueError: msg = sock.recv(500)
    
    lost_pckt = pckt_sent - pckt_recv2

    printDataDownload(bytes_recv, pckt_recv, lost_pckt)





def speedTestUDP(host, port, execType):

    print(f"Connected to {host}:{port}")

    if execType == 'upload':

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("Iniciando teste de upload...")
        uploadUDP(sock, (host, port))
        
        sock.close()
        
    elif execType == 'download':
        # Create a TCP socket        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', port))
        
        print("Iniciando teste de download...")
        downloadUDP(sock)
        
        sock.close()
    
    else: print("tipo de execução inválido.")





def speedTestTCP(host, port, execType):

    print(f"Connected to {host}:{port}")

    if execType == 'upload':

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        print("Iniciando teste de upload...")
        uploadTCP(sock)
        
    elif execType == 'download':
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.bind(('0.0.0.0', port))
        sock.listen()
        sock, addr = sock.accept()
        
        print("Iniciando teste de download...")
        downloadTCP(sock)
        
        sock.close()

    else: print("tipo de execução inválido.")





tipo = input("UDP ou TCP: ").lower()
host = input("Entre com o endereço a ser conectado: ")
port = int(input("Digite a porta a ser utilizada: "))
mode = input("Modo de execução (upload, download): ")

if   tipo.lower() == 'udp':
    speedTestUDP(host, port, mode)

elif tipo.lower() == 'tcp':
    speedTestTCP(host, port, mode)

else:print("Tipo de conexão inválido.")
