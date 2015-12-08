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
        # reseta o socket
        self.reset()

        # fragmentos do dado
        fragments = {}

        # numero de sequencia de 32 bits
        sequence_number = random.randint(0, 4294967295)

        # base da janela
        base = sequence_number

        # proximo numero de sequencia (inicia na base)
        nextseqnum = sequence_number

        # tamanho da janela de envio
        n = self.window_size

        # fragmenta os dados em porcoes iguais de tamanho packet_size
        for fragment in [data[i:i + self.packet_size] for i in range(0, len(data), self.packet_size)]:

            # cada posicao dos fragmentos e igual a [pacote gerado, ultimo momento de envio (explicado adiante)]
            fragments[sequence_number] = [self.make_pkt(sequence_number, self.checksum(fragment), 'DATA', fragment), 0]

            # numero de sequencia incrementado
            sequence_number+=1

        # ultimo numero de sequencia
        last_sequence_number = sequence_number

        # enquanto existirem fragmentos no dicionario
        while len(fragments)>0:

            # dentro do range da base ate a base + tamanho da janela
            for i in range(base, base+n):

                # se o fragmento existir e o pacote ter sido enviado ha mas de 0.2 segundos
                if i in fragments and (time.time() - fragments[i][1])>=0.2:

                    # calculo probabilistico de corromper
                    if random.uniform(0, 1) > self.pc:
                        # nao corromper
                        print str(i) + "\tSENT\t\tPACKET\t\t\tOK"

                        # envia o pacote nao corrompido
                        self.sock.sendto(fragments[i][0], addr)
                    else:
                        # corromper
                        print str(i) + "\tSENT\t\tPACKET\t\t\tCORRUPTED"

                        # envia o pacote corrompido, adicionando string _CORRUPTED_ ao final do pacote
                        # checksum tera falha no recebimento do pacote
                        self.sock.sendto(fragments[i][0]+"_CORRUPTED_", addr)

                    # atualiza o tempo de ultimo envio deste pacote
                    fragments[i][1] = time.time()

            # bloco try/except - usado para tentar receber ACKS
            try:
                # tenta receber um pacote
                packet = self.sock.recv(2048)

                # extrai as informacoes do pacote recebido (cabecalho + payload)
                # numero de sequencia, checksum, tipo de pacote e os dados (payload)
                sequence_number, checksum, packet_type, data = self.parse_packet(packet)

                #calculo probabilistico de perda
                if random.uniform(0, 1) > self.pl:
                    # pacote nao perdido

                    # verifica se o checksum e valido
                    if self.verify_checksum(data, checksum):
                        # nao corrompido

                        # se o tipo de pacote for 43690, eh um ACK
                        if packet_type == 43690:
                            # pacote ack
                            print str(sequence_number) + "\tRECEIVED\tACK\t\t\tOK"

                            # se existir um fragmento com este numero de sequencia
                            # caso contrario esta recebendo um ACK que ja foi recebido anteriormente
                            if sequence_number in fragments:
                                # exclui o fragmento
                                del fragments[sequence_number]
                            # se ainda existirem fragmentos que nao receberam ACK
                            if len(fragments)>0:
                                # atualiza a base pro menor numero de sequencia existente nos fragmentos
                                base = min(k for k in fragments.keys())
                        # se o tipo de pacote for 65280, eh um NAK
                        elif packet_type == 65280:
                            # pacote NAK
                            print str(sequence_number) + "\tRECEIVED\tNAK\t\t\tOK"

                            # se existir um fragmento com este numero de sequencia
                            if sequence_number in fragments:
                                # atualiza o tempo de ultimo envio deste pacote para que seja reenviado imediatamente
                                fragments[sequence_number][1] = -10

                    # se o pacote estiver corrompido
                    else:
                        # pacote corrompido - o emissor do ACK/NAK corrompeu o pacote
                        print str(sequence_number) + "\tRECEIVED\tACK/NAK\t\t\tCORRUPTED"
                # pacote periddo
                else:
                    # perde o ACK/NAK pacote de proposito
                    print str(sequence_number) + "\tLOST\t\tACK/NAK\t\t\tON PURPOSE"
            # caso nao seja recebido nada pelo socket
            except socket.error:
                # nao faz nada, apenas continua
                pass

        # fora do while dos fragmentos
        # quer dizer que todos os pacotes ja foram enviados E seus respectivos ACKS foram recebidos

        # declara um timer
        timer = time.time()

        print str(last_sequence_number) + "\tSEND\t\tBURST\t\t\tEND_OF_PACKETS"

        # cria um pacote do tipo EOP (End Of Packets)
        last_packet = self.make_pkt(last_sequence_number, self.checksum('010101_END_OF_PACKETS_101010'), 'EOP', '010101_END_OF_PACKETS_101010')

        # durante 1 segundo, envia um burst de pacotes ao receptor, para garantir o recebimento do EOP
        # ha probabilidade de ser corrompido
        while time.time()-timer < 1:
            if random.uniform(0, 1) > self.pc:
                # envia EOP
                self.sock.sendto(last_packet, addr)
            else:
                # envia EOP corrompido
                self.sock.sendto(last_packet+"_CORRUPTED_", addr)

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
