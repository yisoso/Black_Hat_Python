import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)
print("[*] Listening on %s:%d" % (bind_ip, bind_port))


# this is the client processing thread
def handle_client(client_socket):
    # print the data received from the client
    request = client_socket.recv(1024)

    print("[*] Received:%s" % request)

    # return a data package
    data='ACK!'
    send_data=data.encode()
    client_socket.send(send_data)

    client_socket.close()


while True:
    client, addr = server.accept()

    print("[*] Accepted connection from: %s %d" % (addr[0], addr[1]))

    # suspend client thread, processing the data
    client_hanlder = threading.Thread(target=handle_client, args=(client,))
    client_hanlder.start()
