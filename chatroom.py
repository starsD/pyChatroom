from tkinter import *
from tkinter import messagebox
import tkinter as tk
import socket
import sys
import select
import threading


class ChatRoomApplication:
    def __init__(self, _root, _client):
        self.client = _client
        self.root = _root
        self.root.resizable(False, False)
        '''
        Create Top
        '''
        self.frm_top = tk.LabelFrame(self.root)
        self.frm_top_record = tk.Text(self.frm_top, width=58, height=16, state='disabled')
        self.frm_top_record.grid(row=0, column=0)
        self.frm_top_scroll = tk.Scrollbar(self.frm_top, orient=VERTICAL,
                                           command=self.frm_top_record.yview)
        self.frm_top_record['yscrollcommand'] = self.frm_top_scroll.set
        self.frm_top_scroll.grid(row=0, column=1, sticky='s'+'w'+'e'+'n')
        self.frm_top.grid(row=0, column=0, padx=5, pady=2, sticky='WESN')
        '''
        Create Bottom
        '''
        self.frm_bottom = tk.LabelFrame(self.root)
        self.frm_bottom.grid(row=1, column=0, sticky='WESN')
        self.frm_bottom_sendbox = tk.Text(self.frm_bottom, width=50, height=8)
        self.frm_bottom_sendbox.grid(row=0, column=0, padx=5, pady=2)

        self.frm_bottom_send = tk.Button(self.frm_bottom, text='Send', command=self.send)
        self.frm_bottom_send.grid(row=0, column=1, padx=5, pady=0, sticky='WE')

    def send(self):
        self.frm_top_record.configure(state='normal')
        msg = self.frm_bottom_sendbox.get(0.0, END)
        self.client.s.send(msg.encode('utf-8'))
        self.frm_top_record.insert(END, "You:\n  {}".format(msg))
        self.frm_bottom_sendbox.delete(0.0, END)
        self.frm_top_record.configure(state='disabled')
        self.frm_top_record.see(END)

    def run(self):
        try:
            self.client.s.connect((self.client.des_host, self.client.des_port))
        except Exception as err:
            tk.messagebox.showerror('Error', str(err))
            sys.exit()
        while True:
            rlist = [self.client.s]
            read_list, write_list, error_list = select.select(rlist, [], [])
            for sock in read_list:
                if sock == self.client.s:
                    data = sock.recv(4096)
                    if data:
                        self.frm_top_record.configure(state='normal')
                        self.frm_top_record.insert(END, data.decode('utf-8'))
                        self.frm_top_record.configure(state='disabled')
                        self.frm_top_record.see(END)
                    else:
                        tk.messagebox.showerror('Error', 'Disconnected from server')
                        sys.exit()


class Client:
    def __init__(self, host='localhost', port=8998):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(2)
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.des_host = host
        self.des_port = port

root = tk.Tk()
root.title('ChatRoom')
client = Client('115.28.131.208')
chat = ChatRoomApplication(root, client)

t1 = threading.Thread(target=chat.run, args=())
t1.start()
root.mainloop()





