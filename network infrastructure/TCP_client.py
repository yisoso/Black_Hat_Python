import socket

target_host = "0.0.0.0"
target_port = 9999

# creat a socket object
# AF_INET-- standard IPv4 address or host name
# SOCKET_STREAM-- TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect client
client.connect((target_host, target_port))

# send some data
#python2
# client.send("GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n")

#python3
data="from client to server"
send_data=data.encode()
client.send(send_data)

# receive some data
response = client.recv(4096)

print(response)
