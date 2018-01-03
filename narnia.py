#!/usr/bin/env python3
""" narnia """

import curses
import os
import sys
import time

from narnia.colorstr import add_cstr, init_colors
from narnia.common import Config as c, Globals as g, refresh_windows
from narnia.common import Header, Status
from narnia.download import Download
from narnia.process import start_threads, thread_priority_data, thread_action


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


    def confirm_del():
        g.status.win.nodelay(False)
        curses.echo(True)
        add_cstr(0, 0, '<red.b>confirm deletion? [y/N] </red.b>' + ' ' * (int(g.tty['curr_w']) - 32), g.status.win)
        curses.echo(False)
        response = g.status.win.getch()
        g.status.win.nodelay(True)
        g.status.draw(True)
        return True if response == ord('y') else False

    def nav_up():
        y_pos = g.focused.win.getbegyx()[0]
        if g.num_downloads > g.tty['curr_h']:
            if g.focused == g.downloads[0]:
                g.start_idx = g.num_downloads - (g.tty['curr_h'] - 3)
            elif y_pos == 1:
                g.start_idx -= 1

        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) - 1) %
                                g.num_downloads]

    def nav_down():
        y_pos = g.focused.win.getbegyx()[0]
        if g.focused == g.downloads[-1]:
            g.start_idx = 0
        elif (y_pos + 3) >= g.tty['curr_h']:
            g.start_idx += 1

        g.focused.highlight = 0
        g.focused = g.downloads[(g.downloads.index(g.focused) + 1) %
                                g.num_downloads]

    def end():
        sys.exit()

    def pause():
        if g.focused.status == 'active' or g.focused.status == 'waiting':
            thread_action("c.aria2.pause('{}')".format(g.focused.gid))
        elif g.focused.status == 'paused':
            thread_action("c.aria2.unpause('{}')".format(g.focused.gid))

    def pause_all():
        if not c.aria2.tell_active():
            thread_action('c.aria2.unpause_all()')
        else:
            thread_action('c.aria2.pause_all()')

    def queue_up():
        if g.focused.status == 'waiting':
            thread_action("c.aria2.change_position('{}', -1, 'POS_CUR')".format(g.focused.gid))
            thread_priority_data()          # TODO: Optimize here

    def queue_down():
        if g.focused.status == 'waiting':
            thread_action("c.aria2.change_position('{}', 1, 'POS_CUR')".format(g.focused.gid))
            thread_priority_data()          # TODO: Optimize here

    def purge():
        thread_action('c.aria2.purge_download_result()')

    def retry():
        # TODO: TEST
        if g.focused.status == "error":
            url = g.focused.data['files'][0]['uris'][0]['uri'].strip()
            thread_action("c.aria2.remove_download_result('{}')".format(g.focused.gid))
            thread_action("c.aria2.add_uri(['{}'])".format(url))

    def delete():
        if g.focused.status == 'complete' or g.focused.status == 'removed' or g.focused.status == 'error':
            thread_action("c.aria2.remove_download_result('{}')".format(g.focused.gid))
            nav_up()
        elif confirm_del():
            thread_action("c.aria2.remove('{}')".format(g.focused.gid))
            g.status.draw(True)
            nav_up()

    def add():
        g.status.win.nodelay(False)
        curses.echo(True)
        add_cstr(0, 0, '<base3.b>add: </base3.b>' + ' ' * (int(g.tty['curr_w']) - 13), g.status.win)
        url = g.status.win.getstr(0, 5, 200)
        thread_action("c.aria2.add_uri([{}])".format(url.strip()))
        curses.echo(False)
        g.status.win.nodelay(True)
        g.status.draw(True)

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
        c.keys.add: add,
        c.keys.delete: delete,
        c.keys.purge: purge,
        c.keys.queue_up: queue_up,
        c.keys.queue_down: queue_down,
        # c.keys.select: select,
        # c.keys.expand: expand,
        c.keys.retry: retry,
        c.keys.quit: end,
        }

    if g.num_downloads != 0 or \
            key == c.keys.add or key == c.keys.quit or key == curses.KEY_RESIZE:
        actions.get(key, none)()


def main(screen):
    """ main """

    curses.curs_set(False)
    init_colors()
    screen.nodelay(True)
    screen.keypad(True)
    screen.getch()

    g.timer_ui = c.refresh_interval * 100

    g.header = Header()
    g.status = Status()

    g.file_status = curses.newwin(1, g.tty['curr_w'], g.tty['curr_h'] - 2, 0)
    g.pos_status = curses.newwin(1, 8, g.tty['curr_h'] - 1, g.tty['curr_w'] - 7)
    add_cstr(0, 0, g.s_pos, g.pos_status)
    g.pos_status.noutrefresh()

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

                for i in range(g.start_idx, min(g.num_downloads, g.tty['curr_h'] - 3) + g.start_idx):
                    g.downloads[i].draw(i - g.start_idx + 1, False)

                file_status_data = '[{}] {}'.format(g.focused.gid, g.focused.name)
                file_status_data += ' ' * (g.tty['curr_w'] - len(file_status_data) - 1)
                add_cstr(0, 0, file_status_data, g.file_status)
                g.file_status.noutrefresh()

                g.curr_pos = g.downloads.index(g.focused)
                if g.num_downloads == 1 or g.curr_pos == 0:
                    g.s_pos = '[top]'
                elif g.curr_pos + 1 == g.num_downloads:
                    g.s_pos = '[bot]'
                else:
                    g.s_pos = '[{:2}%]'.format(round(((g.curr_pos + 1) / g.num_downloads) * 100))

                g.s_pos = '<status.b>  {}</status.b>'.format(g.s_pos)

                g.pos_status.clear()
                add_cstr(0, 0, g.s_pos, g.pos_status)
                g.pos_status.noutrefresh()
            else:
                file_status_data = ' ' * (g.tty['curr_w'] - 1)
                add_cstr(0, 0, file_status_data, g.file_status)
                g.file_status.noutrefresh()

                g.pos_status.clear()
                add_cstr(0, 0, g.s_pos, g.pos_status)
                g.pos_status.noutrefresh()


            g.status.draw(False)

            g.tty['prev_h'] = g.tty['curr_h']
            g.tty['prev_w'] = g.tty['curr_w']

            curses.doupdate()
            g.timer_ui = 0

        time.sleep(0.01)
        g.timer_ui += 1

        key_in = screen.getch()
        if key_in != -1:
            g.timer_ui = c.refresh_interval * 100
        key_actions(key_in)

    input()


curses.wrapper(main)
