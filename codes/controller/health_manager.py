import sys
import requests
import json
import threading
# TODO: add dynamical ability of add/remove servers through APIs.
# import flask
import argparse
import time
import re
import signal

# TODO: logging...

stop_checking = False

# TDOO: abstract Checker class for multiple checker types
class HttpGet:
    
    @staticmethod
    def alives(servers):
        lock = threading.Lock()
        alvs = []
        thrs = []

        def check(srvr):
            try:
                # print("checking %s" % srvr)
                resp = requests.get('http://%s' % srvr, timeout=2)
                if resp.status_code == 200:
                    lock.acquire()
                    alvs.append(srvr)
                    lock.release()
            except Exception as e:
                # print(e)
                pass
        
        for s in servers:
            tn = threading.Thread(target=check, args=(s,))
            thrs.append(tn)
            tn.start()

        for tn in thrs:
            tn.join()
        
        return sorted(alvs)

def update_nginx_upstream(nginx_hosts, endpoint, upstream_zone, alive_servers):
    original_upstreams = {}
    for ngx_host in nginx_hosts: 
        # TODO asynchronizingly/parallelly handle nginx_hosts
        # TODO handle exception of requests.get
        resp = requests.get(url='http://%s/%s?upstream=%s' % (ngx_host, endpoint, upstream_zone))

        orig_servers = []
        for line in resp.text.split('\n'):
            # TODO: matching upstream servers as well as upstream parameters.
            matched = re.match(r'server ((\d{1,3}\.){3}\d{1,3}\:\d{1,8}).*', line)
            if matched:
                orig_servers.append(matched.group(1))
        
        print("original servers: %s" % orig_servers)

        if set(orig_servers) == set(alive_servers):
            print("nope operations to upstream setting.")

        if len(set(orig_servers) - set(alive_servers)) != 0:
            remove_servers = set(orig_servers) - set(alive_servers)
            print("removing servers %s .." % remove_servers)
            for rm_srvr in remove_servers:
                # TODO: handle exception of requests.get
                resp = requests.get(url='http://%s/%s?upstream=%s&remove=&server=%s' % (ngx_host, endpoint, upstream_zone, rm_srvr))
                # TODO: handle reversing if fails to update upstream.
                # TODO: use up=/down= instead of add=/remove=
        
        if len(set(alive_servers) - set(orig_servers)) != 0:
            add_servers = set(alive_servers) - set(orig_servers)
            print("adding servers %s .." % add_servers)
            for add_srvr in add_servers:
                # TODO: handle exception of requests.get
                resp = requests.get(url='http://%s/%s?upstream=%s&add=&server=%s' % (ngx_host, endpoint, upstream_zone, add_srvr))
                # TODO: handle reversing if fails to update upstream.
                # TODO: use up=/down= instead of add=/remove=

def check_and_update_upstream(server_hosts, nginx_hosts, endpoint, upstream_zone):
    global stop_checking
    while not stop_checking:
        alive_servers = HttpGet.alives(server_hosts)
        print("alive_servers: %s" % alive_servers)
        update_nginx_upstream(nginx_hosts, endpoint, upstream_zone, alive_servers)
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file", default='./health_manager.json')
    args = parser.parse_args()
    print(args)

    # TODO: configuration file checking: existence, format validation.
    conf = None
    with open(args.config, 'r') as fr:
        conf = json.load(fr)
    
    def signal_handler(signum, h):
        global stop_checking
        print("signal received.")
        stop_checking = True

    signal.signal(signal.SIGINT, signal_handler)
    check_and_update_upstream(
        conf['upstream_servers'].keys(), 
        conf['nginx_cluster']['nginx_hosts'], 
        conf['nginx_cluster']['dyups_endpoint'],
        conf['nginx_cluster']['upstream_zone']
    )
