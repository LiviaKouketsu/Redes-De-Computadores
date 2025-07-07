import socket
import time
import locale
import threading


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


payload = "teste de rede *2025*"
content = ("<>" + (payload * ((500 // len(payload) - 1))) + "--").encode()

exec_time = 20

def timer():
    for i in range(1, exec_time + 1):
        time.sleep(1)
        print(i)

t1 = threading.Thread(target=timer)



tipo = input("UDP ou TCP: ").lower()
host = input("Entre com o endereço a ser conectado: ")
port = int(input("Digite a porta a ser utilizada: "))
mode = input("Modo de execução (upload, download): ")





def printDataUpload(packet_sent, bytes_sent):
    print(f"Numero total de bytes: ", locale.format_string('%d', bytes_sent, grouping=True))
    print(f"Numero total de bits enviados por segundo: ", locale.format_string('%.2f', (8*bytes_sent)/exec_time, grouping=True))
    print(f"Numero total de pacotes enviados: ", locale.format_string('%d', packet_sent, grouping=True))
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
        bytes_sent += sock.sendto(b''.join([str(packet_sent).zfill(16).encode(), content]), addr)
        packet_sent += 1

    print(f"\nTaxa de UPLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
    printDataUpload(packet_sent, bytes_sent)

    sock.settimeout(None)
    msg, _ = sock.recvfrom(500)
    bytes_recv, pckt_recv, lost_pckt = msg.decode().split("><")
    sock.sendto(f"{packet_sent}><{bytes_sent}".encode(), addr)

    print(f"\nTaxa de DOWNLOAD na outra maquina({host}):")
    printDataDownload(int(bytes_recv), int(pckt_recv), int(lost_pckt))




def uploadTCP(sock):
    
    packet_sent = 0
    bytes_sent = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    tempo = exec_time + inicio
    t1.start()
    while(time.monotonic() < tempo):
        bytes_sent += sock.send(b''.join([str(packet_sent).zfill(16).encode(), content]))             
        packet_sent += 1

    print(f"\nTaxa de UPLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
    printDataUpload(packet_sent, bytes_sent)

    sock.settimeout(None)
    bytes_recv, pckt_recv, lost_pckt = sock.recv(500).decode().split("><")
    sock.send(f"{packet_sent}><{bytes_sent}".encode())

    print(f"\nTaxa de DOWNLOAD na outra maquina({host}):")
    printDataDownload(int(bytes_recv), int(pckt_recv), int(lost_pckt))
    




def downloadUDP(sock):
    s = set()

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
    for data in v:
        bytes_recv += len(data)

        buffer += data.decode()
        while "--" in buffer:
            pacote, buffer = buffer.split("--", 1)

            try:
                identifier, _ = pacote.split("<>") 
                s.add(int(identifier))
            except ValueError: continue

    pckt_recv = len(v)
    lost_pckt = max(s) - (len(s) - 1)

    print(f"\nTaxa de DOWNLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
    printDataDownload(bytes_recv, pckt_recv, lost_pckt)

    sock.settimeout(None)
    sock.sendto(f"{bytes_recv}><{pckt_recv}><{lost_pckt}".encode(), addr)
    msg, _ = sock.recvfrom(500)
    while b"><" not in msg:
        msg, _ = sock.recvfrom(500)
    try: packet_sent, bytes_sent = msg.decode().split("><")
    except: print(msg.decode())

    print(f"\nTaxa de UPLOAD na outra maquina({host}):")
    printDataUpload(int(packet_sent), int(bytes_sent))





def downloadTCP(sock):
    s = set()

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
    for data in v:
        bytes_recv += len(data)

        buffer += data.decode()
        while "--" in buffer:
            pacote, buffer = buffer.split("--", 1)

            try:
                identifier, _ = pacote.split("<>") 
                s.add(int(identifier))
            except ValueError: continue

    pckt_recv = len(v)
    lost_pckt = max(s) - (len(s) - 1)

    print(f"\nTaxa de DOWNLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
    printDataDownload(bytes_recv, pckt_recv, lost_pckt)

    sock.settimeout(None)
    sock.send(f"{bytes_recv}><{pckt_recv}><{lost_pckt}".encode())
    msg = sock.recv(500)
    while b"><" not in msg:
        msg = sock.recv(500)
    packet_sent, bytes_sent = msg.decode().split("><")

    print(f"\nTaxa de UPLOAD na outra maquina({host}):")
    printDataUpload(int(packet_sent), int(bytes_sent))





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


if   tipo.lower() == 'udp':
    speedTestUDP(host, port, mode)

elif tipo.lower() == 'tcp':
    speedTestTCP(host, port, mode)

else:print("Tipo de conexão inválido.")