import time
import termcolor
import os
import copy

print("start")

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

    def __init__(self, art: str, color: int):
        lines = art.splitlines()
        lines = [x for x in lines if len(x) > 0]

        self.height: int = len(lines)
        self.width: int = len(lines[0])
        assert color < 256
        self.colors = init_grid(self.width, self.height, color)
        self.chars = init_grid(self.width, self.height, " ")

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                self.chars[y][x] = char

    def getChar(self, x: int, y: int) -> str:
        return self.chars[self.height-y-1][x]

    def setChar(self, x: int, y: int, value: str) -> None:
        self.chars[self.height-y-1][x] = value

    def getColor(self, x: int, y: int) -> int:
        return self.colors[self.height-y-1][x]

    def setColor(self, x: int, y: int, value: int) -> None:
        assert value < 256
        self.colors[self.height-y-1][x] = value

    def getPixel(self, x: int, y: int) -> (str, int):
        return (self.getChar(x, y), self.getColor(x, y))

    def setPixel(self, x: int, y: int, value: (str, int)) -> None:
        char, color = value
        self.setChar(x, y, char)
        self.setColor(x, y, color)


test = """123a
456b
789c"""

overlay_test = """ab
cd"""
overlay_testImage = AsciiImage(overlay_test, 35)

testImage = AsciiImage(test, 6)


def print_image(image: AsciiImage):
    for y in range(0, image.height):
        out = ""
        last_color = None
        for x in range(0, image.width):
            color = image.getColor(x, image.height-y-1)
            if last_color is not color:
                out += get_color_by_code(color)
                last_color = color
            out += image.getChar(x, image.height-y-1)
        out += RESET
        print(out)


def composite(base: AsciiImage, overlay: AsciiImage, x: int, y: int):
    for j in range(0, overlay.height):
        for i in range(0, overlay.width):
            base.setPixel(x + i, y + j, overlay.getPixel(i, j))
    return base


flower_yellow_base = """
 * 
\|/
"""

flower_yellow_Image = AsciiImage(flower_yellow_base, 40)
# flower_yellow_Image.setColor(1, 0, 11)


def animateTurtle():
    turtleRightImage = AsciiImage(turtleRight, 28)
    grassImage = AsciiImage(grass, 46)

    composite(grassImage, flower_yellow_Image, 3,3)
    print(grassImage.height)
    print(turtleRightImage.height)
    assert turtleRightImage.height == grassImage.height
    nlines = grassImage.height

    # scroll up to make room for output
    print(f"\033[{nlines}S", end="")

    # move cursor back up
    print(f"\033[{nlines}A", end="")

    # save current cursor position
    print("\033[s", end="")
    width = os.get_terminal_size().columns

    for t in range(0, width - turtleRightImage.width):
        # restore saved cursor position
        print("\033[u", end="")
        buffer = copy.deepcopy(grassImage)
        composite(buffer, turtleRightImage, t, 0)
        print_image(buffer)
        time.sleep(.5)


animateTurtle()
