import socket
import struct
import array
import threading
import sys
import time
import random
import Queue
import os
import collections
import select

class udpi:

    # construtor da classe udpi
    def __init__(self, window_size, pl, pc, packet_size):


    # metodo bind
    # criar o socket UDP que sera usado para enviar ou receber dados
    # argumento addr - endereco do socket criado
    def bind(self, addr):


    # metodo reset
    # recria o socket UDP
    def reset(self):


    # metodo sendto
    # usado para enviar dados para um endereco especifico
    # argumento data - dado a ser enviado
    # addr - endereco de destino
    def sendto(self, data, addr):


    # metodo recvfrom
    # usado para receber dados
    # retorna os dados + endereco do emissor
    def recvfrom(self):


    # metodo de calculo de checksum
    # extraido do software Scapy
    # abrange little endian e big endian
    if struct.pack("H", 1) == "\x00\x01":
        def checksum(self, pkt):

    else:
        def checksum(self, pkt):


    # metodo verify_checksum
    # verifica a validade dos dados recebidos
    def verify_checksum(self, data, checksum):


    # metodo make_pkt
    # cria um pacote para ser enviado
    # argumentos
    # sequence_number - numero de sequencia do pacote
    # checksum
    # packet_type - tipo do pacote
    # data - dados a ser enviado
    # utiliza struct.pack para criar estruturas de dados do tamanho desejado
    # sequence_number - 4 bytes
    # checksum - 2 bytes
    # packet_type - 2 bytes
    # header (cabecalho) soma 8 bytes
    def make_pkt(self, sequence_number, checksum, packet_type, data):


    # metodo parse_packet
    # extrai informacoes de um pacote (header + payload)
    def parse_packet(self, packet):


    # metodo get_settings
    # retorna informacoes sobre o UDPI: endereco (IP + PORTA), tamanho da janela, probabilidade de perda, probaiblidade de corromper, tamanho de pacote
    def get_settings(self):


    # metodo close
    # fecha o socket utilizado
    def close(self):
        self.sock.close()
