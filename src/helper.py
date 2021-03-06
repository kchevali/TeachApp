import os
from os.path import isfile, join
import pygame as pg
from random import randint
from math import sqrt
import numpy as np

import pygame.gfxdraw as pgx
import json
import subprocess
from colorsys import hsv_to_rgb
import sys


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


fonts = []
fontInc = 3
ssDict = dict(zip(u"0123456789", u"⁰¹²³⁴⁵⁶⁷⁸⁹"))


# def initFontSizer(fontName, minSize, maxSize):
#     global fonts
#     pg.font.init()
#     fonts = [pg.font.SysFont(fontName, i) for i in range(minSize, maxSize + 1, fontInc)]
#     # print("Font Ready")


def getFont(txt, targetWidth, targetHeight, color):
    # print("Target Width:", targetWidth, "Height:", targetHeight)
    font = searchFont(txt, targetWidth, targetHeight, a=0, b=len(fonts) - 1)
    width, height = font.size(txt)
    # print("Final Width:", width, "Height:", height)
    return font.render(txt, True, color), width, height


def searchFont(txt, targetWidth, targetHeight, a, b):

    index = (a + b) // 2
    font = fonts[index]
    width, height = font.size(txt)
    # print("A:", a, "B:", b, "W:", width, "H:", height)

    if a >= b:
        return font if index == 0 or (width <= targetHeight and height <= targetWidth) else fonts[index - 1]
    if width <= targetWidth and height <= targetHeight:
        return searchFont(txt, targetWidth, targetHeight, index + 1, b)
    return searchFont(txt, targetWidth, targetHeight, a, index - 1)


def findPosition(width, height, containerX, containerY, containerWidth, containerHeight, dx=0.0, dy=0.0):
    return containerX + (dx + 1.0) * (containerWidth - width) / 2, containerY + (dy + 1.0) * (containerHeight - height) / 2


def map(x, a, b, A, B, clamp=True):
    if clamp:
        if(x <= a):
            return A
        if(x >= b):
            return B
    return((B - A) * (x - a) / (b - a)) + A


def rangx(start, end=None, delta=1, outputEnd=False):
    if(end == None):
        start, end = 0, start
    if(type(end) == float or type(delta) == float):
        start = float(start)
    while(start < end):
        yield start
        start += delta
    if outputEnd:
        yield end


def superscript(s):
    return u''.join(ssDict.get(c, c) for c in str(s))


def calcAlignment(x, y, dw, dh, isX=False, isY=False):
    return 2.0 * x / dw - 1.0 if isX and dw != 0 else 0.0, 2.0 * y / dh - 1.0 if isY and dh != 0 else 0.0


def calmColor(hue):
    r, g, b = hsv_to_rgb(hue, 0.54, 0.8)
    return (r * 255, g * 255, b * 255, 0)


def blueShade(blue):
    blue = map(blue, 0, 1, 100, 255)
    const = 40
    return (const, const, blue, 0)


def randomString():
    return str(randint(0, 1 << 31))


def quad(a, b, c):
    d = sqrt(b * b - 4 * a * c)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def solveEquations(a, b):
    """
    a are the coefficients as a 2D numpy array.
    b are the constants as a 1D numpy array.

    Example:
        ax + by = c
        dx + ey = f

        a = np.array([[a,b],[d,e]])
        b = np.array([c,f])
        return np.array([x,y])
    """
    return np.linalg.inv(a).dot(b)


def resourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """

    # print("Input path:", relative_path)
    # print("Path 1:", os.path.abspath(os.curdir))
    # print("Path 2:", os.path.dirname(os.path.realpath(__file__)))
    # print("Path 3:", sys._MEIPASS)

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        relative_path = relative_path.split("/")[-1]
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))[:-4]  # remove the '/src'

    return os.path.join(base_path, relative_path)


def getFiles(path, ext, prefix=""):
    path = resourcePath(path)
    return [f.split(".")[0] for f in os.listdir(path) if isfile(join(path, f)) and f.endswith(ext) and f.startswith(prefix)]


def loadJSON(filePath):
    with open(resourcePath(filePath)) as f:
        return json.load(f)


def openFile(sender):
    subprocess.run(['open', resourcePath(sender.tag)], check=True)


def getDisplayCoord(coord):
    from gui import windowHeight
    # return coord[0], windowHeight - coord[1]
    # TODO - code above moves the origin to the bottom left - fix issues when you have time
    return float(coord[0]), float(coord[1])


def draw_circle(surface, color, rect):
    coord, width, height = rect
    pg.draw.ellipse(surface, color, (*getDisplayCoord((coord[0] - width // 2, coord[1] - height // 2)), width, height))


def draw_rounded_rect(surface, rect, color, corner_radius):
    if rect.width < 2 * corner_radius or rect.height < 2 * corner_radius:
        return
        # raise ValueError(f"Both height (rect.height) and width (rect.width) must be > 2 * corner radius ({corner_radius})")

    # need to use anti aliasing circle drawing routines to smooth the corners
    pgx.aacircle(surface, rect.left + corner_radius, rect.top + corner_radius, corner_radius, color)
    pgx.aacircle(surface, rect.right - corner_radius - 1, rect.top + corner_radius, corner_radius, color)
    pgx.aacircle(surface, rect.left + corner_radius, rect.bottom - corner_radius - 1, corner_radius, color)
    pgx.aacircle(surface, rect.right - corner_radius - 1, rect.bottom - corner_radius - 1, corner_radius, color)

    pgx.filled_circle(surface, rect.left + corner_radius, rect.top + corner_radius, corner_radius, color)
    pgx.filled_circle(surface, rect.right - corner_radius - 1, rect.top + corner_radius, corner_radius, color)
    pgx.filled_circle(surface, rect.left + corner_radius, rect.bottom - corner_radius - 1, corner_radius, color)
    pgx.filled_circle(surface, rect.right - corner_radius - 1, rect.bottom - corner_radius - 1, corner_radius, color)

    rect_tmp = pg.Rect(rect)

    rect_tmp.width -= 2 * corner_radius
    rect_tmp.center = rect.center
    pg.draw.rect(surface, color, rect_tmp)

    rect_tmp.width = rect.width
    rect_tmp.height -= 2 * corner_radius
    rect_tmp.center = rect.center
    pg.draw.rect(surface, color, rect_tmp)


def draw_bordered_rounded_rect(surface, rect, color, border_color, corner_radius, border_thickness):
    if corner_radius < 0:
        raise ValueError(f"border radius ({corner_radius}) must be >= 0")
    rect_tmp = pg.Rect(rect)
    center = rect_tmp.center

    if border_thickness:
        if corner_radius <= 0:
            pg.draw.rect(surface, border_color, rect_tmp)
        else:
            draw_rounded_rect(surface, rect_tmp, border_color, corner_radius)

        rect_tmp.inflate_ip(-2 * border_thickness, -2 * border_thickness)
        inner_radius = corner_radius - border_thickness + 1
    else:
        inner_radius = corner_radius

    if inner_radius <= 0:
        pg.draw.rect(surface, color, rect_tmp)
    else:
        draw_rounded_rect(surface, rect_tmp, color, inner_radius)


if __name__ == '__main__':
    clear()
    print("RUNNING Helper")
    print("x", superscript("23"))
