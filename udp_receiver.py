
import socket
import time
import _thread
import matplotlib.pyplot as plt
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9876))
byteCount=0
samples=[]
samplingTime = []
speed = []
recvStart = 0
recvEnd = 0
recvTime = 0
def sample():
    s=time.time()
    print(s)
    while time.time()-s<10:
        time.sleep(0.05)
        samples.append(byteCount/1024/1024)
        samplingTime.append(time.time()-s)

    # i = 1
    # while i < len(samples):
    #     if samples[i] - samples[i-1] > 0:
    #         recvStart = samplingTime[i-1]
    #         break
    #     i += 1

    i = len(samples) - 1
    while i > 0:
        if samples[i] - samples[i-1] > 0:
            recvEnd = samplingTime[i-1]
            break
        i -= 1

    # calculate the receiving speed between two sampling points
    speed.append(0)
    i = 1
    while i < len(samples):
        speed.append((samples[i]-samples[i-1])/(samplingTime[i]-samplingTime[i-1]))
        i += 1

    duration = recvEnd - (recvStart - s)
    # print(samples)
    print("byteCount:", byteCount)
    # print("Start:", recvStart)
    # print("End:", recvEnd)
    print("Duration:", duration)
    print("Speed:", byteCount/1024/1024/duration)
    plt.subplot(121)
    plt.plot(samplingTime, samples)
    # plt.show()
    plt.subplot(122)
    plt.plot(samplingTime, speed)
    plt.show()

def checker():
    lastByteCount = byteCount
    while byteCount == 0 or lastByteCount != byteCount:
        lastByteCount = byteCount
        time.sleep(0.01)

# def receiver():



if __name__== '__main__':
    # _thread.start_new_thread(sample,())
    _thread.start_new_thread(checker, ())
    while True:
        data, addr = s.recvfrom(2048)
        if recvStart == 0:
            recvStart = time.time()
            print("Start receiving:", recvStart)
        recvTime = time.time() - recvStart
        byteCount+=len(data)

