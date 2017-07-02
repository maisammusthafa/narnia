#!/bin/env python3
""" narnia """

import argparse
import curses
import os
import sys
import time

from narnia2.common import Config as c, Globals as g
from narnia2.common import Header, Status
from narnia2.download import Download
from narnia2.process import start_threads, thread_priority_data


def create_downloads():
    """ get downloads and create classes """

    response = []
    prev_downloads = list(g.downloads)
    g.downloads = []

    def lookup(query):
        """ lookup downloads """

        for item in prev_downloads:
            if item.gid == query:
                return prev_downloads.index(item)
        return -1

    for state in g.download_states:
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
            item.win.noutrefresh()

    g.num_downloads = len(g.downloads)


def key_actions(key):
    """ actions based on key input """

    def refresh_windows():
        """ update window widths and refresh them """

        g.tty['curr_h'], g.tty['curr_w'] = list(map(
            int, os.popen('stty size', 'r').read().split()))

        c.widths.name = g.tty['curr_w'] - \
            (c.widths.size + c.widths.status +
             c.widths.progress + c.widths.percent +
             c.widths.seeds_peers + c.widths.speed +
             c.widths.eta)

        g.header.update()

        g.status.win.clear()
        g.status.win.noutrefresh()
        g.status.update(g.status.data)

        for i in range(g.num_downloads):
            g.downloads[i].draw(i + 1, True)
        curses.doupdate()

        g.timer_ui = (c.refresh_interval * 100) - 1

    def nav_up():
        # TODO: implement nav_up on delete

        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) - 1) %
                                g.num_downloads]

    def nav_down():
        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) + 1) %
                                g.num_downloads]

    def end():
        sys.exit()

    def pause():
        if g.focused.status == 'active' or g.focused.status == 'waiting':
            c.aria2.pause(g.focused.gid)
        elif g.focused.status == 'paused':
            c.aria2.unpause(g.focused.gid)

    def pause_all():
        if not c.aria2.tell_active():
            c.aria2.unpause_all()
        else:
            c.aria2.pause_all()

    def queue_up():
        if g.focused.status == 'waiting':
            c.aria2.change_position(g.focused.gid, -1, 'POS_CUR')
            thread_priority_data()          # TODO: Optimize here

    def queue_down():
        if g.focused.status == 'waiting':
            c.aria2.change_position(g.focused.gid, 1, 'POS_CUR')
            thread_priority_data()          # TODO: Optimize here

    def purge():
        c.aria2.purge_download_result()

    def retry():
        if g.focused.status == "error":
            url = g.focused.data['files'][0]['uris'][0]['uri'].strip()
            c.aria2.remove_download_result(g.focused.gid)
            c.aria2.add_uri([url])

    def none():
        pass

    actions = {
        curses.KEY_RESIZE: refresh_windows,
        curses.KEY_UP: nav_up,
        c.keys.key_up: nav_up,
        curses.KEY_DOWN: nav_down,
        c.keys.key_down: nav_down,
        c.keys.pause_all: pause_all,
        c.keys.pause: pause,
        # c.keys.add: add,
        # c.keys.delete: delete,
        c.keys.purge: purge,
        c.keys.queue_up: queue_up,
        c.keys.queue_down: queue_down,
        # c.keys.select: select,
        # c.keys.expand: expand,
        c.keys.retry: retry,
        c.keys.quit: end,
        }

    if g.num_downloads != 0 or \
            key == c.keys.quit or key == curses.KEY_RESIZE:
        actions.get(key, none)()


def main(screen):
    """ main """

    curses.curs_set(False)
    screen.nodelay(True)
    screen.keypad(True)
    screen.getch()

    g.timer_ui = c.refresh_interval * 100

    g.header = Header()
    g.status = Status()

    g.header.draw(True)
    g.status.draw(True)

    start_threads()
    # TODO: [BUG] initial delay even on fast networks

    while True:
        if g.timer_ui == c.refresh_interval * 100:
            g.header.draw(False)

            create_downloads()

            if g.num_downloads != 0:
                if g.focused not in g.downloads:
                    g.focused = g.downloads[0]

                g.focused.highlight = curses.A_REVERSE

                for i in range(g.num_downloads):
                    g.downloads[i].draw(i + 1, False)

            g.status.draw(False)

            g.tty['prev_h'] = g.tty['curr_h']
            g.tty['prev_w'] = g.tty['curr_w']

            curses.doupdate()
            g.timer_ui = 0

        # DEBUGGING
        # g.dbg = 0
        # dbg = curses.newwin(20, g.tty['curr_w'], g.tty['curr_h'] - 20, 0)
        # dbg.addstr(0, 0, str(g.dbg))
        # dbg.noutrefresh()

        time.sleep(0.01)
        g.timer_ui += 1

        key_in = screen.getch()
        if key_in != -1:
            g.timer_ui = c.refresh_interval * 100
        key_actions(key_in)

    input()


curses.wrapper(main)
