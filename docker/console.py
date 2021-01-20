#!/usr/local/bin/python3
"""
- read output from a subprocess in a background thread
- show the output in the GUI
"""
import os
import sys

from itertools import islice
from subprocess import Popen, PIPE, STDOUT
from socket import *
from textwrap import dedent
from threading import Thread
from tkinter.scrolledtext import ScrolledText
import time
try:
    import Tkinter as tk
    from Queue import Queue, Empty
except ImportError:
    import tkinter as tk # Python 3
    from queue import Queue, Empty # Python 3


class Console(tk.Frame):
    """Console that displays the output of bash commands"""

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.text_options = {"state": "disabled",
                             "bg": "black",
                             "fg": "#08c614",
                             "insertbackground": "#08c614",
                             "selectbackground": "#f01c1c"}

        self.text = ScrolledText(self, **self.text_options)
        self.text.pack(expand=True, fill="both")
        t = Thread(target=self.network_function)
        t.daemon = True
        t.start()
            

    def show(self, message):
        """Inserts message into the Text wiget based on the host/client
        connection between rillgen2d.py and console.py"""
        self.text.config(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.config(state="disabled")
        self.text.update_idletasks()

    def network_function(self):
        """Handles the connection between rillgen2d.py and console.py in a host/client
        structure with rillgen2d.py as the host and console.py as the client"""
        host = gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number

        client_socket = socket()  # instantiate
        client_socket.connect((host, port))  # connect to the server

        while True:
            data = client_socket.recv(1024).decode()  # receive response
            if not data:
                break
            if data != '\n':
                self.show(data)
            print('Received from server: ' + data)  # show in terminal

        client_socket.close()  # close the connection
        root.destroy()

root = tk.Tk()
root.title("rillgen2D Console")
Console = Console(root)
Console.pack(expand=True, fill="both")
# center window
root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
root.mainloop()