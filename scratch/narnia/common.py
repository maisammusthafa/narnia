#!/usr/bin/env python
""" common objects """

import curses
import configparser
import os

import narnia.pyaria2 as pyaria2


class Globals:
    tty_h, tty_w = list(map(int, os.popen('stty size', 'r').read().split()))
    prev_tty_w = tty_w

    # TODO: bug when value between 1000 and 1024
    suffixes = [(1024 ** 3, ' G'), (1024 ** 2, ' M'), (1024, ' K'), (1, ' B')]

    header = None
    status = None

    downloads = []
    num_downloads = 0
    focused = None

    timer = 0
    dbg = 0


class Keybindings:
    def __init__(self, keybindings):
        self.key_up = ord(keybindings.get('up', 'k'))
        self.key_down = ord(keybindings.get('down', 'j'))
        self.pause_all = ord(keybindings.get('pause-all', 'P'))
        self.pause = ord(keybindings.get('pause', 'p'))
        self.add = ord(keybindings.get('add', 'a'))
        self.delete = ord(keybindings.get('delete', 'd'))
        self.purge = ord(keybindings.get('purge', 'D'))
        self.queue_up = ord(keybindings.get('queue-up', 'K'))
        self.queue_down = ord(keybindings.get('queue-down', 'J'))
        self.select = ord(keybindings.get('select-file', 'v'))
        self.expand = ord(keybindings.get('expand-torrent', 'h'))
        self.quit = ord(keybindings.get('quit', 'q'))


class Colors:
    def __init__(self, colors):
        self.active = colors.get('dl-active', 'base2').join('<>')
        self.paused = colors.get('dl-paused', 'default').join('<>')
        self.skip = colors.get('dl-skip', 'default').join('<>')
        self.waiting = colors.get('dl-waiting', 'blue').join('<>')
        self.pending = colors.get('dl-pending', 'blue').join('<>')
        self.complete = colors.get('dl-complete', 'green').join('<>')
        self.removed = colors.get('dl-removed', 'yellow').join('<>')
        self.error = colors.get('dl-error', 'red').join('<>')


class Widths:
    def __init__(self, interface):
        self.size = interface.getint('width-size', 10)
        self.status = interface.getint('width-status', 11)
        self.progress = interface.getint('width-progress', 15)
        self.percent = interface.getint('width-percent', 10)
        self.seeds_peers = interface.getint('width-seeds-peers', 10)
        self.speed = interface.getint('width-speed', 16)
        self.eta = interface.getint('width-eta', 10)
        self.name = Globals.tty_w - (self.size + self.status + self.progress +
                                     self.percent + self.seeds_peers +
                                     self.speed + self.eta)


class Config:
    config = configparser.ConfigParser()
    config_file = os.path.expanduser("~/.config/narnia/config")

    if not os.path.isfile(config_file):
        import io
        config_file = io.StringIO('[Connection]\n[UI]\n \
                [Colors]\n[Keybindings]')
        config.readfp(config_file)
    else:
        config.read(config_file)

    interface = config['UI']

    server = config['Connection'].get('server', 'localhost')
    port = config['Connection'].getint('port', 6800)
    aria2 = pyaria2.PyAria2(server, port, None)

    refresh_interval = interface.getfloat('refresh-interval', 0.5)
    progress_markers = interface.get('progress-bar-markers', '[]')
    progress_char = interface.get('progress-bar-char', '#')

    keys = Keybindings(config['Keybindings'])
    colors = Colors(config['Colors'])
    widths = Widths(interface)


def create_row(*fields):
    """ generate aligned row """

    row = ""
    for field in fields:
        value, width, padding, alignment = \
                field[0], field[1], field[2], field[3]

        value = value[:(width - padding)] + ".." \
            if len(value) > width - padding else value

        if alignment == 'right':
            row += (value + (width - len(value)) * ' ')
        else:
            row += ((width - len(value) - padding) * ' ' +
                    value + padding * ' ')

    return row


class Header:
    """ header class """

    def __init__(self):
        self.update()

    def update(self):
        """ generate header """

        self.win = curses.newwin(1, Globals.tty_w, 0, 0)

        name, size, status, progress, percent, seeds_peers, speed, eta = \
            "NAME", "SIZE", "STATUS", "PROGRESS", "", "S/P", "D/U", "ETA"

        self.string = create_row(
            (name, Config.widths.name, 3, 'right'),
            (size, Config.widths.size, 3, 'left'),
            (status, Config.widths.status, 3, 'right'),
            (progress, Config.widths.progress, 3, 'right'),
            (percent, Config.widths.percent, 3, 'right'),
            (seeds_peers, Config.widths.seeds_peers, 3, 'left'),
            (speed, Config.widths.speed, 3, 'left'),
            (eta, Config.widths.eta, 1, 'left')
            )

    def draw(self):
        """ draw header """

        self.win.clear()
        try:
            self.win.addstr(0, 0, self.string, curses.A_BOLD)
        except curses.error:
            pass
        self.win.refresh()


class Status:
    """ status class """

    def __init__(self):
        self.update()

    def update(self):
        """ generate status """

        self.win = curses.newwin(1, Globals.tty_w, Globals.tty_h - 1, 0)

        s_server = 'server: ' + Config.server + ':' + str(Config.port) + \
            ' ' + ('v' + Config.aria2.getVersion()['version']).join('()')

        s_downloads = 'downloads: ' + \
            Config.aria2.getGlobalStat()['numStopped'] + \
            '/' + str(Globals.num_downloads)

        dl_global = int(Config.aria2.getGlobalStat()['downloadSpeed'])
        ul_global = int(Config.aria2.getGlobalStat()['uploadSpeed'])

        s_speed = 'D/U: ' + str("%0.0f" % (dl_global / 1024)) + 'K / ' + \
            str("%0.0f" % (ul_global / 1024)) + 'K'

        # TODO resizing bug here
        self.string = create_row(
            (s_server, Globals.tty_w - 21 - 20, 3, 'right'),
            (s_downloads, 21, 3, 'right'),
            (s_speed, 20, 1, 'left')
            )

    def draw(self):
        """ draw status """

        self.win.clear()
        self.win.refresh()
        try:
            self.win.addstr(0, 0, self.string, curses.A_BOLD)
        except curses.error:
            pass
        self.win.refresh()
