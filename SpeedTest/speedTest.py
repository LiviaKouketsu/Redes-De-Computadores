import socket
import time
import locale

exec_time = 20





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
    
    payload = "teste de rede *2025*"
    content = (payload * ((500 // len(payload) - 1)))
    packet_sent = 0
    bytes_sent = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        bytes_sent += sock.sendto((str(packet_sent).zfill(18)+"<>"+content).encode(), addr)
        packet_sent += 1

    printDataUpload(packet_sent, bytes_sent)
    




def uploadTCP(sock):
    
    payload = "teste de rede *2025*"
    content = (payload * ((500 // len(payload) - 1)))
    packet_sent = 0
    bytes_sent = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        bytes_sent += sock.send((str(packet_sent).zfill(18)+"<>"+content+"--").encode())             
        packet_sent += 1

    printDataUpload(packet_sent, bytes_sent)
    




def downloadUDP(sock):
    s = set()

    # Pacote Inicial do "fluxo"
    data, addr = sock.recvfrom(500)
    v = [data]

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(1)
    
    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: 
            data, addr = sock.recvfrom(500)
            v.append(data)
        except socket.timeout: break    

    v.pop()     # Por algum motivo tem um pacote void??

    bytes_recv = 0
    for pacote in v:
        bytes_recv += len(pacote)
        identifier, _ = pacote.decode().split("<>") 
        s.add(int(identifier))

    pckt_recv = len(v)
    lost_pckt = max(s) - (len(s) - 1)


    printDataDownload(bytes_recv, pckt_recv, lost_pckt)





def downloadTCP(sock):
    s = set()

    # Pacote Inicial do "fluxo"
    data = sock.recv(500)
    v = [data]

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(1)
    
    #Contagem de 20 segundos de envio 
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: 
            data = sock.recv(500)
            v.append(data)
        except socket.timeout: break

    v.pop()     # Por algum motivo tem um pacote void??

    bytes_recv = 0
    for conjunto in v:
        bytes_recv += len(conjunto)
        pacotesJuntos = conjunto.decode().split("--")
        for pacote in pacotesJuntos:
            try:
                identifier, _ = pacote.decode().split("<>") 
                s.add(int(identifier))
            except ValueError:
                print(pacote.decode())

    pckt_recv = len(v)
    lost_pckt = max(s) - (len(s) - 1)

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
