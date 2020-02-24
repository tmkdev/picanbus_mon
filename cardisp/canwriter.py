#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import can
from threading import Thread, Event
import time
from collections import namedtuple
import random
import logging

OBDPid = namedtuple('OBDPid', ['name', 'arbid', 'data', 'frequency'])

sendpids = [
    OBDPid('Calc Engine Load', 0x7df, [0x03, 0x22,  0x00, 0x04, 0x00, 0x00, 0x00, 0x00], 1),
    OBDPid('STFTB1', 0x7df, [0x03, 0x22, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00], 1),
    OBDPid('LTFTB1', 0x7df, [0x03, 0x22, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00], 5),
    OBDPid('STFTB2', 0x7df, [0x03, 0x22, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00], 1),
    OBDPid('LTFTB2', 0x7df, [0x03, 0x22, 0x00, 0x09, 0x00, 0x00, 0x00, 0x00], 5),
    OBDPid('Timing', 0x7df, [0x03, 0x22, 0x00, 0x0e, 0x00, 0x00, 0x00, 0x00], 1),
    OBDPid('O2_S1', 0x7df, [0x03, 0x22, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00], 0.5),
    OBDPid('O2_S2', 0x7df, [0x03, 0x22, 0x00, 0x15, 0x00, 0x00, 0x00, 0x00], 0.5),
    OBDPid('O2_S3', 0x7df, [0x03, 0x22, 0x00, 0x16, 0x00, 0x00, 0x00, 0x00], 0.5),
    OBDPid('O2_S4', 0x7df, [0x03, 0x22, 0x00, 0x17, 0x00, 0x00, 0x00, 0x00], 0.5),
    OBDPid('IAT2', 0x7df, [0x03, 0x22, 0x20, 0x06, 0x00, 0x00, 0x00, 0x00], 2.5),
    OBDPid('KnockRetard', 0x7df, [0x03, 0x22, 0x11, 0xA6, 0x00, 0x00, 0x00, 0x00], 0.5),
    OBDPid('MAF', 0x7df, [0x03, 0x22, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00], 0.5)]


class CanWriter(Thread):
    def __init__(self, group=None, target=None, name=None,
                 canbus='vcan0', bustype='socketcan', pid=None, isrunning=None):
        super(CanWriter, self).__init__(group=group, target=target, name=name)

        self.can_bus = can.interface.Bus(canbus, bustype=bustype)
        self.isrunning = isrunning
        self.pid = pid

    def run(self):
        msg = can.Message(arbitration_id=self.pid.arbid, data=self.pid.data, is_extended_id=False)
        task = self.can_bus.send_periodic(msg, self.pid.frequency)
        assert isinstance(task, can.CyclicSendTaskABC)

        while self.isrunning.is_set():
            time.sleep(0.1)

        self.can_bus.stop_all_periodic_tasks()

        logging.warning(f"stopped cyclic send of pid {self.pid.name}")


if __name__ == '__main__':
    isrunning = Event()
    isrunning.set()
    writers = []
    for pid in sendpids:
        writer = CanWriter(canbus='vcan0', pid=pid, isrunning=isrunning)
        writer.start()
        writers.append(writer)

        time.sleep(random.random())

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    isrunning.clear()

    for writer in writers:
        writer.join()

    exit(1)
