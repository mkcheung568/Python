import threading, socket, sys, time
from datetime import datetime

#Connection Data
host = '192.168.8.113'
port = 8085

#Start Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#The first one (AF_INET) indicates that we are using an internet socket rather than an unix socket. The second parameter stands for the protocol we want to use. SOCK_STREAM indicates that we are using TCP and not UDP.
server.bind((host, port))
server.listen()

#List for Clients and their nicknames
clients = []
nicknames = []

#Send message to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)
        print("{}".format(message.decode('ascii')))
        

# handle all messaging from clients        
def handle(client):
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        try:
            #broadcast message
            message = client.recv(1024)
            broadcast(message)
        except:
            # remove clients and close client connection when error happens
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('[{0}][Server] {1} left!'.format(current_time,nickname).encode('ascii'))
            nicknames.remove(nickname)
            break

#receiving/ listening function 
def receive():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #accept connection
        client, address = server.accept()
        print("Connected with{}".format(str(address)))
        
        #request and store nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')    
        nicknames.append(nickname)
        clients.append(client)
        
        #print and broadcast nickname
        print("[{0}] [Server] Nickname is {1}".format(current_time,nickname))
        broadcast("[{0}] [Server] {1} joined!".format(current_time,nickname).encode('ascii'))
        client.send('[{0}] [Server] Connected to the server!'.format(current_time).encode('ascii'))
        
        #start handle thread for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server Started...")
receive()