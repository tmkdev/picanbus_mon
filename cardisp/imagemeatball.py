#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
from PIL import Image, ImageDraw, ImageFont

ImageMeatballStyle = namedtuple('ImageMeatballStyle', ['width', 'height', 'bgcolor', 'fgcolor',
                                                       'textcolor', 'accelquadcolor',
                                                       'decelquadcolor', 'latquadcolor', 'gridcolor',
                                                       'font'])


class ImageMeatball(object):
    g_force = 9.81

    def __init__(self, gaugestyle: ImageMeatballStyle):
        self.style = gaugestyle
        self.fontsmall = ImageFont.truetype(self.style.font, size=32)
        self.fonttext = ImageFont.truetype(self.style.font, size=24)

    def drawmeatball(self, ax, ay, history):
        balldim = min(self.style.width, self.style.height)

        g_scaler = int((balldim / 2) / 1.25)
        quarter_g = int(g_scaler * 0.25)

        slicecol = [self.style.latquadcolor,
                    self.style.accelquadcolor,
                    self.style.latquadcolor,
                    self.style.decelquadcolor]

        im = Image.new('RGB', (self.style.width, self.style.height), self.style.bgcolor)
        draw = ImageDraw.Draw(im)

        draw.ellipse((0, 0, balldim, balldim), self.style.fgcolor)
        sq = self.scalequads(ax, ay)

        for x in range(0, 4):
            sc = self.scalecolor(slicecol[x], sq[x])
            draw.pieslice((3, 3, balldim-3, balldim-3), (x * 90) - 45, (x * 90) + 45, sc)

        draw.ellipse((quarter_g, quarter_g,
                     balldim-quarter_g,
                     balldim-quarter_g),
                     self.style.bgcolor,
                     self.style.gridcolor,
                     width=2)

        for gval in [0.25, 0.5, 0.75, 1.0]:
                thisg = int(g_scaler * gval)
                draw.ellipse((thisg, thisg, balldim-thisg, balldim-thisg),
                             self.style.bgcolor,
                             self.style.gridcolor,
                             width=2)

        draw.line((balldim/2, 0, balldim/2, balldim), fill=self.style.gridcolor)
        draw.line((0, balldim/2, balldim, balldim/2), fill=self.style.gridcolor)

        hist = list(history)

        for i, point in enumerate(hist):
            dotx, doty = self.dotcoord(point[0], point[1])
            dotscale = 15/len(history)
            thisdot = int(i * dotscale)
            colscale = 200/len(history)
            thiscol = int(i * colscale)

            draw.ellipse((dotx-thisdot, doty-thisdot, dotx+thisdot, doty+thisdot), (thiscol, thiscol, 0))

        dotx, doty = self.dotcoord(ax, ay)
        draw.ellipse((dotx-15, doty-15, dotx+15, doty+15),
                     self.style.bgcolor,
                     self.style.textcolor,
                     width=2)
        draw.ellipse((dotx-10, doty-10, dotx+10, doty+10), self.style.textcolor)

        self.drawvals(draw, ax, ay)

        del draw

        return im

    def dotcoord(self, ax, ay):
        balldim = min(self.style.width, self.style.height)
        g_scaler = int((balldim / 2) / 1.25)

        scalex = int((ax / ImageMeatball.g_force) * g_scaler)
        scaley = int((ay / ImageMeatball.g_force) * g_scaler)
        dotx = balldim/2 + scalex
        doty = balldim/2 + scaley

        return dotx, doty

    def drawvals(self, draw, ax, ay):
        gx = ax / ImageMeatball.g_force
        gy = ay / ImageMeatball.g_force

        xtext = f'Lateral: {gx:.02f}g'
        ytext = f'Accel: {gy:.02f}g'

        # fontbox1 = draw.textsize(xtext, font=self.fontsmall)
        fontbox2 = draw.textsize(ytext, font=self.fontsmall)

        draw.text((5, self.style.height - 50),
                  xtext,
                  fill=self.style.textcolor,
                  font=self.fontsmall)

        draw.text((self.style.width - 5 - fontbox2[0], self.style.height - 50),
                  ytext,
                  fill=self.style.textcolor,
                  font=self.fontsmall)

        return draw

    def drawminmax(self, draw, minmaxx, minmany):
        raise NotImplementedError

    def scalequads(self, ax, ay):
        # Min scale factor for color. IE: color * minscale is the darkest
        minscale = 0.4
        # Min G before scaling - 0 was annoying while driving. Make the coloring matter.. 
        min_g = 0.15
        
        #            ax+   ay+ ax-  ay-
        scalequad = [minscale, minscale, minscale, minscale]

        if ax > min_g:
            scalequad[0] = max(min(minscale, abs(ax / ImageMeatball.g_force)), 1)
        if ax < -min_g:
            scalequad[2] = max(min(minscale, abs(ax / ImageMeatball.g_force)), 1)
        if ay > min_g:
            scalequad[1] = max(min(minscale, abs(ay / ImageMeatball.g_force)), 1)
        if ay < -min_g:
            scalequad[3] = max(min(minscale, abs(ay / ImageMeatball.g_force)), 1)

        return scalequad

    def scalecolor(self, color, scale):
        return tuple(int(c * scale) for c in color)


if __name__ == '__main__':
    style = ImageMeatballStyle(width=640,
                               height=720,
                               bgcolor=(0, 0, 0),
                               fgcolor=(255, 255, 255),
                               textcolor=(255, 255, 255),
                               accelquadcolor=(0, 255, 0),
                               decelquadcolor=(255, 0, 0),
                               latquadcolor=(255, 255, 0),
                               gridcolor=(128, 128, 128),
                               font='fonts/segoeui.ttf')

    mb = ImageMeatball(style)

    mbi = mb.drawmeatball(6, 6)

    mbi.save('meatball.png')
