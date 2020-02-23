#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from threading import Thread, Event
import time
import datetime
from collections import namedtuple, deque
from pprint import pprint
import logging

import can
import cantools


CanSignal = namedtuple('CanSignal', ['name', 'minimum', 'maximum', 'unit', 'comment'])

class CanReader(Thread):
    UNKNOWN = 0
    READY = 1
    RUNNING = 2
    COMPLETE = 3

    PERFSTATES = ['Not Ready', 'Ready', 'Running', 'Complete']

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
        self.perfdata = {
            'state': CanReader.UNKNOWN,
            'curr_et': 0,
            'distance': 0,
            '0-60': 0,
            '0-100': 0,
            '1/4 Mile': 0,
            'starttime': 0,
        }
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

        


    def run(self):
        while self.running.is_set():
            message = self.can_bus.recv()
            if message:
                try:
                    newdata = self.db.decode_message(message.arbitration_id, message.data)
                    
                    for sig in newdata:
                        self.data[sig].append( (datetime.datetime.now(), newdata[sig]) )

                        if sig == 'speed_average_non_driven':
                            self.perftracker()

                except KeyError:
                    pass
                except:
                    logging.exception(f'Packet decode failed for arbid {message.arbitration_id}')


    def perftracker(self):
        if self.perfdata['state'] in (CanReader.UNKNOWN, CanReader.RUNNING, CanReader.COMPLETE):
            #Are we stopped?
            if self.data['speed_average_non_driven'][-1][1] == 0.0:
                self.perfdata['state'] = CanReader.READY
        
        if self.perfdata['state'] == CanReader.READY:
            if self.data['speed_average_non_driven'][-1][1] > 0.0:
                self.perfdata['state'] = CanReader.RUNNING
                self.perfdata['starttime'] = self.data['speed_average_non_driven'][-1][0]
                self.perfdata['distance'] = 0
                self.perfdata['curr_et'] = 0
                self.perfdata['0-60'] = 0
                self.perfdata['0-100'] = 0
                self.perfdata['1/4 Mile'] = 0

        if self.perfdata['state'] == CanReader.RUNNING:
            self.perfdata['curr_et'] = (self.data['speed_average_non_driven'][-1][0] - self.perfdata['starttime']).total_seconds()
            self.perfdata['distance'] += (
                ((self.data['speed_average_non_driven'][-1][1] + self.data['speed_average_non_driven'][-2][1])/2) * 0.27777777 *
                (self.data['speed_average_non_driven'][-1][0] - self.data['speed_average_non_driven'][-2][0]).total_seconds()
                * 0.000621371
            ) 

            if self.data['speed_average_non_driven'][-1][1] > 96.5 and self.perfdata['0-60']==0:
                self.perfdata['0-60'] = self.perfdata['curr_et']          
            if self.data['speed_average_non_driven'][-1][1] > 160.934 and self.perfdata['0-100']==0:
                self.perfdata['0-100'] = self.perfdata['curr_et']          
            if self.perfdata['distance'] > 0.25 and self.perfdata['1/4 Mile']==0:
                self.perfdata['1/4 Mile'] = self.perfdata['curr_et']
            

        
if __name__ == '__main__':
    e = Event()
    e.set()
    myreader = CanReader(canbus='can0', dbc=['canbus_dbc/gm_global_a_hs.dbc', 'canbus_dbc/m22_obd.dbc'], isrunning=e)

    pprint(myreader.cansignals)
