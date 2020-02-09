#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import can
import cantools
from threading import Thread
import time
from collections import namedtuple
from pprint import pprint

CanSignal = namedtuple('CanSignal', ['name', 'minimum', 'maximum', 'unit', 'comment'])


class CanReader(Thread):
    def __init__(self, group=None, target=None, name=None,
                 canbus='vcan0', bustype='socketcan', dbc=None):
        super(CanReader,self).__init__(group=group, target=target, 
              name=name)
        
        self.can_bus = can.interface.Bus(canbus, bustype=bustype)
        self.db = cantools.database.load_file(dbc)
        self.data = {}
        self.running = True
        self.cansignals = {}

        for message in self.db.messages:
            signals = message.signals

            for signal in signals:
                self.cansignals[signal.name] = (CanSignal(signal.name, 
                    signal.minimum, 
                    signal.maximum, 
                    signal.unit, 
                    signal.comment))

    def run(self):
        while self.running:
            message = self.can_bus.recv()
            if message:
                try:
                    newdata = self.db.decode_message(message.arbitration_id, message.data)
                    self.data = { **self.data, **newdata }
                except:
                    pass

if __name__ == '__main__':
    myreader = CanReader(canbus='can0', dbc='gm_global_a_hs.dbc')

    pprint(myreader.cansignals)
