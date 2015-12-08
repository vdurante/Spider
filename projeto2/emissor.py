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
