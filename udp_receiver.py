
import socket
import time
import _thread
import matplotlib.pyplot as plt
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9876))
byteCount=0
samples=[]
def sample():
    s=time.time()
    print(s)
    while time.time()-s<10:
        time.sleep(0.05)
        samples.append(byteCount)
    print(samples)
    plt.plot(samples)
    plt.show()


if __name__== '__main__':
    # _thread.start_new_thread(sample,())
    while True:
        print(time.time())
        data, addr = s.recvfrom(2048)
        print(data)
        byteCount+=len(data)

