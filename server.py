#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import select
import netifaces as ni
import psutil
import os

# 読み取りが可能になるまで待っているソケットと、可能になったときに呼び出されるハンドラ・引数の対応を持つ
read_waiters = {}
# 書き込みが可能になるまで待っているソケットと、可能になったときに呼び出されるハンドラ・引数の対応を持つ
write_waiters = {}
# 接続してきたクライアントとの接続情報を格納する
connections = {}

recv_message = ''
recv_flg = 0
connect_flg = 0

def get_ip():
    result = []
    address_list = psutil.net_if_addrs()
    for nic in address_list.keys():
        ni.ifaddresses(nic)
        try:
            ip = ni.ifaddresses(nic)[ni.AF_INET][0]['addr']
            if ip not in ["127.0.0.1"]:
                #result.append(ip)
                return ip
        except KeyError as err:
            pass
    return result

def accept_handler(serversocket):
    global fileno
    global connect_flg

    """サーバソケットが読み取り可能になったとき呼ばれるハンドラ"""
    # 準備ができているので、すぐに accept() できる
    clientsocket, (client_address, client_port) = serversocket.accept()

    # クライアントソケットもノンブロックモードにする
    clientsocket.setblocking(False)

    # 接続してきたクライアントの情報を出力する
    # ただし、厳密に言えば print() もブロッキング I/O なので避けるべき
    print('New client: {0}:{1}'.format(client_address, client_port))

    # ひとまずクライアントの一覧に入れておく
    connections[clientsocket.fileno()] = (clientsocket,
                                          client_address,
                                          client_port)

    # 次はクライアントのソケットが読み取り可能になるまで待つ
    read_waiters[clientsocket.fileno()] = (recv_handler,
                                           (clientsocket.fileno(), ))

    # 次のクライアントからの接続を待ち受ける
    read_waiters[serversocket.fileno()] = (accept_handler, (serversocket, ))

    fileno = clientsocket.fileno()
    connect_flg = 1

def recv_handler(fileno):
    global recv_message
    global recv_flg
    global connect_flg
    global serversocket

    """クライアントソケットが読み取り可能になったとき呼ばれるハンドラ"""
    def terminate():
        """クライアントとの接続が切れたときの後始末"""
        # クライアント一覧から取り除く
        del connections[clientsocket.fileno()]
#        del read_waiters[clientsocket.fileno()]
#        del write_waiters[clientsocket.fileno()]
        # ソケットを閉じる
        clientsocket.close()
        connect_flg = 0
        print('Bye-Bye: {0}:{1}'.format(client_address, client_port))

        serversocket.shutdown(1)
        serversocket.close()
        #print "Closed"
        print('CONNECT FLG TER: {0}'.format(connect_flg))
        read_waiters = {}
        write_waiters = {}
        #connections = {}
        server_init()
        #print   "Reopen"

    # クライアントとの接続情報を取り出す
    clientsocket, client_address, client_port = connections[fileno]

    try:
        # 準備ができているので、すぐに recv() できる
        message = clientsocket.recv(1024)
    except OSError:
        terminate()
        connect_flg = 0
        print('CONNECT FLG: {0}'.format(connect_flg))
        return

    if len(message) == 0:
        terminate()
        connect_flg = 0
        print('CONNECT FLG REC: {0}'.format(connect_flg))
        return

    #print('Recv: {0} to {1}:{2}'.format(message,
    #                                    client_address,
    #                                    client_port))
    recv_message = message
    recv_flg = 1
    recv_fileno = clientsocket.fileno()


def send_handler(fileno, message):
    """クライアントソケットが書き込み可能になったとき呼ばれるハンドラ"""
    # クライアントとの接続情報を取り出す
    clientsocket, client_address, client_port = connections[fileno]

    # 準備ができているので、すぐに　send() できる
    sent_len = clientsocket.send(message)
    #print('Send: {0} to {1}:{2}'.format(message[:sent_len],
    #                                    client_address,
    #                                    client_port))

def server_init():
    global serversocket

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ソケットをノンブロックモードにする
    serversocket.setblocking(False)

    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    #host = socket.gethostbyname(socket.gethostname())
    #print(host)
    #host = '192.168.1.204'
    host = get_ip()
    port = 10000
    serversocket.bind((host, port))
    #serversocket.bind(('192.168.1.201', 10000))

    serversocket.listen(128)

    # クライアントからの接続がくるまで待つ
    read_waiters[serversocket.fileno()] = (accept_handler, (serversocket, ))

def server_loop():

    #print   read_waiters
    #print   write_waiters
    #print   connect_flg
    rlist, wlist, _ = select.select(read_waiters.keys(),
                                    write_waiters.keys(),
                                    [],
                                    0)
    #print   rlist
    #print   wlist
    # 読み取り可能になったソケット (のファイル番号) の一覧
    for r_fileno in rlist:
        # 読み取り可能になったときに呼んでほしいハンドラを取り出す
        handler, args = read_waiters.pop(r_fileno)
        # ハンドラを実行する
        handler(*args)

    # 書き込み可能になったソケット (のファイル番号の一覧)
    for w_fileno in wlist:
        # 書き込み可能になったときに呼んでほしいハンドラを取り出す
        handler, args = write_waiters.pop(w_fileno)
        # ハンドラを実行する
        handler(*args)

def server_recv():
    global recv_message
    global recv_flg
    global fileno
    global connect_flg

    if connect_flg == 0:
        return  ''
    if recv_flg == 1:
        recv_flg = 0
        #read_waiters[recv_fileno] = (recv_handler,(recv_fileno, ))
        read_waiters[fileno] = (recv_handler,(fileno, ))
        #print recv_message
        return  recv_message
    else:
        return  ''

def server_send(mes):
    global fileno
    global connect_flg

    if connect_flg == 0:
        return
    write_waiters[fileno] = (send_handler, (fileno, mes))
