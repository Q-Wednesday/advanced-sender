import ctypes
import socket
import threading
import time
import _thread

start_time=time.time()
server_address="127.0.0.1"
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((server_address, 9878))

key = str(time.time())

tcp_sock.send(key.encode("utf-8"))

time.sleep(0.1)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.settimeout(0.5)
udp_sock.sendto(key.encode("utf-8"), (server_address, 9877))
tcp_sock.recv(1024)
send_speed = 50


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
        time.sleep(0.05)

duration="100"
while True:
    message=str(send_speed)+","+duration
    tcp_sock.send(message.encode("utf-8"))
    receiver = Receiver(udp_sock)
    receiver.start()
    check(receiver)
    receiver.join()
    print(receiver.byte_count, receiver.start_time, receiver.end_time)
    server_send=tcp_sock.recv(1024)
    print(str(server_send))
    cost=receiver.end_time - receiver.start_time
    print("time cost:",cost)
    rate_of_receive= receiver.byte_count / int(server_send)
    print("receive/send",rate_of_receive)
    if rate_of_receive<0.8 or rate_of_receive>1:
        time.sleep(cost)
        continue
    if cost>0.13:
        tcp_sock.send(b"END")
        print(send_speed*int(duration)/1000/cost)
        break

    send_speed=send_speed*2
    time.sleep(int(duration)/1000)

print(time.time()-start_time)
