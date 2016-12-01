#!/bin/python
from narnia import pyaria2, cstr
import argparse, configparser, curses, os, re, sys, time
from socket import gaierror

class Download:
    rows = []
    downloads = []
    num_rows = 0
    num_downloads = 0
    expanded = {}

    def __init__(self, data):
        self.data = data
        self.gid = self.data['gid']

        self.num_files = len(self.data['files'])
        if self.num_files > 1 and self.gid not in Download.expanded:
            Download.expanded[self.gid] = False

        try:
            self.name = self.data['bittorrent']['info']['name']
        except:
            self.name = os.path.basename(self.data['files'][0]['path'])
        if self.name == '':
            self.name = 'N/A'

        self.size = int(self.data['totalLength'])
        self.refresh()

        if self.num_files > 1 and Download.expanded[self.gid] == True:
            Download.num_rows += 1 + self.num_files
        else:
            Download.num_rows += 1
        Download.num_downloads += 1

    def refresh(self):
        self.done = int(self.data['completedLength'])
        self.status = self.data['status']

        if self.size != 0:
            self.progress = self.done / self.size * 100
        else:
            self.progress = 0

        try:
            self.seeds = int(self.data['numSeeders'])
        except:
            self.seeds = 0

        self.peers = int(self.data['connections'])
        self.dl = int(self.data['downloadSpeed']) / 1024
        self.ul = int(self.data['uploadSpeed']) / 1024

        if self.dl != 0:
            eta_s = (self.size - self.done) / (self.dl * 1024)
            m, s = divmod(eta_s, 60)
            h, m = divmod(m, 60)
            self.eta = "%d:%02d:%02d" % (h, m, s)
        else:
            self.eta = "-"

        return self


class Window:
    def __init__(self, height, width, y, x):
        self.height, self.width  = height, width
        self.y, self.x = y, x
        self.win = None

        self.enable_colors = colors.getboolean('colors', True)
        self.progress_markers = ui.get('progress-bar-markers', '[]')
        self.progress_char = ui.get('progress-bar-char', '#')

        self.w_size = ui.getint('width-size', 10)
        self.w_status = ui.getint('width-status', 11)
        self.w_progress = ui.getint('width-progress', 15)
        self.w_percent = ui.getint('width-percent', 10)
        self.w_sp = ui.getint('width-seeds-peers', 10)
        self.w_speed = ui.getint('width-speed', 16)
        self.w_eta = ui.getint('width-eta', 10)
        self.w_name = self.width - (self.w_size + self.w_status + self.w_progress +
                self.w_percent + self.w_sp + self.w_speed + self.w_eta + 1)

        self.option = 0
        self.count = 0
        self.refresh_marker = ui.getfloat('refresh-interval', 0.5) / 0.01
        self.highlight = []

        self.t_string = ""
        self.r_string = ""
        self.s_string = ""

        self.suffixes = [(1024 ** 3, ' G'), (1024 ** 2, ' M'), (1024, ' K'), (1, ' B')]      # bug: value between 1000 and 1024

        if self.enable_colors == True:
            self.status_colors = {
                    'active':colors.get('dl-active', 'base2').join('<>'),
                    'paused':colors.get('dl-paused', 'default').join('<>'),
                    'skip':colors.get('dl-skip', 'default').join('<>'),
                    'waiting':colors.get('dl-waiting', 'blue').join('<>'),
                    'pending':colors.get('dl-pending', 'blue').join('<>'),
                    'complete':colors.get('dl-complete', 'green').join('<>'),
                    'removed':colors.get('dl-removed', 'yellow').join('<>'),
                    'error':colors.get('dl-error', 'red').join('<>'),
                    }
        else:
            self.status_colors = {
                    }


    def create(self):
        self.win = curses.newwin(self.height, self.width, self.y, self.x)
        self.win.nodelay(True)
        self.win.keypad(True)
        self.refresh_header()
        self.refresh_status()

    def create_row(self, *items):
        row = ""
        for item in items:
            value = item[0][:(item[1] - item[2])] + ".." if len(item[0]) > item[1] - item[2] else item[0]
            if item[3] == 0:
                row += (value +  (item[1] - len(value)) * ' ')
            else:
                row += ((item[1] - len(value) - item[2]) * ' ' + value + item[2] * ' ')
        return row

    def refresh_header(self):
        t_name, t_size, t_status, t_progress, t_percent, t_sp, t_speed, t_eta = \
        "NAME", "SIZE", "STATUS", "PROGRESS", "", "S/P", "D/U", "ETA"

        t_string = self.create_row(
                (t_name, self.w_name, 3, 0),
                (t_size, self.w_size, 3, 1),
                (t_status, self.w_status, 3, 0),
                (t_progress, self.w_progress, 3, 0),
                (t_percent, self.w_percent, 3, 0),
                (t_sp, self.w_sp, 3, 1),
                (t_speed, self.w_speed, 3, 1),
                (t_eta, self.w_eta, 3, 1)
                )

        self.t_string = "<header.b>" + t_string + "</header.b>"

    def refresh_status(self):
        s_server = 'server: ' + server + ':' + str(port) + ' ' + ('v' + aria2.getVersion()['version']).join('()')
        s_downloads = 'downloads: ' + aria2.getGlobalStat()['numStopped'] + '/' + str(Download.num_downloads)
        s_speed = 'D/U: ' + str("%0.0f" % (int(aria2.getGlobalStat()['downloadSpeed']) / 1024)) + 'K / ' + \
                str("%0.0f" % (int(aria2.getGlobalStat()['uploadSpeed']) / 1024)) + 'K'

        s_string = self.create_row((s_server, self.width - 21 - 21, 3, 0),      # resizing bug here
                (s_downloads, 21, 3, 0),
                (s_speed, 20, 1, 1)
                )
        self.s_string = "<status.b>" + s_string + "</status.b>"

    def draw(self):
        self.win.clear()
        time.sleep(0.01)
        self.count += 1

        self.highlight = [0] * Download.num_rows
        self.highlight[self.option] = curses.A_REVERSE

        get_rows(self)

        cstr.add(0, 0, self.t_string, self.win, True)
        cstr.add(1, 0, self.r_string, self.win, True)
        # try:
            # cstr.add(1, 0,
                    # self.r_string + "\n[debugging]\ngid: " +
                    # Download.rows[self.option]['gid'] + "\nindex: " +
                    # str(Download.rows[self.option]['index']) +
                    # "\nstatus: " + Download.rows[self.option]['status'] +
                    # "\nselected: " + str(Download.rows[self.option - Download.rows[self.option]['index'] - 1]['selected']) +
                    # "\n\n" + str(create_tree(Download.downloads[self.option])),
                    # self.win, True)                                             # debugging
        # except:
            # try:
                # cstr.add(1, 0,
                        # self.r_string + "\n[debugging]\ngid: " +
                        # Download.rows[self.option]['gid'] + "\nindex: " +
                        # str(Download.rows[self.option]['index']) +
                        # "\nstatus: " + Download.rows[self.option]['status'],
                        # self.win, True)                                             # debugging
            # except:
                # pass
        if Download.num_downloads != 0:
            selected_file = self.create_row((str(Download.rows[self.option]['name']), self.width, 3, 0))
            cstr.add(self.height - 2, 0, selected_file, self.win, True)

        cstr.add(self.height - 1, 0, self.s_string, self.win, True)

        self.win.refresh()


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


