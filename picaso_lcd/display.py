# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import serial
from . import utils
from .constants import ACK
from .exceptions import PicasoError, CommunicationError


# TODO introduce logging

class Display(object):
    """This class represents a 4D Systems serial LCD."""

    def __init__(self, port, baudrate=9600, read_timeout=10, write_timeout=10):
        """
        Initialize an instance of the LCD.

        :param port: serial port to which the display is connected
        :type port: str or unicode
        :param baudrate: default 9600 in SPE2 rev 1.1
        :type baudrate: int
        :param read_timeout: Serial read timeout. This may be ``None``
            (blocking), ``0`` (non-blocking) or an integer > 0 (seconds).
        :type read_timeout: int or None
        :param write_timeout: Serial write timeout. This may be ``None``
            (blocking), ``0`` (non-blocking) or an integer > 0 (seconds).
        :type write_timeout: int or None
        :rtype: Display instance
        """
        self._ser = serial.Serial(port, baudrate=baudrate, stopbits=1,
                timeout=read_timeout, writeTimeout=write_timeout)
        self._contrast = 15

        # Initialize subsystems
        self.text = DisplayText(self)
        self.touch = DisplayTouch(self)

    ### Serial communication handling ###

    def write_cmd(self, cmd, return_bytes=0):
        """
        Write list of words to the serial port.

        Values are always converted into a word (16bit value, consisting of two
        bytes: high byte, low byte) even if they would fit into a single byte.

        The communication protocol is based on exchanging words. Only a few
        special commands use single byte values, in this case use write_raw_cmd
        instead.

        :param cmd: The list of command words (16 bit) to send.
        :type cmd: list of int
        :param return_bytes: Number of return bytes. Default 0.
        :type return_bytes: int
        :returns: List of response bytes if there are any, else None.
        :rtype: list or none

        """
        for c in cmd:
            high_byte, low_byte = utils.int_to_dword(c)
            self._ser.write(chr(high_byte))
            self._ser.write(chr(low_byte))
        return self._get_ack(return_bytes)

    def write_raw_cmd(self, cmd, return_bytes=0):
        """
        Write list of bytes directly to the serial port.

        :param cmd: List containing numeric bytes.
        :type cmd: list of int
        :param return_bytes: Number of return bytes. Default 0.
        :type return_bytes: int
        :returns: List of response bytes if there are any, else None.
        :rtype: list or none

        """
        for c in cmd:
            self._ser.write(chr(c))
        return self._get_ack(return_bytes)

    def _get_ack(self, return_bytes=0):
        """
        Wait for the ACK byte. If applicable, fetch and return the response
        values.

        :param return_bytes: Number of return bytes. Default 0.
        :type return_bytes: int
        :returns: List of response bytes if there are any, else None.
        :rtype: list or none

        """
        # First return value must be an ACK byte (0x06).
        ack = self._ser.read()
        if not ack:
            raise CommunicationError('Read timeout reached.')
        if ord(ack) != ACK:
            msg = 'Instead of an ACK byte, "{!r}" was returned.'.format(ord(ack))
            print(msg)
            raise PicasoError(msg)

        # If applicable, fetch response values
        values = [] if return_bytes else None
        for i in xrange(return_bytes):
            val = ord(self._ser.read())
            print('Return byte: {0}'.format(val))
            values.append(val)

        return values

    def gfx_rect(self, x1, y1, x2, y2, color, filled=False):
        cmd = 0xffc5
        if filled:
            cmd = 0xffc4
        return self.write_cmd([cmd, x1, y1, x2, y2, color])

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

    def gfx_circle(self, x, y, rad, color, filled=False):
        self.gfx_ellipse(x, y, rad, rad, color, filled=filled)

    def gfx_ellipse(self, x, y, xrad, yrad, color, filled=False):
        cmd = 0xffb2
        if filled:
            cmd = 0xffb1
        self.write_cmd([cmd, x, y, xrad, yrad, color])

    def gfx_line(self, x1, y1, x2, y2, color):
        self.write_cmd([0xffc8, x1, y1, x2, y2, color])

    def cls(self):
        self.write_cmd([0xffcd])



    def set_background_color(self, color):
        self.write_cmd([0xffa4, color], 2)

    def set_contrast(self, contrast):
        """Set the contrast. Note that this has no effect on most LCDs."""
        val = self.write_cmd([0xff9c, contrast], 2)
        print('turning off, contrast was: {0}'.format(val))
        dword = map(ord, val)
        self._contrast = utils.dword_to_int(*dword)

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
        response = self.write_cmd([0xff9e, value], 2)
        return response[0]

    def get_display_size(self):
        x = self.write_cmd([0xffa6, 0], 2)
        x_dword = map(ord, [x[0], x[1]])
        y = self.write_cmd([0xffa6, 1], 2)
        y_dword = map(ord, [y[0], y[1]])
        return utils.dword_to_int(*x_dword), utils.dword_to_int(*y_dword)


