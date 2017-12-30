#!/bin/env python3
""" provides wrapper class for aria2 rpc """

import time
import xmlrpc.client

'''The MIT License (MIT)

Copyright (c) 2014 Killua

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Description: pyaria2 is a Python 3 module that provides a wrapper class around
Aria2's RPC interface. It can be used to build applications that use Aria2 for
downloading data.
Author: Killua
Email: killua_hzl@163.com
'''

wait_time = 0.0


class PyAria2(object):
    def __init__(self, host, port, token=''):
        server_uri = '{}:{:d}/rpc'.format(host, port)
        self.server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)
        self.token = 'token:{}'.format(token)

    def add_uri(self, uris, options=None, position=None):
        time.sleep(wait_time)
        return self.server.aria2.addUri(self.token, uris, options, position)

    def add_torrent(self, torrent, uris=None, options=None, position=None):
        time.sleep(wait_time)
        return self.server.aria2.addTorrent(self.token, xmlrpc.client.Binary(open(torrent, 'rb').read()), uris, options, position)

    def add_metalink(self, metalink, options=None, position=None):
        time.sleep(wait_time)
        return self.server.aria2.addMetalink(self.token, xmlrpc.client.Binary(open(metalink, 'rb').read()), options, position)

    def remove(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.remove(self.token, gid)

    def force_remove(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.forceRemove(self.token, gid)

    def pause(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.pause(self.token, gid)

    def pause_all(self):
        time.sleep(wait_time)
        return self.server.aria2.pauseAll(self.token)

    def force_pause(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.forcePause(self.token, gid)

    def force_pause_all(self):
        time.sleep(wait_time)
        return self.server.aria2.forcePauseAll(self.token)

    def unpause(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.unpause(self.token, gid)

    def unpause_all(self):
        time.sleep(wait_time)
        return self.server.aria2.unpauseAll(self.token)

    def tell_status(self, gid, keys=None):
        time.sleep(wait_time)
        return self.server.aria2.tellStatus(self.token, gid, keys)

    def get_uris(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.getUris(self.token, gid)

    def get_files(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.getFiles(self.token, gid)

    def get_peers(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.getPeers(self.token, gid)

    def get_servers(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.getServers(self.token, gid)

    def tell_active(self, keys=None):
        time.sleep(wait_time)
        return self.server.aria2.tellActive(self.token, keys)

    def tell_waiting(self, offset, num, keys=None):
        time.sleep(wait_time)
        return self.server.aria2.tellWaiting(self.token, offset, num, keys)

    def tell_stopped(self, offset, num, keys=None):
        time.sleep(wait_time)
        return self.server.aria2.tellStopped(self.token, offset, num, keys)

    def change_position(self, gid, pos, how):
        time.sleep(wait_time)
        return self.server.aria2.changePosition(self.token, gid, pos, how)

    def change_uri(self, gid, fileIndex, delUris, addUris, position=None):
        time.sleep(wait_time)
        return self.server.aria2.changeUri(self.token, gid, fileIndex, delUris, addUris, position)

    def get_option(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.getOption(self.token, gid)

    def change_option(self, gid, options):
        time.sleep(wait_time)
        return self.server.aria2.changeOption(self.token, gid, options)

    def get_global_option(self):
        time.sleep(wait_time)
        return self.server.aria2.getGlobalOption(self.token)

    def change_global_option(self, options):
        time.sleep(wait_time)
        return self.server.aria2.changeGlobalOption(self.token, options)

    def get_global_stat(self):
        time.sleep(wait_time)
        return self.server.aria2.getGlobalStat(self.token)

    def purge_download_result(self):
        time.sleep(wait_time)
        return self.server.aria2.purgeDownloadResult(self.token)

    def remove_download_result(self, gid):
        time.sleep(wait_time)
        return self.server.aria2.removeDownloadResult(self.token, gid)

    def get_version(self):
        time.sleep(wait_time)
        return self.server.aria2.getVersion(self.token)

    def get_session_info(self):
        time.sleep(wait_time)
        return self.server.aria2.getSessionInfo(self.token)

    def shutdown(self):
        time.sleep(wait_time)
        return self.server.aria2.shutdown(self.token)

    def force_shutdown(self):
        time.sleep(wait_time)
        return self.server.aria2.forceShutdown(self.token)
