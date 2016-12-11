#!/usr/bin/env python
""" narnia """

import argparse
import curses
import os
import sys
import time
from collections import defaultdict

from narnia.common import create_row
from narnia.common import Config as c
from narnia.common import Globals as g
from narnia.download import Download


def get_header():
    """ generate header """

    name, size, status, progress, percent, seeds_peers, speed, eta = \
        "NAME", "SIZE", "STATUS", "PROGRESS", "", "S/P", "D/U", "ETA"

    h_string = create_row(
        (name, c.widths.name, 3, 'right'),
        (size, c.widths.size, 3, 'left'),
        (status, c.widths.status, 3, 'right'),
        (progress, c.widths.progress, 3, 'right'),
        (percent, c.widths.percent, 3, 'right'),
        (seeds_peers, c.widths.seeds_peers, 3, 'left'),
        (speed, c.widths.speed, 3, 'left'),
        (eta, c.widths.eta, 3, 'left')
        )

    return h_string


def get_status():
    """ generate status bar """

    s_server = 'server: ' + c.server + ':' + str(c.port) + \
        ' ' + ('v' + c.aria2.getVersion()['version']).join('()')

    s_downloads = 'downloads: ' + \
        c.aria2.getGlobalStat()['numStopped'] + \
        '/' + str(Download.num_downloads)

    dl_global = int(c.aria2.getGlobalStat()['downloadSpeed'])
    ul_global = int(c.aria2.getGlobalStat()['uploadSpeed'])

    s_speed = 'D/U: ' + str("%0.0f" % (dl_global / 1024)) + 'K / ' + \
        str("%0.0f" % (ul_global / 1024)) + 'K'

    s_string = create_row(
        (s_server, g.tty_w - 21 - 21, 3, 'right'),      # resizing bug here
        (s_downloads, 21, 3, 'right'),
        (s_speed, 20, 1, 'left')
        )
    return s_string


def get_downloads():
    """ get downloads and create classes """

    result = []

    active = c.aria2.tellActive()
    waiting = c.aria2.tellWaiting(0, 100)
    stopped = c.aria2.tellStopped(-1, 100)
    states = [active, waiting, stopped]

    for state in states:
        for item in state:
            result.append(Download(item))

    Download.num_downloads = len(result)
    return result


def refresh_header():
    """ refresh header """

    pass


def refresh_status():
    """ refresh status bar """

    g.status.clear()
    g.status.refresh()


def key_actions(key):
    """ actions based on key input """

    def refresh_windows():
        """ update window widths and refresh them """

        tty_dims = list(map(int, os.popen('stty size', 'r').read().split()))
        g.tty_h, g.tty_w = tty_dims

        c.widths.name = g.tty_w - (c.widths.size + c.widths.status +
                                   c.widths.progress + c.widths.percent +
                                   c.widths.sp + c.widths.speed +
                                   c.widths.eta + 1)
        refresh_status()

    def nav_up():
        """ nav up """

        g.info[g.downloads[g.focused].gid]['highlight'] = 0
        g.focused = (g.focused - 1) % Download.num_downloads

    def nav_down():
        """ nav down """

        g.info[g.downloads[g.focused].gid]['highlight'] = 0
        g.focused = (g.focused + 1) % Download.num_downloads

    def end():
        """ quit """

        sys.exit()

    def none():
        """ do nothing """

        pass

    actions = {
        curses.KEY_RESIZE: refresh_windows,
        curses.KEY_UP: nav_up,
        c.keys.key_up: nav_up,
        curses.KEY_DOWN: nav_down,
        c.keys.key_down: nav_down,
        # c.keys.pause_all: pause_all,
        # c.keys.pause: pause,
        # c.keys.add: add,
        # c.keys.delete: delete,
        # c.keys.purge: purge,
        # c.keys.queue_up: queue_up,
        # c.keys.queue_down: queue_down,
        # c.keys.select: select,
        # c.keys.expand: expand,
        c.keys.quit: end,
        }

    actions.get(key, none)()


def main(screen):
    """ main """

    curses.curs_set(False)
    screen.nodelay(True)
    screen.keypad(True)

    while True:
        g.header = curses.newwin(1, g.tty_w, 0, 0)
        g.header.addstr(0, 0, get_header(), curses.A_BOLD)
        g.header.refresh()

        g.downloads = get_downloads()

        rows = {}
        for i in range(len(g.downloads)):
            if g.downloads[i].gid not in g.info:
                g.info[g.downloads[i].gid] = defaultdict(int)
                g.info[g.downloads[i].gid]['bt'] = g.downloads[i].torrent

            rows[i] = curses.newwin(1, g.tty_w, i + 1, 0)

            rows[i].addstr(0, 0, g.downloads[i].row,
                           g.info[g.downloads[i].gid]['highlight'])

            rows[i].refresh()

        g.info[g.downloads[g.focused].gid]['highlight'] = curses.A_REVERSE

        # dbg = curses.newwin(5, g.tty_w, g.tty_h - 20, 0)
        # dbg.addstr(0, 0, '0: ', g.info[g.downloads[0].gid]['highlight'])
        # dbg.addstr(1, 0, '1: ', g.info[g.downloads[1].gid]['highlight'])
        # dbg.addstr(2, 0, '2: ', g.info[g.downloads[2].gid]['highlight'])
        # dbg.addstr(3, 0, '3: ', g.info[g.downloads[3].gid]['highlight'])
        # dbg.refresh()

        g.status = curses.newwin(1, g.tty_w, g.tty_h - 1, 0)
        g.status.addstr(0, 0, get_status(), curses.A_BOLD)
        g.status.refresh()

        time.sleep(0.01)
        key_in = screen.getch()
        key_actions(key_in)

        g.header.clear()
        for i in range(len(g.downloads)):
            rows[i].clear()
        g.status.clear()

    input()


curses.wrapper(main)
