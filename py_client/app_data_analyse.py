import csv
import json
import pandas as pd
from matplotlib import pyplot as plt


def json_to_csv(filepath):
    # 读json然后写csv
    with open(filepath + '.json', 'r') as json_file, open(filepath + '.csv', 'w', newline='') as csv_file:
        data = json.load(json_file)
        csv_writer = csv.writer(csv_file)
        print(len(data))
        for row in data:
            print(data[row])
            csv_writer.writerow(data[row])


def data_process(file_path):
    data = pd.read_csv(file_path+'.csv')
    # print(data)

    # 横轴数据：发送速率/Mbps
    speed = []
    # 图1纵轴为接收时间，图2纵轴为丢包率
    r_time = []
    packet_loss = []

    # 获取数据组数
    loop = int((len(data.columns)-1)/2)
    print("loop:", loop)

    # 读取数据
    for col_name in data.columns:
        if col_name.startswith('Speed'):
            for i in range(loop):
                speed.extend(data[col_name].tolist())
        elif col_name.startswith('rTime'):
            r_time.extend(data[col_name].tolist())
        # todo: 计算丢包率

    print(len(speed))
    print(len(r_time))

    # 画图
    # plt.subplot(121)
    plt.scatter(speed, r_time)
    plt.xlabel("speed/Mbps")
    plt.ylabel("receive_time/ms")
    plt.title("speed-receive_time")
    # plt.subplot(122)
    # plt.xlabel("speed/Mbps")
    # plt.ylabel("saturated")
    # plt.title("speed-packet_saturated")
    # plt.scatter(speed, saturated)
    # plt.subplot(133)
    # plt.scatter(r_time, packet_loss)

    plt.show()


if __name__ == '__main__':
    filepath = './res/appData/20230412-qjx-telecom_5G'
    # json_to_csv(filepath)
    data_process(filepath)