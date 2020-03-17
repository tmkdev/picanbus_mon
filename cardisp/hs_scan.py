#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pygame
import time
import random
import logging
import datetime
from collections import deque
from threading import Thread, Event
from queue import Queue

import config as gcfg
from canreader import CanReader
import canwriter
from evdev import InputDevice, ecodes
import gpiozero

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

canbus = os.getenv('CANBUS', 'vcan0')
logging.warning(f'Running on CANBUS {canbus}')

events = Queue()

isrunning = Event()
isrunning.set()
canreader = CanReader(canbus=canbus, dbc=gcfg.dbcfiles,
                      isrunning=isrunning)


class HS_Scan(object):
    screen = None

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logging.warning("I'm running under X display = {0}".format(disp_no))

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
        self.font1 = pygame.font.Font(gcfg.g_font, 40)
        self.font2 = pygame.font.Font(gcfg.g_font, 96)
        self.font3 = pygame.font.Font(gcfg.g_font, 20)

        self.displayimage(gcfg.g_bootimage)

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        pass

    def displayimage(self, imagename):
        self.screen.fill(gcfg.g_black)
        startuplogo = pygame.image.load(imagename)
        startuplogo = pygame.transform.scale(startuplogo, (1280, 720))
        self.screen.blit(startuplogo, (0, 0))

        pygame.display.update()

    def updateKPIs(self, curscreen):
        self.screen.fill(gcfg.g_black)

        for x in range(4):
            for y in range(2):
                i = x + (4*y)
                gauge = curscreen[i]

                try:
                    val = canreader.currentdata[gauge.name][-1][1]
                except IndexError:
                    val = None
                except Exception:
                    logging.exception('KPI conversion failed')

                pilimage = gauge.gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (x*320, y*360))

        self.drawheader()

    def assemblegraphdata(self, graphdata):
        kpis = {}
        for kpi in graphdata:
            kpis[kpi] = canreader.data[graphdata[kpi]]

        return kpis

    def updategraph(self, graphdata):
        self.screen.fill(gcfg.g_black)
        kpis = self.assemblegraphdata(graphdata)

        pilimage = gcfg.graphgauge.drawgraph(kpis)
        raw_str = pilimage.tobytes("raw", 'RGBA')
        surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGBA')
        self.screen.blit(surface, (0, 0))

        pygame.display.update()

    def perfscreen(self):
        self.screen.fill(gcfg.g_black)
        pt = canreader.perftracker

        textImage = self.font1.render(f'Current', True, gcfg.g_white)
        self.screen.blit(textImage, (40, 0))

        textImage = self.font1.render(f'Last', True, gcfg.g_white)
        self.screen.blit(textImage, (500, 0))

        y = 42
        for perf in pt.current_result:
            textImage = self.font1.render(f'{perf}: {pt.current_result[perf]:0.2f}',
                                          True, gcfg.g_white)
            self.screen.blit(textImage, (40, y))
            textImage = self.font1.render(f'{perf}: {pt.results[-1][perf]:0.2f}',
                                          True, gcfg.g_white)
            self.screen.blit(textImage, (500, y))
            y += 42

        textImage = self.font2.render(f"ET: {pt.curr_et:0.2f}s", True, gcfg.g_white)
        self.screen.blit(textImage, (40, 350))

        textImage = self.font2.render(f"Dist: {pt.distance:0.4f}mi", True, gcfg.g_white)
        self.screen.blit(textImage, (40, 450))

        textImage = self.font2.render(f"{pt.PERFSTATES[pt.state]}", True, gcfg.g_white)
        self.screen.blit(textImage, (40, 550))

        # draw gauges
        for y in range(len(gcfg.perfgauges)):
                gauge = gcfg.perfgauges[y]
                try:
                    val = canreader.currentdata[gauge.name][-1][1]
                except Exception:
                    val = None

                pilimage = gauge.gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (960, y * 360))

        pygame.display.update()

    def meatball(self):
        self.screen.fill(gcfg.g_black)

        pilimage = gcfg.meatballgauge.drawmeatball(canreader.acceltracer.lat, canreader.acceltracer.accel, canreader.acceltracker.history)

        raw_str = pilimage.tobytes("raw", 'RGB')
        surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
        self.screen.blit(surface, (320, 0))

        quads = [(0, 0), (0, 360), (960, 0), (960, 360)]

        for i, gauge in enumerate(gcfg.meatballguages):
            try:
                val = canreader.currentdata[gauge.name][-1][1]
            except KeyError:
                val = None

            pilimage = gauge.gaugeclass.drawval(val)
            raw_str = pilimage.tobytes("raw", 'RGB')
            surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
            self.screen.blit(surface, quads[i])

        pygame.display.update()

    def drawheader(self):
        cpu = gpiozero.CPUTemperature()
        loadaverage = gpiozero.LoadAverage(minutes=1)
        nowstring = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cputempstring = f'CPU Temp: {cpu.temperature:0.0f}C'
        loadavgstring = f'CPU Load: {loadaverage.load_average:0.2f}'

        textImage = self.font3.render(nowstring, True, gcfg.g_white)
        self.screen.blit(textImage, (0, 0))

        textImage = self.font3.render(cputempstring, True, gcfg.g_white)
        self.screen.blit(textImage, (500, 0))

        textImage = self.font3.render(loadavgstring, True, gcfg.g_white)
        self.screen.blit(textImage, (1125, 0))

        pygame.display.update()

    def screenshot(self):
        tstamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'{gcfg.screenshotpath}/screenshot_{tstamp}.jpg'
        pygame.image.save(self.screen, filename)