def get_downloads():
    Download.num_rows = 0
    Download.num_downloads = 0
    Download.rows = []
    downloads = []
    active = aria2.tellActive()
    waiting = aria2.tellWaiting(0, 100)
    stopped = aria2.tellStopped(-1, 100)
    states = [active, waiting, stopped]

    for state in states:
        for i in range(len(state)):
            downloads.append(Download(state[i]))

    return downloads


def create_tree(item):
    result = ''
    for i in range(item.num_files):
        f = item.data['files'][i]
        result += f['path'].replace(item.data['dir'] + '/' + item.name, '') + "\n"
    return result


def get_rows(screen):
    screen.r_string = ""

    if Download.num_downloads != 0:
        j = 0
        for i in range(Download.num_downloads):
            if i > screen.height - 3:
                break
            item = Download.downloads[i]

            if screen.progress_markers != '':
                marker_b = screen.progress_markers[0]
                marker_e = screen.progress_markers[1]
                marker_p = 3
            else:
                marker_b = ''
                marker_e = ''
                marker_p = 1

            if item.num_files  > 1:
                tree_node = '+ ' if Download.expanded[item.gid] == False else '- '
            else:
                tree_node = ''

            d_name = tree_node + item.name

            for x in screen.suffixes:
                if item.size >= x[0]:
                    suffix = x
                    break
                suffix = x

            d_size = str("%0.1f" % (item.size / suffix[0])) + suffix[1]

            d_status = item.status
            d_progress = int((item.progress) / 100 * (screen.w_progress - marker_p)) * screen.progress_char
            d_progress = marker_b + d_progress + (screen.w_progress - len(d_progress) - marker_p) * ' ' + marker_e
            d_percent = str("%0.2f" % item.progress) + "%"

            d_sp = str(item.seeds) + "/" + str(item.peers)
            d_sp = re.sub('0/0', '-', d_sp)

            d_speed = str("%0.0f" % item.dl) + "K / " + str("%0.0f" % item.ul) + "K"
            d_speed = re.sub(' / 0K', '', (re.sub('^0K', '-', d_speed)))

            d_eta = item.eta

            row = screen.create_row(
                    (d_name, screen.w_name, 5, 0),
                    (d_size, screen.w_size, 3, 1),
                    (d_status, screen.w_status, 3, 0),
                    (d_progress, screen.w_progress, 1, 0),
                    (d_percent, screen.w_percent, 3, 1),
                    (d_sp, screen.w_sp, 3, 1),
                    (d_speed, screen.w_speed, 3, 1),
                    (d_eta, screen.w_eta, 2, 1)
                    )

            color = screen.status_colors.get(d_status, '<default>')

            if screen.highlight[i + j] != 0:
                color = color.replace('>', '.r>')

            screen.r_string += color + row + color.replace('<', '</') + '\n'
            Download.rows.append({'gid':item.gid, 'index':(-2 if item.num_files > 1 else -1), 'status':item.status, 'selected':[], 'name':item.name})

            if item.num_files > 1 and Download.expanded[item.gid] == True:
                for k in range(item.num_files):
                    if k == item.num_files - 1:
                        tree_char = "  └─ "
                    else:
                        tree_char = "  ├─ "

                    f_selected = item.data['files'][k]['selected']
                    f_name = tree_char + os.path.basename(item.data['files'][k]['path'])

                    f_size = int(item.data['files'][k]['length'])

                    for x in screen.suffixes:
                        if f_size >= x[0]:
                            suffix = x
                            break
                        suffix = x

                    f_size = str("%0.1f" % (f_size / suffix[0])) + suffix[1]

                    if int(item.data['files'][k]['length']) != 0:
                        progress = int(item.data['files'][k]['completedLength']) / int(item.data['files'][k]['length']) * 100
                    else:
                        progress = 0

                    if progress == 100:
                        f_status = 'complete'
                        color = screen.status_colors.get(f_status, '<default>')
                    elif f_selected == 'true':
                        f_status = 'pending'
                    else:
                        f_status = 'skip'

                    if d_status == 'active' or d_status == 'waiting' or d_status == 'complete':
                        color = screen.status_colors.get(f_status, '<default>')
                    color = color.replace('.r', '')

                    f_progress = int((progress / 100) * (screen.w_progress - marker_p)) * screen.progress_char
                    f_progress = marker_b + f_progress + (screen.w_progress - len(f_progress) - marker_p) * ' ' + marker_e
                    f_percent = str("%0.2f" % progress) + "%"

                    f_row = screen.create_row(
                            (f_name, screen.w_name, 5, 0),
                            (f_size, screen.w_size, 3, 1),
                            (f_status, screen.w_status, 3, 0),
                            (f_progress, screen.w_progress, 1, 0),
                            (f_percent, screen.w_percent, 3, 1),
                            )

                    if screen.highlight[i + j + k + 1] != 0:
                        color = color.replace('>', '.r>')

                    screen.r_string += (color + f_row + color.replace('<', '</')) + '\n'

                    Download.rows.append({'gid':item.gid, 'index':k, 'status':item.status, 'selected':[f_selected], 'name':f_name.replace(tree_char, '')})
                    if k + 1 not in Download.rows[i + j]['selected'] and f_selected == 'true':
                        Download.rows[i + j]['selected'].append(k + 1)

                j += item.num_files


