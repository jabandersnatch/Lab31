"""
This is a server that communicates with a client using sockets with TCP protlcol.
The purpose of this server is to strore and send files to the client.
"""
import socket
import threading
import os
import time

IP = '192.168.1.100'
PORT = 5050
ADDR = (IP, PORT)
FORMAT = 'utf-8'

FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
FILESIZE_100MB = os.path.getsize(FILE_100MB)
#FILESIZE_250MB = os.path.getsize(FILE_250MB)
HELLO  = 'hello.txt'


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def main():
    """
    this function will start the server and wait for a connection from the client.
    """
    
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
        print(f'[RECEIVED] {file_name}')
        if file_name == '100MB.bin':
            file = FILE_100MB
        elif file_name == '250MB.bin':
            file = FILE_250MB
            #bar = tqdm.tqdm(range(FILESIZE_250MB), f'Sending {file_name}', unit='B', unit_scale=True, unit_divisor=1024)
        else:
            print('File not found')
            conn.close()
            return

        ## Send the size of the file to the client
        conn.send(str(FILESIZE_100MB).encode(FORMAT))
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

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

if __name__ == '_main_':
    main()