# Black Widow

Projeto 2 para a disciplina Redes de Computadores

## Transferencia Confiavel de Dados Baseada em Janela com Repeticao Seletiva Usando Python

Professor: Cesar Marcondes (https://github.com/cmarcond) - marcondes@dc.ufscar.br

## Objetivo

O objetivo deste projeto e usar sockets UDP e a linguagem de programacao python para implementar um protocolo de transferencia de dados confiavel

## Esta aplicação esta dividida entre:

- emissor.py: o servidor que possui os arquivos
- recepitor.py: o cliente que deseja receber um arquivo
- /modules/udpi/__init__py: modulo UDPI (UDP Improved) que contem a logica da transferencia confiavel

- /server: contem os arquivos no servidor
- /client: contem os arquivos baixados pelo cliente

## Requerimentos

Python 2.7 - (https://www.python.org/)

## Uso

Basta copiar os conteudos deste repositorio para uma pasta em seu computador

Abra 2 terminais no diretorio da pasta:

Terminal 1 - emissor
Formato do comando - python emissor.py <numero da porta> CWnd Pl Pc

Sugestao:
``` bash
$ python emissor.py 5005 10 0.4 0.4
```

Terminal 2 - receptor
Formato do comando - python receptor.py <sender-hostname> <sender-porta> <filename> Pl Pc

Sugestao:
``` bash
$ python receptor.py 127.0.0.1 5005 teste.png 0.4 0.4
ou
$ python receptor.py 127.0.0.1 5005 teste.txt 0.4 0.4
```

Os arquivos do emissor podem ser acessados dentro da pasta /server. Ja sao incluidos 2 arquivos para testes: teste.txt ou teste.png

Os arquivos baixados podem ser acessados dentro da pasta /client

## Uso avançado

O modulo UDPI possui as seguintes configuracoes:
* IP - ip do socket UDP
* PORT - porta do socket UDP
* CWND - tamanho da janela
* PL - probabilidade de perda
* PC - probabilidade de corromper
* PCKT_SIZE - tamanho maximo do payload dos pacotes que serao enviados

O emissor e receptor possuem alguns valores default configurados dentro dos arquivos emissor.py e receptor.py. Para uma configuracao mais precisa, altere os valores das variaveis dentro destes arquivos que se encontram dentro dos blocos delimitados pelos comentarios "CONFIGURACAO AVANCADA" e "FIM CONFIGURACAO AVANCADA"
