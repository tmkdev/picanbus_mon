#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
from imagegauge import ImageGauge, ImageGaugeConfig, ImageGaugeStyle
from imagemeatball import ImageMeatball, ImageMeatballStyle
from imagegraph import ImageGraph

GaugeDef = namedtuple('GuageDef', ['name', 'gaugeclass'])

# Colors
g_red = (255, 0, 0)
g_blue = (0, 0, 255)
g_green = (0, 255, 0)
g_yellow = (255, 255, 0)
g_cyan = (0, 255, 255)
g_white = (255, 255, 255)
g_grey = (0x22, 0x22, 0x22)
g_alert = (0xf0, 0xb0, 0x1d)
g_black = (0, 0, 0)
g_grey50 = (128, 128, 128) 

# files and paths
dbcfiles = ['canbus_dbc/gm_global_a_hs.dbc',
            'canbus_dbc/m22_obd.dbc']
screenshotpath = '/home/pi/logs/screenshots'
g_font = 'fonts/segoeui.ttf'
g_bootimage = "cardisp/images/v-black.jpg"

# evdev key events (Cheap round ble media controller - mine enumerates as BT003)
g_modechange = 164
g_screenup = 115
g_screendown = 114
g_screenshot = 165


# Base Guage Classes
base_red = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                           barcolor=g_red, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                           font=g_font, sweepthick=25, gutter=20, outline=3,
                           outlinecolor=g_white, sweeptype=ImageGauge.STD, textcolor=g_white)

base_blue = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                            barcolor=g_blue, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                            font=g_font, sweepthick=25, gutter=20, outline=3,
                            outlinecolor=g_white, sweeptype=ImageGauge.STD, textcolor=g_white)

base_cyan = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                            barcolor=g_cyan, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                            font=g_font, sweepthick=25, gutter=20, outline=3,
                            outlinecolor=g_white, sweeptype=ImageGauge.STD, textcolor=g_white)

defaultdelta = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                               barcolor=g_red, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                               font=g_font, sweepthick=25, gutter=20, outline=3,
                               outlinecolor=g_white, sweeptype=ImageGauge.DELTA, textcolor=g_white)

defaultbool = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                              barcolor=g_red, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                              font=g_font, sweepthick=25, gutter=20, outline=3,
                              outlinecolor=g_white, sweeptype=ImageGauge.BOOL, textcolor=g_white)

textgauge = ImageGaugeStyle(width=320, height=360, bgcolor=g_black, alertcolor=g_alert,
                            barcolor=g_red, barbgcolor=g_grey, sweepstart=140, sweepend=400,
                            font=g_font, sweepthick=25, gutter=20, outline=3,
                            outlinecolor=g_white, sweeptype=ImageGauge.TEXT, textcolor=g_white)