class DisplayText(object):
    """Text/String related functions."""

    def __init__(self, display):
        """
        :param display: The display instance.
        :type display: Display
        """
        self.d = display

    def move_cursor(self, line, column):
        """
        Move cursor to specified position.

        The *Move Cursor* command moves the text cursor to a screen position
        set by line and column parameters. The line and column position is
        calculated, based on the size and scaling factor for the currently
        selected font. When text is outputted to screen it will be displayed
        from this position. The text position could also be set with *Move
        Origin* command if required to set the text position to an exact pixel
        location. Note that lines and columns start from 0, so line 0, column 0
        is the top left corner of the display.

        :param line: Line number (0..n)
        :type line: int
        :param column: Column number (0..n)
        :type column: int

        """
        self.d.write_cmd([0xffe9, line, column])

    def put_character(self, char):
        """
        Write a single character to the display.

        The *Put Character* command prints a single character to the display.

        :param char: The character to print. Must be a printable ASCII character.
        :type char: str

        """
        self.d.write_cmd([0xfffe, ord(char)])

    def put_string(self, string):
        """
        Write a string to the display.

        The *Put String* command prints a string to the display. Maximum string
        length is 511 chars.

        """
        # Validate input
        if len(string) > 511:
            raise ValueError('Max string length is 511 chars')

        # Build and send command
        cmd = [0x00, 0x18]
        for char in string:
            cmd.append(ord(char))
        cmd.append(0x00)
        response = self.d.write_raw_cmd(cmd, 2)

        # Verify return values
        length_written = utils.dword_to_int(*response)
        assert length_written == len(string), \
                'Length of string does not match length of original string'

    def get_character_width(self, character):
        """
        Get the width of a character in pixels.

        The *Character Width* command is used to calculate the width in pixel
        units for a character, based on the currently selected font. The font can be
        proportional or mono-spaced. If the total width of the character exceeds 255
        pixel units, the function will return the 'wrapped' (modulo 8) value.

        TODO: Handle and hide this strange modulo stuff!

        :param character: The ASCII character for which to calculate the width.
        :type character: str
        :returns: The width of the character. If the total width of the
            character exceeds 255 pixel units, the function will return the
            'wrapped' (modulo 8) value.
        :rtype: int

        """
        response = self.d.write_raw_cmd([0x00, 0x1e, ord(character)], 2)
        return utils.dword_to_int(*response)

     def get_character_height(self, character):
        """
        Get the height of a character in pixels.

        The *Character Height* command is used to calculate the height in pixel
        units for a character, based on the currently selected font. The font
        can be proportional or mono-spaced. If the total height of the
        character exceeds 255 pixel units, the function will return the
        'wrapped' (modulo 8) value.

        TODO: Handle and hide this strange modulo stuff!

        :param character: The ASCII character for which to calculate the height.
        :type character: str
        :returns: The height of the character. If the total height of the
            character exceeds 255 pixel units, the function will return the
            'wrapped' (modulo 8) value.
        :rtype: int

        """
        response = self.d.write_raw_cmd([0x00, 0x1d, ord(character)], 2)
        return utils.dword_to_int(*response)   

    def set_fg_color(self, color):
        """
        Set the text foreground color.

        The *Text Foreground Color* command sets the text foreground color, and
        reports back the previous foreground color.

        :param color: The color to be set as foreground color.
        :type color: int
        :returns: The previous foreground color.
        :rtype: int

        """
        response = self.write_cmd([0xffe7, color], 2)
        return utils.dword_to_int(*response)

    def set_bg_color(self, color):
        """
        Set the text background color.

        The *Text Background Color* command sets the text background color, and
        reports back the previous background color.

        :param color: The color to be set as background color.
        :type color: int
        :returns: The previous background color.
        :rtype: int

        """
        response = self.write_cmd([0xffe6, color], 2)
        return utils.dword_to_int(*response)

    def set_font(self, font):
        """
        Set the used font.

        The *Set Font* command sets the required font using its ID, and report
        back the previous font ID used.

        :param font: The font ID to use.
            0 - Font1 (System Font)
            1 - Font2
            3 - Font3 (Default Font)
        :type font: int
        :returns: The previous font ID used.
        :rtype: int

        """
        response = self.write_cmd([0xffe5, font], 2)
        return utils.dword_to_int(*response)

    def set_width(self, multiplier):
        """
        Set the text width.

        The *Text Width* command sets the text width multiplier between 1 and
        16, and returns the previous multiplier.

        :param multiplier: Width multiplier, 1 to 16 (Default 1).
        :type multiplier: int
        :returns: Previous multiplier.
        :rtype: int

        """
        response = self.write_cmd([0xffe4, multiplier], 2)
        return utils.dword_to_int(*response)

    def set_height(self, multiplier):
        """
        Set the text height.

        The *Text Height* command sets the text height multiplier between 1 and
        16, and returns the previous multiplier.

        :param multiplier: Height multiplier, 1 to 16 (default 1).
        :type multiplier: int
        :returns: Previous multiplier.
        :rtype: int

        """
        response = self.write_cmd([0xffe3, multiplier], 2)
        return utils.dword_to_int(*response)

    def set_size(self, multiplier):
        """
        Set the text size.

        This is a shortcut functions that calls both :meth:``set_width`` and
        :meth:``set_height``. The return value is a tuple containing previous
        width- and height- multipliers.

        :param multiplier: Size multiplier, 1 to 16 (default 1).
        :type multiplier: int
        :returns: Tuple ``(previous_width, previous_height)``
        :rtype: tuple(int, int)

        """
        return self.set_width(multiplier), self.set_height(multiplier)

    def set_x_gap(self, pixelcount):
        """
        Set the horizontal gap between characters.

        The *Text X-gap* command sets the pixel gap between characters
        (x-axis), where the gap is in pixel units, and the response is the
        previous pixelcount value.

        :param pixelcount: Gap size in pixels, 0 to 32 (default 0).
        :type pixelcount: int
        :returns: Previous pixelcount value.
        :rtype: int

        """
        response = self.write_cmd([0xffe2, pixelcount], 2)
        return utils.dword_to_int(*response)

    def set_y_gap(self, pixelcount):
        """
        Set the vertical gap between characters.

        The *Text Y-gap* command sets the pixel gap between characters
        (y-axis), where the gap is in pixel units, and the response is the
        previous pixelcount value.

        This command is required to be used if setting text to have an
        Underline using the *Text Underline* command, or *Text Attributes*
        command with the suitable bits set.  See these command for further
        information.

        :param pixelcount: Gap size in pixels, 0 to 32 (default 0).
        :type pixelcount: int
        :returns: Previous pixelcount value.
        :rtype: int

        """
        response = self.write_cmd([0xffe1, pixelcount], 2)
        return utils.dword_to_int(*response)

    def set_gap(self, pixelcount)
        """
        Set both the x- and the y-gap between characters.

        This is a shortcut function that calls both :meth:``set_x_gap`` and
        :meth:``set_y_gap``. The return value is a tuple containing the
        previous pixelcount values.

        :param pixelcount: Gap size in pixels, 0 to 32 (default 0).
        :type pixelcount: int
        :returns: Tuple ``(previous_x_gap, previous_y_gap)``
        :rtype: tuple(int, int)

        """
        return self.set_x_gap(pixelcount), self.set_y_gap(pixelcount)


