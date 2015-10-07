# -*- coding: utf-8 -*-

import socket
import threading
import commands
import sys


def verificar(t):
    # função para verificar o comando e caracteres
    # retorna string com cabeçalho pronto ou string "error"
    # o formato do cabeçalho foi definido pelo professor e padronizado para o trabalho

    # verifica caracteres maliciosos
    # se existir algum caractere malicioso, retorna erro na função
    if t.find(";") > 0 or t.find("|") > 0 or t.find(">") > 0:
        return "error"

    c = t.split()  # separa as palavras da string recebida

    # Verifica se é uma requisição
    if c[0].upper() != "REQUEST":
        return "error"

    c.pop(0)

    comandos = ['ps', 'df', 'finger', 'uptime']

    index = int(c[0])
    c.pop(0)

    if index <= len(comandos):
        a = comandos[index - 1] + " " + " ".join(c)
        return a
    else:
        return "error"

# Configura Daemon


class ThreadedServer(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        # Quantidade Connection Queue
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print "Connection From:", address
            # termina conexão em caso de 60 segundos sem comunicação
            client.settimeout(60)
            threading.Thread(target=self.listenToClient,
                             args=(client, address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    verified = verificar(data)  # verifica input

                    if verified == "error":
                        client.send(verified)
                    else:
                        response = commands.getoutput(
                            verified)  # pega output dos comandos

                        # Envia resposta como exigida
                        client.send("RESPONSE " + data.split()
                                    [1] + " " + response)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        port_num = int(sys.argv[1])  # porta a ser utilizada
    else:
        port_num = 9000

    print 'The server is ready to receive'
    print 'Port: ' + str(port_num)
    ThreadedServer('', port_num).listen()
