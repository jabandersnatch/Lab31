# Client-Side Multithreaded TCP Socket with external server

import socket
import threading
import sys
import time
import tqdm
import os

# Define external server IP and port
host = '192.168.1.100'
port = 5050
ADDR = (host, port)
FORMAT = 'utf-8'
FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
FILESIZE_100MB = os.path.getsize(FILE_100MB)
#FILESIZE_250MB = os.path.getsize(FILE_250MB)
file_global = FILE_100MB
filesize_global = FILESIZE_100MB

# Define ClientMultiSocket
class ClientMultiSocket:

    connected = False

    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
            self.connected = True
            print('Connected to server')
        except:
            print('Connection failed')
            sys.exit()

        self.client.send('ready'.encode(FORMAT))

        file = file_global
        filesize = 0

        if self.client.recv(1024).decode(FORMAT) == 'ack':
            self.client.send(file.encode(FORMAT))
        else:
            print('Error')
            sys.exit()
        filesize = int(self.client.recv(1024).decode(FORMAT))
        print (f'file size: {filesize}')

        self.client.send('ack'.encode(FORMAT))

        file_folder = 'ArchivosPrueba/'
        with open(file_folder+file, 'w') as f:
            while filesize:
                data = self.client.recv(1024).decode(FORMAT)
                f.write(data)
                filesize -= len(data)
                self.client.send('ack'.encode(FORMAT))

        # wait a few seconds to make sure the file is fully downloaded

        file_hash = self.client.recv(1024).decode(FORMAT)

        client_hash = generate_hash(file_folder + file).decode(FORMAT)

        print('Checking file integrity...')
        print(f'Client hash: {client_hash}')
        print(f'Server hash: {file_hash}')

        if file_hash == client_hash:
            print('Hashes are the same')
        else:
            print('Hashes are not the same')

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

def main():
    # Request in console the file to download and the number of clientes between 1, 5 and 10
    file = input('File to download: (1) 100MB.bin or (2) 250MB.bin): ')
    if file == '1':
        file_global = FILE_100MB
        filesize_global = FILESIZE_100MB

    elif file == '2':
        file_global = FILE_250MB
        filesize_global = FILESIZE_250MB
    else:
        print('Invalid option')
        sys.exit()
    
    num_clients = input('Number of clients (1, 5 or 10): ')
    if num_clients == '1':
        num_clients = 1
    elif num_clients == '5':
        num_clients = 5
    elif num_clients == '10':
        num_clients = 10
    else:
        print('Invalid option')
        sys.exit()
    
    # Create a list of threads
    threads = []
    for i in range(num_clients):
        threads.append(ClientMultiSocket(host, port))
        time.sleep(0.1)
    
    # Start all threads
    for i in range(num_clients):
        threads[i].start()

    # Wait for all of them to finish
    for i in range(num_clients):
        threads[i].join()
    
    # Close clients
    for i in range(num_clients):
        threads[i].client.close()
    
    print('All threads finished')

if __name__ == '__main__':
    main()


