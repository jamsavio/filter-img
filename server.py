"""server.py obtem a imagem via multithreaded socket e executa uma das tres transformacoes, 
"troca_red_blue", "escalacinza", ou "inverte", usando threading"""

# A seguinte sincronizacao eh necessaria entre as threads:
# Cada thread tem que terminar seu processamento antes que a
# funcao principal retorne a imagem para o client.py.

# -*- coding: utf-8 -*-
#! /usr/local/bin/python


MAX_THREADS = 500

import argparse
import sys
import threading
import socket
from pilha_thread import PilhaThread
from PIL import Image

def troca_red_blue(pixel_tuple):
    """recebe uma tupla de valores RGB,
    e retorna um pixel com canais vermelhos e azuis trocados"""
    return ((pixel_tuple[2], pixel_tuple[1], pixel_tuple[0]))

def escalacinza(pixel_tuple):
    """recebe uma tupla de valores RGB,
    e retorna seu equivalente em tons de cinza usando a formula de luminosidade"""
    gray_val = int(0.21*pixel_tuple[0]+0.72*pixel_tuple[1]+0.07*pixel_tuple[2])
    return ((gray_val, gray_val, gray_val))

def inverte(pixel_tuple):
    """recebe uma tupla de valores RGB
    e retorna o pixel com suas cores invertidas"""
    return ((255-pixel_tuple[2], 255-pixel_tuple[1], 255-pixel_tuple[0]))

def func_consumidora(pix_map, pilha, function_to_use):
    """leva em uma matriz de pixels a largura e altura,
    e aplica function_to_use a cada uma"""
    while not pilha.is_empty():
        data = pilha.pop()

        if data is not None:
            row_limits, col_limits = data
            for col in range(row_limits[0], row_limits[1]):
                for row in range(col_limits[0], col_limits[1]):
                    pix_map[col,row] = function_to_use(pix_map[col,row])

def func_produtora(pilha, width, height, rows, columns):
    width_per_block = width/rows + (0 if width%rows == 0 else 1)
    height_per_block = height/columns + (0 if width%columns == 0 else 1)
    all_threads = list()
    for row_block in range(rows):
        for col_block in range (columns):
            min_row = row_block * width_per_block
            max_row = (row_block + 1) * width_per_block
            if max_row > width:
                max_row = width
            min_col = col_block * height_per_block
            max_col = (col_block + 1) * height_per_block
            if max_col > height:
                max_col = height
             
            pilha.push(((int(min_row), int(max_row)), (int(min_col), int(max_col))))

def threaded_transform(image_to_transform, rows, columns, function_to_use, number_of_threads):
    width, height = image_to_transform.size
    pix_map = image_to_transform.load()
    pilha = PilhaThread(width * height)
    thread_produtora = threading.Thread(target = func_produtora, args = (pilha, width, height, rows, columns))
    thread_produtora.start()
    thread_produtora.join()
    
    all_threads = []

    for i in range(number_of_threads):
        all_threads.append(threading.Thread(target=func_consumidora, \
            args=(pix_map, pilha, function_to_use)))

    for thread in all_threads:
        thread.start()
    for thread in all_threads:
        thread.join()
        
    return image_to_transform

def substring_after(s, delim):
    return s.partition(delim)[2]

def multi_threaded_client(connection):

    while True:
        photo = b""
        chunk = connection.recv(4096)
        while chunk:
            photo += chunk
            chunk = connection.recv(4096)

        data = substring_after(str(photo),"$data$").split(",") 
        data = {'rows' : data[0], 'columns' : data[1], 'transformation' : data[2], 'width' : data[3], 'height' : data[4].replace("'","")}

        rows = int(data['rows']) if data['rows'] != "" else 2
        columns = int(data['columns']) if data['columns'] != "" else 2

        number_of_threads = rows * columns

        transform_functions = dict([('troca_red_blue', troca_red_blue), \
                     ('escalacinza', escalacinza), \
                     ('inverte', inverte)])

        if number_of_threads > MAX_THREADS:
            connection.send(str("ERROR: A quantidade de threads {0} e' maior que o limite max. de {1}"\
            .format(number_of_threads, MAX_THREADS)).encode())
            connection.shutdown(socket.SHUT_WR)
            break

        if not str(data['transformation']).lower() in transform_functions:
            connection.send(str("Transformacao desconhecida: {0}".format(str(data['transformation']))).encode())
            connection.shutdown(socket.SHUT_WR)
            break

        function_to_use = transform_functions[str(data['transformation']).lower()] 

        img = Image.frombytes(data=photo, size=(int(data['width']), int(data['height'])), mode="RGB")
        final_image = threaded_transform(img, rows, \
                                            columns, function_to_use, number_of_threads)

        bytes_img = img.tobytes()
        connection.send(bytes_img)
        break

    connection.close()

def main():

    ServerSideSocket = socket.socket()
    host = '127.0.0.1'
    port = 2004
    ThreadCount = 0
    try:
        ServerSideSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Socket is listening..')
    ServerSideSocket.listen(5)

    while True:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        threading.Thread(target = multi_threaded_client, args=(Client,)).start()
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSideSocket.close()

if __name__ == '__main__':
    main()
