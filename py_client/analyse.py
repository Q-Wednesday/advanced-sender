import dpkt
import matplotlib.pyplot as plt
import numpy
import numpy as np
from collections import OrderedDict


def get_timestamps(filename):
    timestamps = []
    with open(filename, 'rb') as fp:
        pcap = dpkt.pcapng.Reader(fp)
        for timestamp, buffer in pcap:
            timestamps.append(timestamp)
    return timestamps


def scatter_timestamps(timestamps):
    ts = np.array(timestamps)
    ts = ts - np.min(ts)
    y = np.ones_like(ts)
    plt.scatter(ts, y, s=1)
    plt.show()


def scatter_timestamps_advanced(timestamps, show=True):
    counter = OrderedDict()
    for timestamp in timestamps:
        if counter.get(timestamp) is None:
            counter[timestamp] = 1
        else:
            counter[timestamp] += 1
    x = np.array([key * 1000 for key in counter.keys()])
    x = x - x.min()
    y = [value for key, value in counter.items()]
    plt.ylim(ymin=0, ymax=max(y) + 1)
    plt.scatter(x, y, s=1)
    plt.xlabel("time(ms)")
    plt.ylabel("num of packet")
    if show:
        plt.show()


def scatter_2data(timestamps1, timestamps2):
    plt.subplot(1, 2, 1)
    scatter_timestamps_advanced(timestamps1, show=False)
    plt.subplot(1, 2, 2)
    scatter_timestamps_advanced(timestamps2, show=False)


def specified_period(timestamps, duration):
    ts = np.array(timestamps)
    ts_min = np.min(ts)
    idx = np.where(ts < ts_min + duration)
    return ts[idx]


def max_gap(arr):
    arr = np.array(arr)
    # 计算相邻元素之间的差值
    diff = np.diff(arr)

    # 返回差值中的最大值
    return np.max(diff)