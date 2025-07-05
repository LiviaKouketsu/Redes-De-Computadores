import socket
import time
import locale

exec_time = 20





def printDataUpload(packet_send, total_bits):
    print(f"Numero total de bytes: ", locale.format_string('%.2f', total_bits, grouping=True))
    print(f"Numero total de bytes por segundo: ", locale.format_string('%.2f', total_bits/exec_time, grouping=True))
    print(f"Numero de pacotes enviados: ", locale.format_string('%.2f', packet_send, grouping=True))
    print(f"Numero de pacotes enviados por segundo: ", locale.format_string('%.2f', packet_send/exec_time, grouping=True))





def printDataDownload(bytes_recv, pckt_recv, lost_pckt):
    print(f"Numero total de bytes recebidos:", locale.format_string('%d', bytes_recv, grouping=True))
    print(f"Numero total de bytes recebidos por segundo:", locale.format_string('%.2f', bytes_recv/exec_time, grouping=True))
    print(f"Numero total de pacotes recebidos:", locale.format_string('%d', pckt_recv, grouping=True))
    print(f"Numero total de pacotes recebidos por segundo:", locale.format_string('%.2f', pckt_recv / exec_time, grouping=True))
    print(f"Numero total de pacotes perdidos:", locale.format_string('%d', lost_pckt, grouping=True))





def uploadUDP(sock, target):
    
    payload = "teste de rede *2025*"
    content = (payload * (500 // len(payload))).encode()
    packet_send = 0
    total_bytes = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        total_bytes += sock.sendto(content, target)
        packet_send += 1

    # Espera receber o pedido por numero de pacotes, então o retorna
    sock.recvfrom(500)
    sock.sendto(f"{packet_send}".encode(), target)

    total_bits = total_bytes * 8
    printDataUpload(packet_send, total_bits)
    




def uploadTCP(sock):
    
    payload = "teste de rede *2025*"
    content = (payload * (500 // len(payload))).encode()
    packet_send = 0
    total_bytes = 0

    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        total_bytes += sock.send(content)             
        packet_send += 1

    # Espera receber o pedido por numero de pacotes, então o retorna
    sock.recv(500)
    sock.send(f"{packet_send}".encode())

    total_bits = total_bytes * 8
    printDataUpload(packet_send, total_bits)
    




def downloadUDP(sock):

    bytes_recv = 0
    pckt_recv = 0
    lost_pckt = 0

    # Pacote Inicial do "fluxo"
    data, addr = sock.recvfrom(500)
    bytes_recv += len(data)
    pckt_recv += 1

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(1)
    
    # Loop de (exec_time) segundos
    inicio = time.monotonic()
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: data, addr = sock.recvfrom(500)
        except socket.timeout: break

        bytes_recv += len(data)
        pckt_recv += 1

    # Desabilita o timeout e envia o pedido pelo numero de pacotes enviados
    sock.settimeout(None)
    sock.sendto("GET".encode(), addr)

    # Espera receber o pacote com o numero de pacotes, desconsiderando os pacotes de teste de rede (que dão exception pq são diferentes de um inteiro)
    msg, addr = sock.recvfrom(500)
    while not lost_pckt:
        try: int(msg.decode()) - pckt_recv
        except: msg, addr = sock.recvfrom(500)

    printDataDownload(bytes_recv, pckt_recv, lost_pckt)





def downloadTCP(sock):

    bytes_recv = 0
    pckt_recv = 0
    lost_pckt = 0

    # Pacote Inicial do "fluxo"
    data = sock.recv(500)
    bytes_recv += len(data)
    pckt_recv += 1

    # Define um timeout (garante que não fica travado esperando receber um pacote final no loop)
    sock.settimeout(1)
    inicio = time.monotonic()
    
    #Contagem de 20 segundos de envio 
    while(time.monotonic() - inicio <= exec_time):
        print(time.monotonic() - inicio)
        # Tenta receber um pacote se passa do tempo de timeout sai do loop pela exceção socket.timeout
        try: data = sock.recv(500)
        except socket.timeout: break

        bytes_recv += len(data)
        pckt_recv += 1

    # Desabilita o timeout e envia o pedido pelo numero de pacotes enviados
    sock.settimeout(None)
    sock.send("GET".encode())

    # Espera receber o pacote com o numero de pacotes, desconsiderando os pacotes de teste de rede (que dão exception pq são diferentes de um inteiro)
    msg = sock.recv(500)
    while not lost_pckt:
        try: lost_pckt = int(msg.decode()) - pckt_recv
        except: msg = sock.recv(500)

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
        
        sock.close()
        
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
addr = input("Entre com o endereço a ser conectado: ")
port = int(input("Digite a porta a ser utilizada: "))
mode = input("Modo de execução (upload, download): ")

if   tipo.lower() == 'udp':
    speedTestUDP(addr, port, mode)

elif tipo.lower() == 'tcp':
    speedTestTCP(addr, port, mode)

else:print("Tipo de conexão inválido.")
