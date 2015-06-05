#!/usr/bin/env python

import datetime
import socket
import json
import sys
import argparse
import time
import math

def convert_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def check_shares(data):
    print("Your Miner Solved The Following Shares")
    total_shares = 0
    total_diff = 0
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = convert_to_datetime(0)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    for line in data.split("\n"):
        if not line.strip():
          continue

        output = json.loads(line)
        result = output['result']
        for share in result:
            share = json.loads(share)
            share['valid_share'] = "was" if share['valid_share'] == 'Y' else "wasn't"
            share['valid_block'] = "was" if share['valid_block'] == 'Y' else "wasn't"

            # Hashrate Stats
            if convert_to_datetime(share['time']) < start_time:
               start_time = convert_to_datetime(share['time'])
               start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

            if convert_to_datetime(share['time']) > end_time:
               end_time = convert_to_datetime(share['time'])
               end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

            total_diff += share['difficulty']
            total_shares += 1
            share['time'] = convert_to_datetime(share['time']).strftime('%Y-%m-%d %H:%M:%S')
            print("At {time} You found a {coin} share with a difficulty of {difficulty} which {valid_share} a valid share and {valid_block} a valid block. It resulted in a hash of {share_hash}.".format(**share))

    interval = (end_time - start_time).total_seconds()
    hashrate = (total_diff * math.pow(2,16)) / interval / 1000000
    #hashrate = (total_diff * math.pow(2,32)) / interval / 1000000000000
    print("Of %i Shares sent. Your Avg Hashrate from %s to %s was %f MH/s" % (total_shares, start_time, end_time, hashrate))
    #print("Of %i Shares sent. Your Avg Hashrate from %s to %s was %f TH/s" % (total_shares, start_time, end_time, hashrate))

def recv_timeout(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)

    #total data partwise in an array
    total_data=[];
    data='';

    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break

        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break

        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    #join all parts to make final string
    return ''.join(total_data)

host = '127.0.0.1'
port = 3109

#message = {'id': 1, 'method': 'mining.get_shares', 'params': ['NZhBDowFnhMA1VYj4yfyzujDqhqtPqKZ8Z']}
message = {'id': 1, 'method': 'mining.get_shares', 'params': ['bigvern.1', time.time()-86400, time.time()]}

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps(message)+"\n")
    data = recv_timeout(s)
    check_shares(data)
    s.close()
except IOError:
    print "blocknotify: Cannot connect to the pool"
    sys.exit()

