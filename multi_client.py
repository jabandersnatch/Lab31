# Client-Side Multithreaded TCP Socket with external server

from json import load
import socket
import threading
import sys
import time
import logging
import os

# Define external server IP and port
host = '192.168.1.100'
global_port = 5050
FORMAT = 'utf-8'
FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
# Define ClientMultiSocket
class ClientMultiSocket(threading.Thread):

    connected = False
    def __init__(self, port, id, file, n_clients):
        self.port = port
        self.id = id
        self.file = file
        self.n_clients = n_clients
        threading.Thread.__init__(self)        
    
    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, self.port))
            self.connected = True
            print('Connected to server on port: ', self.port)
        except socket.error as e:
            print(str(e))
            print('Connection failed')
            sys.exit()

        self.client.send('ready'.encode(FORMAT))

        filesize = 0

        if self.client.recv(1024).decode(FORMAT) == 'ack':
            self.client.send(self.file.encode(FORMAT))
        else:
            print('Error')
            sys.exit()
        filesize = int(self.client.recv(1024).decode(FORMAT))
        print (f'file size: {filesize}')

        # log the file name and the filesize
        logging.info(f'file name: {self.file}, file size: {filesize}')
        # log the address of the client
        logging.info(f'client address: {self.client.getsockname()}, client_id: {self.id}')



        self.client.send('ack'.encode(FORMAT))
        tiempoDeTransferencia = 0
        file_folder = 'ArchivosRecibidos/'
        tamArchivo = filesize
        file_path = file_folder+'Cliente'+str(self.id)+'-Prueba-'+str(self.n_clients)+'.txt'
        with open(file_path, 'w') as f:
            # Obtener tiempo de transferencia de cliente
            start = time.time()
            while filesize:
                data = self.client.recv(1024).decode(FORMAT)
                f.write(data)
                filesize -= len(data)
                self.client.send('ack'.encode(FORMAT))
            end = time.time()
            tiempoDeTransferencia = end - start

        print(f'Tiempo de transferencia desde cliente: {tiempoDeTransferencia} s')
        print(f'Tasa de transferencia: {(tamArchivo/tiempoDeTransferencia)} B/s')

        # wait a few seconds to make sure the file is fully downloaded

        file_hash = self.client.recv(1024).decode(FORMAT)

        client_hash = generate_hash(file_path).decode(FORMAT)

        print('Checking file integrity...')
        print(f'Client hash: {client_hash}')
        print(f'Server hash: {file_hash}')


        if file_hash == client_hash:
            print('Hashes are the same')
            # notify the server that the file was downloaded correctly
            self.client.send('ack'.encode(FORMAT))
            # log if the file was downloaded correctly
            logging.info(f'file downloaded correctly: {self.file}')
        else:
            print('Hashes are not the same')
            # notify the server that the file was not downloaded correctly
            self.client.send('nack'.encode(FORMAT))
            # log if the file was not downloaded correctly
            logging.info(f'file downloaded incorrectly: {self.file}')

        # log the time it took to download the file
        logging.info(f'time to download file: {tiempoDeTransferencia} s')

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

def main():
    # Request in console the file to download and the number of clientes between 1, 5 and 10

    # Create a loggin file that follows the format year-month-day_hour-minute-second-log.txt
    logging.basicConfig(filename=f'ArchivosRecibidos/{time.strftime(f"%Y-%m-%d_%H-%M-%S")}-log.txt', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

    file = input('File to download: (1) 100MB.bin or (2) 250MB.bin): ')

    file_name = ''
    if file == '1':
        file_name = FILE_100MB
    elif file == '2':
        file_name = FILE_250MB
    else:
        print('Invalid option')
        sys.exit()
    
    num_clients = input('Number of clients (1, 5, 10, 25): ')

    if num_clients == '1':
        num_clients = 1
    elif num_clients == '5':
        num_clients = 5
    elif num_clients == '10':
        num_clients = 10
    elif num_clients == '25':
        num_clients = 25
    else:
        print('Invalid option')
        sys.exit()
    
    # Create a list of threads
    threads = []
    for i in range(num_clients):
        print(f'Creating thread {i}')
        threads.append(ClientMultiSocket(global_port, i, file_name, num_clients))
        time.sleep(0.1)
    
    # Start all threads
    for thread in threads:  
        thread.start()
        time.sleep(0.1)
    
    # Wait for all of them to finish
    for i in range(num_clients):
        threads[i].join()
    
    # Close clients
    for i in range(num_clients):
        threads[i].client.close()
    
    print('All threads finished')

if __name__ == '__main__':
    main()