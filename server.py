import socket
import select
import time


class ChatServer:
    def __init__(self, host='localhost', port=8998):
        self.CONNECTIONS = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(20)
        self.port = port
        self.RCVBUF = 4096

    def broadcast_data(self, sock_set, message):
        """
        :param sock_set: sockets that are going to send message to
        :param message: message to send
        """
        for sock in sock_set:
            if sock != self.server:
                try:
                    sock.send(message.encode('utf-8'))
                except:
                    sock.close()
                    self.CONNECTIONS.remove(sock)

    def run(self):
        print('ChatServer running on port:{}'.format(self.port))
        self.CONNECTIONS.append(self.server)
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.CONNECTIONS, [], [])
            for sock in read_sockets:
                if sock == self.server:
                    sockfd, addr = self.server.accept()
                    self.CONNECTIONS.append(sockfd)
                    print('Client {} has connected'.format(addr))
                    self.broadcast_data(set(self.CONNECTIONS), '\r{} entered room\n'.format(addr))
                else:
                    try:
                        data = sock.recv(self.RCVBUF)
                        if data and data != b'exit':
                            self.broadcast_data(set(self.CONNECTIONS)-{sock},
                            ("\r" + '<' + str(sock.getpeername()) + '>\n   ' +
                             data.decode('utf-8')).encode('utf-8'))
                        else:
                            raise Exception()
                    except:
                        try:
                            self.broadcast_data(set(self.CONNECTIONS)-{self.server, sock},
                                                "\rClient {} is offline\n".format(sock.getpeername()))
                            print("Client {} is offline".format(sock.getpeername()))
                        except:
                            continue
                        if sock in self.CONNECTIONS:
                            self.CONNECTIONS.remove(sock)
                        sock.close()
                        continue
        self.server.close()
server = ChatServer()
server.run()

