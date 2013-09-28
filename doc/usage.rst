Usage
=====

Connect the LCD to your computer using a serial connection (e.g. USB). Then
create a new :class:`picaso_lcd.Display` instance, with the serial port as
argument:

.. sourcecode:: python

    import picaso_lcd
    disp = picaso_lcd.Display('/dev/ttyUSB0')

(If you're using Windows, the port string would probably be something like
``COM3``.)

The different functionality groups are provided in their own namespaces. For
example the text related functions are grouped in ``disp.text``, while the
graphics related functions are grouped in ``disp.gfx``. General purpose methods
are not in a sub-namespace and can be accessed directly.

**Example:**

.. sourcecode:: python

    import picaso_lcd
    disp = picaso_lcd.Display('/dev/ttyUSB0')
    
    disp.cls()
    disp.text.put_string('Welcome\nThis is a nice library.')
    disp.text.move_cursor(0, 7)
    disp.text.put_character('!')

This will result in the following text being written on the display::

    Welcome!
    This is a nice library.

For more information, please refer to the `API Docs <api.html>`_.
