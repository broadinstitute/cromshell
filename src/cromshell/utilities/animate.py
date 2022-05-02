import math
import random
import time
import os
import copy

turtleRight = """
               __  
    .,-;-;-,. /'_\ 
  _/_/_/_|_\_\) /  
'-<_><_><_><_>=/\  
  `/_/====/_/-'\_\ 
   ""     ""    "" 
"""

turtleLeft = """
  __
 /_'\.,-;-;-,.
  \ (/_/__|_\_\_
  /\=<_><_><_><_>-'
 /_/'-\_\====\_\'
 ""    ""     ""
 """

grass = """                                                                              
 |      |                  \   /     \         |      |                            \        
||\||  ||||/// |||\ ||| \||\ \|/ | \ ||| \|| /||\||  ||||/// |||\ ||| \||\ \|/ | \ ||| \|| /
"""


def merge_line(base, addon, position):
    return base[0: position] + addon + base[position + len(addon):]


print(merge_line('123456789', "ab", 2))

RESET = '\033[0m'


def get_color_by_code(code):
    return u"\u001b[38;5;" + str(code) + "m"


def init_grid(width, height, value):
    return [[value for x in range(width)] for y in range(height)]


class AsciiImage:
    def __init__(self, chars: list[list[str]], colors: list[list[int]], transparentChar: str = None):
        self.transparentChar = transparentChar
        self.height: int = len(colors)
        self.width: int = len(colors[0])
        self.colors = colors
        self.chars = chars

    def getChar(self, x: int, y: int) -> str:
        return self.chars[self.height - y - 1][x]

    def setChar(self, x: int, y: int, value: str) -> None:
        self.chars[self.height - y - 1][x] = value

    def getColor(self, x: int, y: int) -> int:
        return self.colors[self.height - y - 1][x]

    def setColor(self, x: int, y: int, value: int) -> None:
        assert value < 256
        self.colors[self.height - y - 1][x] = value

    def getPixel(self, x: int, y: int) -> (str, int):
        return (self.getChar(x, y), self.getColor(x, y))

    def setPixel(self, x: int, y: int, value: (str, int)) -> None:
        char, color = value
        self.setChar(x, y, char)
        self.setColor(x, y, color)

    def isTransparent(self, x: int, y: int) -> bool:
        return self.getChar(x, y) == self.transparentChar


def from_ascii(art: str, color: int, transparentChar=" "):
    transparentChar = transparentChar
    lines = art.splitlines()
    lines = [x for x in lines if len(x) > 0]

    height: int = len(lines)
    width: int = len(lines[0])
    assert color < 256
    colors = init_grid(width, height, color)
    chars = init_grid(width, height, " ")

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            chars[y][x] = char
    return AsciiImage(chars, colors, transparentChar)


def make_blank(width, height):
    colors = init_grid(width, height, 0)
    chars = init_grid(width, height, " ")
    return AsciiImage(chars, colors, " ")


test = """123a
456b
789c"""

overlay_test = """ab
cd"""
overlay_testImage = from_ascii(overlay_test, 35)

testImage = from_ascii(test, 6)


def print_image(image: AsciiImage):
    for y in range(0, image.height):
        out = ""
        last_color = None
        for x in range(0, image.width):
            color = image.getColor(x, image.height - y - 1)
            if last_color is not color:
                out += get_color_by_code(color)
                last_color = color
            out += image.getChar(x, image.height - y - 1)
        out += RESET
        print(out)


def composite(base: AsciiImage, overlay: AsciiImage, x: int, y: int):
    for j in range(0, overlay.height):
        for i in range(0, overlay.width):
            if x + i < base.width and y + j < base.height:
                if not overlay.isTransparent(i, j):
                    base.setPixel(x + i, y + j, overlay.getPixel(i, j))
    return base


flower_yellow_base = """
 * 
\|/
"""

flower_yellow_Image = from_ascii(flower_yellow_base, 40)
flower_yellow_Image.setColor(1, 1, 11)

flower_purple_base = """
8
|
"""
flower_purple_image = from_ascii(flower_purple_base, 36)
flower_purple_image.setColor(0, 1, 207)

grass1 = from_ascii(
    """

|
""", 40)

grass2 = from_ascii(
    """
|
|
""", 40)

grass3 = from_ascii(
    """
 
/
""", 40)

grass4 = from_ascii(
    """
 
\
""", 40)

grass5 = from_ascii(
    """
 
 
""", 40)


def generateBackground(width: int) -> AsciiImage:
    blank = make_blank(width, 7)
    grassElements = random.choices(
        [grass1, grass2, grass3, grass4, grass5],
        weights=[10, 2, 2, 2, 1],
        k=width
    )
    for i, element in enumerate(grassElements):
        composite(blank, element, i, 0)
    return blank

def get_flower_overlay(flower: AsciiImage, percent, width):
    actual_percent = min(random.gauss(percent, percent / 2), 100)
    number_of_flowers = math.floor((actual_percent / 100) * width)
    flowers = make_blank(width, flower.height)
    for i in range(0, number_of_flowers):
        composite(flowers, flower, random.randint(0,width), 0)
    return flowers

def animateTurtle():
    turtleRightImage = from_ascii(turtleRight, 28, " ")
    width = os.get_terminal_size().columns

    grassImage = generateBackground(width)
    composite(grassImage, get_flower_overlay(flower_yellow_Image, 5, width), 0,0)
    composite(grassImage, get_flower_overlay(flower_purple_image, 10, width), 0, 0)

    print(grassImage.height)
    print(turtleRightImage.height)

    nlines = grassImage.height

    # scroll up to make room for output
    print(f"\033[{nlines}S", end="")

    # move cursor back up
    print(f"\033[{nlines}A", end="")

    # save current cursor position
    print("\033[s", end="")

    for t in range(0, width - turtleRightImage.width):
        # restore saved cursor position
        print("\033[u", end="")
        buffer = copy.deepcopy(grassImage)
        composite(buffer, turtleRightImage, t, 0)
        print_image(buffer)
        time.sleep(.5)


animateTurtle()
