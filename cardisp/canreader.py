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
        self.running = isrunning
        self.cansignals = {}

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
                except KeyError:
                    pass
                except:
                    logging.exception(f'Packet decode failed for arbid {message.arbitration_id}')

if __name__ == '__main__':
    e = Event()
    e.set()
    myreader = CanReader(canbus='can0', dbc=['canbus_dbc/gm_global_a_hs.dbc', 'canbus_dbc/m22_obd.dbc'], isrunning=e)

    pprint(myreader.cansignals)