# Perf Gauge Screens
screens = [
    # Driving Parms
    [
        GaugeDef(name='accelerator_actual_position',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Throttle", unit="%", 
                    altunit=None, min=0, max=100, alertval=95, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='platform_brake_position',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Brake", unit="%", altunit=None,
                    min=0, max=100, alertval=65, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='steering_wheel_angle',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="Steering", unit="Deg", altunit=None,
                    min=-2048, max=2048, alertval=None, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='speed_average_non_driven',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="Speed", unit="kph", altunit="mph",
                    min=0, max=256, alertval=140, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='tcs_active',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="TCS", unit="", altunit=None,
                    min=0, max=1, alertval=1, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='abs_active',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="ABS", unit="", altunit=None,
                    min=0, max=1, alertval=1, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='vehicle_stability_lateral_acceleration',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="LatAccel", unit="m/s^2", altunit=None,
                    min=-32, max=32, alertval=8.5, alertvallow=-8.5, fmtstring='{0:.1f}'))),
        GaugeDef(name='vdcs_active',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="VDCS", unit="", altunit=None,
                    min=0, max=1, alertval=1, alertvallow=None, fmtstring='{0}'))),
    ],
    # ENGINE 1
    [
        GaugeDef(name='Commanded_Air_Fuel_Ratio',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="AFR(CMD)", unit=None, altunit=None,
                    min=0, max=32, alertval=16, alertvallow=12, fmtstring='{0:.1f}'))),
        GaugeDef(name='boost_pressure_indication',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="Boost", unit="%", altunit=None,
                    min=0, max=100, alertval=65, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='engine_intake_temperature',
                    gaugeclass=ImageGauge(gaugestyle=base_cyan, 
                    gaugeconfig=ImageGaugeConfig(displayname="IAT", unit="C", altunit="F",
                    min=-40, max=215, alertval=60, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='OE_IntakeAirTemp2',
                    gaugeclass=ImageGauge(gaugestyle=base_cyan, 
                    gaugeconfig=ImageGaugeConfig(displayname="IAT2", unit="C", altunit="F",
                    min=-40, max=215, alertval=60, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='engine_speed',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="RPM", unit=None, altunit=None,
                    min=0, max=8000, alertval=6500, alertvallow=400, fmtstring='{0:.0f}'))),
        GaugeDef(name='engine_coolant_temperature',
                    gaugeclass=ImageGauge(gaugestyle=base_blue, 
                    gaugeconfig=ImageGaugeConfig(displayname="ECT", unit="C", altunit="F", 
                    min=-40, max=215, alertval=100, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='engine_oil_pressure',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="OilPres", unit="kPa", altunit=None,
                    min=0, max=1020, alertval=None, alertvallow=120, fmtstring='{0}'))),
        GaugeDef(name='engine_torque_actual_ex',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="Torque", unit="ftlb", altunit=None,
                    min=-848, max=1200, alertval=800, alertvallow=-200, fmtstring='{0:.0f}'))),
    ],
    # Transmission 1
    [
        GaugeDef(name='transmission_commanded_gear',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Gear", unit=None, altunit=None,
                    min=0, max=16, alertval=None, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='trans_oil_temp',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="TransTemp", unit="C", altunit=None,
                    min=-40, max=215, alertval=190, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='transmission_torque_converter_clutch_mode',
                    gaugeclass=ImageGauge(gaugestyle=textgauge,
                    gaugeconfig=ImageGaugeConfig(displayname="ClutchMode", unit=None, altunit=None,
                    min=0, max=100, alertval=None, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='requested_gear',
                    gaugeclass=ImageGauge(gaugestyle=textgauge,
                    gaugeconfig=ImageGaugeConfig(displayname="ReqGear", unit=None, altunit=None,
                    min=0, max=16, alertval=None, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='engine_speed',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="RPM", unit=None, altunit=None,
                    min=0, max=8000, alertval=6500, alertvallow=400, fmtstring='{0:.0f}'))),
        GaugeDef(name='Output_Shaft_Angular_Velocity',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="TransRPM", unit=None, altunit=None,
                    min=0, max=8000, alertval=None, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='Estimated_Torque_Ratio',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="TrqRatio", unit=None, altunit=None,
                    min=-64, max=64, alertval=None, alertvallow=None, fmtstring='{0:.2f}'))),
        GaugeDef(name='engine_torque_actual_ex',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Torque", unit="ftlb", altunit=None,
                    min=-848, max=1200, alertval=800, alertvallow=-200, fmtstring='{0:.0f}'))),
    ],
    # OBD Based pids
    [
        GaugeDef(name='O_ShortFuelTrimBank1',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta,
                    gaugeconfig=ImageGaugeConfig(displayname="STFTB1", unit="%", altunit=None,
                    min=-100, max=100, alertval=15, alertvallow=-15, fmtstring='{0:.1f}'))),
        GaugeDef(name='O_ShortFuelTrimBank2',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="STFTB2", unit="%", altunit=None,
                    min=-100, max=100, alertval=15, alertvallow=-15, fmtstring='{0:.1f}'))),
        GaugeDef(name='O_TimingAdvance',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Timing", unit="Deg", altunit=None,
                    min=-64, max=64, alertval=None, alertvallow=-5, fmtstring='{0:.0f}'))),
        GaugeDef(name='O_CalcEngineLoad',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Load", unit="%", altunit=None,
                    min=0, max=100, alertval=85, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='O_LongFuelTrimBank1',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta,
                    gaugeconfig=ImageGaugeConfig(displayname="LTFTB1", unit="%", altunit=None,
                    min=-100, max=100, alertval=10, alertvallow=-10, fmtstring='{0:.1f}'))),
        GaugeDef(name='O_LongFuelTrimBank2',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta,
                    gaugeconfig=ImageGaugeConfig(displayname="LTFTB2", unit="%", altunit=None,
                    min=-100, max=100, alertval=10, alertvallow=-10, fmtstring='{0:.1f}'))),
        GaugeDef(name='engine_intake_temperature',
                    gaugeclass=ImageGauge(gaugestyle=base_cyan,
                    gaugeconfig=ImageGaugeConfig(displayname="IAT", unit="C", altunit="F",
                    min=-40, max=215, alertval=60, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='OE_IntakeAirTemp2',
                    gaugeclass=ImageGauge(gaugestyle=base_cyan, 
                    gaugeconfig=ImageGaugeConfig(displayname="IAT2", unit="C", altunit="F",
                    min=-40, max=215, alertval=60, alertvallow=None, fmtstring='{0:.0f}'))),
    ],
    # FUEL
    [
        GaugeDef(name='Advance_Fuel_Flow_Rate',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="AdvanceFF", unit="g/s", altunit=None,
                    min=0, max=84, alertval=None, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='Instantaneous_Fuel_Flow_Rate',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="InstantFF", unit="g/s", altunit=None,
                    min=0, max=84, alertval=None, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='fuel_consumption_rate',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="FuelCompRate", unit="l/h", altunit=None,
                    min=0, max=103, alertval=None, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='fuel_level_percent',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="FuelLevel", unit="%", altunit=None,
                    min=0, max=100, alertval=None, alertvallow=10, fmtstring='{0:.1f}'))),
        GaugeDef(name='Fuel_Delivery_Pressue_Requested',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="FSREQ_P", unit="kpa", altunit=None,
                    min=0, max=1023, alertval=None, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='fuel_system_estimated_pressure',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="FSEST_P", unit="KPA", altunit=None,
                    min=0, max=1023, alertval=None, alertvallow=10, fmtstring='{0}'))),
        GaugeDef(name='Fuel_Alcohol_Composition',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="FS_AL_C", unit="%", altunit=None,
                    min=0, max=100, alertval=10, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='Engine_Fuel_Control_State', 
                    gaugeclass=ImageGauge(gaugestyle=textgauge, 
                    gaugeconfig=ImageGaugeConfig(displayname="E_FC_State", unit=None, altunit=None, 
                    min=0, max=100, alertval=None, alertvallow=None, fmtstring='{0}'))),
    ],
    # OTHERS...
    [
        GaugeDef(name='Fan_Speed', 
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="FanSpeed", unit="%", altunit=None,
                    min=0, max=100, alertval=90, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='Egine_Cooling_Fan_Adjustment',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta,
                    gaugeconfig=ImageGaugeConfig(displayname="EngFanAdjust", unit="%", altunit=None,
                    min=-100, max=100, alertval=None, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='Generator_Duty_Setpoint',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="GenSetpoint", unit="%", altunit=None,
                    min=-100, max=100, alertval=None, alertvallow=None, fmtstring='{0:.1f}'))),
        GaugeDef(name='Oil_Life_Remaining',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="OilLifeRem", unit="%", altunit=None,
                    min=0, max=100, alertval=None, alertvallow=10, fmtstring='{0:.0f}'))),
        GaugeDef(name='engine_run_active',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="EngRun", unit=None, altunit=None,
                    min=0, max=1, alertval=None, alertvallow=0, fmtstring='{0}'))),
        GaugeDef(name='engine_idle_active',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool, 
                    gaugeconfig=ImageGaugeConfig(displayname="Idle", unit=None, altunit=None,
                    min=0, max=1, alertval=1, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='system_power_mode',
                    gaugeclass=ImageGauge(gaugestyle=textgauge,
                    gaugeconfig=ImageGaugeConfig(displayname="SysPower", unit=None, altunit=None,
                    min=0, max=1, alertval=None, alertvallow=None, fmtstring='{0}'))),
        GaugeDef(name='power_mode_master_accessory',
                    gaugeclass=ImageGauge(gaugestyle=defaultbool,
                    gaugeconfig=ImageGaugeConfig(displayname="AccPower", unit=None, altunit=None,
                    min=0, max=1, alertval=None, alertvallow=0, fmtstring='{0}'))),
    ]
]


