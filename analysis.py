import json
import os
import matplotlib.pyplot as plt

sz_s=[]
sz_r=[]

delta_s=[]
delta_r=[]

index=[]

with open('result/1K_10ms_s.json', 'r', encoding='utf-8') as f_s:
    data_s = json.load(f_s)
    for i in data_s:
        sz_s.append(i['_source']['layers']['opensafety_udp']['data']['data.len'])
    for i in range(1, len(data_s)+1, 2):
        delta_s.append(float(data_s[i]['_source']['layers']['udp']['Timestamps']['udp.time_delta'])*1000)
    print(delta_s)

    # chart
    for i in range(len(delta_s)):
        plt.bar(str(i+1), delta_s[i])

    plt.show()