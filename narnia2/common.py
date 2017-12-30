#!/bin/env python3
""" common objects """

import argparse
import configparser
import curses
import io
import os
import sys

import narnia2.pyaria2 as pyaria2

from datetime import datetime

class Globals:
    tty = {}
    tty['curr_h'], tty['curr_w'] = list(map(
        int, os.popen('stty size', 'r').read().split()))

    tty['prev_h'] = tty['curr_h']
    tty['prev_w'] = tty['curr_w']

    suffixes = [(1024 ** 3, ' G'), (1024 ** 2, ' M'), (1024, ' K'), (1, ' B')]

    header = None
    status = None

    downloads = []
    download_states = [[], [], []]
    num_downloads = 0
    focused = None

    timer_ui = 0
    dbg = 0

    queue = None

    def log(message):
        with open('log.txt', 'a') as log_file:
            time = datetime.now().strftime('%H:%M:%S')
            line = '{} {}\n'.format(time, message)
            log_file.write(line)


g = Globals


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
        self.retry = ord(keybindings.get('retry', 'r'))
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
        self.name = g.tty['curr_w'] - \
            (self.size + self.status + self.progress +
             self.percent + self.seeds_peers +
             self.speed + self.eta)


class Config:
    def load_conf(name, sections):
        conf = configparser.ConfigParser()
        conf_file = os.path.expanduser("~/.config/narnia/" + name)

        if not os.path.isfile(conf_file):
            conf_file = io.StringIO(sections)
            conf.readfp(conf_file)
        else:
            conf.read(conf_file)
        return conf

    # TODO: Fix crash on missing config sections
    config = load_conf('config', '[Connection]\n[UI]\n[Colors]\n[Keybindings]')
    profiles = load_conf('profiles', '[default]')

    profile = config['Connection'].get('profile', 'default')

    parser = argparse.ArgumentParser(description='A curses-based console client for aria2')
    parser.add_argument('-c', '--connection', help='Pre-configured narnia connection profile to use', default=profile)
    parser.add_argument('-s', '--server', help='Server to connect to')
    parser.add_argument('-p', '--port', help='Port to connect through')
    parser.add_argument('-t', '--token', help='aria2 RPC secret token')
    parser.add_argument('-d', '--delete', help='Delete a download using its GID')
    parser.add_argument('-i', '--info', help='Returns info on a download using its GID')
    parser.add_argument('file', nargs='*')

    args = parser.parse_args()
    profile = args.connection

    server = profiles[profile].get('server', 'localhost') if args.server is None else \
        args.server
    port = profiles[profile].getint('port', 6800) if args.port is None else \
        int(args.port)
    token = profiles[profile].get('rpc-secret', '') if args.token is None else \
        args.token

    aria2 = pyaria2.PyAria2(server, port, token)

    if args.file != []:
        for i_file in args.file:
            aria2.add_uri([i_file])
        sys.exit()
    elif args.delete is not None:
        aria2.remove_download_result(args.delete)
        sys.exit()
    elif args.info is not None:
        print(aria2.tell_status(token, args.info))
        sys.exit()

    interface = config['UI']
    keys = Keybindings(config['Keybindings'])
    colors = Colors(config['Colors'])
    widths = Widths(interface)

    refresh_interval = interface.getfloat('refresh-interval', 0.5)
    progress_markers = interface.get('progress-bar-markers', '[]')
    progress_char = interface.get('progress-bar-char', '#')


c = Config


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
    def __init__(self):
        self.update()

    def update(self):
        """ generate header """

        self.win = curses.newwin(1, g.tty['curr_w'], 0, 0)

        name, size, status, progress, percent, seeds_peers, speed, eta = \
            "NAME", "SIZE", "STATUS", "PROGRESS", "", "S/P", "D/U", "ETA"

        self.string = create_row(
            (name, c.widths.name, 3, 'right'),
            (size, c.widths.size, 3, 'left'),
            (status, c.widths.status, 3, 'right'),
            (progress, c.widths.progress, 3, 'right'),
            (percent, c.widths.percent, 3, 'right'),
            (seeds_peers, c.widths.seeds_peers, 3, 'left'),
            (speed, c.widths.speed, 3, 'left'),
            (eta, c.widths.eta, 1, 'left')
            )

    def draw(self, init):
        """ draw header """

        if g.tty['prev_w'] == g.tty['curr_w'] and not init:
            return

        self.win.clear()
        try:
            self.win.addstr(0, 0, self.string, curses.A_BOLD)
        except curses.error:
            pass
        self.win.noutrefresh()


class Status:
    def __init__(self):
        self.data = {'downloadSpeed': '0', 'numActive': '0', 'numStopped': '0',
                     'numStoppedTotal': '0', 'numWaiting': '0', 'uploadSpeed': '0'}
        self.version = "0.00.0"
        self.string = None
        self.update(self.data)

    def refresh_data(self):
        """ refresh status bar data """

        data = c.aria2.get_global_stat()
        if self.version == "0.00.0":
            self.version = c.aria2.get_version()['version']
        self.update(data)

    def update(self, data):
        """ generate status """

        if self.string is not None and \
                g.tty['prev_h'] == g.tty['curr_h'] and \
                g.tty['prev_w'] == g.tty['curr_w'] and \
                self.data == data:
            self.changed = False
            return

        self.changed = True
        self.data = data
        self.win = curses.newwin(1, g.tty['curr_w'],
                                 g.tty['curr_h'] - 1, 0)

        s_server = 'server: ' + c.server + ':' + str(c.port) + \
            ' ' + ('v' + self.version).join('()')

        num_downloads = int(self.data['numActive']) + \
            int(self.data['numWaiting']) + int(self.data['numStopped'])
        s_downloads = 'downloads: ' + self.data['numStopped'] + \
            '/' + str(num_downloads)

        dl_global = int(self.data['downloadSpeed'])
        ul_global = int(self.data['uploadSpeed'])

        s_speed = 'D/U: ' + str("%0.0f" % (dl_global / 1024)) + 'K / ' + \
            str("%0.0f" % (ul_global / 1024)) + 'K'

        self.string = create_row(
            (s_server, g.tty['curr_w'] - 21 - 20, 3, 'right'),
            (s_downloads, 21, 3, 'right'),
            (s_speed, 20, 1, 'left')
            )

    def draw(self, init):
        if not self.changed and not init:
            return

        self.win.clear()
        self.win.noutrefresh()

        try:
            self.win.addstr(0, 0, self.string, curses.A_BOLD)
        except curses.error:
            pass
        self.win.noutrefresh()
