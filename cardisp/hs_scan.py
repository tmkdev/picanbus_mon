#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import pygame
import time
import datetime
import random
import logging
import sys
import textwrap
from collections import deque
import itertools

from imagegauge import *
from config import * 
from canreader import CanReader

stdguagestyle = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='fonts/segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=ImageGauge.STD, textcolor='#FFFFFF' )

absguagestyle = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='fonts/segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=ImageGauge.DELTA, textcolor='#FFFFFF' )

canreader = CanReader(canbus='vcan0', dbc='canbus_dbc/gm_global_a_hs.dbc')

class HS_Scan:
    screen = None;
    fontcolor = (0, 255, 0)
    white = (255, 255, 255)
    black = (0,0,0)
    red = (255,0,0)

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logging.warning( "I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logging.warning('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        logging.warning("Framebuffer size: %d x %d" % (size[0], size[1]))
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.mouse.set_visible(False)
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        pass

    def updateKPIs(self):
        self.screen.fill(self.black)

        for x in range(4):
            for y in range(2):
                i = x + (4*y)
      
                gauge = screens[0][i]
 
                try:
                    val = canreader.data[gauge.name]
                except:
                    val = None

                pilimage = screens[0][i].gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (x*320,y*360))

        pygame.display.update()

    def updateGraph(self, kpi):
        raise NotImplemented

if __name__ == '__main__':
    scanner = HS_Scan()
    canreader.start()

    while True:
        time.sleep(0.1)
        scanner.updateKPIs()
