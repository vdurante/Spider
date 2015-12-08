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
