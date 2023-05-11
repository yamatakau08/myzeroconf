#!/usr/bin/env python3

# https://github.com/python-zeroconf/python-zeroconf/blob/master/examples/browser.py

""" Example of browsing for a service.

The default is HTTP and HAP; use --find to search for all available services in the network
"""

import argparse
import logging
from time import sleep
from typing import cast

import json
import urllib.request

import pprint

from zeroconf import (
    IPVersion,
    ServiceBrowser,
    ServiceStateChange,
    Zeroconf,
    ZeroconfServiceTypes,
)


ipaddress = None

def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    #print(f"Service {name} of type {service_type} state changed: {state_change}")

    cpath = None

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)

        infoipaddress = info.parsed_scoped_addresses()[0]
        if ipaddress == None:
            pass
        else:
            if ipaddress != infoipaddress:
                return

        print(f"Service {name} of type {service_type} state changed: {state_change}")
        print("Info from zeroconf.get_service_info: %r" % (info))

        if info:
            addresses = ["%s:%d" % (addr, cast(int, info.port)) for addr in info.parsed_scoped_addresses()]
            print("  Addresses: %s" % ", ".join(addresses))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print(f"  Server: {info.server}")
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print(f"    {key}: {value}")
                    if key == b'CPath':
                        cpath = value.decode('utf-8')
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')

        if service_type == "_spotify-connect._tcp.local.":
            print("###############################################")
            url = "http://" + addresses[0] + cpath + "?action=getInfo"
            print(url)
            r = None
            with urllib.request.urlopen(url) as f:
                r = json.loads(f.read().decode('utf-8'))
                #print(r)
                #print(type(r))
                #print('\n')
            print(r)
            print('\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    #parser.add_argument('--find', action='store_true',help='Browse all available services')
    parser.add_argument('--browse', nargs='*',help='Browse all available services')
    parser.add_argument('--list', action='store_true',help='list available services')
    parser.add_argument('--ip', help='Browse available services specified ip address')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only

    zeroconf = Zeroconf(ip_version=ip_version)

    if args.ip:
        ipaddress = args.ip

    if args.list:
        print("available services")
        services = list(ZeroconfServiceTypes.find(zc=zeroconf))
        sleep(2)
        pprint.pprint(services)
        exit()

    if args.browse == []:
        services = list(ZeroconfServiceTypes.find(zc=zeroconf))
    else:
        services = args.browse

    print("")
    print("Browsing services")
    pprint.pprint(services)
    print("press Ctrl-C to exit...")
    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
