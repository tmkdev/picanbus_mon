import logging
from collections import namedtuple
from PIL import Image, ImageDraw, ImageFont


ImageGaugeStyle = namedtuple('ImageGaugeStyle', ['width', 'height', 'bgcolor', 'alertcolor', 
                    'barcolor', 'barbgcolor', 'sweepstart', 'sweepend', 'font', 'sweepthick', 
                    'gutter', 'outline', 'outlinecolor', 'sweeptype', 'textcolor'])

ImageGaugeConfig = namedtuple('ImageGaugeConfig', ['displayname', 'unit', 'altunit', 'min', 'max', 'alertval'])

defaultguagestyle = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#FF0000", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='segoeui.ttf', sweepthick=25, gutter=20, outline=3,
                                    outlinecolor="#FFFFFF", sweeptype=1, textcolor='#FFFFFF' )

defaultconfig = ImageGaugeConfig(displayname="TransTemp", unit="C", altunit="F", min=-40, max=240, alertval=230)

class ImageGauge(object):
    NOSWEEP = 0
    STD = 1
    DELTA = 2
    BOOL = 3

    def __init__(self, gaugestyle, gaugeconfig):
        self.gaugestyle = gaugestyle
        self.gaugeconfig = gaugeconfig
        self.fontsmall = ImageFont.truetype(self.gaugestyle.font, size=35)
        self.fontlarge = ImageFont.truetype(self.gaugestyle.font, size=110)


    def drawval(self, value):
        cenx = self.gaugestyle.width/2
        ceny = self.gaugestyle.height/2

        bgcol=self.gaugestyle.bgcolor
        if abs(value) >= self.gaugeconfig.alertval:
            bgcol=self.gaugestyle.alertcolor

        im = Image.new('RGB', (self.gaugestyle.width, self.gaugestyle.height), bgcol)
        draw = ImageDraw.Draw(im)

        if self.gaugestyle.sweeptype == ImageGauge.STD:
            draw = self.drawstandardweep(value, draw, bgcol)
        elif self.gaugestyle.sweeptype == ImageGauge.DELTA:
            draw = self.drawabssweep(value, draw, bgcol)

        if self.gaugeconfig.unit:
            text = f"{self.gaugeconfig.displayname}: {self.gaugeconfig.unit}"
        else: 
            text = f"{self.gaugeconfig.displayname}"

        fontbox1 = draw.textsize(text, font=self.fontsmall)
        fontbox2 = draw.textsize(str(value), font=self.fontlarge)

        draw.text( (self.gaugestyle.width / 2-(fontbox1[0]/2),
                    self.gaugestyle.height-fontbox1[1] - self.gaugestyle.gutter), 
                    text, 
                    fill=self.gaugestyle.textcolor, 
                    font=self.fontsmall)
        draw.text( (self.gaugestyle.width / 2-(fontbox2[0]/2), 
                    ceny - fontbox2[1]/2), 
                    str(value), 
                    fill=self.gaugestyle.textcolor, 
                    font=self.fontlarge)

        del draw

        # write to stdout
        return im

    def drawstandardsweep(self, value, draw, bgcolor):
        goff = (self.gaugestyle.height-(2 * self.gaugestyle.gutter)) / 4 - 2 * self.gaugestyle.gutter 

        valscale = (value - self.gaugeconfig.min) / (self.gaugeconfig.max - self.gaugeconfig.min)
       
        barscale = ( self.gaugestyle.sweepend - self.gaugestyle.sweepstart)

        valbar = int( ( valscale * barscale )  + self.gaugestyle.sweepstart)
    
        draw.pieslice(( self.gaugestyle.gutter, 
                        self.gaugestyle.gutter + goff, 
                        self.gaugestyle.width - self.gaugestyle.gutter , 
                        self.gaugestyle.width - self.gaugestyle.gutter + goff ), 
                        self.gaugestyle.sweepstart, 
                        self.gaugestyle.sweepend, 
                        fill=self.gaugestyle.barbgcolor, 
                        outline=self.gaugestyle.outlinecolor,
                        width=self.gaugestyle.outline)

        draw.pieslice(( self.gaugestyle.gutter + self.gaugestyle.outline, 
                        self.gaugestyle.gutter + self.gaugestyle.outline + goff, 
                        self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.outline, 
                        self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.outline + goff ), 
                        self.gaugestyle.sweepstart + 1, 
                        valbar, 
                        fill=self.gaugestyle.barcolor,
                        outline=None)

        draw.ellipse(( self.gaugestyle.sweepthick + self.gaugestyle.gutter, 
                    self.gaugestyle.sweepthick + self.gaugestyle.gutter + goff, 
                    self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.sweepthick, 
                    self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.sweepthick + goff), 
                    fill=bgcolor, 
                    outline=None)

        return draw

    def drawabssweep(self, value, draw, bgcolor):
        goff = (self.gaugestyle.height-(2 * self.gaugestyle.gutter)) / 4 - 2 * self.gaugestyle.gutter 
        sweepmidpoint = (self.gaugestyle.sweepend + self.gaugestyle.sweepstart) / 2

        valscale = (value - (self.gaugeconfig.max + self.gaugeconfig.min)/2) / (self.gaugeconfig.max - self.gaugeconfig.min)
       
        barscale = ( self.gaugestyle.sweepend - self.gaugestyle.sweepstart)

        valbar = int( ( valscale * barscale ) + sweepmidpoint )
    
        draw.pieslice(( self.gaugestyle.gutter, 
                        self.gaugestyle.gutter + goff, 
                        self.gaugestyle.width - self.gaugestyle.gutter , 
                        self.gaugestyle.width - self.gaugestyle.gutter + goff ), 
                        self.gaugestyle.sweepstart, 
                        self.gaugestyle.sweepend, 
                        fill=self.gaugestyle.barbgcolor, 
                        outline=self.gaugestyle.outlinecolor,
                        width=self.gaugestyle.outline)

        draw.pieslice(( self.gaugestyle.gutter + self.gaugestyle.outline, 
                        self.gaugestyle.gutter + self.gaugestyle.outline + goff, 
                        self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.outline, 
                        self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.outline + goff ), 
                        min(valbar, sweepmidpoint), 
                        max(valbar, sweepmidpoint), 
                        fill=self.gaugestyle.barcolor,
                        outline=None)

        draw.ellipse(( self.gaugestyle.sweepthick + self.gaugestyle.gutter, 
                    self.gaugestyle.sweepthick + self.gaugestyle.gutter + goff, 
                    self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.sweepthick, 
                    self.gaugestyle.width - self.gaugestyle.gutter - self.gaugestyle.sweepthick + goff), 
                    fill=bgcolor, 
                    outline=None)


        return draw

    def drawboolean(self, value, draw, bgcolor):
        pass


if __name__ == '__main__':
    teststyle = ImageGaugeStyle(width=320, height=360, bgcolor="#000000", alertcolor="#f0b01d",
                                    barcolor="#0000FF", barbgcolor="#222222", sweepstart=140, sweepend=400,
                                    font='segoeui.ttf', sweepthick=25, gutter=20, outline=4,
                                    outlinecolor='#FFFFFF', sweeptype=1, textcolor='#FFFFFF' )

    testconfig = ImageGaugeConfig(displayname="TPS", unit="%", altunit=None, min=-100, max=100, alertval=90)

    ig = ImageGauge(gaugestyle=teststyle, gaugeconfig=testconfig)

    im = ig.drawval(95)

    im.show()
