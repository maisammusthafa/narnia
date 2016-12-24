#!/usr/bin/env python
""" narnia """

import argparse
import curses
import os
import sys
import time
from collections import defaultdict

from narnia.common import create_row, Header, Status
from narnia.common import Config as c
from narnia.common import Globals as g
from narnia.download import Download


def get_downloads():
    """ get downloads and create classes """

    response = []
    prev_downloads = list(g.downloads)
    g.downloads = []

    active = c.aria2.tellActive()
    waiting = c.aria2.tellWaiting(0, 100)
    stopped = c.aria2.tellStopped(-1, 100)
    states = [active, waiting, stopped]

    def lookup(query):
        """ lookup downloads """

        for item in prev_downloads:
            if item.gid == query:
                return prev_downloads.index(item)
        return -1

    for state in states:
        for item in state:
            response.append(item)

    for item in response:
        index = lookup(item['gid'])
        if index != -1:
            prev_downloads[index].refresh(item)
            g.downloads.append(prev_downloads[index])
        else:
            g.downloads.append(Download(item))

    diff = len(prev_downloads) - len(g.downloads)

    if diff != 0:
        for item in prev_downloads[-diff:]:
            item.win.clear()
            item.win.refresh()

    g.num_downloads = len(g.downloads)


def key_actions(key):
    """ actions based on key input """

    def refresh_windows():
        """ update window widths and refresh them """

        tty_dims = list(map(int, os.popen('stty size', 'r').read().split()))
        g.tty_h, g.tty_w = tty_dims

        c.widths.name = g.tty_w - (c.widths.size + c.widths.status +
                                   c.widths.progress + c.widths.percent +
                                   c.widths.seeds_peers + c.widths.speed +
                                   c.widths.eta)

        g.header.update()

        g.status.win.clear()
        g.status.win.refresh()
        g.status.update()

        g.timer = (c.refresh_interval * 100) - 1

    def nav_up():
        """ nav up """
        # TODO implement nav_up on delete

        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) - 1) %
                                g.num_downloads]

    def nav_down():
        """ nav down """

        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) + 1) %
                                g.num_downloads]

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
    screen.getch()

    get_downloads()

    g.header = Header()
    g.status = Status()

    while True:
        g.header.draw()

        if g.timer == c.refresh_interval * 100:
            get_downloads()
            g.status.update()
            g.timer = 0

        if g.focused not in g.downloads:
            g.focused = g.downloads[0]

        g.focused.highlight = curses.A_REVERSE

        for i in range(g.num_downloads):
            g.downloads[i].draw(i + 1)

        # dbg = curses.newwin(20, g.tty_w, g.tty_h - 20, 0)
        # string = ''
        # for download in g.downloads:
            # string += download.gid + '\n'
        # dbg.addstr(0, 0, string + '\n' + str(g.dbg))
        # dbg.refresh()

        g.status.draw()

        time.sleep(0.01)
        key_in = screen.getch()
        key_actions(key_in)

        g.timer += 1

    input()


curses.wrapper(main)
