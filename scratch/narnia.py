#!/usr/bin/env python
from common import Config, create_row
from common import Globals as g
from download import Download
import argparse, curses, os, sys, time
from collections import defaultdict

def get_header():
    name, size, status, progress, percent, sp, speed, eta = \
    "NAME", "SIZE", "STATUS", "PROGRESS", "", "S/P", "D/U", "ETA"

    h_string = create_row(
            (name, Config.widths.name, 3, 'right'),
            (size, Config.widths.size, 3, 'left'),
            (status, Config.widths.status, 3, 'right'),
            (progress, Config.widths.progress, 3, 'right'),
            (percent, Config.widths.percent, 3, 'right'),
            (sp, Config.widths.sp, 3, 'left'),
            (speed, Config.widths.speed, 3, 'left'),
            (eta, Config.widths.eta, 3, 'left')
            )

    return h_string


def get_status():
    s_server = 'server: ' + Config.server + ':' + str(Config.port) + ' ' + ('v' + Config.aria2.getVersion()['version']).join('()')
    s_downloads = 'downloads: ' + Config.aria2.getGlobalStat()['numStopped'] + '/' + str(Download.num_downloads)
    s_speed = 'D/U: ' + str("%0.0f" % (int(Config.aria2.getGlobalStat()['downloadSpeed']) / 1024)) + 'K / ' + \
            str("%0.0f" % (int(Config.aria2.getGlobalStat()['uploadSpeed']) / 1024)) + 'K'

    s_string = create_row((s_server, g.tty_w - 21 - 21, 3, 'right'),      # resizing bug here
            (s_downloads, 21, 3, 'right'),
            (s_speed, 20, 1, 'left')
            )
    return s_string


def get_downloads():
    result = []

    active = Config.aria2.tellActive()
    waiting = Config.aria2.tellWaiting(0, 100)
    stopped = Config.aria2.tellStopped(-1, 100)
    states = [active, waiting, stopped]

    for state in states:
        for i in range(len(state)):
            result.append(Download(state[i]))

    Download.num_downloads = len(result)
    return result


def key_actions(key):
    def refresh_windows():
        g.tty_h, g.tty_w = list(map(int, os.popen('stty size', 'r').read().split()))
        Config.widths.name = g.tty_w - (Config.widths.size + Config.widths.status + Config.widths.progress +
                Config.widths.percent + Config.widths.sp + Config.widths.speed + Config.widths.eta + 1)

        g.status.clear()
        g.status.refresh()
        # screen.refresh_status()

    def nav_up():
        g.info[g.downloads[g.focused].gid]['highlight'] = 0
        g.focused = (g.focused - 1) % Download.num_downloads

    def nav_down():
        g.info[g.downloads[g.focused].gid]['highlight'] = 0
        g.focused = (g.focused + 1) % Download.num_downloads

    def quit():
        sys.exit()

    def none():
        pass

    actions = {
            curses.KEY_RESIZE:refresh_windows,
            curses.KEY_UP:nav_up,
            Config.keys.up:nav_up,
            curses.KEY_DOWN:nav_down,
            Config.keys.down:nav_down,
            # keys.pause_all:pause_all,
            # keys.pause:pause,
            # keys.add:add,
            # keys.delete:delete,
            # keys.purge:purge,
            # keys.queue_up:queue_up,
            # keys.queue_down:queue_down,
            # keys.select:select,
            # keys.expand:expand,
            Config.keys.quit:quit,
            }

    actions.get(key, none)()


def main(screen):
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
                g.info[g.downloads[i].gid]['bt'] = g.downloads[i].bt

            rows[i] = curses.newwin(1, g.tty_w, i + 1, 0)
            rows[i].addstr(0, 0, g.downloads[i].row, g.info[g.downloads[i].gid]['highlight'])
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
