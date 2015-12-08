from modules import udpi

import socket
import sys
import os
import time

# se o numero de argumentos nao for igual a 5
if(len(sys.argv) < 5 or len(sys.argv) > 5):
    # imprime uso correto e termina o programa
    print "Uso correto: python emissor.py <numero de porta> CWnd Pl PC"
    sys.exit()
else:
    # porta
    port = int(sys.argv[1])

    # limita a porta
    if(port < 1 or port > 65535):
        port = 5005

    # tamanho da janela
    cwnd = int(sys.argv[2])

    # limita o tamanho da janela
    if(cwnd < 0 or cwnd > 50):
        cwnd = 10

    # probabilidade de perda
    pl = float(sys.argv[3])

    # limita a probabilidade de perda
    if(pl < 0 or pl >= 1):
        pl = 0.4

    # probabilidade de corromper
    pc = float(sys.argv[4])

    # limita a probaiblidade de corromper
    if(pc < 0 or pc >= 1):
        pc = 0.4


# CONFIGURACAO AVANCADA

# ip default
ip = '127.0.0.1'

# tamanho de pacote default (bytes)
packet_size = 1024

# FIM CONFIGURACAO AVANCADA


# decalara uma variavel da classe udpi
# argumentos
# tamanho da janela
# probabilidade de perda
# probabilidade de corromper
# tamanho do pacote (1024)
u = udpi.udpi(cwnd, pl, pc, packet_size)

# bind no socket no IP e Porta definidos
# cria o socket
u.bind((ip, port))

# get settings, para imprimir a configuracoa do udpi
settings = u.get_settings()


print "\nUDPI SETUP SUCCESSFULL\n\n"

print "IP\t\t"+str(settings[0])
print "PORT\t\t"+str(settings[1])
print "CWND\t\t"+str(settings[2])
print "PL\t\t"+str(settings[3])
print "PC\t\t"+str(settings[4])
print "PCKT_SIZE\t"+str(settings[5])
print ""

print "WAITING REQUEST FROM CLIENT"
print ""

# todos os sleeps servem apenas para visualizacao melhor do processo do envio/recebimento
# podem ser retirados para execucao mais rapida
time.sleep(10)

# recebe request do receptor
# note que o endereco tambem eh recebido
request, sender_address = u.recvfrom()

print "\nREQUEST RECEIVED\t" + request
print "\nSENDING RESPONSE"
print ""

request = request.split(" ", 1)

# supoe-se que o request tenha o seguinte formato
# REQUEST <filename>

# se a primeira palavra da menasgem recebida for REQUEST
if request[0]=="REQUEST":

    # adiciona / ao nome do arquivo se ja nao existir
    if request[1][0]!="/":
        request[1] = "/"+request[1]

    # define o filepath dentro da pasta server
    filepath = os.path.dirname(os.path.abspath(__file__)) + "/server" + request[1]

    # se o arquivo existir
    if os.path.isfile(filepath):
        print "OK\t0\tFILE FOUND. PREPARE FOR RECEIVING IT\t" + request[1]
        print ""
        time.sleep(10)

        # envia resposta no seguinte formato
        # OK    0  FILE FOUND. PREPARE FOR RECEIVING IT
        u.sendto("OK\t0\tFILE FOUND. PREPARE FOR RECEIVING IT\t", sender_address)
        print "\nRESPONSE SENT. SENDING THE FILE"
        print ""

        time.sleep(10)

        # abre o arquivo com permissao de leitura
        f = open(filepath,'rb')
        chunk = f.read(1024)
        file_data = ""

        # transforma o arquivo em uma string de dados
        while (chunk):
            file_data+=str(chunk)
            chunk = f.read(1024)

        # envia a string de dados ao receptor
        u.sendto(file_data, sender_address)

        print "\n\nFILE SUCCESSFULLY SENT"

    # se o arquivo nao existir
    else:
        # envia resposta
        # ERROR 2   FILE NOT FOUND  <filename>
        print "ERROR\t2\tFILE NOT FOUND\t" + ' '.join(str(x) for x in request)

        time.sleep(10)

        u.sendto("ERROR\t2\tFILE NOT FOUND", sender_address)

# se request nao estiver dentro do padrao
else:
    # envia resposta
    # ERROR 1   COMMAND NOT RECOGNIZED  <request recebido>
    print "ERROR\t1\tCOMMAND NOT RECOGNIZED\t" + ' '.join(str(x) for x in request)
    time.sleep(10)
    u.sendto("ERROR\t1\tCOMMAND NOT RECOGNIZED", sender_address)

print "\n\n"

# fecha o udpi (socket)
u.close()