def key_actions(screen, key):
    if Download.rows != []:
        item = Download.rows[screen.option]

    def refresh_windows():
        tty_h, tty_w = list(map(int, os.popen('stty size', 'r').read().split()))
        screen.height = tty_h
        screen.width = tty_w
        screen.w_name = screen.width - (screen.w_size + screen.w_status + screen.w_progress +
                screen.w_percent + screen.w_sp + screen.w_speed + screen.w_eta + 1)

        screen.refresh_header()
        screen.refresh_status()

    def confirm():
        screen.win.nodelay(False)
        curses.echo(True)
        cstr.add(screen.height - 1, 0, "<red.b>" + "confirm deletion: (Y/n)" + "</red.b> ", screen.win, True)
        curses.echo(False)
        response = screen.win.getch()
        screen.win.nodelay(True)
        screen.win.refresh()
        return False if response == ord('n') else True

    def nav_up():
        screen.option = (screen.option - 1) % Download.num_rows

    def nav_down():
        screen.option = (screen.option + 1) % Download.num_rows

    def pause_all():
        if len(aria2.tellActive()) == 0:
            aria2.unpauseAll()
        else:
            aria2.pauseAll()

    def pause():
        if item['status'] == 'active' or item['status'] == 'waiting':
            aria2.pause(item['gid'])
        elif item['status'] == 'paused':
            aria2.unpause(item['gid'])

    def add():
        screen.win.nodelay(False)
        curses.echo(True)
        cstr.add(screen.height - 1, 0, "<base3.b>" + "add:" + "</base3.b> ", screen.win, True)
        url = screen.win.getstr(screen.height - 1, 5, 200)
        try:
            aria2.addUri([url.strip()])
        except pyaria2.xmlrpc.client.Fault:
            cstr.add(screen.height - 1, 0, "<red.b>" + "add:</red.b><red> " + url.decode('utf-8') + "</red>", screen.win, True)
            screen.win.refresh()
            time.sleep(1)
        curses.echo(False)
        screen.win.nodelay(True)
        screen.win.refresh()

    def delete():
        if item['status'] != 'complete' and item['status'] != 'removed' and item['status'] != 'error' and confirm() == False:
            return
        if screen.option == Download.num_rows - 1:
            screen.option -= 1
        try:
            aria2.remove(item['gid'])
        except:
            aria2.removeDownloadResult(item['gid'])
        # del Download.expanded[item['gid']]

    def purge():
        aria2.purgeDownloadResult()

    def queue_up():
        if item['status'] == 'waiting':
            aria2.changePosition(item['gid'], -1, 'POS_CUR')
            screen.option -= 1

    def queue_down():
        if item['status'] == 'waiting':
            aria2.changePosition(item['gid'], 1, 'POS_CUR')
            screen.option += 1

    def select():           # bug: doesn't select active downloads's files
        if item['index'] < 0:
            return
        selected = Download.rows[screen.option - item['index'] - 1]['selected']

        if item['index'] + 1 in selected:
            selected.remove(item['index'] + 1)
        else:
            selected.append(item['index'] + 1)

        selection = ','.join(map(str, selected))
        aria2.changeOption(item['gid'], {'select-file': selection})

    def expand():
        if item['index'] == -1:
            return
        if Download.expanded[item['gid']] == True:
            Download.expanded[item['gid']] = False
            screen.option -= (item['index'] + 1) if item['index'] != -2 else 0
        else:
            Download.expanded[item['gid']] = True


    def quit():
        exit()

    def none():
        pass

    actions = {
            curses.KEY_RESIZE:refresh_windows,
            curses.KEY_UP:nav_up,
            keys.up:nav_up,
            curses.KEY_DOWN:nav_down,
            keys.down:nav_down,
            keys.pause_all:pause_all,
            keys.pause:pause,
            keys.add:add,
            keys.delete:delete,
            keys.purge:purge,
            keys.queue_up:queue_up,
            keys.queue_down:queue_down,
            keys.select:select,
            keys.expand:expand,
            keys.quit:quit,
            }

    actions.get(key, none)()


