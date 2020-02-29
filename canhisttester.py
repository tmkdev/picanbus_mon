import time
from cardisp import canreader
from threading import Event

import numpy as np
import matplotlib.pyplot as plt


def plot(series):
    try:
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        fig.set_size_inches(12.8, 7.2)

        data = list(series)

        x, y = zip(*data)

        x = [(xp-x[-1]).total_seconds() for xp in x]

        ax.plot(x, y)
        ax.set_xlabel('Rel Time(s)')
        ax.set_ylabel('RPM')
        ax.set_title("Engine RPM")

        plt.savefig('test.png', dpi=100)

        plt.close()

    except Exception:
        pass


if __name__ == '__main__':
    e = Event()
    e.set()

    myreader = canreader.CanReader(canbus='vcan0', dbc=['canbus_dbc/gm_global_a_hs.dbc'], maxlen=2000, isrunning=e)

    myreader.start()

    while True:
        # print(myreader.data.keys())
        try:
            plot(myreader.data['speed_average_non_driven'])
            print(myreader.data['speed_average_non_driven'])
            print(myreader.data['throttle_position'])
        except IndexError:
            pass
        except KeyboardInterrupt:
            e.clear()
            myreader.join()
            exit(1)

        time.sleep(2)