class DisplayTouch(object):
    """Touchscreen related functions."""

    def __init__(self, display):
        """
        :param display: The display instance.
        :type display: Display
        """
        self.d = display

    def set_detect_region(self, x1, y1, x2, y2):
        """
        Set the touch detect region.

        Specifies a new touch detect region on the screen. This setting will
        filter out any touch activity outside the region and only touch
        activity within that region will be reported by the status poll *Touch
        Get* command.

        :param x1: X coordinate of top left corner of the region
        :type line: int
        :param y1: Y coordinate of top left corner of the region
        :type column: int
        :param x1: X coordinate of bottom right corner of the region
        :type line: int
        :param y1: Y coordinate of bottom right corner of the region
        :type column: int

        """
        self.d.write_cmd([0xff39, line, column])

    def set_mode(self, mode):
        """
        Set touch screen related parameters.

        mode = 0: Enables and initialises Touch Screen hardware.
        mode = 1: Disables the Touch Screen.
        mode = 2: This will reset the current active region to default which is
        the full screen area.

        Note: Touch Screen task runs in the background and disabling it 
        when not in use will free up extra resources for 4DGL CPU cycles.

        :param mode: The touch mode (0, 1 or 2). See method docstring for more information.
        :type mode: int

        """
        self.d.write_cmd([0xff39, mode])

    def get_status(self, mode):
        """
        Poll the touch screen.

        Returns various Touch Screen parameters to caller, based on the touch
        detect region on the screen set by the *Touch Detect Region* command.

        Request modes:
        --------------

        mode = 0: Get status
        mode = 1: Get X coordinates
        mode = 2: Get Y coordinates

        Response values:
        ----------------

        mode = 0: The various states of the touch screen. Possible values:
            0 = INVALID / NOTOUCH
            1 = PRESS
            2 = RELEASE
            3 = MOVING
        mode = 1: The X coordinates of the touch
        mode = 2: The Y coordinates of the touch

        :param mode: The status mode (0, 1 or 2). See method docstring for more information.
        :type mode: int
        :returns: A value dependent on the request mode.
        :rtype: int

        """
        response = self.d.write_cmd([0xff37, mode], 2)
        return utils.dword_to_int(*response)
