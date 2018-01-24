#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jiavan'

import os
import json
import logging
import socketserver
import threading
import time
import socket
import hashlib
import struct

def get_table(key):
    m = hashlib.md5()
    m.update(key.encode('utf-8'))
    s = m.digest()

    (a, b) = struct.unpack('<QQ', s)
    table = [c for c in bytes.maketrans(b'', b'')]

    # TODO: encrypt
    table = [str(a % (b % (c + 1) + 1)) for c in table]

    return table

def lock_print(msg):
    my_lock.acquire()
    try:
        print('[%s]%s' % (time.ctime, msg))
    finally:
        my_lock.release()

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Socks5Server(socketserver.StreamRequestHandler):
    def encrypt(self, data):
        return data.translate(encrypt_table)

    def decrypt(self, data):
        return data.translate(decrypt_table)

    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            counter = 0

            while True:
                r, w, e = select.select(fdset, [], [])

                if sock in r:
                    r_data = sock.recv(4096)

                    if counter == 1:
                        try:
                            lock_print('Connecting ' + r_data[5: 5 + ord(r_data[4])])
                        except Exception:
                            pass
                    
                    if counter < 2:
                        counter += 1
                    if retmote.send(self.encrypt(r_data)) <= 0:
                        break
                
                if remote in r:
                    remote_data = self.decrypt(remote.recv(4096))
                    if sock.send(remote_data) <= 0:
                        break
        finally:
            sock.close()
            remote.close()

    def handle(self):
        try:
            sock = self.connection()
            remote = socket.socket()
            remote.connect((SERVER, REMOTE_PORT))

            self.handle_tcp(sock, remote)
        except Exception as e:
            lock_print(e.message)
            remote.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__) or '.')
    print('lightproxy v0.0.1')

    with open('config.json', 'rb') as f:
        config = json.load(f)
    
    SERVER = config['server']
    REMOTE_PORT = config['server_port']
    PORT = config['local_port']
    KEY = config['password']

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    encrypt_table = ''.join(get_table(KEY))
    decrypt_table = str.maketrans(encrypt_table, encrypt_table)
    my_lock = threading.Lock()

    print('Starting proxy at port %d' % PORT)
    server = ThreadingTCPServer(('127.0.0.1', PORT), Socks5Server)
    server.serve_forever()