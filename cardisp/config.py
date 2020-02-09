#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import namedtuple

from imagegauge import *

GaugeDef = namedtuple('GuageDef', ['name', 'gaugeclass'])

defaultstyle = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='fonts/segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=ImageGauge.STD, textcolor='#FFFFFF' )

defaultdelta  = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='fonts/segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=ImageGauge.DELTA, textcolor='#FFFFFF' )

defaultbool  = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='fonts/segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=ImageGauge.BOOL, textcolor='#FFFFFF' )

screens = [
    # Driving Parms
    [
        GaugeDef(name='accelerator_actual_position', gaugeclass=ImageGauge(gaugestyle=defaultstyle, 
                    gaugeconfig=ImageGaugeConfig(displayname="Throttle", unit="%", altunit=None, min=0, max=100, alertval=95, fmtstring='{0:.0f}'))),
        GaugeDef(name='platform_brake_position', gaugeclass=ImageGauge(gaugestyle=defaultstyle, 
                    gaugeconfig=ImageGaugeConfig(displayname="Brake", unit="%", altunit=None, min=0, max=100, alertval=65, fmtstring='{0:.0f}'))),
        GaugeDef(name='steering_wheel_angle', gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="Steering", unit="Deg", altunit=None, min=-2048, max=2048, alertval=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='speed_average_driven', gaugeclass=ImageGauge(gaugestyle=defaultstyle, 
                    gaugeconfig=ImageGaugeConfig(displayname="Speed", unit="kph", altunit="mph", min=0, max=256, alertval=140, fmtstring='{0:.0f}'))),
        GaugeDef(name='tcs_active', gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="TCS", unit="", altunit=None, min=0, max=1, alertval=1, fmtstring='{0}'))),
        GaugeDef(name='abs_active', gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="ABS", unit="", altunit=None, min=0, max=1, alertval=1, fmtstring='{0}'))),
        GaugeDef(name='vehicle_stability_lateral_acceleration', gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="LatAccel", unit="m/s^2", altunit=None, min=-32, max=32, alertval=8.5, fmtstring='{0:.1f}'))),
        GaugeDef(name='vdcs_active', gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="VDCS", unit="", altunit=None, min=0, max=1, alertval=1, fmtstring='{0}'))),
    ]
]