def curse(screen):
    tty_h, tty_w = list(map(int, os.popen('stty size', 'r').read().split()))
    screen = Window(tty_h, tty_w, 0, 0)
    screen.create()

    screen.win.clear()
    cstr.init_colors()
    curses.curs_set(False)

    Download.downloads = get_downloads()

    while True:
        if Download.num_rows == 0:
            Download.num_rows = 1

        screen.draw()

        key_in = screen.win.getch()
        key_actions(screen, key_in)

        if key_in != -1:
            screen.count = screen.refresh_marker
            screen.win.refresh()

        if screen.count == screen.refresh_marker:
            Download.downloads = get_downloads()
            screen.refresh_status()
            screen.count = 0


def exit():
    sys.exit()


def main():
    global aria2, ui, colors, keys, server, port

    config = configparser.ConfigParser()
    config_file = os.path.expanduser("~/.config/narnia/config")

    if not os.path.isfile(config_file):
        import io
        config_file = io.StringIO('[Connection]\n[UI]\n[Colors]\n[Keybindings]')
        config.readfp(config_file)
    else:
        config.read(config_file)

    server = config['Connection'].get('server', 'localhost')
    port = config['Connection'].getint('port', 6800)

    parser = argparse.ArgumentParser(description='A curses-based console client for aria2')
    parser.add_argument('-s','--server', help='Server to connect to', default=server)
    parser.add_argument('-p','--port', help='Port to connect through', default=port)
    parser.add_argument('file', nargs='*')

    args = parser.parse_args()
    server = args.server
    port = args.port
    aria2 = pyaria2.PyAria2(server, port, None)

    if args.file != []:
        for i_file in args.file:
            aria2.addUri([i_file])
        sys.exit()

    ui = config['UI']
    colors = config['Colors']
    keys = Keybindings(config['Keybindings'])

    try:
        curses.wrapper(curse)
    except gaierror:
        print("Invalid server:", server)
    except ConnectionRefusedError:
        print("Connection refused.\nMake sure aria2 is running or authorized on", server + ":" + str(port))


main()
