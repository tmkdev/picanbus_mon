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

from threading import Thread, Event
from queue import Queue

from imagegauge import *
from config import * 
from canreader import CanReader
import canwriter
from evdev import *

events = Queue()

isrunning = Event()
isrunning.set()
canreader = CanReader(canbus='vcan0', dbc=['canbus_dbc/gm_global_a_hs.dbc', 'canbus_dbc/m22_obd.dbc'], isrunning=isrunning)

class HS_Scan(object):
    screen = None
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
        pygame.mouse.set_visible(False)
        pygame.font.init()
        
        self.displayimage("cardisp/images/v-black.jpg")

    
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        pass

    def displayimage(self, imagename):
        self.screen.fill(self.black)
        startuplogo = pygame.image.load(imagename)
        startuplogo = pygame.transform.scale(startuplogo, (1280,720))
        self.screen.blit(startuplogo, (0 ,0))
        
        pygame.display.update()

    def updateKPIs(self, curscreen):
        self.screen.fill(self.black)

        for x in range(4):
            for y in range(2):
                i = x + (4*y)
      
                gauge = screens[curscreen][i]
 
                try:
                    val = canreader.data[gauge.name][-1][1]
                except:
                    val = None

                pilimage = gauge.gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (x*320,y*360))

        pygame.display.update()

    def updateGraph(self, kpi):
        raise NotImplemented

    
def keyboardworker():
    while isrunning.is_set():
        try:        
            dev = InputDevice('/dev/input/event1')
            for event in dev.read_loop():
               if event.type == ecodes.EV_KEY:
                    events.put(event)
        except:
            logging.info('Waiting for input device')
            time.sleep(1)


if __name__ == '__main__':
    #Start screen and reader
    scanner = HS_Scan()
    canreader.start()

    #Start can senders
    logging.warning('Starting OBD senders')
    writers = []
    for pid in canwriter.sendpids:
        writer = canwriter.CanWriter(canbus='vcan0', pid=pid, isrunning=isrunning)
        writer.start()
        writers.append(writer)

        time.sleep(random.random())

    logging.warning('Starting keybord reader')
    keyboard = Thread(target=keyboardworker)
    keyboard.start()

    curscreen = 0

    while True:
        try:
            if not events.empty():
                event = events.get_nowait()
                logging.warning(event)
                if event.type == 1 and event.value == 1:
                    if event.code == 115:
                        curscreen += 1
                    if event.code == 114:
                        curscreen -= 1

                    if curscreen >= len(screens):
                        curscreen=0
                    if curscreen < 0:
                        curscreen = len(screens) -1 
            
            
            time.sleep(0.1)
            scanner.updateKPIs(curscreen)
        except KeyboardInterrupt:
            isrunning.clear()
            break

    keyboard.join()
    canreader.join()

    #Shut down writers. 
    for writer in writers:
        writer.join()       

    exit(0)
