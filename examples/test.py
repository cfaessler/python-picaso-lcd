import display
import time
import math
import colors


def demo_sine(display):
    max_x, max_y = display.get_display_size()

    f = lambda x: math.sin(x / 10.0) * max_y / 2 + max_y / 2
    for i in range(1, max_x):
        display.gfx_line(i - 1, int(f(i - 1)), i, int(f(i)), 21 << 11)


def demo_text(display):
    display.set_font_size(2)
    display.set_text_color(31 << 11)
    display.print_string("Whole Lotta Rosie\n")
    display.set_font_size(1)
    display.print_string("Wanna tell you a story\n'Bout a woman I know\nWhen it comes to lovin'"
                         "\nOh, she steals the show\nShe ain't exactly pretty\nShe ain't exactly small\n"
                         "42-39-56\nYou could say she's got it all!\n\n"
                         "Never had a woman, never had a woman like you\n"
                         "Doin' all the things, doin' all the things you do\n"
                         "Ain't no fairy story\n"
                         "Ain't no skin-and-bones\n"
                         "But you give all you got, weighin' in at nineteen stone")


display = Display.Display("COM4", 9600)
time.sleep(3)
display.cls()
display.set_orientation(1)

while True:
    demo_text(display)
    time.sleep(10)
    display.cls()
    demo_sine(display)

    #display.off()
    #time.sleep(2)
    #display.on()

    #blue = display.to_16bit_color(0, 0, 255)
    #red = display.to_16bit_color(255, 0, 0)
    #green = display.to_16bit_color(0, 255, 0)
    #display.cls()
    #
    #display.gfx_circle(100, 100, 10, Colors.ALICEBLUE, filled=True)
    #display.gfx_circle(200, 100, 10, Colors.ALICEBLUE, filled=True)
    #display.gfx_polyline([(120, 100), (130, 110), (140, 115), (150, 115), (160, 110), (170, 100)], Colors.BLUE)
    #
    #display.gfx_rect(200, 120, 300, 200, Colors.DARKBLUE, filled=True)
    display.cls()
