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

                # extrai as informacoes do pacote recebido (cabecalho + payload)
                sequence_number, checksum, packet_type, data = self.parse_packet(packet)

                # calculo probabilistico de perda de pacote
                if random.uniform(0, 1) > self.pl:
                    # pacote nao perdido

                    # verifica o checksum
                    if self.verify_checksum(data, checksum):
                        # checksum ok - pacote nao corrompido

                        # verifica o tipo de pacote
                        # se o pacote for do tipo 3855, eh um pacote de dados
                        if packet_type==3855:
                            # pacote de dados
                            print str(sequence_number) + "\tRECEIVED\tPACKET\t\t\tOK"

                            # adiciona os dados do pacote aos fragmentos no numero de sequencia correspondente
                            fragments[sequence_number] = data

                            # calculo probabilistico para corromper o pacote
                            if random.uniform(0, 1) > self.pc:
                                # nao corromper
                                print str(sequence_number) + "\tSENT\t\tACK\t\t\tOK"

                                # envia ACK para o servidor
                                # utiliza-se payload igual a 39321 para o pacote ACK
                                self.sock.sendto(self.make_pkt(sequence_number, self.checksum(39321), 'ACK', 39321), addr)
                            else:
                                # corromper
                                print str(sequence_number) + "\tSENT\t\tACK\t\t\tCORRUPTED"

                                # envia ACK corrompido para o servidor
                                # utiliza-se payload igual a 1 para o pacote corrompido
                                # observe que o checksum eh calculado sobre outro payload (39321)
                                self.sock.sendto(self.make_pkt(sequence_number, self.checksum(39321), 'ACK', 1), addr)

                        # se o pacote for do tipo 15567, eh um pacote EOP (End of Packets)
                        if packet_type==15567:
                            # pacote EOP
                            print str(sequence_number) + "\tRECEIVED\tPACKET\t\t\tEND_OF_PACKETS"

                            # ultimo pacote eh igual ao numero de sequencia do pacote EOP
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
                            self.sock.sendto(self.make_pkt(sequence_number, self.checksum(39321), 'NAK', 39321), addr)
                        else:
                            # corromper
                            print str(sequence_number) + "\tSENT\t\tNAK\t\t\tCORRUPTED"

                            # envia NAK corrompido
                            self.sock.sendto(self.make_pkt(sequence_number, self.checksum(39321), 'NAK', 1), addr)
                # se o pacote for perdido
                else:
                    # pacote perdido
                    print str(sequence_number) + "\tLOST\t\tPACKET\t\t\tON PURPOSE"
            # except - nenhum pacote foi recebido
            except socket.error:
                # prossiga com o loop
                pass

        # ordena os pacotes recebidos de acordo com os numeros de sequencia
        # evita que pacotes recebidos fora de ordem componham dados fora de ordem
        ordered_fragments = collections.OrderedDict(sorted(fragments.items()))

        message = ""
        # para cada pedaco do fragmento
        for i in ordered_fragments:
            # concatena o fragmento na mensagem
            message+=fragments[i]

        # retorna a mensagem e o endereco do servidor que enviou os dados
        return message, addr