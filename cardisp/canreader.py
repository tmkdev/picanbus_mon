#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread, Event
import datetime
from collections import namedtuple, deque
from pprint import pprint
import logging

import can
import cantools

CanSignal = namedtuple('CanSignal',
                       ['name', 'minimum', 'maximum', 'unit', 'comment'])


class CanReader(Thread):
    """Read CANBUS data and store/process it for downstream display

    signals - dictionary of CanSignal objects read from the passed in DBCs
    data - 100ms, 2 minute dict of deques for trending/graphing.
    currentdata - dict of deque(2) for current and last sample.
    perftracker - performance data
    acceltracker - acceleration data
    """

    def __init__(self, group=None, target=None, name=None,
                 canbus='vcan0', bustype='socketcan',
                 dbc=[], maxlen=1200, isrunning=Event()):
        super(CanReader, self).__init__(group=group, target=target,
                                        name=name)

        self.can_bus = can.interface.Bus(canbus, bustype=bustype)

        self.db = cantools.database.Database()
        for dbcfile in dbc:
            logging.warning(f'Loading {dbcfile} into reader database.')
            self.db.add_dbc_file(dbcfile)
        self.data = {}
        self.currentdata = {}
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
            self.currentdata[sig] = deque(maxlen=2)

        self.perftracker = PerfTracker()
        self.acceltracer = AccelTracker()

    def _updatedata(self, sig, datapoint):
        try:
            sampletimedelta = datapoint[0] - self.data[sig][-1][0]

            if sampletimedelta / datetime.timedelta(milliseconds=1) > 100:
                self.data[sig].append(datapoint)

        except IndexError:
            self.data[sig].append(datapoint)

    def run(self):
        while self.running.is_set():
            message = self.can_bus.recv()
            if message:
                try:
                    newdata = self.db.decode_message(message.arbitration_id, message.data)

                    for sig in newdata:
                        datapoint = (datetime.datetime.now(), newdata[sig])
                        self.currentdata[sig].append(datapoint)
                        self._updatedata(sig, datapoint)

                        if sig == 'speed_average_non_driven':
                            self.perftracker.tick(self.currentdata[sig])
                            self.acceltracer.updateaccel(self.currentdata[sig])

                        if sig == 'vehicle_stability_lateral_acceleration':
                            self.acceltracer.updatelat(self.currentdata[sig])

                except KeyError:
                    pass
                except Exception:
                    logging.exception(f'Packet decode failed for arbid {message.arbitration_id}')


class AccelTracker(object):
    def __init__(self):
        self.accel = 0
        self.accelminmax = [0, 0]
        self.lat = 0
        self.latminmax = [0, 0]
        self.history = deque(maxlen=30)

    def updateaccel(self, speeddata):
        try:
            lastspeed = speeddata[-2]
            curspeed = speeddata[-1]
            self.accel = (curspeed[1] - lastspeed[1]) * 0.277778 / (curspeed[0] - lastspeed[0]).total_seconds()
            self.setminmax()

            self.history.append((self.accel, self.lat))

        except IndexError:
            pass
        except Exception:
            logging.exception('Accel calc failed.')

    def updatelat(self, lateraldata):
        try:
            self.lat = lateraldata[-1][1]
            self.setminmax()
            self.history.append((self.accel, self.lat))

        except IndexError:
            pass
        except Exception:
            logging.exception('Accel calc failed.')

    def setminmax(self):
        self.accelminmax[0] = min(self.accelminmax[0], self.accel)
        self.accelminmax[1] = max(self.accelminmax[1], self.accel)
        self.latminmax[0] = min(self.latminmax[0], self.lat)
        self.latminmax[1] = max(self.latminmax[1], self.lat)


class PerfTracker(object):
    UNKNOWN = 0
    READY = 1
    RUNNING = 2
    COMPLETE = 3

    PERFSTATES = ['Stop to Reset', 'Ready', 'Running', 'Complete']

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
        if self.state in (PerfTracker.UNKNOWN,
                          PerfTracker.RUNNING,
                          PerfTracker.COMPLETE):
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
                (speeddata[-1][0] - speeddata[-2][0]).total_seconds() * 0.000621371)

            if speeddata[-1][1] > 96.5 and self.current_result['0-60'] == 0:
                self.current_result['0-60'] = self.curr_et

            if speeddata[-1][1] > 160.934 and self.current_result['0-100'] == 0:
                self.current_result['0-100'] = self.curr_et

            if self.distance > 0.125 and self.current_result['1/8 Mile'] == 0:
                self.current_result['1/8 Mile'] = self.curr_et
                self.current_result['1/8 Mile MPH'] = speeddata[-1][1] * 0.621371

            if self.distance > 0.25 and self.current_result['1/4 Mile'] == 0:
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
    myreader = CanReader(canbus='can0', dbc=['canbus_dbc/gm_global_a_hs.dbc',
                                             'canbus_dbc/m22_obd.dbc'],
                         isrunning=e)

    pprint(myreader.cansignals)
