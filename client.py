"""
This is a client script that communicates with a server using sockets with TCP protlcol.
The purpuose of this client is to recive files for the server.
"""
import socket
import time
import os

IP = '192.168.1.100'
PORT = 5050
ADDR = (IP, PORT)
FORMAT = 'utf-8'
FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
FILESIZE_100MB = os.path.getsize(FILE_100MB)
#FILESIZE_250MB = os.path.getsize(FILE_250MB)

print (IP)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def main():
    """
    1. first first the client sends a ready message to the server
    2. th
    2. first the client sends a message to the server deciding wich file should it download the 100MB or 250MB.
    3. the server sends the file to the client along with the hash of the file
    4. the client checks the hash of the file it recived and compares it to the hash it got from the server
    """

    connected = True

    while connected:

        # 1. first first the client sends a ready message to the server
        client.send('ready'.encode(FORMAT))
        file = input('Enter the file you want to download: \n 1:100MB \n 2:250MB\n')

        # 2. if the client recive an ack from the server it sends the file name to the server
        if client.recv(1024).decode(FORMAT) == 'ack':
            # make a switch case for the file
            if file == '1':
                file = FILE_100MB
            elif file == '2':
                file = FILE_250MB
                #bar = tqdm.tqdm(range(FILESIZE_250MB), f"Sending {FILE_250MB}", unit="B", unit_scale=True, unit_divisor=1024)
            else:
                print ('invalid input')
                return 0

        else:
            print ('something went wrong')
            return 0


        client.send(file.encode(FORMAT))

        # The server sends the size of the file
        filesize = int(client.recv(1024).decode(FORMAT))

        print (f'file size: {filesize}')

        # The client acks the server
        client.send('ack'.encode(FORMAT))

        file_folder = 'ArchivosPrueba/'
        with open(file_folder+file, 'w') as f:
            while filesize>0:
                data = client.recv(1024).decode(FORMAT)
                f.write(data)
                filesize -= len(data)
                client.send('ack'.encode(FORMAT))

        # wait a few seconds to make sure the file is fully downloaded

        file_hash = client.recv(1024).decode(FORMAT)

        client_hash = generate_hash(file_folder + file).decode(FORMAT)

        print('Checking file integrity...')
        print(f'Client hash: {client_hash}')
        print(f'Server hash: {file_hash}')

        if file_hash == client_hash:
            print('Hashes are the same')
        else:
            print('Hashes are not the same')

        print('Closing connection...')
        client.close()

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

if __name__ == '__main__':
    main()
