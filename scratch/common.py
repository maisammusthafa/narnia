#!/usr/bin/env python
import configparser, os

class Keybindings:
    def __init__(self, keybindings):
        self.up = ord(keybindings.get('up', 'k'))
        self.down = ord(keybindings.get('down', 'j'))
        self.pause_all = ord(keybindings.get('pause-all', 'P'))
        self.pause = ord(keybindings.get('pause', 'p'))
        self.add = ord(keybindings.get('add', 'a'))
        self.delete = ord(keybindings.get('delete', 'd'))
        self.purge = ord(keybindings.get('purge', 'D'))
        self.queue_up = ord(keybindings.get('queue-up', 'K'))
        self.queue_down = ord(keybindings.get('queue-down', 'J'))
        self.select = ord(keybindings.get('select-file', 'v'))
        self.expand = ord(keybindings.get('expand-torrent', 'h'))
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
    def __init__(self, ui, tty_w):
        self.size = ui.getint('width-size', 10)
        self.status = ui.getint('width-status', 11)
        self.progress = ui.getint('width-progress', 15)
        self.percent = ui.getint('width-percent', 10)
        self.sp = ui.getint('width-seeds-peers', 10)
        self.speed = ui.getint('width-speed', 16)
        self.eta = ui.getint('width-eta', 10)
        self.name = tty_w - (self.size + self.status + self.progress +
                self.percent + self.sp + self.speed + self.eta + 1)


class Config:
    config = configparser.ConfigParser()
    config_file = os.path.expanduser("~/.config/narnia/config")

    if not os.path.isfile(config_file):
        import io
        config_file = io.StringIO('[Connection]\n[UI]\n[Colors]\n[Keybindings]')
        config.readfp(config_file)
    else:
        config.read(config_file)

    ui = config['UI']
    tty_h, tty_w = list(map(int, os.popen('stty size', 'r').read().split()))

    server = config['Connection'].get('server', 'localhost')
    port = config['Connection'].getint('port', 6800)

    refresh_interval = ui.getfloat('refresh-interval', 0.5)
    progress_markers = ui.get('progress-bar-markers', '[]')
    progress_char = ui.get('progress-bar-char', '#')

    keys = Keybindings(config['Keybindings'])
    colors = Colors(config['Colors'])
    widths = Widths(ui, tty_w)

    suffixes = [(1024 ** 3, ' G'), (1024 ** 2, ' M'), (1024, ' K'), (1, ' B')]      # bug: value between 1000 and 1024


def create_row(*fields):
    row = ""
    for field in fields:
        value, width, padding, alignment = field[0], field[1], field[2], field[3]
        value = value[:(width - padding)] + ".." if len(value) > width - padding else value
        if alignment == 'right':
            row += (value +  (width - len(value)) * ' ')
        else:
            row += ((width - len(value) - padding) * ' ' + value + padding * ' ')
    return row
