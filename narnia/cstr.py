#!/bin/env python3
import curses

def get_style(tag):
    global colors
    color = tag.split('.')[0]
    highlight = 0

    try:
        attribs = tag.split('.')[1]
        if 'b' in attribs:
            highlight |= curses.A_BOLD
        if 'r' in attribs:
            highlight |= curses.A_REVERSE
        if 'u' in attribs:
            highlight |= curses.A_UNDERLINE
    except:
        pass

    try:
        return curses.color_pair(colors[color]) | highlight
    except:
        return 0


def add(y_start, x_start, color_str, in_screen, make_newlines_br):
    curr_color = get_style('default')

    x = x_start
    y = y_start
    remaining_str = color_str.replace('\n', '')
    if make_newlines_br:
        remaining_str = color_str.replace('\n', '<br>')

    while len(remaining_str) > 0:
        pos = remaining_str.find('<')
        if pos >= 0:
            part_str = remaining_str[:pos]
            in_screen.addstr(y, x, part_str, curr_color)
            remaining_str = remaining_str[pos+1:]
            x = x + pos

            pos_end = remaining_str.find('>')
            if pos_end >= 0:
                tag_str = remaining_str[:pos_end]
                curr_color = get_style(tag_str)
                remaining_str = remaining_str[pos_end+1:]
                if tag_str == 'br' or tag_str == 'p':
                    y = y+1
                    x = x_start
        else:
            in_screen.addstr(y, x, remaining_str, curr_color)
            remaining_str = ''
            return y - y_start + 1


def init_colors():
    global colors
    curses.start_color()
    curses.use_default_colors()

    for i in range(16):
        curses.init_pair(i, i, -1)

    curses.init_pair(100, 0, 6)
    curses.init_pair(101, 11, 0)

    colors = {
              'red': 1,
              'green': 2,
              'yellow': 3,
              'blue': 4,
              'magenta': 5,
              'cyan': 6,
              'orange': 9,
              'violet': 13,
              'base0': 12,
              'base00': 11,
              'base1': 14,
              'base01': 10,
              'base2': 7,
              'base3': 15,
              'base03': 8,
              'default': 12,
              'br': 12,
              'header': 100,
              'status': 101
             }

