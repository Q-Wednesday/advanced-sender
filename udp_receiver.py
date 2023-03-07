
import socket
import time
import _thread
import matplotlib.pyplot as plt
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9876))
byteCount=0
samples=[]
samplingTime = []
def sample():
    s=time.time()
    print(s)
    while time.time()-s<10:
        time.sleep(0.05)
        samples.append(byteCount/1024/1024)
        samplingTime.append(time.time()-s)

    recvStart = 0
    recvEnd = 0

    i = 1
    while i < len(samples):
        if samples[i] - samples[i-1] > 0:
            recvStart = samplingTime[i-1]
            break
        i += 1

    i = len(samples) - 1
    while i > 0:
        if samples[i] - samples[i-1] > 0:
            recvEnd = samplingTime[i-1]
            break
        i -= 1

    duration = recvEnd - recvStart
    # print(samples)
    print("byteCount:", byteCount)
    # print("Start:", recvStart)
    # print("End:", recvEnd)
    print("Duration:", duration)
    print("Speed:", byteCount/1024/1024/duration)
    plt.plot(samplingTime, samples)
    plt.show()


if __name__== '__main__':
    _thread.start_new_thread(sample,())
    while True:
        data, addr = s.recvfrom(2048)
        byteCount+=len(data)

