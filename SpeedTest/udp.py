import socket 
import time 
import locale

HOST = input("IP: ")
PORT = int(input("Porta: "))

target = (HOST, PORT)       #alvo da transmissao
eu = ('127.0.0.1', PORT)    #meu endereco a porta 
me = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #udp
me.bind(eu)                    ##link meu endereco a porta

def print_data(send, total_bits):
    print(f"Numero total de bytes: ", locale.format_string('%.2f', total_bits, grouping=True))
    print(f"Numero de pacotes enviados: ", locale.format_string('%.2f', send, grouping=True))
    print(f"Numero de pacotes enviados por segundo: ", locale.format_string('%.2f', send/20, grouping=True))

def upload(target):
    
    payload = "teste de rede *2025*"
    content = (payload * (500 // len(payload))).encode()
    packet_send = 0

    inicio = time.time()
    
    #Contagem de 20 segundos de envio 
    while(time.monotonic() - inicio <= 20):
        total_bytes += me.sendto(content, target)
        packet_send += 1

    me.recvfrom(500)
    #envio do nro de pacotes gerados e enviados 
    me.sendto(f'{packet_send}', target)

    total_bits = total_bytes * 8
    #total_bits = packet_send * 500 * 8
    print_data()
    