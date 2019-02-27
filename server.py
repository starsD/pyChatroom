import socket
import select
import time
import queue


class ChatServer:
    def __init__(self, host='localhost', port=8998):
        self.outputs = []
        self.message_queues = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs = [self.server]
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
                    print(sock)
                    sock.send(message)

                    print('kkk')
                except:
                    sock.close()
                    self.iutputs.remove(sock)

    def run(self):
        print('ChatServer running on port:{}'.format(self.port))
        
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.inputs, self.outputs, self.inputs)
            for sock in read_sockets:
                if sock == self.server:
                    sockfd, addr = self.server.accept()
                    self.inputs.append(sockfd)
                    print('Client {} has connected'.format(addr))
                    self.message_queues[sockfd] = queue.Queue()
                    # self.broadcast_data(set(self.inputs), '\r{} entered room\n'.format(addr))
                else:
                    try:
                        data = sock.recv(self.RCVBUF)
                        print(data)
                        if data and data != b'exit':
                            self.message_queues[sock].put(("\r" + '<' + str(sock.getpeername()) + '>\n   ' +
                             data.decode('utf-8')).encode('utf-8'))
                            if sock not in self.outputs:
                                self.outputs.append(sock)
                            # self.broadcast_data(set(self.outputs)-{sock},
                            # ("\r" + '<' + str(sock.getpeername()) + '>\n   ' +
                            #  data.decode('utf-8')).encode('utf-8'))
                        elif data == b'exit':
                            sock.close()
                            self.inputs.remove(sock)
                            if sock in self.outputs:
                                self.outputs.remove(sock)
                        else:

                            raise Exception()
                    except:
                        try:
                            self.broadcast_data(set(self.inputs)-{self.server, sock},
                                                "\rClient {} is offline\n".format(sock.getpeername()))
                            # self.broadcast_data(set(self.outputs)-{self.server, sock},
                            #                     "\rClient {} is offline\n".format(sock.getpeername()))
                            print("Client {} is offline".format(sock.getpeername()))
                        except:
                            if sock in self.message_queues:
                                del self.message_queues[sock]
                            
                            continue

                        sock.close()
                        continue
            for sock in write_sockets:
                print("write socks" + str(sock))
                try:
                    next_msg = self.message_queues[sock].get_nowait() 
                except queue.Empty:
                    err_msg = "Output Queue is Empty!"
                    #g_logFd.writeFormatMsg(g_logFd.LEVEL_INFO, err_msg)
                    self.outputs.remove(sock)
                else:
                    self.broadcast_data(set(self.inputs)-{sock},next_msg)
                    # sock.send(next_msg)
        self.server.close()

server = ChatServer()
server.run()

