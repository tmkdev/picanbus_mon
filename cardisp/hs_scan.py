#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pygame
import time
import random
import logging
import itertools
from threading import Thread, Event
from queue import Queue

import config as gcfg
from canreader import CanReader
import canwriter
from evdev import InputDevice, ecodes

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

canbus = os.getenv('CANBUS', 'vcan0')
logging.warning(f'Running on CANBUS {canbus}')

events = Queue()

isrunning = Event()
isrunning.set()
canreader = CanReader(canbus=canbus, dbc=['canbus_dbc/gm_global_a_hs.dbc',
                                          'canbus_dbc/m22_obd.dbc'],
                      isrunning=isrunning)


class HS_Scan(object):
    screen = None
    fontcolor = (0, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)

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

        self.displayimage(gcfg.g_bootimage)

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        pass

    def displayimage(self, imagename):
        self.screen.fill(self.black)
        startuplogo = pygame.image.load(imagename)
        startuplogo = pygame.transform.scale(startuplogo, (1280, 720))
        self.screen.blit(startuplogo, (0, 0))

        pygame.display.update()

    def updateKPIs(self, curscreen):
        self.screen.fill(self.black)

        for x in range(4):
            for y in range(2):
                i = x + (4*y)
                gauge = gcfg.screens[curscreen][i]

                try:
                    val = canreader.data[gauge.name][-1][1]
                except IndexError:
                    val = None
                except Exception:
                    logging.exception('KPI conversion failed')

                pilimage = gauge.gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (x*320, y*360))

        pygame.display.update()

    def updategraph(self):
        self.screen.fill(self.black)

        data = {'Brake': canreader.data['platform_brake_position'],
                'TPS': canreader.data['throttle_position'],
                'Speed': canreader.data['speed_average_non_driven'],
                'Steer': canreader.data['steering_wheel_angle'],
                }

        pilimage = gcfg.graphgauge.drawgraph(data)
        raw_str = pilimage.tobytes("raw", 'RGBA')
        surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGBA')
        self.screen.blit(surface, (0, 0))

        pygame.display.update()

    def perfscreen(self):
        self.screen.fill(self.black)
        pt = canreader.perftracker

        textImage = self.font1.render(f'Current', True, (255, 255, 255))
        self.screen.blit(textImage, (40, 0))

        textImage = self.font1.render(f'Last', True, (255, 255, 255))
        self.screen.blit(textImage, (500, 0))

        y = 42
        for perf in pt.current_result:
            textImage = self.font1.render(f'{perf}: {pt.current_result[perf]:0.2f}',
                                          True, (255, 255, 255))
            self.screen.blit(textImage, (40, y))
            textImage = self.font1.render(f'{perf}: {pt.results[-1][perf]:0.2f}',
                                          True, (255, 255, 255))
            self.screen.blit(textImage, (500, y))
            y += 42

        textImage = self.font2.render(f"ET: {pt.curr_et:0.2f}s", True, (255, 255, 255))
        self.screen.blit(textImage, (40, 350))

        textImage = self.font2.render(f"Dist: {pt.distance:0.4f}mi", True, (255, 255, 255))
        self.screen.blit(textImage, (40, 450))

        textImage = self.font2.render(f"{pt.PERFSTATES[pt.state]}", True, (255, 255, 255))
        self.screen.blit(textImage, (40, 550))

        # draw gauges
        for y in range(len(gcfg.perfgauges)):
                gauge = gcfg.perfgauges[y]
                try:
                    val = canreader.data[gauge.name][-1][1]
                except Exception:
                    val = None

                pilimage = gauge.gaugeclass.drawval(val)
                raw_str = pilimage.tobytes("raw", 'RGB')
                surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
                self.screen.blit(surface, (960, y * 360))

        pygame.display.update()

    def meatball(self):
        self.screen.fill(self.black)

        pilimage = gcfg.meatballgauge.drawmeatball(canreader.acceltracer.lat, canreader.acceltracer.accel)

        raw_str = pilimage.tobytes("raw", 'RGB')
        surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
        self.screen.blit(surface, (320, 0))

        quads = [(0, 0), (0, 360), (960, 0), (960, 360)]

        for i, gauge in enumerate(gcfg.meatballguages):
            try:
                val = canreader.data[gauge.name][-1][1]
            except KeyError:
                val = None

            pilimage = gauge.gaugeclass.drawval(val)
            raw_str = pilimage.tobytes("raw", 'RGB')
            surface = pygame.image.fromstring(raw_str, pilimage.size, 'RGB')
            self.screen.blit(surface, quads[i])

        pygame.display.update()


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

    perfscreens = itertools.cycle([scanner.perfscreen, scanner.meatball, scanner.updategraph])
    perfscreen = next(perfscreens)
    curscreen = 0
    mode = 0

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
                    if event.code == 115:
                        curscreen += 1
                        mode = 0
                    if event.code == 114:
                        curscreen -= 1
                        mode = 0

                    if event.code in [165, 163]:
                        mode = 1
                        perfscreen = next(perfscreens)

                    if curscreen >= len(gcfg.screens):
                        curscreen = 0
                    if curscreen < 0:
                        curscreen = len(gcfg.screens) - 1

            time.sleep(0.1)
            if mode == 0:
                scanner.updateKPIs(curscreen)
            elif mode == 1:
                perfscreen()
        except KeyboardInterrupt:
            isrunning.clear()
            break

    keyboard.join()
    canreader.join()

    # Shut down writers.
    for writer in writers:
        writer.join()

    exit(0)
