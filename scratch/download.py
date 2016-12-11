#!/usr/bin/env python
import os
import re

from common import Globals, Config, create_row


class Download:
    num_downloads = 0
    w_name = Globals.tty_w - (Config.widths.size + Config.widths.status +
                              Config.widths.progress + Config.widths.percent +
                              Config.widths.sp + Config.widths.speed + Config.widths.eta)

    def __init__(self, data):
        self.data = data
        self.gid = self.data['gid']
        self.num_files = len(self.data['files'])
        self.bt = True if ('bittorrent' in self.data and 'info' in self.data['bittorrent']) else False

        self.name = 'N/A'
        self.name = self.data['bittorrent']['info']['name'] if self.bt else \
            os.path.basename(self.data['files'][0]['path'])

        self.size = int(self.data['totalLength'])
        self.row = None
        self.refresh()


    def refresh(self):
        self.done = int(self.data['completedLength'])
        self.status = self.data['status']
        self.progress = (self.done / self.size) if self.size != 0 else 0
        self.seeds = int(self.data['numSeeders']) if self.bt else 0
        self.peers = int(self.data['connections'])
        self.dl = int(self.data['downloadSpeed'])
        self.ul = int(self.data['uploadSpeed'])
        self.eta = (self.size - self.done) / (self.dl) if self.dl != 0 else -1

        self.format()

    def format(self):
        if Config.progress_markers != '':
            marker_b = Config.progress_markers[0]
            marker_e = Config.progress_markers[1]
            marker_p = 3
        else:
            marker_b = ''
            marker_e = ''
            marker_p = 1

        if self.num_files > 1:
            tree_node = '+ '
        else:
            tree_node = ''

        d_name = tree_node + self.name

        for item in Globals.suffixes:
            if self.size >= item[0]:
                suffix = item
                break
            suffix = item

        d_size = str("%0.1f" % (self.size / suffix[0])) + suffix[1]
        d_status = self.status

        d_progress = int(self.progress * (Config.widths.progress - marker_p)) * Config.progress_char
        d_progress = marker_b + d_progress + (Config.widths.progress - len(d_progress) - marker_p) * ' ' + marker_e
        d_percent = str("%0.2f" % (self.progress * 100)) + "%"

        d_sp = str(self.seeds) + "/" + str(self.peers)
        d_sp = re.sub('0/0', '-', d_sp)

        d_speed = str("%0.0f" % (self.dl / 1024)) + "K / " + str("%0.0f" % (self.ul / 1024)) + "K"
        d_speed = re.sub(' / 0K', '', (re.sub('^0K', '-', d_speed)))

        if self.eta != -1:
            eta_s = (self.size - self.done) / self.dl
            m, s = divmod(eta_s, 60)
            h, m = divmod(m, 60)
            d_eta = "%d:%02d:%02d" % (h, m, s)
        else:
            d_eta = "-"

        self.row = create_row(
            (d_name, Config.widths.name, 5, 'right'),
            (d_size, Config.widths.size, 3, 'left'),
            (d_status, Config.widths.status, 3, 'right'),
            (d_progress, Config.widths.progress, 1, 'right'),
            (d_percent, Config.widths.percent, 3, 'right'),
            (d_sp, Config.widths.sp, 3, 'left'),
            (d_speed, Config.widths.speed, 3, 'left'),
            (d_eta, Config.widths.eta, 2, 'left'))
