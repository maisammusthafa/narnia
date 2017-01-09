#!/bin/env python3

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

import xmlrpc.client


class PyAria2(object):
    def __init__(self, host, port, session=None):
        server_uri = 'http://{}:{:d}/rpc'.format(host, port)
        self.server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)

    def addUri(self, token, uris, options=None, position=None):
        return self.server.aria2.addUri(token, uris, options, position)

    def addTorrent(self, token, torrent, uris=None, options=None, position=None):
        return self.server.aria2.addTorrent(token, xmlrpc.client.Binary(open(torrent, 'rb').read()), uris, options, position)

    def addMetalink(self, token, metalink, options=None, position=None):
        return self.server.aria2.addMetalink(token, xmlrpc.client.Binary(open(metalink, 'rb').read()), options, position)

    def remove(self, token, gid):
        return self.server.aria2.remove(token, gid)

    def forceRemove(self, token, gid):
        return self.server.aria2.forceRemove(token, gid)

    def pause(self, token, gid):
        return self.server.aria2.pause(token, gid)

    def pauseAll(self, token):
        return self.server.aria2.pauseAll(token)

    def forcePause(self, token, gid):
        return self.server.aria2.forcePause(token, gid)

    def forcePauseAll(self, token):
        return self.server.aria2.forcePauseAll(token)

    def unpause(self, token, gid):
        return self.server.aria2.unpause(token, gid)

    def unpauseAll(self, token):
        return self.server.aria2.unpauseAll(token)

    def tellStatus(self, token, gid, keys=None):
        return self.server.aria2.tellStatus(token, gid, keys)

    def getUris(self, token, gid):
        return self.server.aria2.getUris(token, gid)

    def getFiles(self, token, gid):
        return self.server.aria2.getFiles(token, gid)

    def getPeers(self, token, gid):
        return self.server.aria2.getPeers(token, gid)

    def getServers(self, token, gid):
        return self.server.aria2.getServers(token, gid)

    def tellActive(self, token, keys=None):
        return self.server.aria2.tellActive(token, keys)

    def tellWaiting(self, token, offset, num, keys=None):
        return self.server.aria2.tellWaiting(token, offset, num, keys)

    def tellStopped(self, token, offset, num, keys=None):
        return self.server.aria2.tellStopped(token, offset, num, keys)

    def changePosition(self, token, gid, pos, how):
        return self.server.aria2.changePosition(token, gid, pos, how)

    def changeUri(self, token, gid, fileIndex, delUris, addUris, position=None):
        return self.server.aria2.changeUri(token, gid, fileIndex, delUris, addUris, position)

    def getOption(self, token, gid):
        return self.server.aria2.getOption(token, gid)

    def changeOption(self, token, gid, options):
        return self.server.aria2.changeOption(token, gid, options)

    def getGlobalOption(self, token):
        return self.server.aria2.getGlobalOption(token)

    def changeGlobalOption(self, token, options):
        return self.server.aria2.changeGlobalOption(token, options)

    def getGlobalStat(self, token):
        return self.server.aria2.getGlobalStat(token)

    def purgeDownloadResult(self, token):
        return self.server.aria2.purgeDownloadResult(token)

    def removeDownloadResult(self, token, gid):
        return self.server.aria2.removeDownloadResult(token, gid)

    def getVersion(self, token):
        return self.server.aria2.getVersion(token)

    def getSessionInfo(self, token):
        return self.server.aria2.getSessionInfo(token)

    def shutdown(self, token):
        return self.server.aria2.shutdown(token)

    def forceShutdown(self, token):
        return self.server.aria2.forceShutdown(token)
