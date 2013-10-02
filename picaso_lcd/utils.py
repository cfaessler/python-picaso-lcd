# -*- coding: utf-8 -*-
"""
This module contains different utility functions, e.g. for handling of binary
data or colors.
"""
from __future__ import print_function, division, absolute_import, unicode_literals


def int_to_dbyte(value):
    """Convert a single integer to a double byte: ``(high byte, low byte)``.
    
    The value (which must be < 2**16) is split up into a two-byte structure:
    (high byte, low byte).

    :param value: The value to be converted.
    :type value: int < 2**16
    :returns: 2-Tuple with high byte and low byte.
    :raises: ValueError
    :rtype: (int, int)

    """
    if value >= (1 << 16):
        raise ValueError('Value must be smaller than 2^16')
    if value < 0:
        raise ValueError('Value must be positive')
    return value >> 8, value & 0xFF


def dbyte_to_int(high_byte, low_byte):
    """Convert a double byte ``(high byte, low byte)`` to a single integer.

    If you're already dealing with a 2-tuple, you can simply convert it to an
    integer by using arg unpacking::

        >>> dbyte = (0x1, 0x2)
        >>> dbyte_to_int(*dbyte)

    :param high_byte: The high byte.
    :type high_byte: int
    :param low_byte: The low byte.
    :type low_byte: int
    :returns: Single integer.
    :rtype: int

    """
    # TODO input validation could be done using decorator
    if not high_byte < (1 << 8):
        raise ValueError('high_byte must be smaller than 2^8')
    if not low_byte < (1 << 8):
        raise ValueError('low_byte must be smaller than 2^8')
    if high_byte < 0 or low_byte < 0:
        raise ValueError('All arguments must be positive')
    return (high_byte << 8) | low_byte


def to_16bit_color(red, green, blue):
    """Convert rgb color to 16 bit color.
    
    Color scheme is 16bit (565). Greater values are truncated.

    :param red: The red value. Should be smaller than 32, larger values are truncated.
    :type red: int
    :param green: The green value. Should be smaller than 64, larger values are truncated.
    :type green: int
    :param blue: The blue value. Should be smaller than 32, larger values are truncated.
    :type blue: int
    :returns: 16 bit color value.
    :rtype: int

    """
    return min(red, 31) << 11 | min(green, 63) << 5 | min(blue, 31)
