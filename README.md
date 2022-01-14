# TESTE_API_AMO_OFICIAL
teste como resultado de processamento para obtenção de combinações de voos e valores finais.

PADRÃO PARA A REALIZAÇÃO DA REQUISIÇÃO :

![image](https://user-images.githubusercontent.com/85443836/149560212-e17c9cd7-02b5-4ca4-a1c3-6ea898552b35.png)


* BASTA UTILIZAR A URL : 'https://shockedwoefuloffices.leonardosouza32.repl.co/buscar/{iata_ida}/{iata_volta}/{data_ida}/{data_volta}', (COMO EXEMPLO DA IMAGEM SUPERIOR)
* PADRÃO DE DATA : AAAA-MM-DD
* PADRÃO IATA : EXEMPLO /ABC/ - CASO CONTRARIO A API RETORNARA UM ERRO DIZENDO QUE O ACRONIMO DO AEROPORTO É INVALIDO
* RETORNO DA API : JSON QUE TEM CHAVES DE VALORES COMO TOTAL ORDENADO ,DATA DE IDA/VOLTA ,VELOCIDADE, CUSTO POR KM , ETC...
* DATAS NÃO PODEM SER IGUAIS OU MENOR QUE IDA
* IDA E VOLTA NÃO PODEM TER O MESMO AEROPORTO
* REQUISIÇÃO DISPONIVEL ( GET )

A API FOI HOSPEDADA EM UM SITE TEMPORARIO ( https://shockedwoefuloffices.leonardosouza32.repl.co )
![image](https://user-images.githubusercontent.com/85443836/149559970-e95e43c6-994c-4088-b017-ed0625af50a8.png)

