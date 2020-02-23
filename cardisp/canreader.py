#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from threading import Thread, Event
import time
import datetime
from collections import namedtuple, deque
from pprint import pprint
import logging
from enum import Enum

import can
import cantools


CanSignal = namedtuple('CanSignal', ['name', 'minimum', 'maximum', 'unit', 'comment'])

class CanReader(Thread):
    def __init__(self, group=None, target=None, name=None,
                 canbus='vcan0', bustype='socketcan', dbc=[], maxlen=200, isrunning=Event()):
        super(CanReader,self).__init__(group=group, target=target, 
              name=name)
        
        self.can_bus = can.interface.Bus(canbus, bustype=bustype)

        self.db = cantools.database.Database()
        for dbcfile in dbc:
            logging.warning(f'Loading {dbcfile} into reader database.')
            self.db.add_dbc_file(dbcfile)
        self.data = {}
        self.cansignals = {}

        self.running = isrunning

        for message in self.db.messages:
            signals = message.signals

            for signal in signals:
                self.cansignals[signal.name] = (CanSignal(signal.name, 
                    signal.minimum, 
                    signal.maximum, 
                    signal.unit, 
                    signal.comment))

        for sig in self.cansignals:
            self.data[sig] = deque(maxlen=maxlen)

        self.perftracker = PerfTracker()
        

    def run(self):
        while self.running.is_set():
            message = self.can_bus.recv()
            if message:
                try:
                    newdata = self.db.decode_message(message.arbitration_id, message.data)
                    
                    for sig in newdata:
                        self.data[sig].append( (datetime.datetime.now(), newdata[sig]) )

                        if sig == 'speed_average_non_driven':
                            self.perftracker.tick(self.data[sig])

                except KeyError:
                    pass
                except:
                    logging.exception(f'Packet decode failed for arbid {message.arbitration_id}')


class PerfTracker(object):
    UNKNOWN = 0
    READY = 1
    RUNNING = 2
    COMPLETE = 3

    PERFSTATES = ['Not Ready', 'Ready', 'Running', 'Complete']

    def __init__(self):
        self.results = [self.genPerfResult()]

        self.current_result = self.genPerfResult()

        self.state = PerfTracker.UNKNOWN
        self.curr_et = 0
        self.distance = 0
        self.starttime = 0

    def genPerfResult(self):
        return {
            '0-60': 0,
            '0-100': 0,
            '1/8 Mile': 0,
            '1/8 Mile MPH': 0,
            '1/4 Mile': 0,
            '1/4 Mile MPH': 0, 
        }

    def tick(self, speeddata):
        if self.state in (PerfTracker.UNKNOWN, PerfTracker.RUNNING, PerfTracker.COMPLETE):
            if speeddata[-1][1] == 0.0:
                self.state = PerfTracker.READY
        
        if self.state == PerfTracker.READY:
            if speeddata[-1][1] > 0.0:
                self.state = PerfTracker.RUNNING
                self.resetcounters(speeddata)

        if self.state == PerfTracker.RUNNING:
            self.curr_et = (speeddata[-1][0] - self.starttime).total_seconds()
            self.distance += (
                ((speeddata[-1][1] + speeddata[-2][1])/2) * 0.27777777 *
                (speeddata[-1][0] - speeddata[-2][0]).total_seconds()
                * 0.000621371
            ) 

            if speeddata[-1][1] > 96.5 and self.current_result['0-60'] == 0:
                self.current_result['0-60'] = self.curr_et    

            if speeddata[-1][1] > 160.934 and self.current_result['0-100']==0:
                self.current_result['0-100'] = self.curr_et         

            if self.distance > 0.125 and self.current_result['1/8 Mile']==0:
                self.current_result['1/8 Mile'] = self.curr_et
                self.current_result['1/8 Mile MPH'] = speeddata[-1][1] * 0.621371

            if self.distance > 0.25 and self.current_result['1/4 Mile']==0:
                self.current_result['1/4 Mile'] = self.curr_et
                self.current_result['1/4 Mile MPH'] = speeddata[-1][1] * 0.621371

    def resetcounters(self, speeddata):
            self.starttime = speeddata[-1][0]
            self.distance = 0
            self.curr_et = 0
            self.results.append(self.current_result)
            self.current_result = self.genPerfResult()


        
if __name__ == '__main__':
    e = Event()
    e.set()
    myreader = CanReader(canbus='can0', dbc=['canbus_dbc/gm_global_a_hs.dbc', 'canbus_dbc/m22_obd.dbc'], isrunning=e)

    pprint(myreader.cansignals)
