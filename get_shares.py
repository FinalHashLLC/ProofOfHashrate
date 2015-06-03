#!/usr/bin/env python
# Send notification to Stratum mining instance on localhost that there's new bitcoin block
# You can use this script directly as an variable for -blocknotify argument:
#       ./litecoind -blocknotify="blocknotify.sh --password admin_password"
# This is also very basic example how to use Stratum protocol in native Python

import datetime
import socket
import json
import sys
import argparse
import time
import math

def convert_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

host = '127.0.0.1'
port = 3333

message = {'id': 1, 'method': 'mining.get_shares', 'params': ['NZhBDowFnhMA1VYj4yfyzujDqhqtPqKZ8Z']}

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps(message)+"\n")
    data = s.recv(2147483647)
    s.close()
except IOError:
    print "blocknotify: Cannot connect to the pool"
    sys.exit()

print("Your Miner Solved The Following Shares")
for line in data.split("\n"):
    if not line.strip():
        continue

    output = json.loads(line)
    result = output['result']
    total_diff = 0
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = convert_to_datetime(0)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

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
        share['time'] = convert_to_datetime(share['time']).strftime('%Y-%m-%d %H:%M:%S')
        print("At {time} You found a {coin} share with a difficulty of {difficulty} which {valid_share} a valid share and {valid_block} a valid block. It resulted in a hash of {share_hash}.".format(**share))

    interval = (end_time - start_time).total_seconds()
    hashrate = (total_diff * math.pow(2,32)) / interval / 1000000000000
    print("Your Avg Hashrate from %s to %s was %f TH/s" % (start_time, end_time, hashrate))
