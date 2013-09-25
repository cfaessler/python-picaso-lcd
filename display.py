# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import serial


class Display(object):
    """This class represents a 4D Systems serial LCD."""

    def __init__(self, port, baudrate):
        """
        Initialize the instance of a 4D Systems serial LCD.

        :param port: serial port to which the display is connected
        :param baudrate: default 9600 in SPE2 rev 1.1
        :rtype : Display object
        """
        self._com = port
        self.port = serial.Serial(port, baudrate=baudrate, stopbits=1)
        self._contrast = 15

    def _get_ack(self, *expected_values):
        ack = self.port.read()
        acks = []
        if ord(ack) != 6:
            print('Error Code: {0}'.format(ord(ack)))
            raise Exception(ack)
        for arg in expected_values:
            ack = self.port.read()
            print('value {0}'.format(ord(ack)))
            acks.append(ack)
        return acks

    def write_raw_cmd(self, cmd):
        """
        Writes list of bytes to the serial port

        :type self: object
        :param cmd:
        """
        for c in cmd:
            self.port.write(chr(c))

    def write_cmd(self, cmd):
        """
        Writes list of values to the serial port - values are always converted
        into a word (16bit value, consisting of two bytes: high byte, low byte)
        even if they would fit into a single byte.

        The communication protocol is based on exchanging words. Only a few
        special commands use single byte values, in this case use write_raw_cmd
        instead

        """
        for c in cmd:
            high_byte, low_byte = self._int_to_dword(c)
            self.port.write(chr(high_byte))
            self.port.write(chr(low_byte))

    def write(self, byte):
        self.port.write(chr(byte))

    def gfx_rect(self, x1, y1, x2, y2, color, filled=False):
        cmd = 0xFFC5
        if filled:
            cmd = 0xFFC4
        self.write_cmd([cmd, x1, y1, x2, y2, color])
        return self._get_ack()

    ### GRAPHICS FUNCTIONS ###

    def gfx_triangle(self, vertices, filled=False):
        self.gfx_polyline(vertices, closed=True, filled=filled)

    def gfx_polyline(self, lines, color, closed=False, filled=False):
        """
        A polyline could be closed or filled, where filled is always closed.
        """
        cmd = 0x0015
        if closed:
            cmd = 0x0013
        if filled:
            cmd = 0x0014
        size = len(lines)
        print(size)
        cmd_list = [cmd, size]
        for point in lines:
            x, y = point
            cmd_list.append(x)
        for point in lines:
            x, y = point
            cmd_list.append(y)
        cmd_list.append(color)
        self.write_cmd(cmd_list)
        self._get_ack()

    def gfx_circle(self, x, y, rad, color, filled=False):
        self.gfx_ellipse(x, y, rad, rad, color, filled=filled)

    def gfx_ellipse(self, x, y, xrad, yrad, color, filled=False):
        cmd = 0xFFB2
        if filled:
            cmd = 0xFFB1
        self.write_cmd([cmd, x, y, xrad, yrad, color])
        self._get_ack()

    def gfx_line(self, x1, y1, x2, y2, color):
        self.write_cmd([0xFFC8, x1, y1, x2, y2, color])
        self._get_ack()

    def cls(self):
        self.write_cmd([0xFFCD])
        self._get_ack()

    def _int_to_dword(self, value):
        """
        Converts a single int value (< 2**16) into two-byte structure: High byte, Low byte
        """
        assert value < (2 << 15), 'Value too large (max 2^16)'
        return value >> 8, value & 0xFF

    def _dword_to_int(self, high_byte, low_byte):
        return (ord(high_byte) << 8) | ord(low_byte)

    def to_16bit_color(self, red, green, blue):
        #Color scheme is 16bit (565). Greater values are truncated --> min()
        return min(red, 31) << 11 | min(green, 63) << 5 | min(blue, 31)

    def set_pixel(self, x, y, color):
        """Set the color of the pixel at ``x``/``y`` to ``color``."""
        self.write_cmd([0xFFC1, x, y, color])
        self._get_ack()

    def set_cursor(self, line, column):
        self.write_cmd([0xFFE9, line, column])
        return self._get_ack()

    def set_font_size(self, size):
        self.write_cmd([0xFFE4, size])
        self._get_ack(0, 0)
        self.write_cmd([0xFFE3, size])
        self._get_ack(0, 0)

    def set_font(self, font):
        """
        :param font:
        0 - Font1 -> System Font
        1 - Font2
        3 - Font3 -> Default Font
        """
        self.write_cmd([0xFFE5, font])
        self._get_ack(0, 0)

    def print_string(self, string):
        cmd = [0x00, 0x18]
        for char in string:
            cmd.append(ord(char))
        cmd.append(0x00)
        self.write_raw_cmd(cmd)
        #TODO assert that all bytes are writen! compare return value to string length
        return self._get_ack(0, 0)

    def set_text_color(self, color):
        self.write_cmd([0xFFE7, color])
        return self._get_ack(0, 0)

    def set_background_color(self, color):
        self.write_cmd([0xFFA4, color])
        self._get_ack(0, 0)

    def set_contrast(self, contrast):
        self.write_cmd([0xFF9C, contrast])
        val = self._get_ack(0, 0)
        print('turning off, contrast was: {0}'.format(val))
        self._contrast = self._dword_to_int(val[0], val[1])

    def off(self):
        self.set_contrast(0)

    def on(self):
        print('contrast is: {0}'.format(self._contrast))
        self.set_contrast(self._contrast)

    def set_orientation(self, value):
        """Set display orientation
        0 = Landscape
        1 = Landscape reverse
        2 = portrait
        3 = portrait reverse

        :returns: previous orientation
        """
        self.write_cmd([0xFF9E, value])
        return self._get_ack(0, 0)[0]

    def get_display_size(self):
        self.write_cmd([0xFFA6, 0])
        x = self._get_ack(0, 0)
        self.write_cmd([0xFFA6, 1])
        y = self._get_ack(0, 0)
        return self._dword_to_int(x[0], x[1]), self._dword_to_int(y[0], y[1])
