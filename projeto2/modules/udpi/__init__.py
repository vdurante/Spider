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
        # atributos da classe udpi
        # window_size = tamanho da janela limite de pacotes a serem enviados simultaneamente
        # pl = probabilidade de um receptor perder o pacote
        # pc = probabilidade de um emissor corromper o pacote antes de enviar
        # packet_size = tamanho (em bytes) do payload de cada pacote
        # addr = endereco do socket
        self.window_size = window_size
        self.pl = float(pl)
        self.pc = float(pc)
        self.packet_size = int(packet_size)
        self.addr = ()

        # limitar o tamanho do pacote
        if self.packet_size > 1024:
            self.packet_size = 1024

    # metodo bind
    # criar o socket UDP que sera usado para enviar ou receber dados
    # argumento addr - endereco do socket criado
    def bind(self, addr):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)

        # blocking falso para nao ter travamento do programa ao tentar receber
        # dados
        self.sock.setblocking(0)

    # metodo reset
    # recria o socket UDP
    def reset(self):
        self.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.addr)
        self.sock.setblocking(0)

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

            # cada posicao dos fragmentos e igual a [pacote gerado, ultimo
            # momento de envio (explicado adiante)]
            fragments[sequence_number] = [self.make_pkt(
                sequence_number, self.checksum(fragment), 'DATA', fragment), 0]

            # numero de sequencia incrementado
            sequence_number += 1

        # ultimo numero de sequencia
        last_sequence_number = sequence_number

        # enquanto existirem fragmentos no dicionario
        while len(fragments) > 0:

            # dentro do range da base ate a base + tamanho da janela
            for i in range(base, base + n):

                # se o fragmento existir e o pacote ter sido enviado ha mas de
                # 0.2 segundos
                if i in fragments and (time.time() - fragments[i][1]) >= 0.2:

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
                        self.sock.sendto(fragments[i][0] + "_CORRUPTED_", addr)

                    # atualiza o tempo de ultimo envio deste pacote
                    fragments[i][1] = time.time()

            # bloco try/except - usado para tentar receber ACKS
            try:
                # tenta receber um pacote
                packet = self.sock.recv(2048)

                # extrai as informacoes do pacote recebido (cabecalho + payload)
                # numero de sequencia, checksum, tipo de pacote e os dados
                # (payload)
                sequence_number, checksum, packet_type, data = self.parse_packet(
                    packet)

                # calculo probabilistico de perda
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
                            # caso contrario esta recebendo um ACK que ja foi
                            # recebido anteriormente
                            if sequence_number in fragments:
                                # exclui o fragmento
                                del fragments[sequence_number]
                            # se ainda existirem fragmentos que nao receberam
                            # ACK
                            if len(fragments) > 0:
                                # atualiza a base pro menor numero de sequencia
                                # existente nos fragmentos
                                base = min(k for k in fragments.keys())
                        # se o tipo de pacote for 65280, eh um NAK
                        elif packet_type == 65280:
                            # pacote NAK
                            print str(sequence_number) + "\tRECEIVED\tNAK\t\t\tOK"

                            # se existir um fragmento com este numero de
                            # sequencia
                            if sequence_number in fragments:
                                # atualiza o tempo de ultimo envio deste pacote
                                # para que seja reenviado imediatamente
                                fragments[sequence_number][1] = -10

                    # se o pacote estiver corrompido
                    else:
                        # pacote corrompido - o emissor do ACK/NAK corrompeu o
                        # pacote
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
        # quer dizer que todos os pacotes ja foram enviados E seus respectivos
        # ACKS foram recebidos

        # declara um timer
        timer = time.time()

        print str(last_sequence_number) + "\tSEND\t\tBURST\t\t\tEND_OF_PACKETS"

        # cria um pacote do tipo EOP (End Of Packets)
        last_packet = self.make_pkt(last_sequence_number, self.checksum(
            '010101_END_OF_PACKETS_101010'), 'EOP', '010101_END_OF_PACKETS_101010')

        # durante 1 segundo, envia um burst de pacotes ao receptor, para garantir o recebimento do EOP
        # ha probabilidade de ser corrompido
        while time.time() - timer < 1:
            if random.uniform(0, 1) > self.pc:
                # envia EOP
                self.sock.sendto(last_packet, addr)
            else:
                # envia EOP corrompido
                self.sock.sendto(last_packet + "_CORRUPTED_", addr)

    # metodo recvfrom
    # usado para receber dados
    # retorna os dados + endereco do emissor
    def recvfrom(self):

        # reseta o socket
        self.reset()

        # fragmentos recebidos, correspondente aos enviados pelo servidor
        fragments = {}

        # ultimo pacote
        last_packet = -1

        # done - para verificar se acabaram-se os pacotes
        done = False

        # endereco do servidor
        addr = ()

        # enquanto nao estiver acabado
        while not done:

            # tenta receber um pacote
            try:
                # recvfrom usado para receber o endereco do servidor
                # tamanho 2048 para garantir recebimento do pacote inteiro
                packet, addr = self.sock.recvfrom(2048)

                # extrai as informacoes do pacote recebido (cabecalho +
                # payload)
                sequence_number, checksum, packet_type, data = self.parse_packet(
                    packet)

                # calculo probabilistico de perda de pacote
                if random.uniform(0, 1) > self.pl:
                    # pacote nao perdido

                    # verifica o checksum
                    if self.verify_checksum(data, checksum):
                        # checksum ok - pacote nao corrompido

                        # verifica o tipo de pacote
                        # se o pacote for do tipo 3855, eh um pacote de dados
                        if packet_type == 3855:
                            # pacote de dados
                            print str(sequence_number) + "\tRECEIVED\tPACKET\t\t\tOK"

                            # adiciona os dados do pacote aos fragmentos no
                            # numero de sequencia correspondente
                            fragments[sequence_number] = data

                            # calculo probabilistico para corromper o pacote
                            if random.uniform(0, 1) > self.pc:
                                # nao corromper
                                print str(sequence_number) + "\tSENT\t\tACK\t\t\tOK"

                                # envia ACK para o servidor
                                # utiliza-se payload igual a 39321 para o
                                # pacote ACK
                                self.sock.sendto(self.make_pkt(
                                    sequence_number, self.checksum(39321), 'ACK', 39321), addr)
                            else:
                                # corromper
                                print str(sequence_number) + "\tSENT\t\tACK\t\t\tCORRUPTED"

                                # envia ACK corrompido para o servidor
                                # utiliza-se payload igual a 1 para o pacote corrompido
                                # observe que o checksum eh calculado sobre
                                # outro payload (39321)
                                self.sock.sendto(self.make_pkt(
                                    sequence_number, self.checksum(39321), 'ACK', 1), addr)

                        # se o pacote for do tipo 15567, eh um pacote EOP (End
                        # of Packets)
                        if packet_type == 15567:
                            # pacote EOP
                            print str(sequence_number) + "\tRECEIVED\tPACKET\t\t\tEND_OF_PACKETS"

                            # ultimo pacote eh igual ao numero de sequencia do
                            # pacote EOP
                            last_packet = sequence_number

                            # done recebe true como flag de termino do servidor
                            done = True

                    # se o checksum falhar
                    else:
                        # pacote corrompido
                        print str(sequence_number) + "\tRECEIVED\tPACKET\t\t\tCORRUPTED"

                        # calculo probabilistico de corromper o NAK
                        if random.uniform(0, 1) > self.pc:
                            # nao corromper
                            print str(sequence_number) + "\tSENT\t\tNAK\t\t\tOK"

                            # envia NAK
                            self.sock.sendto(self.make_pkt(
                                sequence_number, self.checksum(39321), 'NAK', 39321), addr)
                        else:
                            # corromper
                            print str(sequence_number) + "\tSENT\t\tNAK\t\t\tCORRUPTED"

                            # envia NAK corrompido
                            self.sock.sendto(self.make_pkt(
                                sequence_number, self.checksum(39321), 'NAK', 1), addr)
                # se o pacote for perdido
                else:
                    # pacote perdido
                    print str(sequence_number) + "\tLOST\t\tPACKET\t\t\tON PURPOSE"
            # except - nenhum pacote foi recebido
            except socket.error:
                # prossiga com o loop
                pass

        # ordena os pacotes recebidos de acordo com os numeros de sequencia
        # evita que pacotes recebidos fora de ordem componham dados fora de
        # ordem
        ordered_fragments = collections.OrderedDict(sorted(fragments.items()))

        message = ""
        # para cada pedaco do fragmento
        for i in ordered_fragments:
            # concatena o fragmento na mensagem
            message += fragments[i]

        # retorna a mensagem e o endereco do servidor que enviou os dados
        return message, addr

    # metodo de calculo de checksum
    # extraido do software Scapy
    # abrange little endian e big endian
    if struct.pack("H", 1) == "\x00\x01":
        def checksum(self, pkt):
            pkt = str(pkt)
            if len(pkt) % 2 == 1:
                pkt += "\0"
            s = sum(array.array("H", pkt))
            s = (s >> 16) + (s & 0xffff)
            s += s >> 16
            s = ~s
            return s & 0xffff
    else:
        def checksum(self, pkt):
            pkt = str(pkt)
            if len(pkt) % 2 == 1:
                pkt += "\0"
            s = sum(array.array("H", pkt))
            s = (s >> 16) + (s & 0xffff)
            s += s >> 16
            s = ~s
            return (((s >> 8) & 0xff) | s << 8) & 0xffff

    # metodo verify_checksum
    # verifica a validade dos dados recebidos
    def verify_checksum(self, data, checksum):
        # bitwise AND do checksum recebido e a negacao do checksum calculado
        result = checksum & ~ self.checksum(data)

        # se for zero, dados nao esta corrompido
        if result == 0:
            return True
        else:
            return False

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
        sequence_number = struct.pack("=I", sequence_number)

        checksum = struct.pack("=H", checksum)

        # tipos de pacotes possiveis: ACK, NAK, DATA e EOP (end of packets)
        # cada um tem uma sequencia de bits correspondente (43690, 65280, 3855,
        # 15567)
        if packet_type == 'ACK':
            packet_type = struct.pack("=H", 43690)
        elif packet_type == 'NAK':
            packet_type = struct.pack("=H", 65280)
        elif packet_type == 'DATA':
            packet_type = struct.pack("=h", 3855)
        elif packet_type == 'EOP':
            packet_type = struct.pack("=h", 15567)

        # retorna o pacote composto por header + payload
        return sequence_number + checksum + packet_type + bytes(data)

    # metodo parse_packet
    # extrai informacoes de um pacote (header + payload)
    def parse_packet(self, packet):
        # numero de sequenceia correspondente aos 4 primeiros bytes
        sequence_number = struct.unpack('=I', packet[0:4])

        # checksum correspondente aos 2 bytes seguintes
        checksum = struct.unpack("=H", packet[4:6])

        # tipo do pacote correspondente aos 2 bytes seguintes
        packet_type = struct.unpack("=H", packet[6:8])

        # dados correspondente ao restante
        data = packet[8:]

        # retorna os valores acima extraidos
        return int(sequence_number[0]), int(checksum[0]), int(packet_type[0]), data

    # metodo get_settings
    # retorna informacoes sobre o UDPI: endereco (IP + PORTA), tamanho da
    # janela, probabilidade de perda, probaiblidade de corromper, tamanho de
    # pacote
    def get_settings(self):
        return (self.addr[0], self.addr[1], self.window_size, self.pl, self.pc, self.packet_size)

    # metodo close
    # fecha o socket utilizado
    def close(self):
        self.sock.close()
