import socket
import select
import time
import queue
import json

class ChatServer:
    def __init__(self, host='localhost', port=8998):
        self.outputs = []
        self.message_queues = {}
        self.address = (host, str(port))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs = [self.server]
        self.server.bind((host, port))
        self.server.listen(20)
        self.RCVBUF = 4096
        self.func = {
            '0001': self.process_code_0001,
            '0002': self.process_code_0002,
        }

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
                except:
                    sock.close()
                    self.inputs.remove(sock)

    def handle_request_data(self, data, sock):
        if data==b'exit':
            # return str(sock.getpeername() + ' is offline'
            # self.inputs.remove(sock)
            return 'exit'
            pass
        request_json_data = json.loads(data.decode('utf-8'))
        if request_json_data['request_code']!='':
            try:
                print(request_json_data['request_code'])
                request_code = request_json_data['request_code']
                if request_code == '0001':
                    response_data = self.process_code_0001(request_json_data,sock)
                # process_func = self.func[request_json_data['request_code']]
                # response_data = process_func(request_json_data,sock)
                return response_data
            except Exception as e:
                print(e)
                return ''
        pass

    def process_code_0001(self, request_json_data, sock):
        response_dict = {}
        response_dict['message'] = request_json_data['message']
        response_dict['length'] = len(request_json_data['message'])
        response_dict['from_client'] = str(sock.getpeername())
        response_dict['from_server'] = ':'.join(list(self.address))
        response_dict['response_code'] = request_json_data['request_code']
        return json.dumps(response_dict).encode('utf-8')
        pass

    def process_code_0002(self, request_json_data, sock):
        pass

    def handle_response_data(self, response_data, sock):
        if response_data == '':
            self.message_queues[sock].put(str(sock.getpeername()) + ' is offline')
            self.inputs.remove(sock)
            return 
        if response_data == 'exit':
            self.message_queues[sock].put('exit')
        else:
            self.message_queues[sock].put(response_data)
        if sock not in self.outputs:
            self.outputs.append(sock)

    def run(self):
        print('ChatServer running on port:{}'.format(str(self.address)))
        
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.inputs, self.outputs, self.inputs)
            for sock in read_sockets:
                if sock == self.server:
                    sockfd, addr = self.server.accept()
                    self.inputs.append(sockfd)
                    print('Client {} has connected'.format(addr))
                    self.message_queues[sockfd] = queue.Queue()
                    self.broadcast_data(set(self.inputs), ('\r{} entered room\n'.format(addr)).encode("utf-8"))
                else:
                    try:
                        data = sock.recv(self.RCVBUF)
                        print(data)
                        # if data and data != b'exit':
                        response_data = self.handle_request_data(data, sock)
                        self.handle_response_data(response_data, sock)
                            # self.message_queues[sock].put(("\r" + '<' + str(sock.getpeername()) + '>\n   ' +
                            #  data.decode('utf-8')).encode('utf-8'))
                            # if sock not in self.outputs:
                            #     self.outputs.append(sock)

                        # elif data == b'exit':
                        #     # sock.close()
                        #     # self.inputs.remove(sock)
                        #     # if sock in self.outputs:
                        #     #     self.outputs.remove(sock)
                        #     print("breakpoint 0")
                        #     self.message_queues[sock].put('exit')
                        #     if sock not in self.outputs:
                        #         self.outputs.append(sock)

                        # else:

                        #     raise Exception()
                    except:
                        try:
                            self.broadcast_data(set(self.inputs)-{self.server, sock},
                                                "\rClient {} is offline\n".format(sock.getpeername()))
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
                    self.outputs.remove(sock)
                else:
                    print("breakpoint 1 ")
                    if next_msg == 'exit':
                        self.broadcast_data(set(self.inputs)-{self.server, sock},
                                                "\rClient {} is offline\n".format(sock.getpeername()).encode('utf-8'))
                        sock.close()
                        if sock in self.inputs:
                            self.inputs.remove(sock)
                        if sock in self.outputs:
                            self.outputs.remove(sock)
                    else:
                        self.broadcast_data(set(self.inputs)-{sock}, next_msg)
                    # sock.send(next_msg)
        self.server.close()

server = ChatServer()
server.run()

