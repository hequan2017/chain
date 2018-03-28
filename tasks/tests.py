from django.test import TestCase

# Create your tests here.

import threading
import time

def  sayhi(num):
    print("running is {}".format(num))
    time.sleep(3)

if __name__=="__main__":
    t1 = threading.Thread(target=sayhi,args=(1,))
    t2 = threading.Thread(target=sayhi, args=(2,))
    t1.start()
    t2.start()
    print(t1.getName())
    print(t2.getName())
    t2.join()
    print("--main---")


    t_list = []
    for i in range(10):    ##循环调用
        t = threading.Thread(target=sayhi,args=[i,])
        t.start()
        t_list.append(t)

    for i in t_list:
        i.join()
    print("结束了")