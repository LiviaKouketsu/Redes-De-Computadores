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

t1 = threading.Thread(target=timer, daemon=True)



tipo = input("UDP ou TCP: ").lower()
host = input("Entre com o endereço a ser conectado: ")
port = int(input("Digite a porta a ser utilizada: "))
mode = input("Modo de execução (upload, download): ")



mediada_Byteps = ["B", "kB", "MB", "GB"]
mediada_bitps = ["bps", "kbps", "Mbps", "Gbps"]
def getMedida(num_bits, vet_medida):
    i = 0
    while num_bits > 1024:
        num_bits /= 1024
        i += 1
    return locale.format_string('%.2f', num_bits, grouping=True) + ' ' + vet_medida[i]


def printDataUpload(packet_sent, bytes_sent):
    print(f"\nNumero total de bytes enviados:", getMedida(bytes_sent, mediada_Byteps))
    print(f"Numero total de pacotes enviados:", locale.format_string('%d', packet_sent, grouping=True))
    print(f"Numero total de bits enviados por segundo:", getMedida((8*bytes_sent)/exec_time, mediada_bitps))
    print(f"Numero total de pacotes enviados por segundo:", locale.format_string('%.2f', packet_sent/exec_time, grouping=True), "\n")




def printDataDownload(bytes_recv, pckt_recv, lost_pckt, non_recv):
    print(f"\nNumero total de bytes recebidos:", getMedida(bytes_recv, mediada_Byteps))
    print(f"Numero total de pacotes recebidos:", locale.format_string('%d', pckt_recv, grouping=True))
    print(f"Numero total de bits recebidos por segundo:", getMedida((8*bytes_recv)/exec_time, mediada_bitps))
    print(f"Numero total de pacotes recebidos por segundo:", locale.format_string('%.2f', pckt_recv / exec_time, grouping=True))
    print(f"Numero total de pacotes perdidos:", locale.format_string('%d', lost_pckt, grouping=True))
    print(f"Numero total de pacotes não recebidos:", locale.format_string('%d', non_recv, grouping=True), "\n")


# UPLOAD UDP ---------------------------------------------------------------------------------------------------------------


def printUploadUDP(sock, addr, packet_sent, bytes_sent):
    sock.settimeout(10)
    try:
        msg, _ = sock.recvfrom(500)
        bytes_recv, pckt_recv, lost_pckt, lenghtS = msg.decode().split("><")

        print(f"\nTaxa de UPLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
        printDataUpload(packet_sent, bytes_sent)
    
        non_recv = packet_sent - int(lenghtS)

        print(f"\nTaxa de DOWNLOAD na outra maquina({host}):")
        printDataDownload(int(bytes_recv), int(pckt_recv), int(lost_pckt), non_recv)
    except socket.timeout: print("Pacote referente a outra maquina não recebido")

    sock.sendto(f"{packet_sent}><{bytes_sent}".encode(), addr)



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

    printUploadUDP(sock, addr, packet_sent, bytes_sent)


# UPLOAD TCP ---------------------------------------------------------------------------------------------------------------


def printUploadTCP(sock, packet_sent, bytes_sent):
    sock.settimeout(10)
    try:
        msg = sock.recv(500)
        bytes_recv, pckt_recv, lost_pckt, lenghtS = msg.decode().split("><")

        print(f"\nTaxa de UPLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
        printDataUpload(packet_sent, bytes_sent)
        
        non_recv = packet_sent - int(lenghtS)

        print(f"\nTaxa de DOWNLOAD na outra maquina({host}):")
        printDataDownload(int(bytes_recv), int(pckt_recv), int(lost_pckt), non_recv)
    except socket.timeout: print("Pacote referente a outra maquina não recebido")
    
    sock.send(f"{packet_sent}><{bytes_sent}".encode())



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

    printUploadTCP(sock, packet_sent, bytes_sent)
    

# DOWNLOAD -----------------------------------------------------------------------------------------------------------------


def reestruturarPacotes (v):
    s = set()

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

    num_pckt = len(s)
    pckt_recv = len(v)
    lost_pckt = max(s) - (len(s) - 1)

    return bytes_recv, pckt_recv, lost_pckt, num_pckt


# DOWNLOAD UDP -------------------------------------------------------------------------------------------------------------


def printDownloadUDP(sock, addr, bytes_recv, pckt_recv, lost_pckt, lenghtS):
    sock.sendto(f"{bytes_recv}><{pckt_recv}><{lost_pckt}><{lenghtS}".encode(), addr)
    sock.settimeout(10)
    try:
        msg, _ = sock.recvfrom(500)
        while b"><" not in msg: msg, _ = sock.recvfrom(500)
        packet_sent, bytes_sent = msg.decode().split("><")

        non_recv = int(packet_sent) - lenghtS
        print(f"\nTaxa de DOWNLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
        printDataDownload(bytes_recv, pckt_recv, lost_pckt, non_recv)

        print(f"\nTaxa de UPLOAD na outra maquina({host}):")
        printDataUpload(int(packet_sent), int(bytes_sent))
    except socket.timeout: print("Pacote referente a outra maquina não recebido")



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

    bytes_recv, pckt_recv, lost_pckt, lenghtS = reestruturarPacotes(v)
    printDownloadUDP(sock, addr, bytes_recv, pckt_recv, lost_pckt, lenghtS)


# DOWNLOAD TCP -------------------------------------------------------------------------------------------------------------


def printDownloadTCP(sock, bytes_recv, pckt_recv, lost_pckt, lenghtS):
    
    sock.send(f"{bytes_recv}><{pckt_recv}><{lost_pckt}><{lenghtS}".encode())
    sock.settimeout(10)
    
    try:
        msg = sock.recv(500)
        while b"><" not in msg: msg = sock.recv(500)
        if b"--" in msg: _, msg = msg.split(b"--", 1)
        packet_sent, bytes_sent = msg.decode().split("><")
        
        non_recv = int(packet_sent) - lenghtS
        print(f"\nTaxa de DOWNLOAD nessa maquina({socket.gethostbyname(socket.gethostname())}):")
        printDataDownload(bytes_recv, pckt_recv, lost_pckt, non_recv)

        print(f"\nTaxa de UPLOAD na outra maquina({host}):")
        printDataUpload(int(packet_sent), int(bytes_sent))
    except socket.timeout: print("Pacote referente a outra maquina não recebido")



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

    bytes_recv, pckt_recv, lost_pckt, lenghtS = reestruturarPacotes(v)
    printDownloadTCP(sock, bytes_recv, pckt_recv, lost_pckt, lenghtS)
    

# BASE SOCKET --------------------------------------------------------------------------------------------------------------



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