def keyboardworker():
    while isrunning.is_set():
        try:
            dev = InputDevice('/dev/input/event1')
            dev.grab()
            for event in dev.read_loop():
                if event.type == ecodes.EV_KEY:
                    events.put(event)
        except Exception:
            logging.info('Waiting for input device')
            time.sleep(1)
    dev.ungrab()


if __name__ == '__main__':
    # Start screen and reader
    scanner = HS_Scan()
    canreader.start()

    perfscreens = deque([scanner.perfscreen, scanner.meatball])
    perfscreen = perfscreens[0]

    gaugescreens = deque(gcfg.screens)
    gaugescreen = gaugescreens[0]

    graphs = deque(gcfg.graphs)
    graph = graphs[0]

    modes = deque([0, 1, 2])
    mode = modes[0]

    # Start can senders
    logging.warning('Starting OBD senders')
    writers = []
    for pid in canwriter.sendpids:
        writer = canwriter.CanWriter(canbus=canbus, pid=pid, isrunning=isrunning)
        writer.start()
        writers.append(writer)

        time.sleep(random.random())

    logging.warning('Starting keybord reader')
    keyboard = Thread(target=keyboardworker)
    keyboard.start()

    while True:
        try:
            if not events.empty():
                event = events.get_nowait()
                logging.warning(event)
                if event.type == 1 and event.value == 1:
                    if event.code == gcfg.g_screenup:
                        if mode == 0:
                            gaugescreens.rotate(1)
                            gaugescreen = gaugescreens[0]
                        if mode == 1:
                            perfscreens.rotate(1)
                            perfscreen = perfscreens[0]
                        if mode == 2:
                            graphs.rotate(1)
                            graph = graphs[0]
                    if event.code == gcfg.g_screendown:
                        if mode == 0:
                            gaugescreens.rotate(-1)
                            gaugescreen = gaugescreens[0]
                        if mode == 1:
                            perfscreens.rotate(-1)
                            perfscreen = perfscreens[0]
                        if mode == 2:
                            graphs.rotate(-1)
                            graph = graphs[0]

                    if event.code == gcfg.g_modechange:
                        modes.rotate(1)
                        mode = modes[0]

                    if event.code == gcfg.g_screenshot:
                        scanner.screenshot()

            time.sleep(0.1)
            if mode == 0:
                scanner.updateKPIs(gaugescreen)
            elif mode == 1:
                perfscreen()
            elif mode == 2:
                scanner.updategraph(graph)

        except KeyboardInterrupt:
            isrunning.clear()
            break

    keyboard.join()
    canreader.join()

    # Shut down writers.
    for writer in writers:
        writer.join()

    exit(0)
