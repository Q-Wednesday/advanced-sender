import datetime
import json
import os
import time
from packet_train_client import  PacketTrainClient



columns=[]
for speed in ['100','200','400']:
    for item in ['recv','duration','speed']:
        for num in ['1','2','3']:
            columns.append("{}_{}_{}".format(speed,item,num))

columns.append('speed_test')
with open('test_result_{}.csv'.format(datetime.datetime.now()),'w') as fp:
    fp.write(",".join(columns)+'\n')
    for i in range(30):
        client=PacketTrainClient('81.70.55.189')
        result=client.test_speed()
        line=[]
        for speed in [100,200,400]:
            for r in result[speed]:
                line.append(str(r[1]))
                line.append(str(r[0]))
                line.append(str(speed*0.1/r[0]))
        st_result=os.popen('speedtest-cli --no-upload --json')
        st_result=json.load(st_result)
        line.append(str(st_result['download']/1024/1024))
        fp.write(",".join(line)+'\n')