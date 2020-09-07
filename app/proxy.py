import socket
import selectors
import types
import signal

from app import tasks

sel = selectors.DefaultSelector()
running = True


class Proxy:

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.lsock = None
        self.init_socket(host, port)

    def receiveSignal(self, signal_number, frame):
        print('Received:', signal_number)
        self.lsock.close()
        print("socket chiuso")
        return

    def init_socket(self, host, port):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        signal.signal(signal.SIGTERM, self.receiveSignal)
        #signal.signal(signal.SIGKILL, self.receiveSignal)
        self.lsock.bind((host, int(port)))
        self.lsock.listen()
        print('listening on', (host, port))
        self.lsock.setblocking(False)
        sel.register(self.lsock, selectors.EVENT_READ, data=None)
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    # print('mask: '+str(mask))
                    service_connection(key, mask)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = None
        try:
            sock.settimeout(10)
            recv_data = sock.recv(1024)  # Should be ready to read
            print("recv ok: " + str(recv_data))
        except Exception as e:
            print("errore timeout: " + e)
        # print('recv_data: '+str(recv_data))
        if recv_data:
            # print('recv_data: '+str(recv_data))
            data.inb += recv_data
        else:
            print('all data red')
            data.outb = data.inb
            # data.inb = data.inb[len(str(data.inb)):]
            # my_data = data.inb
            data.inb = data.inb[len(str(data.inb)):]
            # data.outb = data.outb[len(str(data.outb)):]
            # data.inb = []
            sel.unregister(sock)
            sock.close()
            print('connection closed with client')
            print('socket: ' + str(sock))
            # parse_data(my_data.decode("utf-8"))

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # parse_data(data.outb.decode("utf-8"))
            #tasks.parse_proxy_data.delay(data.outb.decode("utf-8"))
            print("data outbuffer: "+data.outb.decode("utf-8"))
            data.outb = data.outb[len(str(data.outb)):]
            data.outb = []


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def init_socket(host, port):
    Proxy(host, port)
