

"""
This is a server that communicates with a client using sockets with TCP protlcol.
The purpose of this server is to strore and send files to the client.
"""
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (IP, PORT)
FORMAT = 'utf-8'

FILE_100MB = '100MB.bin'
FILE_250MB = '250MB.bin'
HELLO  = 'hello.txt'


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def main(n_clients: int = 3):
    """
    The server will only accept n_clients connections.
    """
    server.listen(n_clients)
    print(f'[LISTENING] Server is listening on {IP}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')
        if threading.activeCount() - 1 == n_clients:
            break
        
def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')
    connected = True

    while connected:
        msg = conn.recv(1024).decode(FORMAT)
        if msg == '100MB':
            with open(FILE_100MB, 'rb') as f:
                file_data = f.read(1024)
                file_hash = generate_hash(FILE_100MB)
                conn.send(file_hash)
                conn.send(file_data)
                print(f'[SENDING] {FILE_100MB} to {addr}')
        elif msg == '250MB':
            with open(FILE_250MB, 'rb') as f:
                file_data = f.read(1024)
                file_hash = generate_hash(FILE_250MB)
                conn.send(file_hash)
                conn.send(file_data)
                print(f'[SENDING] {FILE_250MB} to {addr}')

        elif msg == 'hello':
            with open(HELLO, 'rb') as f:
                file_data = f.read(1024)
                file_hash = generate_hash(HELLO)
                conn.send(file_hash)
                conn.send(file_data)
                print(f'[SENDING] {HELLO} to {addr}')
        elif msg == 'DISCONNECT':
            connected = False
    conn.close()

def generate_hash(file):
    import hashlib
    with open(file, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        print (file_hash.encode(FORMAT))
        return file_hash.encode(FORMAT)

if __name__ == '__main__':
    main()