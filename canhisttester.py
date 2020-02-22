import time
from cardisp import canreader
from threading import Event

if __name__ == '__main__':
    e = Event()
    e.set()

    myreader = canreader.CanReader(canbus='vcan0', dbc=['canbus_dbc/gm_global_a_hs.dbc'], maxlen=2000, isrunning=e)

    myreader.start()

    while True:
        #print(myreader.data.keys())
        try:
            print(len(myreader.data['trans_oil_temp']))
        except IndexError:
            pass
        except KeyboardInterrupt:
            e.clear()
            myreader.join()
            exit(1)

        time.sleep(1)