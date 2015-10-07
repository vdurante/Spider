# Tarantula

Projeto para a disciplina Redes de Computadores

## Servidor de Consultas Linux

Professor: Cesar Marcondes (https://github.com/cmarcond) - marcondes@dc.ufscar.br


## Descricao do projeto

Este projeto (um programa CGI) tem como objetivo obter o "output" de comandos de diferentes maquinas,
feitos atraves de uma interface web. Cada maquina e seus respectivos comandos sao escolhidos
separadamente atraves de uma pagina html. As opcoes de cada comando podem ser escritas.
E usado o modelo Client-Server.

Os comandos sao: 'ps', 'df', 'finger' e 'uptime'.

## Esta aplicacao esta dividida entre:

- backend.py: recebe as informacoes inseridas na pagina web e as envia para o daemon da maquina adequada
- daemon.py: verifica se os comandos sao validos, executa localmente e retorna suas saidas para o backend
- index.py: importa webserver
--- Web Server
- webserver.html: contem as informa��es exibidas na pagina
- webserver.js: script com os elementos funcionais e de coleta de dados da pagina
- webserver.py: invocado pelo index.py, verifica os metodos GET & POST da pagina, importando o backend.py.

##Requerimentos

Apache HTTP Server - (https://httpd.apache.org/)
Python 2.7 - (https://www.python.org/)
