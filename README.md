samsungctl
==========

samsungctl is a library and a command line tool for remote controlling Samsung QLED
televisions via a websocket. Its a fork of https://github.com/Ape/samsungctl but support for moder QLED TV's was addad
also in interactive mode menu was redesigned to match QLED remote control.
At this moment installation breaks with newest vestion on websocket-client co be sure tu install version <=0.57.0

The app should also runs with older samung TV when run in legacy mode.

Before running app go to TV Manu and choose:

General -> External Device Manager -> Device Connection Manager -> Access Notification = Allways on

After that run application and accept incoming connection to tv.

then switch

General -> External Device Manager -> Device Connection Manager -> Access Notification = off

Otherwise you will have problem with connection to tv or you will be asked to authenticate everytime the app is run

This is work in progress. The sometimes have problem with websocket connection and drops with broken pipe error but
it should work most of the time.


Dependencies
============

- Python 3
- ``websocket-client==0.56.0``
- ``curses`` - for the interactive mode

Installation and running
========================

::

    pip install 'websocket-client==0.56.0'

::

    sudo python setup.py install

::

    python -m samsungctl --host samsung --method websocket --port 8002 -i

Other than that you can follow manual of original samsungctl:

Command line usage
==================

You can use ``samsungctl`` command to send keys to a TV:

::

    $ samsungctl --host <host> [options] <key> [key ...]

``host`` is the hostname or IP address of the TV. ``key`` is a key code, e.g.
``KEY_VOLDOWN``. See `Key codes`_.

There is also an interactive mode (ncurses) for sending the key presses:

::

    $ samsungctl --host <host> [options] --interactive

Use ``samsungctl --help`` for more information about the command line
arguments:

::

    usage: samsungctl [-h] [--version] [-v] [-q] [-i] [--host HOST] [--port PORT]
                      [--method METHOD] [--name NAME] [--description DESC]
                      [--id ID] [--timeout TIMEOUT]
                      [key [key ...]]

    Remote control Samsung televisions via TCP/IP connection

    positional arguments:
      key                 keys to be sent (e.g. KEY_VOLDOWN)

    optional arguments:
      -h, --help          show this help message and exit
      --version           show program's version number and exit
      -v, --verbose       increase output verbosity
      -q, --quiet         suppress non-fatal output
      -i, --interactive   interactive control
      --host HOST         TV hostname or IP address
      --port PORT         TV port number (TCP)
      --method METHOD     Connection method (legacy or websocket)
      --name NAME         remote control name
      --description DESC  remote control description
      --id ID             remote control id
      --timeout TIMEOUT   socket timeout in seconds (0 = no timeout)

    E.g. samsungctl --host 192.168.0.10 --name myremote KEY_VOLDOWN

The settings can be loaded from a configuration file. The file is searched from
``$XDG_CONFIG_HOME/samsungctl.conf``, ``~/.config/samsungctl.conf``, and
``/etc/samsungctl.conf`` in this order. A simple default configuration is
bundled with the source as `samsungctl.conf <samsungctl.conf>`_.

Library usage
=============

samsungctl can be imported as a Python 3 library:

.. code-block:: python

    import samsungctl

A context managed remote controller object of class ``Remote`` can be
constructed using the ``with`` statement:

.. code-block:: python

    with samsungctl.Remote(config) as remote:
        # Use the remote object

The constructor takes a configuration dictionary as a parameter. All
configuration items must be specified.

===========  ======  ===========================================
Key          Type    Description
===========  ======  ===========================================
host         string  Hostname or IP address of the TV.
port         int     TCP port number. (Default: ``55000``)
method       string  Connection method (``legacy`` or ``websocket``)
name         string  Name of the remote controller.
description  string  Remote controller description.
id           string  Additional remote controller ID.
timeout      int     Timeout in seconds. ``0`` means no timeout.
===========  ======  ===========================================

The ``Remote`` object is very simple and you only need the ``control(key)``
method. The only parameter is a string naming the key to be sent (e.g.
``KEY_VOLDOWN``). See `Key codes`_. You can call ``control`` multiple times
using the same ``Remote`` object. The connection is automatically closed when
exiting the ``with`` statement.

When something goes wrong you will receive an exception:

=================  =======================================
Exception          Description
=================  =======================================
AccessDenied       The TV does not allow you to send keys.
ConnectionClosed   The connection was closed.
UnhandledResponse  An unexpected response was received.
socket.timeout     The connection timed out.
=================  =======================================

Example program
---------------

This simple program opens and closes the menu a few times.

.. code-block:: python

    #!/usr/bin/env python3

    import samsungctl
    import time

    config = {
        "name": "samsungctl",
        "description": "PC",
        "id": "",
        "host": "192.168.0.10",
        "port": 55000,
        "method": "legacy",
        "timeout": 0,
    }

    with samsungctl.Remote(config) as remote:
        for i in range(10):
            remote.control("KEY_MENU")
            time.sleep(0.5)

Key codes
=========

The list of accepted keys may vary depending on the TV model, but the following
list has some common key codes and their descriptions.

=================  ============
Key code           Description
=================  ============
KEY_POWEROFF       Power off
KEY_UP             Up
KEY_DOWN           Down
KEY_LEFT           Left
KEY_RIGHT          Right
KEY_CHUP           P Up
KEY_CHDOWN         P Down
KEY_ENTER          Enter
KEY_RETURN         Return
KEY_CH_LIST        Channel List
KEY_MENU           Menu
KEY_SOURCE         Source
KEY_GUIDE          Guide
KEY_TOOLS          Tools
KEY_INFO           Info
KEY_RED            A / Red
KEY_GREEN          B / Green
KEY_YELLOW         C / Yellow
KEY_BLUE           D / Blue
KEY_PANNEL_CHDOWN  3D
KEY_VOLUP          Volume Up
KEY_VOLDOWN        Volume Down
KEY_MUTE           Mute
KEY_0              0
KEY_1              1
KEY_2              2
KEY_3              3
KEY_4              4
KEY_5              5
KEY_6              6
KEY_7              7
KEY_8              8
KEY_9              9
KEY_DTV            TV Source
KEY_HDMI           HDMI Source
KEY_CONTENTS       SmartHub
=================  ============

Please note that some codes are different on the 2016+ TVs. For example,
``KEY_POWEROFF`` is ``KEY_POWER`` on the newer TVs.

References
==========

I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
- https://github.com/kyleaa/homebridge-samsungtv2016
