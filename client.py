"""
This is a client script that communicates with a server using sockets with TCP protlcol.
The purpuose of this client is to recive files for the server.
"""
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (IP, PORT)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def main():
    """
    1. first the client sends a message to the server deciding wich file should it download the 100MB or 250MB.
    2. the server sends the file to the client along with the hash of the file
    3. the client checks the hash of the file it recived and compares it to the hash it got from the server
    """
    file = input('Enter the file you want to download: \n 100MB \n 250MB \n hello \n')
    client.send(file.encode(FORMAT))
    file_hash = client.recv(1024).decode(FORMAT)
    file_folder = 'ArchivosPrueba/'
    with open(file_folder + file + '.txt', 'wb') as f:
        file_data = client.recv(1024)
        f.write(file_data)
        print(f'[RECIVING] {file}.bin from server')
    client_hash = generate_hash(file_folder + file + '.txt')

    print('Checking file integrity...')
    print(f'Client hash: {client_hash}')
    print(f'decoded client hash: {client_hash.decode(FORMAT)}')
    print(f'Server hash: {file_hash}')

    if file_hash == client_hash.decode(FORMAT):
        print('Hashes are the same')
    else:
        print('Hashes are not the same')

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash.encode(FORMAT)

if __name__ == '__main__':
    main()
