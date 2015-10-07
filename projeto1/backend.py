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
        self.machine_id = (thread_id - 1) % len(machines)
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
                    results["results"][index][
                        "response"] = "Erro: algo ocorreu"

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
    print "<div style='border: 1px solid #000; display:inline-block;margin:10px;padding:10px;vertical-align:top;'>"

    # exibe o id linear da maquina
    print "<h1>Maquina " + result["machine_id"] + "</h1>"

    # exibe o IP e porta, para facilitar visualização
    print "<h4>Servidor: " + result["server"]["IP"] + ":" + result["server"]["port"] + "</h3>"

    if result["success"]:
        # se o socket conectou-se ao daemon
        for r in result["results"]:
            # exibe o comando requerido
            print "<h3>Comando: " + r["command"] + "</h3>"
            print "<pre style='margin-left:15px'>"

            # exibe a resposta
            print r["response"]
            print "</pre>"
    else:
        # caso contrario, conexão foi mal sucedida
        print "Conexão mal sucedida"

    print "</div>"

if method == "POST":

    # fila usada para armazenar os resultados dos comandos de cada máquina (thread)
    # utiliza-se uma Queue porque é indicada para programas multi-thread,
    # já que ela possui métodos de sincronização já implementados,
<<<<<<< HEAD
    # garantindo segurança na troca e acesso de informação entre threads
    # executando em paralelo
=======
    # garantindo segurança na troca e acesso de informação entre threads executando em paralelo
>>>>>>> ba27938b312340a91f42d9575ab69bc8e8e537b3
    queue = Queue.Queue()

    # queue_lock, usado para sincronização de escrita dentro da thread
    queue_lock = threading.Lock()

    # adquirir dados POST vindos da form presente na página anterior
    form = cgi.FieldStorage()
    data = json.loads(form.getvalue("data"))["machines"]

    # array para as K threads que forem criadas (uma por máquina)
    threads = []

    for (index, machine) in enumerate(data):
        # para cada máquina requerida, cria uma thread e passa como argumento
        # index + 1 - identificador linear de cada thread - correspondente à contagem de Máquinas vinda do front-end
        # array de comandos da máquina desejada
        # queue para ser usado dentro da thread
        thread = machine_thread(index + 1, machine["commands"], queue)
        thread.start()

        # thread criada adicionada ao array de threads
        threads.append(thread)

    for t in threads:
        # sincronização - aguarda todads as threads encerrarem
        t.join()

    # cria array vazio com K posições (número de máquinas)
    # será usado para ordernar as respostas existentes na queue
    # a queue é preenchida em ordem de término de threads
    # a queue não está ordenada por contagem de máquina
    results = [None] * queue.qsize()

    while not queue.empty():
        r = queue.get()
        # machine_id é único e linear
<<<<<<< HEAD
        results[int(r["machine_id"]) - 1] = r
=======
        results[int(r["machine_id"])-1] = r
>>>>>>> ba27938b312340a91f42d9575ab69bc8e8e537b3

    for r in results:
        # para cada resultado das máquinas, imprime usando função print_results
        print_results(r)

    # ALTERNATIVA
<<<<<<< HEAD
    # printar em ordem de término das threads, para verificar funcionamento do
    # paralelismo
=======
    # printar em ordem de término das threads, para verificar funcionamento do paralelismo
>>>>>>> ba27938b312340a91f42d9575ab69bc8e8e537b3

    '''while not queue.empty():
        # enquanto a queue não estiver vazia
        # extrai primeiro elemento da lista a imprime ele usando a função de print_results
        print_results(queue.get())'''

else:
    # caso método não seja POST, negar acesso
    print "PERMISSION DENIED"

print '</body></html>'
