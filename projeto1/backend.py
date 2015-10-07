#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgitb
import cgi
import os
import json
from socket import *
import threading
import Queue

# modo debug - traceback para cgi
cgitb.enable()

print "Content-Type: text/html\n"

print '<html><head><meta charset="utf-8"></head><body>'

method = os.environ['REQUEST_METHOD']

# array de maquinas
machines = []

# para cada daemon desejado, coloque o IP e Porta correspondentes
machines.append({"IP": "localhost", "port": 9000})
#machines.append({"IP" : "localhost", "port" : 9001 })
#machines.append({"IP" : "localhost", "port" : 9001 })

# thread de cada maquina
# para cada maquina que o usuario selecionou uma thread nova será criada
# as conexões aos sockets serão feitos em paralelo
# os comandos serão enviados sequencialmente por cada socket de cada máquina


class machine_thread (threading.Thread):

    def __init__(self, thread_id, commands, q):
        # inicializacao da maquina
        # thread_id é um identificador da máquina (linear com valor 1~K)
        # machine_id é o identificador da máquina, usado para acessar a máquina no array machines
        # é obtido utilizando o a divisão identificador único (que é linear) pelo número de máquinas existentes
        # machine_id é usado para aumentar a abstração para o usuário final,
        # já que o usuário pode selecionar K máquinas e se apenas 2 estiverem disponíveis,
        # os comandos serão distribuídos entre as 2 máquinas paralelamente
        # commands é um array contendo os comandos desejados por máquina

        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.machine_id = (thread_id-1)%len(machines)
        self.commands = commands
        self.q = q

    def run(self):

        # results é um dicionário que armazenará informações da máquina e as
        # respostas aos comandos
        results = {}

        # machine_id é o thread_id - linear
        results["machine_id"] = str(self.thread_id)
        results["server"] = {}

        # IP e port para mostrar ao usuário qual máquina recebeu o comando
        results["server"]["IP"] = str(machines[self.machine_id]["IP"])
        results["server"]["port"] = str(machines[self.machine_id]["port"])

        # results armazenarão as respostas dos comandos
        results["results"] = []

        try:

            # inicia o socket
            clientSocket = socket(AF_INET, SOCK_STREAM)

            # conecta ao socket usando IP e port vindo do array de maquinas
            clientSocket.connect(
                (machines[self.machine_id]["IP"], machines[self.machine_id]["port"]))

            # conexão ao socket foi bem sucedida
            results["success"] = True
            # para cada command existente em commands
            for (index, command) in enumerate(self.commands):

                # cria um dicionário novo dentro de results[results]
                # cada posição do dicionário vai armazenar informações sobre
                # cada comando
                results["results"].append({})

                # armazena o command - comando emitido pelo usuario
                results["results"][index]["command"] = command

                # envia o command ao daemon no formato desejado, estipulado
                # pelo arquivo
                clientSocket.send("REQUEST " + command)

                # pega a resposta e separa a primeira palavra do restante
                # utilizado para separar o RESPONSE do restante da resposta
                response = clientSocket.recv(1024).split(' ', 2)

                if response[0] == 'RESPONSE' and response[1] == command.split(' ', 1)[0]:
                    # se a resposta inicia com RESPONSE e o comando desejado do
                    # request é o mesmo da resposta

                    # response do comando no dicionário recebe a resposta vinda
                    # do daemon
                    results["results"][index]["response"] = response[2]
                else:
                    # caso contrario, algum erro ocorreu
                    results["results"][index]["response"] = "Erro: algo ocorreu"

            # fecha o socket apos todos os comandos serem enviados
            clientSocket.close

        except Exception, e:
            # se uma excessao ocorrer, nao foi possivel conectar ao socket
            results["success"] = False

        # adquire lock para escrever na queue
        queue_lock.acquire()
        # insere os resultados na queue
        self.q.put(results)
        # libera o lock da queue
        queue_lock.release()


# metodo para printar os resultados obtidos de uma máquina
def print_results(result):
    print "TODO"

if method == "POST":


else:
    # caso método não seja POST, negar acesso
    print "PERMISSION DENIED"

print '</body></html>'
