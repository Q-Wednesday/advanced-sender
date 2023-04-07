import ctypes
import socket
import threading
import time
import _thread
import matplotlib.pyplot as plt
import csv


class Receiver(threading.Thread):
    def __init__(self, conn: socket.socket):
        super().__init__()
        self.conn = conn
        self.byte_count = 0
        self.stopped = False
        self.start_time = time.time()
        self.end_time = time.time()

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
    start_time = time.time()
    while True:
        if receiver.byte_count == 0 and time.time() - start_time > 1:
            receiver.stopped = True
            return
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
        self.stop_trigger = False

    def send_trigger(self):
        while not self.stop_trigger:
            print("Trigger")
            for i in range(10):
                if not self.stop_trigger:
                    self.udp_sock.sendto(self.key.encode('utf-8'), (self.server_address, self.udp_port))
                else:
                    return
            try:
                time.sleep(0.05)
            except:
                return

    def connect(self):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.server_address, self.tcp_port))
        self.key = str(time.time())
        self.tcp_sock.send(self.key.encode('utf-8'))
        time.sleep(0.1)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.settimeout(0.5)

        # 打洞线程
        self.stop_trigger = False
        send_trigger = threading.Thread(target=self.send_trigger)
        send_trigger.start()

        resp = self.tcp_sock.recv(1024)
        print("server response: {}".format(str(resp)))
        self.stop_trigger = True

    def test_once_with_speed(self, speed):
        self.send_speed = speed
        self.test_once()

    def test_speed(self):
        self.start_time = time.time()
        self.connect()
        result = {100: [], 200: [], 400: []}
        # 每种速度都测三次，不管丢包什么的
        while self.send_speed <= 400:
            for i in range(3):
                byte_count, time_cost = self.test_once()
                # server_send = self.tcp_sock.recv(1024)
                print("byte_count:", byte_count)
                # print("server_send:",str(server_send))
                # result[self.send_speed].append((time_cost, byte_count / int(server_send)))
                time.sleep(time_cost)
            self.send_speed = self.send_speed * 2
        self.tcp_sock.send(b"END")
        return result

    def test_once(self):
        message = "{},{};".format(self.send_speed, self.duration)
        # try:
        #     while True:
        #         data = self.udp_sock.recv(1024)
        #         if not data:
        #             break
        # except Exception:
        #     pass
        # print('clear done')
        self.receiver = Receiver(self.udp_sock)
        self.receiver.start()
        self.tcp_sock.send(message.encode('utf-8'))

        check(self.receiver)
        self.receiver.join()
        return self.receiver.byte_count, self.receiver.end_time - self.receiver.start_time

    def continue_send(self):
        message = "{},{};".format(self.send_speed, 5000)
        self.receiver = Receiver(self.udp_sock)
        self.receiver.start()
        self.tcp_sock.send(message.encode('utf-8'))

    def stop_send(self):
        message = "STOP;"
        self.tcp_sock.send(message.encode('utf-8'))
        self.receiver.join()
        print("receive:", self.receiver.byte_count)

    def get_usage(self):
        self.tcp_sock.send("USAGE;".encode('utf-8'))
        while True:
            massage = self.tcp_sock.recv(1024)
            massage = massage.decode('utf-8')
            print("message:", massage)
            if massage.startswith("USAGE:"):
                return int(massage[6:])

    # 以下为误饱和实验方法
    def change_speed_test(self):
        self.start_time = time.time()
        self.connect()

        k = []
        speed = []
        lost = []

        self.duration = 100

        # 记录结果
        with open('speed-k.csv', 'w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['speed/Mbps'])

            for s in range(30, 201, 5):
                self.send_speed = s
                data = [s]
                print("s = ", s)
                for i in range(50):
                    print(str(i + 1) + "/50")
                    byte_count, time_cost = self.test_once()
                    speed.append(s)
                    # 如果丢包率过高，记k为0（无效值）
                    if byte_count / 1024 / 1024 * 8 / (self.duration * s / 1000) < 0.8:
                        k.append(0)
                        data.append(0)
                    else:
                        data.append(time_cost * 10)
                        k.append(time_cost * 10)

                    time.sleep(1)
                writer.writerow(data)

        self.tcp_sock.send(b"END")

        plt.scatter(speed, k)
        plt.title('speed-k')
        plt.xlabel('speed')
        plt.ylabel('k')
        plt.show()

    def change_sendtime_test(self):
        self.start_time = time.time()
        self.connect()

        k = []
        sendTime = []

        # 记录结果
        with open('duration-k.csv', 'w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['time/ms'])

            self.send_speed = 60

            # 发送时间从50到1000，跨度为10，每组测50次
            for s in range(600, 611, 10):
                self.duration = s
                data = [s]
                print("duration = ", s)
                for i in range(10):
                    print(str(i + 1) + "/50")
                    byte_count, time_cost = self.test_once()
                    sendTime.append(s)
                    # 如果丢包率过高，记k为0（无效值）
                    if byte_count / 1024 / 1024 * 8 / (self.send_speed * s / 1000) < 0.8:
                        k.append(0)
                        data.append(0)
                    else:
                        k.append(time_cost * 1000 / s)
                        data.append(time_cost * 1000 / s)
                    time.sleep(time_cost)
                writer.writerow(data)

        self.tcp_sock.send(b"END")

        plt.scatter(sendTime, k)
        plt.title('duration-k')
        plt.xlabel('duration')
        plt.ylabel('k')
        plt.show()

    # 多次发送避免误饱和实验
    def multi_test(self, k, loop):
        self.start_time = time.time()
        self.connect()

        # 设置duration
        self.duration = 100

        # 画图：speed为横轴，multi_saturated为纵轴
        multi_speed = []
        multi_saturated = []
        single_speed = []
        single_saturated = []

        # 记录结果
        with open('multi_test_' + str(loop) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['speed/Mbps'])

            for s in range(10, 151):
                self.send_speed = s
                data = [s]
                print("s = ", s)
                # 跑多次
                for i in range(loop):
                    byte_count, time_cost = self.test_once()
                    print(time_cost * 1000)
                    # 如果丢包率过高，记saturated为2（无效值）
                    if byte_count / 1024 / 1024 * 8 / (self.duration * s / 1000) < 0.8:
                        saturated = 2
                    else:
                        if time_cost * 1000 >= k * self.duration:
                            saturated = 1
                        else:
                            saturated = 0
                    print(str(s), ",", str(i + 1), "/ 3 :", saturated)
                    # 表
                    data.append(saturated)
                    # 单个散点
                    single_speed.append(s)
                    single_saturated.append(saturated)
                    time.sleep(time_cost)
                # multi散点
                multi_speed.append(s)
                # 有一个没跑满就认为没跑满
                # 取出第二个到最后一个元素
                sub_lst = data[1:]
                # 如果有0，直接返回0
                if 0 in sub_lst:
                    multi_saturated.append(0)
                # 如果都是2，返回2
                elif all(x == 2 for x in sub_lst):
                    multi_saturated.append(2)
                # 如果列表中有1，且剩下的都是2，返回1
                elif 1 in sub_lst:
                    multi_saturated.append(1)
                # 写表格
                writer.writerow(data)

        plt.scatter(single_speed, single_saturated)
        plt.title('speed-saturated-single')
        plt.xlabel('speed')
        plt.ylabel('saturated')

        plt.subplot(122)
        plt.scatter(multi_speed, multi_saturated)
        plt.title('speed-saturated-' + str(loop))
        plt.xlabel('speed')
        plt.ylabel('saturated')

        plt.show()

        self.tcp_sock.send(b"END")


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


if __name__ == '__main__':
    client = PacketTrainClient('81.70.55.189')
    client.multi_test(1.2, 3)
    # print(client.test_speed())
    # client.connect()
    # client.continue_send()
    # time.sleep(3)
    # client.stop_send()
    # print(client.get_usage())