perfgauges = [
    GaugeDef(name='speed_average_driven',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Speed", unit="kph", altunit="mph",
                    min=0, max=256, alertval=140, alertvallow=None, fmtstring='{0:.0f}'))),
    GaugeDef(name='accelerator_actual_position',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Throttle", unit="%",
                    altunit=None, min=0, max=100, alertval=95, alertvallow=None, fmtstring='{0:.0f}'))),
]

meatballgauge = ImageMeatball(ImageMeatballStyle(width=640,
                                                height=720,
                                                bgcolor=g_black,
                                                fgcolor=g_white,
                                                textcolor=g_white,
                                                accelquadcolor=g_green,
                                                decelquadcolor=g_red,
                                                latquadcolor=g_yellow,
                                                gridcolor=g_grey50,
                                                font=g_font))

meatballguages =  [
        GaugeDef(name='accelerator_actual_position',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Throttle", unit="%", 
                    altunit=None, min=0, max=100, alertval=95, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='platform_brake_position',
                    gaugeclass=ImageGauge(gaugestyle=base_red,
                    gaugeconfig=ImageGaugeConfig(displayname="Brake", unit="%", altunit=None,
                    min=0, max=100, alertval=65, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='speed_average_non_driven',
                    gaugeclass=ImageGauge(gaugestyle=base_red, 
                    gaugeconfig=ImageGaugeConfig(displayname="Speed", unit="kph", altunit="mph",
                    min=0, max=256, alertval=140, alertvallow=None, fmtstring='{0:.0f}'))),
        GaugeDef(name='steering_wheel_angle',
                    gaugeclass=ImageGauge(gaugestyle=defaultdelta, 
                    gaugeconfig=ImageGaugeConfig(displayname="Steering", unit="Deg", altunit=None,
                    min=-2048, max=2048, alertval=None, alertvallow=None, fmtstring='{0:.0f}'))),
]

graphgauge = ImageGraph(graphstyle='dark_background')

graphs = [
    # Drive perf
    {
        'Brake%': 'platform_brake_position',
        'Throt%': 'accelerator_actual_position',
        'Speed': 'speed_average_non_driven',
        'Steer': 'steering_wheel_angle',
    },
    # TRIMS
    {
        'STFT1': 'O_ShortFuelTrimBank1',
        'SHFT2': 'O_ShortFuelTrimBank1',
        'LTFT1': 'O_LongFuelTrimBank1',
        'LTFT2': 'O_LongFuelTrimBank2'
    },
    # Supercharger Perf
    {
        'IAT': 'engine_intake_temperature',
        'IAT2': 'OE_IntakeAirTemp2',
        'Boost%': 'boost_pressure_indication'
    },
    # Timing
    {
        'Timing': 'O_TimingAdvance',
        'KnockRetard': 'OE_KnockRetard'
    }
]
