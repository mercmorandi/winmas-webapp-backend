import socket
import selectors
import types
import signal
import requests

from socket import error as socket_error
from app import tasks, celery


def close_proxy_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            s.sendall(b"close")
        except socket_error as serr:
            print("socket error: " + serr)
            return


class Proxy:
    def __init__(self, host, port):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = int(port)
        self.lsock = None
        self.init_socket(host, port)

    def receiveSignal(self, signal_number, frame):
        print("Received:", signal_number)
        self.lsock.shutdown(socket.SHUT_RDWR)
        self.lsock.close()
        requests.post("http://backend:5000/proxy_status", json={"status": "off"})
        print("socket chiuso")
        return

    def init_socket(self, host, port):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        signal.signal(signal.SIGTERM, self.receiveSignal)
        try:
            self.lsock.bind((host, int(port)))
        except socket_error as serr:
            print("socket error: " + str(serr))
            requests.post(
                "http://backend:5000/proxy_status",
                json={"status": "off"},
            )
            return
        self.lsock.listen()
        self.lsock.settimeout(60)
        task_id = celery.current_task.request.id
        requests.post(
            "http://backend:5000/proxy_status",
            json={"status": "on", "task_id": str(task_id)},
        )
        print("listening on", (host, port))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
        while True:
            events = self.sel.select(timeout=60)
            status = None
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    status = self.service_connection(key, mask)
                    # print("status: " + str(status))
            if status:
                break
        self.lsock.shutdown(socket.SHUT_RDWR)
        self.lsock.close()
        requests.post("http://backend:5000/proxy_status", json={"status": "off"})

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        conn.settimeout(60)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        sock.settimeout(10)
        if mask & selectors.EVENT_READ:
            recv_data = None
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
                print("recv ok: " + str(recv_data))
            except Exception as e:
                print("errore timeout: " + str(e))
                return

            if recv_data:
                data.inb += recv_data
            elif data.inb == b"close":
                data.inb = data.inb[len(str(data.inb)):]
                self.sel.unregister(sock)
                sock.close()
                return "close"
            else:
                print("all data red")
                data.outb = data.inb
                data.inb = data.inb[len(str(data.inb)):]
                self.sel.unregister(sock)
                sock.close()
                print("connection closed with client")
                print("socket: " + str(sock))

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                tasks.parse_proxy_data.delay(data.outb.decode("utf-8"))
                data.outb = data.outb[len(str(data.outb)):]
                data.outb = []


def init_socket(host, port):
    Proxy(host, port)
