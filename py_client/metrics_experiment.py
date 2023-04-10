from packet_train_client import PacketTrainClient
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt

# 每个条件下的循环次数
loop = 5


# 调整发送速度，记录接收时间和丢包率
def test_loss():
    client = PacketTrainClient('81.70.55.189')

    # 发送时间/ms
    client.duration = 100

    # 记录数据
    with open('res/speed-loss-CMCC_4G.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # 表头
        header = ['speed/Mbps']
        for i in range(1, loop + 1):
            header.append('r_time_' + str(i))
            header.append('loss_' + str(i))
        writer.writerow(header)

        # 调整发送速度进行发送
        for s_speed in range(1, 502, 10):
            # 设置发送速度/Mbps
            client.send_speed = s_speed
            # 发送端发出数据量
            data_send = 0
            # 每行数据
            row_data = [s_speed]
            print("speed =", s_speed)
            # 多次实验
            for i in range(loop):
                # 检查发送端是否真的能发到这么多，没发到的话就重试
                while data_send < s_speed * 1024 * 1024 / 8 * (client.duration / 1000):
                    print(str(i + 1) + '/' + str(loop))
                    client.connect()
                    byte_count, time_cost = client.test_once()
                    print(byte_count, time_cost)
                    data_send = client.get_usage()
                    # 如果发送速率达标，记录接收时间和丢包率
                    if data_send >= s_speed * 1024 * 1024 / 8 * (client.duration / 1000):
                        packet_loss = 1 - byte_count / 1024 / 1024 * 8 / (s_speed * client.duration / 1000)
                        row_data.append(time_cost)
                        row_data.append(packet_loss)
                    # 休息一会
                    time.sleep(1)
                # 重置data_send
                data_send = 0
            # 行数据写进表格里
            writer.writerow(row_data)


# 处理丢包数据
def loss_data_process(file_path):
    data = pd.read_csv(file_path)
    # print(data)

    # 横轴数据：发送速率/Mbps
    speed = []
    # 图1纵轴为接收时间，图2纵轴为丢包率
    r_time = []
    packet_loss = []

    # 读取数据
    for col_name in data.columns:
        if col_name.startswith('speed'):
            for i in range(loop):
                speed.extend(data[col_name].tolist())
        elif col_name.startswith('r_time'):
            r_time.extend(data[col_name].tolist())
        elif col_name.startswith('loss'):
            packet_loss.extend(data[col_name].tolist())

    print(len(speed))
    print(len(r_time))
    print(len(packet_loss))

    # 画图
    plt.subplot(121)
    plt.scatter(speed, r_time)
    plt.xlabel("speed/Mbps")
    plt.ylabel("receive_time/s")
    plt.title("speed-receive_time")
    plt.subplot(122)
    plt.xlabel("speed/Mbps")
    plt.ylabel("packet_loss")
    plt.title("speed-packet_loss")
    plt.scatter(speed, packet_loss)
    # plt.subplot(133)
    # plt.scatter(r_time, packet_loss)

    plt.show()


# 调整发送速度和门槛k，记录接收时间和饱和判定结果
def test_saturated(k):
    client = PacketTrainClient('81.70.55.189')

    # 发送时间
    client.duration = 100

    # 记录数据
    with open('res/speed-saturated-CMCC_4G-1.2.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # 表头
        header = ['speed/Mbps']
        for i in range(1, loop + 1):
            header.append('r_time_' + str(i))
            header.append('saturated_' + str(i))
        writer.writerow(header)

        # 调整发送速度开始实验
        for s_speed in range(5, 11, 5):
            # 设置发送速度/Mbps
            client.send_speed = s_speed
            # 发送端发出数据量
            data_send = 0
            # 每行数据
            row_data = [s_speed]
            print("speed =", s_speed)
            # 多次实验
            for i in range(loop):
                # 检查发送端是否真的能发到这么多，没发到的话就重试
                while data_send < s_speed * 1024 * 1024 / 8 * (client.duration / 1000):
                    print(str(i + 1) + '/' + str(loop))
                    client.connect()
                    byte_count, time_cost = client.test_once()
                    print(byte_count, time_cost)
                    data_send = client.get_usage()
                    # 如果发送速率达标，记录接收时间和饱和判断结果
                    if data_send >= s_speed * 1024 * 1024 / 8 * (client.duration / 1000):
                        packet_loss = 1 - byte_count / 1024 / 1024 * 8 / (s_speed * client.duration / 1000)
                        saturated = time_cost > client.duration / 1000 * k
                        row_data.append(time_cost)
                        row_data.append(saturated)
                    # 休息一会
                    time.sleep(1)
                # 重置data_send
                data_send = 0
                # 行数据写进表格里
            writer.writerow(row_data)


# 处理饱和判定数据
def saturated_data_process(file_path):
    data = pd.read_csv(file_path)
    # print(data)

    # 横轴数据：发送速率/Mbps
    speed = []
    # 图1纵轴为接收时间，图2纵轴为判断结果
    r_time = []
    saturated = []

    # 读取数据
    for col_name in data.columns:
        if col_name.startswith('speed'):
            for i in range(loop):
                speed.extend(data[col_name].tolist())
        elif col_name.startswith('r_time'):
            r_time.extend(data[col_name].tolist())
        elif col_name.startswith('saturated'):
            saturated.extend(data[col_name].tolist())

    print(len(speed))
    print(len(r_time))
    print(len(saturated))

    # 画图
    plt.subplot(121)
    plt.scatter(speed, r_time)
    plt.xlabel("speed/Mbps")
    plt.ylabel("receive_time/s")
    plt.title("speed-receive_time")
    plt.subplot(122)
    plt.xlabel("speed/Mbps")
    plt.ylabel("saturated")
    plt.title("speed-packet_saturated")
    plt.scatter(speed, saturated)
    # plt.subplot(133)
    # plt.scatter(r_time, packet_loss)

    plt.show()


if __name__ == '__main__':
    # test_saturated(1.2)
    # saturated_data_process('res/speed-saturated-CMCC_4G-1.2.csv')
    loss_data_process('res/speed-loss-CMCC_4G.csv')
