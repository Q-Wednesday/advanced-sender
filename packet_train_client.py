import ctypes
import socket
import threading
import time
import _thread

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect(("127.0.0.1", 8000))

key = str(time.time())

tcp_sock.send(key.encode("utf-8"))

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.settimeout(0.1)
udp_sock.sendto(key.encode("utf-8"), ("127.0.0.1", 9876))

send_speed = 200


class Receiver(threading.Thread):
    def __init__(self, conn:socket.socket):
        super().__init__()
        self.conn = conn
        self.byte_count = 0
        self.stopped = False
        self.start_time = None
        self.end_time = None

    def run(self) -> None:
        try:
            while not self.stopped:
                r = self.conn.recv(1024)
                if self.start_time is None:
                    self.start_time = time.time()
                self.end_time = time.time()
                self.byte_count += len(r)
        except Exception:
            print(Exception)
            return



def check(receiver: Receiver):
    old_count = 0
    while True:
        if receiver.byte_count == old_count and receiver.byte_count != 0:
            receiver.stopped = True
            #receiver.conn.close()
            return
        old_count = receiver.byte_count
        time.sleep(0.02)

while True:

    receiver = Receiver(udp_sock)
    receiver.start()
    check(receiver)
    receiver.join()
    print(receiver.byte_count, receiver.start_time, receiver.end_time)
    cost=receiver.end_time - receiver.start_time
    print(cost)
    if cost>0.13:
        tcp_sock.send(b"END")
        print(send_speed*0.1/cost)
        break
    send_speed=send_speed*2
    tcp_sock.send(str(send_speed).encode("utf-8"))
