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

Description: pyaria2 is a Python 3 module that provides a wrapper class around Aria2's RPC interface. It can be used to build applications that use Aria2 for downloading data.
Author: Killua
Email: killua_hzl@163.com
'''

#!/bin/python

import subprocess
import xmlrpc.client
import os
import time

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6800
SERVER_URI_FORMAT = 'http://{}:{:d}/rpc'

class PyAria2(object):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, session=None):
        '''
        PyAria2 constructor.

        host: string, aria2 rpc host, default is 'localhost'
        port: integer, aria2 rpc port, default is 6800
        session: string, aria2 rpc session saving.
        '''

        server_uri = SERVER_URI_FORMAT.format(host, port)
        self.server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)

    def addUri(self, secret, uris, options=None, position=None):
        '''
        This method adds new HTTP(S)/FTP/BitTorrent Magnet URI.

        uris: list, list of URIs
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns GID of registered download.
        '''
        return self.server.aria2.addUri(secret, uris, options, position)

    def addTorrent(self, secret, torrent, uris=None, options=None, position=None):
        '''
        This method adds BitTorrent download by uploading ".torrent" file.

        torrent: string, torrent file path
        uris: list, list of webseed URIs
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns GID of registered download.
        '''
        return self.server.aria2.addTorrent(secret, xmlrpc.client.Binary(open(torrent, 'rb').read()), uris, options, position)

    def addMetalink(self, secret, metalink, options=None, position=None):
        '''
        This method adds Metalink download by uploading ".metalink" file.

        metalink: string, metalink file path
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns list of GID of registered download.
        '''
        return self.server.aria2.addMetalink(secret, xmlrpc.client.Binary(open(metalink, 'rb').read()), options, position)

    def remove(self, secret, gid):
        '''
        This method removes the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of removed download.
        '''
        return self.server.aria2.remove(secret, gid)

    def forceRemove(self, secret, gid):
        '''
        This method removes the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of removed download.
        '''
        return self.server.aria2.forceRemove(secret, gid)

    def pause(self, secret, gid):
        '''
        This method pauses the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of paused download.
        '''
        return self.server.aria2.pause(secret, gid)

    def pauseAll(self, secret):
        '''
        This method is equal to calling aria2.pause() for every active/waiting download.

        return: This method returns OK for success.
        '''
        return self.server.aria2.pauseAll(secret)

    def forcePause(self, secret, gid):
        '''
        This method pauses the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of paused download.
        '''
        return self.server.aria2.forcePause(secret, gid)

    def forcePauseAll(self, secret):
        '''
        This method is equal to calling aria2.forcePause() for every active/waiting download.

        return: This method returns OK for success.
        '''
        return self.server.aria2.forcePauseAll(secret)

    def unpause(self, secret, gid):
        '''
        This method changes the status of the download denoted by gid from paused to waiting.

        gid: string, GID.

        return: This method returns GID of unpaused download.
        '''
        return self.server.aria2.unpause(secret, gid)

    def unpauseAll(self, secret):
        '''
        This method is equal to calling aria2.unpause() for every active/waiting download.

        return: This method returns OK for success.
        '''
        return self.server.aria2.unpauseAll(secret)

    def tellStatus(self, secret, gid, keys=None):
        '''
        This method returns download progress of the download denoted by gid.

        gid: string, GID.
        keys: list, keys for method response.

        return: The method response is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellStatus(secret, gid, keys)

    def getUris(self, secret, gid):
        '''
        This method returns URIs used in the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getUris(secret, gid)

    def getFiles(self, secret, gid):
        '''
        This method returns file list of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getFiles(secret, gid)

    def getPeers(self, secret, gid):
        '''
        This method returns peer list of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getPeers(secret, gid)

    def getServers(self, secret, gid):
        '''
        This method returns currently connected HTTP(S)/FTP servers of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getServers(secret, gid)

    def tellActive(self, secret, keys=None):
        '''
        This method returns the list of active downloads.

        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellActive(secret, keys)

    def tellWaiting(self, secret, offset, num, keys=None):
        '''
        This method returns the list of waiting download, including paused downloads.

        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellWaiting(secret, offset, num, keys)

    def tellStopped(self, secret, offset, num, keys=None):
        '''
        This method returns the list of stopped download.

        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellStopped(secret, offset, num, keys)

    def changePosition(self, secret, gid, pos, how):
        '''
        This method changes the position of the download denoted by gid.

        gid: string, GID.
        pos: integer, the position relative which to be changed.
        how: string.
             POS_SET, it moves the download to a position relative to the beginning of the queue.
             POS_CUR, it moves the download to a position relative to the current position.
             POS_END, it moves the download to a position relative to the end of the queue.

        return: The response is of type integer and it is the destination position.
        '''
        return self.server.aria2.changePosition(secret, gid, pos, how)

    def changeUri(self, secret, gid, fileIndex, delUris, addUris, position=None):
        '''
        This method removes URIs in delUris from and appends URIs in addUris to download denoted by gid.

        gid: string, GID.
        fileIndex: integer, file to affect (1-based)
        delUris: list, URIs to be removed
        addUris: list, URIs to be added
        position: integer, where URIs are inserted, after URIs have been removed

        return: This method returns a list which contains 2 integers. The first integer is the number of URIs deleted. The second integer is the number of URIs added.
        '''
        return self.server.aria2.changeUri(secret, gid, fileIndex, delUris, addUris, position)

    def getOption(self, secret, gid):
        '''
        This method returns options of the download denoted by gid.

        gid: string, GID.

        return: The response is of type dict.
        '''
        return self.server.aria2.getOption(secret, gid)

    def changeOption(self, secret, gid, options):
        '''
        This method changes options of the download denoted by gid dynamically.

        gid: string, GID.
        options: dict, the options.

        return: This method returns OK for success.
        '''
        return self.server.aria2.changeOption(secret, gid, options)

    def getGlobalOption(self, secret):
        '''
        This method returns global options.

        return: The method response is of type dict.
        '''
        return self.server.aria2.getGlobalOption(secret)

    def changeGlobalOption(self, secret, options):
        '''
        This method changes global options dynamically.

        options: dict, the options.

        return: This method returns OK for success.
        '''
        return self.server.aria2.changeGlobalOption(secret, options)

    def getGlobalStat(self, secret):
        '''
        This method returns global statistics such as overall download and upload speed.

        return: The method response is of type struct and contains following keys.
        '''
        return self.server.aria2.getGlobalStat(secret)

    def purgeDownloadResult(self, secret):
        '''
        This method purges completed/error/removed downloads to free memory.

        return: This method returns OK for success.
        '''
        return self.server.aria2.purgeDownloadResult(secret)

    def removeDownloadResult(self, secret, gid):
        '''
        This method removes completed/error/removed download denoted by gid from memory.

        return: This method returns OK for success.
        '''
        return self.server.aria2.removeDownloadResult(secret, gid)

    def getVersion(self, secret):
        '''
        This method returns version of the program and the list of enabled features.

        return: The method response is of type dict and contains following keys.
        '''
        return self.server.aria2.getVersion(secret)

    def getSessionInfo(self, secret):
        '''
        This method returns session information.

        return: The response is of type dict.
        '''
        return self.server.aria2.getSessionInfo(secret)

    def shutdown(self, secret):
        '''
        This method shutdowns aria2.

        return: This method returns OK for success.
        '''
        return self.server.aria2.shutdown(secret)

    def forceShutdown(self, secret):
        '''
        This method shutdowns aria2.

        return: This method returns OK for success.
        '''
        return self.server.aria2.forceShutdown(secret)
