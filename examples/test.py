from picaso_lcd import display
from picaso_lcd import colors

import sys
import time
import math


def demo_sine(disp):
    max_x, max_y = disp.get_display_size()

    f = lambda x: math.sin(x / 10.0) * max_y / 2 + max_y / 2
    for i in range(1, max_x):
        disp.gfx_line(i - 1, int(f(i - 1)), i, int(f(i)), 21 << 11)


def demo_text(disp):
    disp.text.set_size(2)
    disp.text.set_fg_color(31 << 11)
    disp.text.put_string("Whole Lotta Rosie\n")
    disp.text.set_size(1)
    disp.text.put_string("Wanna tell you a story\n'Bout a woman I know\nWhen it comes to lovin'"
                         "\nOh, she steals the show\nShe ain't exactly pretty\nShe ain't exactly small\n"
                         "42-39-56\nYou could say she's got it all!\n\n"
                         "Never had a woman, never had a woman like you\n"
                         "Doin' all the things, doin' all the things you do\n"
                         "Ain't no fairy story\n"
                         "Ain't no skin-and-bones\n"
                         "But you give all you got, weighin' in at nineteen stone")


#disp = display.Display('/dev/ttyUSB0', 9600)
disp = display.Display('COM12', 115200)
time.sleep(3)
disp.cls()
disp.set_orientation(1)

while True:
    demo_text(disp)
    time.sleep(3)
    disp.cls()
    demo_sine(disp)

    #disp.off()
    #time.sleep(2)
    #disp.on()

    #blue = disp.to_16bit_color(0, 0, 255)
    #red = disp.to_16bit_color(255, 0, 0)
    #green = disp.to_16bit_color(0, 255, 0)
    #disp.cls()
    #
    #disp.gfx_circle(100, 100, 10, Colors.ALICEBLUE, filled=True)
    #disp.gfx_circle(200, 100, 10, Colors.ALICEBLUE, filled=True)
    #disp.gfx_polyline([(120, 100), (130, 110), (140, 115), (150, 115), (160, 110), (170, 100)], Colors.BLUE)
    #
    #disp.gfx_rect(200, 120, 300, 200, Colors.DARKBLUE, filled=True)
    disp.cls()
