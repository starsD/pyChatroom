from tkinter import *
from tkinter import messagebox
import tkinter as tk
import socket
import select
import threading
import sys


class ChatRoomApplication:
    def __init__(self, _root, _client):
        self.client = _client
        self.root = _root
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
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

        '''
        Create Buttons
        '''
        self.frm_buttons = tk.LabelFrame(self.frm_bottom)
        self.frm_buttons.grid(row=0, column=1, padx=5, pady=2)

        self.frm_bottom_send = tk.Button(self.frm_buttons, text='Send', command=self.send)
        self.frm_bottom_send.grid(row=0, column=0, padx=5, pady=0, sticky='WE')

        self.frm_bottom_clear = tk.Button(self.frm_buttons, text='Clear', command=self.clear)
        self.frm_bottom_clear.grid(row=1, column=0, padx=5, pady=2, sticky='EW')

        self.frm_bottom_save = tk.Button(self.frm_buttons, text='Save', command=None)
        self.frm_bottom_save.grid(row=2, column=0, padx=5, pady=2, sticky='EW')

    def send(self):
        """
        send the text content to server and add it to the chat record
        """
        self.frm_top_record.configure(state='normal')
        msg = self.frm_bottom_sendbox.get(0.0, END)
        self.client.s.send(msg.encode('utf-8'))
        self.frm_top_record.insert(END, "You:\n  {}".format(msg))
        self.frm_bottom_sendbox.delete(0.0, END)
        self.frm_top_record.configure(state='disabled')
        self.frm_top_record.see(END)

    def clear(self):
        """
        clear the chat record
        """
        if tk.messagebox.askokcancel(title='', message='Are you sure to clear the chat record?'):
            self.frm_top_record['state'] = 'normal'
            self.frm_top_record.delete(0.0, END)
            self.frm_top_record['state'] = 'disabled'
            self.frm_top_record.see(END)

    def exit(self):
        """
        when closed, the window sends an exit message and exit the process
        """
        self.root.destroy()
        self.client.s.send(b'exit')


    def run(self):
        """
        listen to the client socket and write the message from server to chat record when it's readable
        """
        try:
            self.client.s.connect((self.client.des_host, self.client.des_port))
        except Exception as err:
            tk.messagebox.showerror('Error', str(err))
            exit(1)
        while True:
            # rlist = [self.client.s]
            # read_list, write_list, error_list = select.select(rlist, [], [])
            # for sock in read_list:
            #     if sock == self.client.s:
            data = self.client.s.recv(4096)
            print(data)
            if data:
                self.frm_top_record.configure(state='normal')
                self.frm_top_record.insert(END, data.decode('utf-8'))
                self.frm_top_record.configure(state='disabled')
                self.frm_top_record.see(END)
            else:
                # tk.messagebox.showerror('Error', 'Disconnected from server')
                self.client.s.send(b'exit')
                self.client.s.close()
                print("exit")
                break
                


class Client:
    def __init__(self, host='localhost', port=8998):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(60)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 10)
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.des_host = host
        self.des_port = port

root = tk.Tk()
root.title('ChatRoom')
# connect to my server
client = Client()
chat = ChatRoomApplication(root, client)

t1 = threading.Thread(target=chat.run, args=()).start()
root.mainloop()
