import socket 
import time 
import locale

HOST = input("IP: ")
PORT = int(input("Porta: "))

target = (HOST, PORT)                                   #alvo da conexao
me = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #tcp
me.connect(target)                                      #quem eu estou me conectando

def print_data(send, total_bits):
    print(f"Numero total de bytes: ", locale.format_string('%.2f', total_bits, grouping=True))
    print(f"Numero de pacotes enviados: ", locale.format_string('%.2f', send, grouping=True))
    print(f"Numero de pacotes por segundo: ", locale.format_string('%.2f', send/20, grouping=True))

def upload(target):
    
    payload = "teste de rede *2025*"
    content = (payload * (500 // len(payload))).encode()
    packet_send = 0

    inicio = time.time()
    
    #Contagem de 20 segundos de envio 
    while(time.monotonic() - inicio <= 20):
        me.sendall(content)             #nao retorna nro de bytes
        packet_send += 1


    me.recv(500)
    #envio do nro de pacotes gerados e enviados 
    me.send(f'{packet_send}')

    total_bits = packet_send * 500 * 8
    print_data()
    