#!/usr/bin/env python
#ecoding:utf-8


import socket
import json




def Run_Socket_Client(data, conn_host):
        addr = (conn_host, 8082)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(addr)
        client.send(json.dumps(data))
        return client.recv(1024)

