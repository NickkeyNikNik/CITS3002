import socket

SERVER_ADDRESS = "127.0.0.1" 
SERVER_PORT = 3333

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

if __name__ == "__main__":
    while True:

        message = input("Enter a message to send: ")
        message += '\0' # null to terminate

        client_socket.sendall(message.encode())
        response = client_socket.recv(1024).decode()
        print("Response from the server: ", response)

    client_socket.close()