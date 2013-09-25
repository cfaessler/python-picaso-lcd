# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from picaso_lcd import utils


### int_to_dword ###

@pytest.mark.parametrize(('arg', 'expected'), [
    (0, (0, 0)),
    (1, (0, 1)),
    (42, (0, 42)),
    (255, (0, 255)),
    (256, (1, 0)),
    ((1 << 16) - 1, (255, 255)),
])
def test_int_to_dword(arg, expected):
    """Test the ``int_to_dword`` function."""
    assert utils.int_to_dword(arg) == expected


@pytest.mark.parametrize('arg', [1 << 16, -1])
def test_int_to_dword_validation(arg):
    with pytest.raises(ValueError):
        utils.int_to_dword(arg)


### dword_to_int ###

@pytest.mark.parametrize(('args', 'expected'), [
    ((0, 0), 0),
    ((0, 1), 1),
    ((0, 42), 42),
    ((0, 255), 255),
    ((1, 0), 256),
    ((255, 255), (1 << 16) - 1),
])
def test_dword_to_int(args, expected):
    """Test the ``dword_to_int`` function."""
    assert utils.dword_to_int(*args) == expected


@pytest.mark.parametrize(('low_byte', 'high_byte'), [
    (1 << 8, 0),
    (0, 1 << 8),
    (1 << 8, 1 << 8),
    (-1, 0),
    (0, -1),
    (-1, -1),
])
def test_dword_to_int_validation(low_byte, high_byte):
    with pytest.raises(ValueError):
        utils.dword_to_int(low_byte, high_byte)


### to_16bit_color ###

# TODO
