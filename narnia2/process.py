#!/bin/env python3
""" handles all threads and queues """

import threading
import time
import queue

from narnia2.common import Config as c, Globals as g
from narnia2.download import Download

# TODO: handle thread errors


def request_data():
    active = c.aria2.tell_active()
    waiting = c.aria2.tell_waiting(0, 100)
    stopped = c.aria2.tell_stopped(-1, 100)

    g.status.refresh_data()
    g.download_states = [active, waiting, stopped]


def consume_queue():
    while True:
        g.queue.get()()
        g.queue.task_done()


def queue_data():
    while True:
        if g.queue.queue.count(request_data) < 2:
            g.queue.put(request_data)
        time.sleep(1)


def queue_priority_data():
    if request_data not in g.queue.queue:
        g.queue.put(request_data)


def queue_action(item):
    g.queue.put(item)


def thread_priority_data():
    threading.Thread(target=queue_priority_data, daemon=True).start()


def thread_action(action):
    threading.Thread(target=queue_action, args=(action,), daemon=True).start()


def start_threads():
    g.queue = queue.Queue(maxsize=10)
    threading.Thread(target=consume_queue, daemon=True).start()
    threading.Thread(target=queue_data, daemon=True).start()
