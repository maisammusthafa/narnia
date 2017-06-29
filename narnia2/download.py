#!/bin/env python3
""" provides download class """

import curses
import os
import re

from narnia2.common import Config as c, Globals as g
from narnia2.common import create_row


class Download:
    w_name = g.tty['curr_w'] - (c.widths.size + c.widths.status +
                                c.widths.progress + c.widths.percent +
                                c.widths.seeds_peers + c.widths.speed +
                                c.widths.eta)

    def __init__(self, data):
        self.data = data
        self.gid = self.data['gid']
        self.num_files = len(self.data['files'])
        self.torrent = True if ('bittorrent' in self.data and
                                'info' in self.data['bittorrent']) else False

        self.row = None
        self.highlight = 0
        self.prev_highlight = 0

        self.refresh(self.data)

        self.win = curses.newwin(1, g.tty['curr_w'], 1, 0)
        self.win.nodelay(True)
        self.win.keypad(True)

    def refresh(self, data):
        """ refresh values """

        if self.row is not None and \
                g.tty['prev_w'] == g.tty['curr_w'] and \
                self.data == data:
            self.changed = False
            return
        else:
            self.changed = True

        self.data = data
        self.name = self.data['bittorrent']['info']['name'] if self.torrent \
            else os.path.basename(self.data['files'][0]['path'])
        if self.name == '':
            self.name = 'N/A'

        self.size = int(self.data['totalLength'])
        self.done = int(self.data['completedLength'])
        self.status = self.data['status']
        self.progress = (self.done / self.size) if self.size != 0 else 0
        # TODO: [bug] progress percentage is 0 on complete for 0 byte files
        self.seeds = int(self.data['numSeeders']) if self.torrent else 0
        self.peers = int(self.data['connections'])
        self.dl_speed = int(self.data['downloadSpeed'])
        self.ul_speed = int(self.data['uploadSpeed'])
        self.eta = (self.size - self.done) / (self.dl_speed) \
            if self.dl_speed != 0 else -1

        self.format()

    def format(self):
        """ apply formatting to fields """

        marker = {'begin': '', 'end': '', 'padding': 1}

        if c.progress_markers != '':
            marker['begin'] = c.progress_markers[0]
            marker['end'] = c.progress_markers[1]
            marker['padding'] = 3

        if self.num_files > 1:
            tree_node = '+ '
        else:
            tree_node = ''

        d_name = tree_node + self.name

        size = 0
        for item in g.suffixes:
            if self.size >= item[0]:
                size = self.size / item[0]
                if size > 999 and size < 1024:
                    size /= 1024
                    suffix = g.suffixes[g.suffixes.index(item) - 1][1]
                    break
                suffix = item[1]
                break
            suffix = item[1]
        d_size = str("%0.1f" % size) + suffix

        d_status = self.status

        d_progress = int(self.progress *
                         (c.widths.progress - marker['padding'])) * \
            c.progress_char

        p_whitespaces = (c.widths.progress - len(d_progress) -
                         marker['padding']) * ' '
        d_progress = marker['begin'] + d_progress + \
            p_whitespaces + marker['end']

        d_percent = str("%0.2f" % (self.progress * 100)) + "%"

        d_sp = str(self.seeds) + "/" + str(self.peers)
        d_sp = re.sub('0/0', '-', d_sp)

        d_speed = str("%0.0f" % (self.dl_speed / 1024)) + "K / " + \
            str("%0.0f" % (self.ul_speed / 1024)) + "K"
        d_speed = re.sub(' / 0K', '', (re.sub('^0K', '-', d_speed)))

        if self.eta != -1:
            eta_s = (self.size - self.done) / self.dl_speed
            mins, secs = divmod(eta_s, 60)
            hrs, mins = divmod(mins, 60)
            d_eta = "%d:%02d:%02d" % (hrs, mins, secs)
        else:
            d_eta = "-"

        self.row = create_row(
            (d_name, c.widths.name, 5, 'right'),
            (d_size, c.widths.size, 3, 'left'),
            (d_status, c.widths.status, 3, 'right'),
            (d_progress, c.widths.progress, 1, 'right'),
            (d_percent, c.widths.percent, 3, 'right'),
            (d_sp, c.widths.seeds_peers, 3, 'left'),
            (d_speed, c.widths.speed, 3, 'left'),
            (d_eta, c.widths.eta, 1, 'left'))

    def draw(self, y_pos, resized):
        if resized:
            self.refresh(self.data)
            # TODO: [BUG] network request is being made for new data

        # TODO: Optimize draw here
        # if self.changed or (self.highlight != self.prev_highlight):
            # self.prev_highlight = self.highlight
        # else:
            # return

        self.win.clear()
        self.win.mvwin(y_pos, 0)
        try:
            self.win.addstr(0, 0, self.row, self.highlight)
        except curses.error:
            pass
        self.win.noutrefresh()
