import json
import os
import matplotlib.pyplot as plt
import numpy as np

sz_s=[]
sz_r=[]

delta_a_s=[]
delta_s=[]
delta_r=[]

index_d=[]
index_s=[]

with open('result/1K_10ms_s.json', 'r', encoding='utf-8') as f_s:
    data_s = json.load(f_s)
    for i in data_s:
        sz_s.append(i['_source']['layers']['opensafety_udp']['data']['data.len'])
    for i in range(1, len(data_s)+1, 2):
        delta_s.append(float(data_s[i]['_source']['layers']['udp']['Timestamps']['udp.time_delta'])*1000)
    print(delta_s)

    # interval chart
    plt.subplot(121)
    for i in range(len(delta_s)):
        index_d.append(str(i+1))
        delta_a_s.append(10)
    x = np.arange(len(index_d))
    width = 0.25
    plt.bar(x - width/2, delta_a_s, width, label='app_send')
    plt.bar(x, delta_s, width, label='network_send')
    # plt.bar(x + width/2, delta_r, width, label='network_receive')
    plt.xticks(x, labels=index_d)
    plt.ylabel('Interval')
    plt.legend()

    # size chart
    plt.subplot(122)
    for i in range(len(sz_s)):
        index_s.append(str(i+1))
    x = np.arange(len(index_s))
    width = 0.25
    plt.bar(x - width/2, sz_s, width, label='size_send')
    plt.bar(x + width/2, sz_s, width, label='size_receive')
    plt.xticks(x, labels=index_s)
    plt.ylabel('Size')
    plt.legend()

    plt.show()