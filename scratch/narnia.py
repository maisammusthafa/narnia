#!/bin/python
import aria2
from common import Config
import curses, os, re, sys, time

class Download:
    num_downloads = 0

    def __init__(self, data):
        self.data = data
        self.gid = self.data['gid']
        self.num_files = len(self.data['files'])
        self.bt = True if 'bittorrent' in self.data else False

        self.name = 'N/A'
        self.name = self.data['bittorrent']['info']['name'] if self.bt else \
                os.path.basename(self.data['files'][0]['path'])

        self.size = int(self.data['totalLength'])
        self.refresh()

        Download.num_downloads += 1


    def refresh(self):
        self.done = int(self.data['completedLength'])
        self.status = self.data['status']
        self.progress = (self.done / self.size) if self.size !=0 else 0
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

        if self.num_files  > 1:
            tree_node = '+ '
        else:
            tree_node = ''

        d_name = tree_node + self.name

        for item in Config.suffixes:
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

        self.row = self.create_row(
                (d_name, 40, 5, 'right'),
                (d_size, Config.widths.size, 3, 'left'),
                (d_status, Config.widths.status, 3, 'right'),
                (d_progress, Config.widths.progress, 1, 'right'),
                (d_percent, Config.widths.percent, 3, 'right'),
                (d_sp, Config.widths.sp, 3, 'left'),
                (d_speed, Config.widths.speed, 3, 'left'),
                (d_eta, Config.widths.eta, 2, 'left'))


    def create_row(self, *fields):
        row = ""
        for field in fields:
            value, width, padding, alignment = field[0], field[1], field[2], field[3]
            value = value[:(width - padding)] + ".." if len(value) > width - padding else value
            if alignment == 'right':
                row += (value +  (width - len(value)) * ' ')
            else:
                row += ((width - len(value) - padding) * ' ' + value + padding * ' ')
        return row

def main():
    downloads = []

    waiting = aria2.tellWaiting()
    stopped = aria2.tellStopped()
    states = [waiting, stopped]

    for state in states:
        for i in range(len(state)):
            downloads.append(Download(state[i]))

    tty_h, tty_w = list(map(int, os.popen('stty size', 'r').read().split()))

    print(downloads[0].row)
    print(downloads[1].row)
    print(downloads[2].row)
    print(downloads[3].row)


main()
