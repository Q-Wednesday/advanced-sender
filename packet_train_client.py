import ctypes
import socket
import threading
import time
import _thread


class Receiver(threading.Thread):
    def __init__(self, conn: socket.socket):
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

            return


def check(receiver: Receiver):
    old_count = 0
    while True:
        if receiver.byte_count == old_count and receiver.byte_count != 0:
            receiver.stopped = True
            return
        old_count = receiver.byte_count
        time.sleep(0.05)


class PacketTrainClient:
    def __init__(self, server_address, tcp_port=9878, udp_port=9877):
        self.key = None
        self.start_time = None
        self.server_address = server_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_sock = None
        self.udp_sock = None
        self.send_speed = 100
        self.duration = 100

    def test_speed(self):
        self.start_time = time.time()
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.server_address, self.tcp_port))
        self.key = str(time.time())
        self.tcp_sock.send(self.key.encode('utf-8'))
        time.sleep(0.1)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.settimeout(0.5)
        self.udp_sock.sendto(self.key.encode('utf-8'), (self.server_address, self.udp_port))
        resp = self.tcp_sock.recv(1024)
        print("server response: {}".format(str(resp)))
        result = {100: [], 200: [], 400: []}
        # 每种速度都测三次，不管丢包什么的
        while self.send_speed <= 400:
            for i in range(3):
                byte_count, time_cost = self.test_once()
                server_send = self.tcp_sock.recv(1024)
                result[self.send_speed].append((time_cost, byte_count / int(server_send)))
                time.sleep(time_cost)
            self.send_speed = self.send_speed * 2
        self.tcp_sock.send(b"END")
        return result

    def test_once(self):
        message = "{},{}".format(self.send_speed, self.duration)
        # try:
        #     while True:
        #         data = self.udp_sock.recv(1024)
        #         if not data:
        #             break
        # except Exception:
        #     pass
        # print('clear done')
        receiver = Receiver(self.udp_sock)
        receiver.start()
        self.tcp_sock.send(message.encode('utf-8'))

        check(receiver)
        receiver.join()
        return receiver.byte_count, receiver.end_time - receiver.start_time


# old method
def test_speed():
    start_time = time.time()
    server_address = "81.70.55.189"
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((server_address, 9878))

    key = str(time.time())

    tcp_sock.send(key.encode("utf-8"))

    time.sleep(0.1)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(0.5)
    udp_sock.sendto(key.encode("utf-8"), (server_address, 9877))
    tcp_sock.recv(1024)
    send_speed = 100
    duration = "100"
    while True:
        message = str(send_speed) + "," + duration
        tcp_sock.send(message.encode("utf-8"))
        receiver = Receiver(udp_sock)
        receiver.start()
        check(receiver)
        receiver.join()
        print(receiver.byte_count, receiver.start_time, receiver.end_time)
        server_send = tcp_sock.recv(1024)
        print(str(server_send))
        cost = receiver.end_time - receiver.start_time
        print("time cost:", cost)
        rate_of_receive = receiver.byte_count / int(server_send)
        print("receive/send", rate_of_receive)
        if rate_of_receive < 0.8 or rate_of_receive > 1:
            time.sleep(cost)
            continue
        if cost > 0.13:
            tcp_sock.send(b"END")
            print(send_speed * int(duration) / 1000 / cost)
            break

        send_speed = send_speed * 2
        time.sleep(int(duration) / 1000)

    print(time.time() - start_time)

if __name__=='__main__':
    client=PacketTrainClient('81.70.55.189')
    print(client.test_speed())