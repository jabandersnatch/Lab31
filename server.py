"""
This is a server that communicates with a client using sockets with TCP protlcol.
The purpose of this server is to strore and send files to the client.
"""
import socket
import threading
import os
import time
import logging

IP = '192.168.1.100'
PORT = 5050
ADDR = (IP, PORT)
FORMAT = 'utf-8'

FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
FILESIZE_100MB = os.path.getsize(FILE_100MB)
FILESIZE_250MB = os.path.getsize(FILE_250MB)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def main():
    """
    this function will start the server and wait for a connection from the client.
    """

    # Create a log_file that follows the format year-month-day_hour-minutes-seconds-log.txt

    logging.basicConfig(filename=f'{time.strftime("%Y-%m-%d_%H-%M-%S")}-log.txt', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

    
    server.listen()

    print(f'[LISTENING] Server is listening on {IP}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        
def handle_client(conn, addr):
    """
    1. First the server will wait for a ready message from the client.
    2. Then the server will send a ack message to the client.
    3. Then the server will wait for the client to send a file name.
    4. Then the server will send the file to the client alogn with the hash.

    """ 

    print(f'[NEW CONNECTION] {addr} connected.')

    ready = conn.recv(1024).decode(FORMAT)


    if ready == 'ready':
        conn.send('ack'.encode(FORMAT))
        print(f'[RECEIVED] {ready}')
        print(f'[SENT] ack')
        file_name = conn.recv(1024).decode(FORMAT)
        file_size = FILESIZE_100MB
        print(f'[RECEIVED] {file_name}')
        if file_name == '100MB.bin':
            file = FILE_100MB

        elif file_name == '250MB.bin':
            file = FILE_250MB
            file_size = FILESIZE_250MB
        else:
            print('File not found')
            conn.close()
            return

        ## Send the size of the file to the client
        conn.send(str(file_size).encode(FORMAT))

        ## log the file name and size 
        logging.info(f'filename:{file_name} , filesize:{file_size}')
        logging.info(f'client_address:{addr}')
        msg = conn.recv(1024).decode(FORMAT)
        tiempoDeTransferencia = 0

        with open(file, 'r') as f:
            start = time.time()
            while True:
                data = f.read(1024)
                if not data:
                    break
                conn.send(data.encode(FORMAT))
                msg = conn.recv(1024).decode(FORMAT)
            end = time.time()
            tiempoDeTransferencia = end - start
        print(f'Tiempo de transferencia desde servidor: {tiempoDeTransferencia}')

        print(f'[SENT] {file_name}')
        file_hash = generate_hash(file)
        conn.send(file_hash)
        print(f'[SENT] {file_hash}')
        # recive the confirmation from the client
        msg = conn.recv(1024).decode(FORMAT)
        print(f'[RECEIVED] {msg}')
        if msg == 'ack':
            print(f'[SENT] ack')
            logging.info(f'The file was sent successfully')
        else:
            print(f'[SENT] nack')
            logging.info(f'The file was not sent successfully')
        print(f'[CLOSED] {addr} disconnected.')
        logging.info(f'transfer time:{tiempoDeTransferencia}')

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

if __name__ == '__main__':
    main()