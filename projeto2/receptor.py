from modules import udpi
import socket
import sys
import os
import time
import subprocess

# se o numero de argumentos nao for igual a 6
if(len(sys.argv) < 6 or len(sys.argv) > 6):
    # imprime uso correto e termina o programa
    print "Uso correto: python receptor.py <sender-hostname> <sender-porta> <filename> Pl PC"
    sys.exit()
else:
    # hostname do servidor (emissor)
    hostname = sys.argv[1]

    # porta do servidor (emissor)
    hostport = int(sys.argv[2])

    # valor default
    if(hostport < 1 or hostport > 65535):
        hostport = 5005

    # nome do arquivo desejado
    filename = sys.argv[3]

    # adiciona / antes do nome do arquivo se nao existir
    if filename[0]!="/":
        filename = "/"+filename
    if(filename[0] != "/"):
        filename = "/" + filename

    # tamanho da janela default
    cwnd = 10

    # probabilidade de perda
    pl = float(sys.argv[4])
    if(pl < 0 or pl >= 1):
        pl = 0.4

    # probabilidade de corromper
    pc = float(sys.argv[5])
    if(pc < 0 or pc >= 1):
        pc = 0.4


# CONFIGURACAO AVANCADA

# ip default
ip = '127.0.0.1'

# porta default
port = 5006

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

# bind no socket no IP e Porta (127.0.0.1, 5006)
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

# define a requisicao do arquivo de acordo com o padrao da aplicacao
# REQUEST <filename>
request = "REQUEST " + filename

print "SENDING REQUEST FOR FILE\t" + filename
print ""
time.sleep(10)

# envia o request ao servidor (emissor)
u.sendto(request, (hostname, hostport))

print "\nREQUEST SENT - WAITING RESPONSE FROM SERVER"
print ""
time.sleep(10)

# aguarda uma resposta do servidor (emissor)
response, sender_address = u.recvfrom()

print "\nRESPONSE RECEIVED"
print response
response = response.split("\t", 1)

# verifica se a resposta comeca com OK
if response[0]=="OK":
    # se comeca, o arquivo foi encontrado

    print "\nRECEIVING FILE"
    print ""
    time.sleep(10)

    # recebe o arquivo em formato de stirng
    data, sender_address = u.recvfrom()

    print "\n\nFILE SUCCESSFULLY RECEIVED"

    # monta o filepath para salvar o arquivo na pasta client
    filepath = os.path.dirname(os.path.abspath(__file__)) + "/client" + filename

    # se o arquivo existir, exclui
    if os.path.isfile(filepath):
        os.remove(filepath)

    # cria o arquivo com permissao de escrita
    f = open(filepath,'wb')

    # particiona a string recebida em pedacos de 1024 bytes
    for chunk in [data[i:i + 1024] for i in range(0, len(data), 1024)]:
        # escreve os pedacos no arquivo, um a um
        f.write(chunk)

    # bloco de codigo usado para abrir o arquivo recebido para exibicao
    # linux/windows/mac
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

print "\n\n"

# fecha o udpi (socket)
u.close()
