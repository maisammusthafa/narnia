#!/usr/bin/env python
import aria2
from common import Config, create_row
from download import Download
import argparse, curses, os, sys, time

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
    s_server = 'server: ' + Config.server + ':' + str(Config.port) + ' ' + ('v' + aria2.getVersion()['version']).join('()')
    s_downloads = 'downloads: ' + aria2.getGlobalStat()['numStopped'] + '/' + str(Download.num_downloads)
    s_speed = 'D/U: ' + str("%0.0f" % (int(aria2.getGlobalStat()['downloadSpeed']) / 1024)) + 'K / ' + \
            str("%0.0f" % (int(aria2.getGlobalStat()['uploadSpeed']) / 1024)) + 'K'

    s_string = create_row((s_server, Config.tty_w - 21 - 21, 3, 'right'),      # resizing bug here
            (s_downloads, 21, 3, 'right'),
            (s_speed, 20, 1, 'left')
            )
    return s_string


def main(screen):
    curses.curs_set(False)
    downloads = []

    header = curses.newwin(1, Config.tty_w, 0, 0)
    header.addstr(0, 0, get_header(), curses.A_BOLD)
    header.refresh()

    waiting = aria2.tellWaiting()
    stopped = aria2.tellStopped()
    states = [waiting, stopped]

    for state in states:
        for i in range(len(state)):
            downloads.append(Download(state[i]))

    rows = {}
    for i in range(len(downloads)):
        rows[i] = curses.newwin(1, Config.tty_w, i + 1, 0)
        rows[i].addstr(0, 0, downloads[i].row, curses.A_REVERSE)
        rows[i].refresh()

    status = curses.newwin(1, Config.tty_w, Config.tty_h - 1, 0)
    status.addstr(0, 0, get_status(), curses.A_BOLD)
    status.refresh()

    input()


curses.wrapper(main)
