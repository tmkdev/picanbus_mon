#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import deque
import datetime
import logging
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


class ImageGraph(object):
    def __init__(self, graphstyle='dark_background'):
        self.graphstyle = graphstyle

    def formatdata(self, kpi):
        x = []
        y = []

        try:
            data = list(kpi)
            x, y = zip(*data)
            x = [(xp-x[-1]).total_seconds() for xp in x]
        except Exception:
            logging.info('Data formatting failed')

        return x, y

    def drawgraph(self, kpis: dict):
        try:
            plt.style.use(self.graphstyle)
            plt.rcParams.update({'font.size': 18})

            fig, ax = plt.subplots()
            fig.set_size_inches(12.8, 7.2)
            # fig.suptitle(', '.join(kpis.keys()), fontsize=16)

            for kpi in kpis:
                x, y = self.formatdata(kpis[kpi])
                ax.plot(x, y)
                ax.set_xlabel('Rel Time(s)')
                ax.grid(color='#333333')
                ax.set_xlim([-120, 0])

            fig.legend(kpis.keys(), loc='upper left', ncol=4, mode="expand")

            im = self._fig2img(fig)
            plt.close()

            return im

        except Exception:
            pass

    def _fig2data(self,  fig):
        """
        @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
        @param fig a matplotlib figure
        @return a numpy 3D array of RGBA values
        """
        # draw the renderer
        fig.canvas.draw()

        # Get the RGBA buffer from the figure
        w, h = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
        buf.shape = (w, h, 4)

        # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
        buf = np.roll(buf, 3, axis=2)
        return buf

    def _fig2img(self, fig):
        """
        @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
        @param fig a matplotlib figure
        @return a Python Imaging Library ( PIL ) image
        http://www.icare.univ-lille1.fr/tutorials/convert_a_matplotlib_figure
        """
        # put the figure pixmap into a numpy array
        buf = self._fig2data(fig)
        w, h, d = buf.shape

        try:
            im = Image.frombuffer("RGBA", (w, h), buf.tostring(), 'raw', "RGBA", 0, 1)
        except Exception:
            logging.exception('Graph Image Creation Failed')

        return im


if __name__ == '__main__':
    data = {
        'speed_average_non_driven': deque([(datetime.datetime(2020, 2, 28, 9, 42, 11, 296388), 55.625), (datetime.datetime(2020, 2, 28, 9, 42, 11, 333536), 55.59375), (datetime.datetime(2020, 2, 28, 9, 42, 11, 370685), 55.75), (datetime.datetime(2020, 2, 28, 9, 42, 11, 460411), 55.71875), (datetime.datetime(2020, 2, 28, 9, 42, 11, 560487), 55.8125), (datetime.datetime(2020, 2, 28, 9, 42, 11, 660135), 55.921875), (datetime.datetime(2020, 2, 28, 9, 42, 11, 759670), 55.875), (datetime.datetime(2020, 2, 28, 9, 42, 11, 859974), 55.90625), (datetime.datetime(2020, 2, 28, 9, 42, 11, 965114), 55.9375), (datetime.datetime(2020, 2, 28, 9, 42, 12, 59960), 55.9375), (datetime.datetime(2020, 2, 28, 9, 42, 12, 159938), 55.90625), (datetime.datetime(2020, 2, 28, 9, 42, 12, 259230), 55.921875), (datetime.datetime(2020, 2, 28, 9, 42, 12, 359954), 56.109375), (datetime.datetime(2020, 2, 28, 9, 42, 12, 459700), 56.109375), (datetime.datetime(2020, 2, 28, 9, 42, 12, 560140), 55.921875), (datetime.datetime(2020, 2, 28, 9, 42, 12, 659736), 56.0625), (datetime.datetime(2020, 2, 28, 9, 42, 12, 765568), 56.140625), (datetime.datetime(2020, 2, 28, 9, 42, 12, 859687), 56.046875), (datetime.datetime(2020, 2, 28, 9, 42, 12, 959702), 55.984375), (datetime.datetime(2020, 2, 28, 9, 42, 13, 59806), 56.046875), (datetime.datetime(2020, 2, 28, 9, 42, 13, 159686), 55.84375), (datetime.datetime(2020, 2, 28, 9, 42, 13, 259668), 55.828125)], maxlen=2000),
        'throttle_position': deque([(datetime.datetime(2020, 2, 28, 9, 42, 11, 295581), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 333264), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 370415), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 459610), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 559668), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 659321), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 759402), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 859174), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 11, 964476), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 59154), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 159137), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 258963), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 359124), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 458898), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 559332), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 658941), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 764933), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 858889), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 12, 959432), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 13, 59527), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 13, 159407), 0.393156), (datetime.datetime(2020, 2, 28, 9, 42, 13, 259395), 0.393156)], maxlen=2000),
    }

    ig = ImageGraph()

    gim = ig.drawgraph(data)

    gim.save('graph.png')
