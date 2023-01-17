Universidade Federal de Alagoas
Disciplinas: Sistemas Distribuídos e Computação Paralela
-------------------------------------

Requerimentos:

Python 3.8.5
Biblioteca Pillow 7.0.0 *

* pip install Pillow==7.0.0

-------------------------------------

Filtros disponíveis:
    troca_red_blue -> Troca os canais vermelhos e azuis da imagem
    escalacinza -> Aplica tons de cinza na imagem
    inverte -> Inverte as cores da imagem

-------------------------------------

Como funciona:
    Thread Produtor -> Pega o mapa de pixels completo, divide-o em pedaços e coloca os índices em uma pilha(implementada manualmente)
    Thread Consumidores ->  Pega os índices da pilha (dá lock para evitar que outra thread tente pegar os mesmos índices 2x) e aplica o filtro escolhido no mapa 

-------------------------------------

Como executar:

    Comando (terminal):
        * Primeiro executa o server.py ("python server.py") que receberá a imagem dos clients, aplicará o filtro e mandará de volta a imagem processada
        * Executa o client.py passando os seguintes argumentos:
            python client.py sample.jpeg (caminho da imagem de entrada) sample_output.jpeg (caminho da imagem de saída) escalacinza (filtro desejado) 3 3 (aqui especifica a quantidade de linhas e colunas dos retângulos (pedaços da imagem) que serão divididos e processados pelas threads consumidoras) - opcional (se não for definido, por default será 2 2) 
    



