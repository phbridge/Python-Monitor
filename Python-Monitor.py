# Title
# Python Monitor
#
# Language
# Python 3.5
#
# Description
# This script will poll various end points from wherever it is running and return the putput ready for Prometheus to
# import it. This is designed to be an easy replacement for the amazing SmokePing as I was getting fed up of having
# multiple dashboards.
#
# Contacts
# Phil Bridges - phbridge@cisco.com
#
# EULA
# This software is provided as is and with zero support level. Support can be purchased by providing Phil bridges
# with a variety of Beer, Wine, Steak and Greggs pasties. Please contact phbridge@cisco.com for support costs and
# arrangements. Until provision of alcohol or baked goodies your on your own but there is no rocket science
# involved so dont panic too much. To accept this EULA you must include the correct flag when running the script.
# If this script goes crazy wrong and breaks everything then your also on your own and Phil will not accept any
# liability of any type or kind. As this script belongs to Phil and NOT Cisco then Cisco cannot be held
# responsible for its use or if it goes bad, nor can Cisco make any profit from this script. Phil can profit
# from this script but will not assume any liability. Other than the boring stuff please enjoy and plagiarise
# as you like (as I have no ways to stop you) but common courtesy says to credit me in some way.
# [see above comments on Beer, Wine, Steak and Greggs.].
#
# Version Control               Comments
# Version 0.01 Date 27/07/20    Initial draft
# Version 0.1  Date 30/07/20    Improved Error handling
# Version 0.2  Date 03/07/20    Restructured some code to work better of various OS's
#
# Version 6.9 Date xx/xx/xx     Took over world and actually got paid for value added work....If your reading this
#                               approach me on Linked-In for details of weekend "daily" rate
# Version 7.0 Date xx/xx/xx     Note to the Gaffer - if your reading this then the above line is a joke only :-)
#
# ToDo *******************TO DO*********************
# 1.0 DONE Import credentials
# 2.0 DONE Run and collect raw data per command
# 3.0 DONE Filter the data for the stats
# 4.0 DONE Display stats for that device on the page
# 5.0 DONE Add argparse for debug and EULA
# 6.0 DONE Implement multiprocessing
# 7.0 NOT FOR THIS PRIJECT Implement connection reuse - Ideally keep SSH connection open full time
# 8.0 Something better than time.sleep() waiting for response.
# 9.0 Figure out why sometimes the CURL probes die
# 10.0 Implement local data collection for bulk upload to influx rather than per probe for scalability
#

from flask import Flask             # Flask to serve pages
from flask import Response          # Flask to serve pages
import logging.handlers             # Needed for logging
import time                         # Only for time.sleep
import wsgiserver                   # from gevent.wsgi
import socket                       # only used to raise socket exceptions
from multiprocessing import Pool    # trying to run in parallel rather than in sequence
import credentials
import traceback
import sys
import json
from scapy.all import Ether, IP, IPv6, ICMP, ICMPv6EchoRequest, sr, TCP, UDP, conf, srp
import pycurl
import threading
import random
import requests
import datetime
import subprocess
import inspect
import gc
from pympler import muppy, summary
import pandas as pd


FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
LOGFILE = credentials.LOGFILE
LOGFILE_COUNT = credentials.LOGCOUNT
LOGFILE_MAX_SIZE = credentials.LOGBYTES
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH
INTERFACE = credentials.INTERFACE
INFLUX_DB_Path = credentials.INFLUX_DB_Path
HOSTS_DB = {}
flask_app = Flask('router_nat_stats')


def process_hosts_in_serial():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_function.info("----------- Processing Serial -----------")
    results = ""
    for host in HOSTS_DB['pingICMPv4'].keys():
        results += pingipv4(host_dictionary=HOSTS_DB['pingICMPv4'][host])
    for host in HOSTS_DB['pingICMPv6'].keys():
        results += pingipv6(host_dictionary=HOSTS_DB['pingICMPv6'][host])
    for host in HOSTS_DB['curlv4'].keys():
        results += curlv4(host_dictionary=HOSTS_DB['curlv4'][host])
    for host in HOSTS_DB['curlv6'].keys():
        results += curlv6(host_dictionary=HOSTS_DB['curlv6'][host])
    return results


def process_hosts_in_parallel():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("----------- Processing Parallel -----------")
    results = ""
    t1 = time.time()
    with Pool(processes=32) as pool:
        array_pingICMPv4 = pool.imap(pingipv4, HOSTS_DB['pingICMPv4'].values())
        array_pingICMPv6 = pool.imap(pingipv6, HOSTS_DB['pingICMPv6'].values())
        array_curlv4 = pool.imap(curlv4, HOSTS_DB['curlv4'].values())
        array_curlv6 = pool.imap(curlv6, HOSTS_DB['curlv6'].values())
        # array_DNSv4 = pool.imap(dnspingipv4, HOSTS_DB['DNSpingv4'].values())
        # array_UDPv4 = pool.imap(udppingipv4, HOSTS_DB['UDPpingv4'].values())
        # array_TCPv4 = pool.imap(tcppingipv4, HOSTS_DB['TCPpingv4'].values())
        # array_DNSv6 = pool.imap(dnspingipv4, HOSTS_DB['DNSpingv6'].values())
        # array_UDPv6 = pool.imap(udppingipv4, HOSTS_DB['UDPpingv6'].values())
        # array_TCPv6 = pool.imap(tcppingipv4, HOSTS_DB['TCPpingv6'].values())
        t2 = time.time()
        function_logger.info("----------- Workers all built Parallel -----------")
        for each in array_pingICMPv4:
            results += each
        for each in array_pingICMPv6:
            results += each
        for each in array_curlv4:
            results += each
        for each in array_curlv6:
            results += each
        t3 = time.time()
        # for each in array_DNSv4:
        #     results += each
        # for each in array_UDPv4:
        #     results += each
        # for each in array_TCPv4:
        #     results += each
        # for each in array_DNSv6:
        #     results += each
        # for each in array_UDPv6:
        #     results += each
        # for each in array_TCPv6:
        #     results += each
        function_logger.info("----------- Sending results Parallel -----------")
        function_logger.info("t2 - t1=" + str("{:.2f}".format(float(t2-t1))) + " t3 - t2=" + str("{:.2f}".format(float(t3-t2))) + " t3 - t1= " + str("{:.2f}".format(float(t3-t1))))
    return results


def dnspingipv4(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def udppingipv4(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def tcppingipv4(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def dnspingipv6(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def udppingipv6(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def tcppingipv6(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def pingipv4(host_dictionary, influx_results=True):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "pingv4"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    time.sleep(random.uniform(0, 1) / timeout)
    function_logger.debug("sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
    address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]

    packet = IP(dst=address_from_hostname, tos=int(tos)) / ICMP()
    drop_pc = 0
    latency_average = -1
    latency_total = 0
    latency_min = -1
    latency_max = -1
    success = 0
    fail = 0
    for x in range(count):
        t1 = time.time()
        ans, unans = sr(packet, verbose=0, timeout=timeout, iface=INTERFACE)
        t2 = time.time()
        if str(ans).split(":")[4][0] == "1":
            if not t2 - packet.sent_time > timeout:
                t = (t2 - packet.sent_time) * 1000
            else:
                t = -1
            if not t == -1:
                latency_total += t
                success += 1
                if t > latency_max:
                    latency_max = t
                if latency_min == -1:
                    latency_min = t
                elif t < latency_min:
                    if not t == -1:
                        latency_min = t
            time.sleep(timeout)
        elif str(unans).split(":")[4][0] == "1":
            fail += 1
    if success > 0:
        latency_average = latency_total / success
    if fail > 0:
        drop_pc += fail * (100 / count)
    results += 'ICMPv4_LatencyAvg{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_average))))
    results += 'ICMPv4_LatencyMin{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_min))))
    results += 'ICMPv4_LatencyMax{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_max))))
    results += 'ICMPv4_drop{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, drop_pc)
    return results


def pingipv6(host_dictionary, influx_results=True):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "pingv6"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    time.sleep(random.uniform(0, 1) / timeout)
    function_logger.debug("sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
    address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
    packet = IPv6(dst=address_from_hostname, tc=int(tos)) / ICMPv6EchoRequest()
    drop_pc = 0
    latency_average = -1
    latency_total = 0
    latency_min = -1
    latency_max = -1
    success = 0
    fail = 0
    for x in range(count):
        t1 = time.time()
        ans, unans = sr(packet, verbose=0, timeout=timeout, iface=INTERFACE)
        t2 = time.time()
        if str(ans).split(":")[4][0] == "1":
            if not t2 - packet.sent_time > timeout:
                t = (t2 - t1)*1000
            else:
                t = -1
            if not t == -1:
                latency_total += t
                success += 1
                if t > latency_max:
                    latency_max = t
                if latency_min == -1:
                    latency_min = t
                elif t < latency_min:
                    if not t == -1:
                        latency_min = t
            time.sleep(timeout)
        # This is only in here to mitigate https://github.com/secdev/scapy/issues/2263 as I couldnt get
        # conf.raw_layer = IPv6 or no filter to work
        elif str(ans).split(":")[5][0] == "1" and str(ans[0]).split(" ")[16].split("=")[1] == str(address_from_hostname) and str(ans[0]).split(" ")[18] == "|<ICMPv6EchoReply":
            if not t2 - packet.sent_time > timeout:
                t = (t2 - t1)*1000
            else:
                t = -1
            if not t == -1:
                latency_total += t
                success += 1
                if t > latency_max:
                    latency_max = t
                if latency_min == -1:
                    latency_min = t
                elif t < latency_min:
                    if not t == -1:
                        latency_min = t
            time.sleep(timeout)
        elif str(unans).split(":")[4][0] == "1":
            fail += 1
    if success > 0:
        latency_average = latency_total / success
    if fail > 0:
        drop_pc += fail * (100 / count)
    results += 'ICMPv6_LatencyAvg{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_average))))
    results += 'ICMPv6_LatencyMin{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_min))))
    results += 'ICMPv6_LatencyMax{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, str("{:.2f}".format(float(latency_max))))
    results += 'ICMPv6_drop{host="%s",label="%s",tos="%s",dns="%s",group="%s"} %s\n' % (hostname, label, tos, dns, group, drop_pc)
    return results


def curlv4(host_dictionary, influx_results=True):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "curlv4"
    function_logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    time.sleep(random.uniform(0, 1) / timeout)
    function_logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
    curl_lookup_average = -1
    curl_connect_average = -1
    curl_app_connect_average = -1
    curl_pre_transfer_average = -1
    curl_total_transfer_average = -1

    curl_lookup_min = -1
    curl_connect_min = -1
    curl_app_connect_min = -1
    curl_pre_transfer_min = -1
    curl_total_transfer_min = -1

    curl_connect_max = -1
    curl_lookup_max = -1
    curl_app_connect_max = -1
    curl_pre_transfer_max = -1
    curl_total_transfer_max = -1

    success = 0
    fail = 0
    drop_pc = 0

    for x in range(count):
        try:
            c = pycurl.Curl()
            c.setopt(c.IPRESOLVE, c.IPRESOLVE_V4)
            c.setopt(c.TIMEOUT, timeout)
            c.setopt(c.URL, url)
            c.setopt(c.NOBODY, 1)
            c.perform()
            if c.getinfo(c.HTTP_CODE) == 200:
                success += 1
                if curl_connect_max < c.getinfo(c.CONNECT_TIME):
                    curl_connect_max = c.getinfo(c.CONNECT_TIME)
                if curl_lookup_max < c.getinfo(c.NAMELOOKUP_TIME):
                    curl_lookup_max = c.getinfo(c.NAMELOOKUP_TIME)
                if curl_app_connect_max < c.getinfo(c.APPCONNECT_TIME):
                    curl_app_connect_max = c.getinfo(c.APPCONNECT_TIME)
                if curl_pre_transfer_max < c.getinfo(c.PRETRANSFER_TIME):
                    curl_pre_transfer_max = c.getinfo(c.PRETRANSFER_TIME)
                if curl_total_transfer_max < c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_max = c.getinfo(c.TOTAL_TIME)
                if curl_connect_min > c.getinfo(c.CONNECT_TIME):
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                if curl_lookup_min < c.getinfo(c.NAMELOOKUP_TIME):
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                if curl_app_connect_min < c.getinfo(c.APPCONNECT_TIME):
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                if curl_pre_transfer_min > c.getinfo(c.PRETRANSFER_TIME):
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)
                if curl_connect_min == -1:
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)
                if not curl_connect_average == -1:
                    curl_connect_average += c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                else:
                    curl_connect_average = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                c.close()
                time.sleep(timeout)
            else:
                fail += 1
        except\
                pycurl.error as e:
            function_logger.error("curlv4 - catching pycurl.error")
            function_logger.error("sending curl label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
            function_logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("curlv4 - Unexpected error:" + str(e))
            function_logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            fail += 1
            c.close()
        except Exception as e:
            function_logger.error("curlv4 - Curl'ing to host")
            function_logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("curlv4 - Unexpected error:" + str(e))
            function_logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            fail += 1
            c.close()
    if success > 0:
        curl_connect_average = curl_connect_average / success
        curl_lookup_average = curl_lookup_average / success
        curl_pre_transfer_average = curl_pre_transfer_average / success
        # curl_start_transfer_average = curl_start_transfer_average / success
        curl_total_transfer_average = curl_total_transfer_average / success
    if fail > 0:
        drop_pc += fail * (100 / count)
    results += 'curlv4_Connect_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_connect_average)*1000)))
    results += 'curlv4_Connect_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_connect_min)*1000)))
    results += 'curlv4_Connect_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_connect_max)*1000)))
    results += 'curlv4_Lookup_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_lookup_average)*1000)))
    results += 'curlv4_Lookup_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_lookup_min)*1000)))
    results += 'curlv4_Lookup_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_lookup_max)*1000)))
    results += 'curlv4_pre_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_pre_transfer_average)*1000)))
    results += 'curlv4_pre_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_pre_transfer_min)*1000)))
    results += 'curlv4_pre_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_pre_transfer_max)*1000)))
    results += 'curlv4_total_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_average)*1000)))
    results += 'curlv4_total_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_min)*1000)))
    results += 'curlv4_total_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_max)*1000)))
    results += 'curlv4_drop{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, drop_pc)
    return results


def curlv6(host_dictionary):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "curlv6"
    measurement_name = "N/A"
    function_logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    time.sleep(random.uniform(0, 1) / timeout)
    function_logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
    curl_lookup_average = -1
    curl_connect_average = -1
    curl_app_connect_average = -1
    curl_pre_transfer_average = -1
    curl_total_transfer_average = -1
    curl_lookup_min = -1
    curl_connect_min = -1
    curl_app_connect_min = -1
    curl_pre_transfer_min = -1
    curl_total_transfer_min = -1
    curl_connect_max = -1
    curl_lookup_max = -1
    curl_app_connect_max = -1
    curl_pre_transfer_max = -1
    curl_total_transfer_max = -1

    success = 0
    fail = 0
    drop_pc = 0

    for x in range(count):
        try:
            c = pycurl.Curl()
            c.setopt(c.IPRESOLVE, c.IPRESOLVE_V6)
            c.setopt(c.TIMEOUT, timeout)
            c.setopt(c.URL, url)
            c.setopt(c.NOBODY, 1)
            c.perform()
            if c.getinfo(c.HTTP_CODE) == 200:
                success += 1
                if curl_connect_max < c.getinfo(c.CONNECT_TIME):
                    curl_connect_max = c.getinfo(c.CONNECT_TIME)
                if curl_lookup_max < c.getinfo(c.NAMELOOKUP_TIME):
                    curl_lookup_max = c.getinfo(c.NAMELOOKUP_TIME)
                if curl_app_connect_max < c.getinfo(c.APPCONNECT_TIME):
                    curl_app_connect_max = c.getinfo(c.APPCONNECT_TIME)
                if curl_pre_transfer_max < c.getinfo(c.PRETRANSFER_TIME):
                    curl_pre_transfer_max = c.getinfo(c.PRETRANSFER_TIME)
                if curl_total_transfer_max < c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_max = c.getinfo(c.TOTAL_TIME)

                if curl_connect_min > c.getinfo(c.CONNECT_TIME):
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                if curl_lookup_min < c.getinfo(c.NAMELOOKUP_TIME):
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                if curl_app_connect_min < c.getinfo(c.APPCONNECT_TIME):
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                if curl_pre_transfer_min > c.getinfo(c.PRETRANSFER_TIME):
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if curl_connect_min == -1:
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if not curl_connect_average == -1:
                    curl_connect_average += c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                else:
                    curl_connect_average = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                    curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                c.close()
                time.sleep(timeout)
            else:
                fail += 1
        except pycurl.error as e:
            function_logger.error("curlv6 - catching pycurl.error")
            function_logger.error("sending curl label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
            function_logger.error("curlv6 - Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("curlv6 - Unexpected error:" + str(e))
            function_logger.error("curlv6 - TRACEBACK=" + str(traceback.format_exc()))
            fail += 1
            c.close()
        except Exception as e:
            function_logger.error("curlv6 - Curl'ing to host")
            function_logger.error("curlv6 - Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("curlv6 - Unexpected error:" + str(e))
            function_logger.error("curlv6 - TRACEBACK=" + str(traceback.format_exc()))
            fail += 1
            c.close()

    if success > 0:
        curl_connect_average = curl_connect_average / success
        curl_lookup_average = curl_lookup_average / success
        curl_pre_transfer_average = curl_pre_transfer_average / success
        curl_total_transfer_average = curl_total_transfer_average / success
    if fail > 0:
        drop_pc += fail * (100 / count)

    results += 'curlv6_Connect_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_connect_average)*1000)))
    results += 'curlv6_Connect_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_connect_min)*1000)))
    results += 'curlv6_Connect_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_connect_max)*1000)))
    results += 'curlv6_Lookup_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_lookup_average)*1000)))
    results += 'curlv6_Lookup_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_lookup_min)*1000)))
    results += 'curlv6_Lookup_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_lookup_max)*1000)))
    results += 'curlv6_pre_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_pre_transfer_average)*1000)))
    results += 'curlv6_pre_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_pre_transfer_min)*1000)))
    results += 'curlv6_pre_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_pre_transfer_max)*1000)))
    results += 'curlv6_total_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_average)*1000)))
    results += 'curlv6_total_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_min)*1000)))
    results += 'curlv6_total_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_max)*1000)))
    results += 'curlv6_drop{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, drop_pc)
    return results


@flask_app.route('/probe_stats')
def get_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    results = ""
    results += process_hosts_in_parallel()
    return Response(results, mimetype='text/plain')


def load_hosts_file_json():
    function_logger = logger.getChild("%s.%s" % (inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        function_logger.debug("load_user_statistics_file_json - opening user statistics file")
        user_filename = ABSOLUTE_PATH + "hosts.json"
        with open(user_filename) as host_json_file:
            return_db_json = json.load(host_json_file)
        function_logger.debug("load_user_statistics_file_json - closing user statistics file")
        function_logger.debug("load_user_statistics_file_json - USERS_JSON =" + str(return_db_json))
        function_logger.info("load_user_statistics_file_json - " + "loaded USER JSON DB total EOL Records = " + str(len(return_db_json)))
        function_logger.debug("load_user_statistics_file_json - USERS_JSON =" + str(return_db_json.keys()))
        function_logger.debug("load_user_statistics_file_json - returning")
        return return_db_json
    except Exception as e:
        function_logger.error("load_user_statistics_file_json - something went bad opening user statistics file")
        function_logger.error("load_user_statistics_file_json - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("load_user_statistics_file_json - Unexpected error:" + str(e))
        function_logger.error("load_user_statistics_file_json - TRACEBACK=" + str(traceback.format_exc()))
    return {}


def child_curl_v6(host_dictionary, offset=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "curl_v6"
    function_logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
        curl_lookup_average = -1
        curl_connect_average = -1
        curl_app_connect_average = -1
        curl_pre_transfer_average = -1
        curl_total_transfer_average = -1
        curl_lookup_min = -1
        curl_connect_min = -1
        curl_app_connect_min = -1
        curl_pre_transfer_min = -1
        curl_total_transfer_min = -1
        curl_connect_max = -1
        curl_lookup_max = -1
        curl_app_connect_max = -1
        curl_pre_transfer_max = -1
        curl_total_transfer_max = -1
        success = 0
        fail = 0
        drop_pc = 0
        tt1 = time.time()
        for x in range(count):
            try:
                c = pycurl.Curl()
                c.setopt(c.IPRESOLVE, c.IPRESOLVE_V6)
                c.setopt(c.TIMEOUT, timeout)
                c.setopt(c.URL, url)
                c.setopt(c.NOBODY, 1)
                c.perform()
                if c.getinfo(c.HTTP_CODE) == 200:
                    success += 1
                    if curl_connect_max < c.getinfo(c.CONNECT_TIME):
                        curl_connect_max = c.getinfo(c.CONNECT_TIME)
                    if curl_lookup_max < c.getinfo(c.NAMELOOKUP_TIME):
                        curl_lookup_max = c.getinfo(c.NAMELOOKUP_TIME)
                    if curl_app_connect_max < c.getinfo(c.APPCONNECT_TIME):
                        curl_app_connect_max = c.getinfo(c.APPCONNECT_TIME)
                    if curl_pre_transfer_max < c.getinfo(c.PRETRANSFER_TIME):
                        curl_pre_transfer_max = c.getinfo(c.PRETRANSFER_TIME)
                    if curl_total_transfer_max < c.getinfo(c.TOTAL_TIME):
                        curl_total_transfer_max = c.getinfo(c.TOTAL_TIME)

                    if curl_connect_min > c.getinfo(c.CONNECT_TIME):
                        curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    if curl_lookup_min < c.getinfo(c.NAMELOOKUP_TIME):
                        curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    if curl_app_connect_min < c.getinfo(c.APPCONNECT_TIME):
                        curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    if curl_pre_transfer_min > c.getinfo(c.PRETRANSFER_TIME):
                        curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                        curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                    if curl_connect_min == -1:
                        curl_connect_min = c.getinfo(c.CONNECT_TIME)
                        curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                    if not curl_connect_average == -1:
                        curl_connect_average += c.getinfo(c.CONNECT_TIME)
                        curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                    else:
                        curl_connect_average = c.getinfo(c.CONNECT_TIME)
                        curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                    c.close()
                    time.sleep(timeout / 4)
                else:
                    fail += 1
            except pycurl.error as e:
                function_logger.warning("catching pycurl.error")
                function_logger.warning("label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
                function_logger.warning("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.warning("Unexpected error:" + str(e))
                function_logger.warning("TRACEBACK=" + str(traceback.format_exc()))
                fail += 1
                c.close()
            except Exception as e:
                function_logger.error("Curl'ing to host")
                function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.error("Unexpected error:" + str(e))
                function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
                fail += 1
                c.close()
        if success > 0:
            curl_connect_average = curl_connect_average / success
            curl_lookup_average = curl_lookup_average / success
            curl_pre_transfer_average = curl_pre_transfer_average / success
            curl_total_transfer_average = curl_total_transfer_average / success
        if fail > 0:
            drop_pc += fail * (100 / count)
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectAvg", interface, str("{:.2f}".format(float(curl_connect_average)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectMin", interface, str("{:.2f}".format(float(curl_connect_min)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectMax", interface, str("{:.2f}".format(float(curl_connect_max)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupAvg", interface, str("{:.2f}".format(float(curl_lookup_average)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupMin", interface, str("{:.2f}".format(float(curl_lookup_min)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupMax", interface, str("{:.2f}".format(float(curl_lookup_max)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferAvg", interface, str("{:.2f}".format(float(curl_pre_transfer_average)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferMin", interface, str("{:.2f}".format(float(curl_pre_transfer_min)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferMax", interface, str("{:.2f}".format(float(curl_pre_transfer_max)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferAvg", interface, str("{:.2f}".format(float(curl_total_transfer_average)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferMin", interface, str("{:.2f}".format(float(curl_total_transfer_min)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferMax", interface, str("{:.2f}".format(float(curl_total_transfer_max)*1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "curlDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.debug("%s - tt1-tt2=%s tt2-tt3=%s tt1-tt3=%s" % (label, str("{:.2f}".format(float(tt2 - tt1))), str("{:.2f}".format(float(tt3 - tt2))), str("{:.2f}".format(float(tt3 - tt1)))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)

        # manual garbage collection for multithreadded thing
        if t.minute == 0:
            if t.hour in {4, 8, 12, 16, 20, 0}:
                ####################################################################################################################################
                function_logger.critical("doing_garbage_collection")
                gc.collect()
                all_objects = muppy.get_objects()
                sum1 = summary.summarize(all_objects)
                # Prints out a summary of the large objects
                summary.print_(sum1)
                # Get references to certain types of objects such as dataframe
                dataframes = [ao for ao in all_objects if isinstance(ao, pd.DataFrame)]
                for d in dataframes:
                    function_logger.critical(d.columns.values)
                    function_logger.critical(len(d))
                ####################################################################################################################################

        time_to_sleep = (future - datetime.datetime.now()).seconds
        # if 30 > time_to_sleep > 0: # guess comit to fix timing thing
        if 29 > time_to_sleep > 0:  # guess comit to fix timing thing
            time.sleep(time_to_sleep)
        else:
            time.sleep(random.uniform(0, 1) * offset) # guess comit to fix timing thing
            time.sleep(90)
            function_logger.warning("had sleep time outside of valid range value was %s" % time_to_sleep)


def child_curl_v4(host_dictionary, offset=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "curl_v4"
    function_logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
        curl_lookup_average = -1
        curl_connect_average = -1
        curl_app_connect_average = -1
        curl_pre_transfer_average = -1
        curl_total_transfer_average = -1
        curl_lookup_min = -1
        curl_connect_min = -1
        curl_app_connect_min = -1
        curl_pre_transfer_min = -1
        curl_total_transfer_min = -1
        curl_connect_max = -1
        curl_lookup_max = -1
        curl_app_connect_max = -1
        curl_pre_transfer_max = -1
        curl_total_transfer_max = -1
        success = 0
        fail = 0
        drop_pc = 0
        tt1 = time.time()
        for x in range(count):
            try:
                c = pycurl.Curl()
                c.setopt(c.IPRESOLVE, c.IPRESOLVE_V4)
                c.setopt(c.TIMEOUT, timeout)
                c.setopt(c.URL, url)
                c.setopt(c.NOBODY, 1)
                c.perform()
                if c.getinfo(c.HTTP_CODE) == 200:
                    success += 1
                    if curl_connect_max < c.getinfo(c.CONNECT_TIME):
                        curl_connect_max = c.getinfo(c.CONNECT_TIME)
                    if curl_lookup_max < c.getinfo(c.NAMELOOKUP_TIME):
                        curl_lookup_max = c.getinfo(c.NAMELOOKUP_TIME)
                    if curl_app_connect_max < c.getinfo(c.APPCONNECT_TIME):
                        curl_app_connect_max = c.getinfo(c.APPCONNECT_TIME)
                    if curl_pre_transfer_max < c.getinfo(c.PRETRANSFER_TIME):
                        curl_pre_transfer_max = c.getinfo(c.PRETRANSFER_TIME)
                    if curl_total_transfer_max < c.getinfo(c.TOTAL_TIME):
                        curl_total_transfer_max = c.getinfo(c.TOTAL_TIME)
                    if curl_connect_min > c.getinfo(c.CONNECT_TIME):
                        curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    if curl_lookup_min < c.getinfo(c.NAMELOOKUP_TIME):
                        curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    if curl_app_connect_min < c.getinfo(c.APPCONNECT_TIME):
                        curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    if curl_pre_transfer_min > c.getinfo(c.PRETRANSFER_TIME):
                        curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                        curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)
                    if curl_connect_min == -1:
                        curl_connect_min = c.getinfo(c.CONNECT_TIME)
                        curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)
                    if not curl_connect_average == -1:
                        curl_connect_average += c.getinfo(c.CONNECT_TIME)
                        curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                    else:
                        curl_connect_average = c.getinfo(c.CONNECT_TIME)
                        curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                        curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                        curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                        curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                    c.close()
                    time.sleep(timeout / 4)
                else:
                    fail += 1
            except pycurl.error as e:
                function_logger.warning("catching pycurl.error")
                function_logger.warning("label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
                function_logger.warning("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.warning("Unexpected error:" + str(e))
                function_logger.warning("TRACEBACK=" + str(traceback.format_exc()))
                fail += 1
                c.close()
            except Exception as e:
                function_logger.error("Curl'ing to host")
                function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.error("Unexpected error:" + str(e))
                function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
                fail += 1
                c.close()
        if success > 0:
            curl_connect_average = curl_connect_average / success
            curl_lookup_average = curl_lookup_average / success
            curl_pre_transfer_average = curl_pre_transfer_average / success
            curl_total_transfer_average = curl_total_transfer_average / success
        if fail > 0:
            drop_pc += fail * (100 / count)
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectAvg", interface, str("{:.2f}".format(float(curl_connect_average) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectMin", interface, str("{:.2f}".format(float(curl_connect_min) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "ConnectMax", interface, str("{:.2f}".format(float(curl_connect_max) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupAvg", interface, str("{:.2f}".format(float(curl_lookup_average) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupMin", interface, str("{:.2f}".format(float(curl_lookup_min) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "LookupMax", interface, str("{:.2f}".format(float(curl_lookup_max) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferAvg", interface,str("{:.2f}".format(float(curl_pre_transfer_average) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferMin", interface,str("{:.2f}".format(float(curl_pre_transfer_min) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "PreTransferMax", interface,str("{:.2f}".format(float(curl_pre_transfer_max) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferAvg", interface,str("{:.2f}".format(float(curl_total_transfer_average) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferMin", interface,str("{:.2f}".format(float(curl_total_transfer_min) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "TotalTransferMax", interface,str("{:.2f}".format(float(curl_total_transfer_max) * 1000)))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (url, label, dns, group, probe_name, "curlDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.debug("%s - tt1-tt2=%s tt2-tt3=%s tt1-tt3=%s" % (label, str("{:.2f}".format(float(tt2 - tt1))), str("{:.2f}".format(float(tt3 - tt2))), str("{:.2f}".format(float(tt3 - tt1)))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)

        # manual garbage collection for multithreadded thing

        if t.minute == 0:
            if t.hour in {4, 8, 12, 16, 20, 0}:
                ####################################################################################################################################
                function_logger.critical("doing_garbage_collection")
                gc.collect()
                all_objects = muppy.get_objects()
                sum1 = summary.summarize(all_objects)
                # Prints out a summary of the large objects
                summary.print_(sum1)
                # Get references to certain types of objects such as dataframe
                dataframes = [ao for ao in all_objects if isinstance(ao, pd.DataFrame)]
                for d in dataframes:
                    function_logger.critical(d.columns.values)
                    function_logger.critical(len(d))
                ####################################################################################################################################

        time_to_sleep = (future - datetime.datetime.now()).seconds
        # if 30 > time_to_sleep > 0: guess comit to fix timing thing
        if 29 > time_to_sleep > 0: # guess comit to fix timing thing
            time.sleep(time_to_sleep)
        else:
            time.sleep(random.uniform(0, 1) * offset)  # guess comit to fix timing thing
            time.sleep(90)
            function_logger.warning("child_curl_v4 - had sleep time outside of valid range value was %s" % time_to_sleep)


def child_icmp_ping_v6(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "icmp_ping_v6"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']

    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("child_icmp_ping_v6 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        drop_pc = 100
        latency_average = -1
        latency_min = -1
        latency_max = -1
        tt1 = time.time()
        try:
            output = subprocess.check_output(['ping6', '-c', str(count), '-Q', str(tos), '-W', str(timeout), '-I', str(interface), str(hostname)], stderr=subprocess.STDOUT)
            if "100%" not in str(output.splitlines()[-1]):
                drop_pc = float(str(output.splitlines()[-2]).split(" ")[5].replace("%", ""))
                latency_min = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[0])
                latency_average = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[1])
                latency_max = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[2])
            else:
                drop_pc = float(str(output.splitlines()[-1]).split(" ")[5].replace("%", ""))
        except subprocess.CalledProcessError as e:
            try:
                if "100%" in str(e.output.splitlines()[-2]):
                    drop_pc = float(str(e.output.splitlines()[-2]).split(" ")[5].replace("%", ""))
                else:
                    function_logger.warning("in in %s" % str(e.output.splitlines()[-2]))
                    function_logger.warning("in in %s - Unexpected error: %s" % (label, str(e.output)))
                    function_logger.warning("in in cmd %s" % str(e.cmd))
                    function_logger.warning("in in return %s" % str(e.returncode))
                    function_logger.warning("in in output %s" % str(e.output))
            except Exception as e:
                drop_pc = 100
                function_logger.error("%s- something went bad sending to doing icmp ping v4 inside")
                function_logger.error("%s- Unexpected error:%s" % (label, str(sys.exc_info()[0])))
                function_logger.error("%s- Unexpected error:%s" % (label, str(e)))
                function_logger.error("%s- TRACEBACK=%s" % (label, str(traceback.format_exc())))
        except Exception as e:
            function_logger.error("- something went bad sending to InfluxDB")
            function_logger.error("%s- Unexpected error:%s" % (label, str(sys.exc_info()[0])))
            function_logger.error("%s- Unexpected error:%s" % (label, str(e)))
            function_logger.error("%s- TRACEBACK=%s" % (label, str(traceback.format_exc())))
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, str(drop_pc))
        update_influx(results, future)
        tt3 = time.time()
        function_logger.debug("%s - tt1-tt2=%s tt2-tt3=%s tt1-tt3=%s" % (label, str("{:.2f}".format(float(tt2 - tt1))), str("{:.2f}".format(float(tt3 - tt2))), str("{:.2f}".format(float(tt3 - tt1)))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)
        # manual garbage collection for multithreadded thing
        if t.minute == 0:
            if t.hour in {4, 8, 12, 16, 20, 0}:
                ####################################################################################################################################
                function_logger.critical("doing_garbage_collection")
                gc.collect()
                all_objects = muppy.get_objects()
                sum1 = summary.summarize(all_objects)
                # Prints out a summary of the large objects
                summary.print_(sum1)
                # Get references to certain types of objects such as dataframe
                dataframes = [ao for ao in all_objects if isinstance(ao, pd.DataFrame)]
                for d in dataframes:
                    function_logger.critical(d.columns.values)
                    function_logger.critical(len(d))
                ####################################################################################################################################

        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)



def child_icmp_ping_v4(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "icmp_ping_v4"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("child_icmp_ping_v4 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        drop_pc = 0
        latency_average = -1
        latency_min = -1
        latency_max = -1
        tt1 = time.time()
        try:
            output = subprocess.check_output(['ping4', '-c', str(count), '-Q', str(tos), '-W', str(timeout), '-I', str(interface), str(hostname)], stderr=subprocess.STDOUT)
            if not "100%" in str(output.splitlines()[-1]):
                drop_pc = float(str(output.splitlines()[-2]).split(" ")[5].replace("%", ""))
                latency_min = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[0])
                latency_average = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[1])
                latency_max = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[2])
            else:
                drop_pc = float(str(output.splitlines()[-1]).split(" ")[5].replace("%", ""))
        except subprocess.CalledProcessError as e:
            try:
                if "100%" in str(e.output.splitlines()[-2]):
                    drop_pc = float(str(e.output.splitlines()[-2]).split(" ")[5].replace("%", ""))
                else:
                    function_logger.warning("in in %s" % str(e.output.splitlines()[-2]))
                    function_logger.warning("in in %s - Unexpected error: %s" % (label, str(e.output)))
                    function_logger.warning("in in cmd %s" % str(e.cmd))
                    function_logger.warning("in in return %s" % str(e.returncode))
                    function_logger.warning("in in output %s" % str(e.output))
            except Exception as e:
                drop_pc = 100
                function_logger.error("%s- something went bad sending to doing icmp ping v4 inside")
                function_logger.error("%s- Unexpected error:%s" % (label, str(sys.exc_info()[0])))
                function_logger.error("%s- Unexpected error:%s" % (label, str(e)))
                function_logger.error("%s- TRACEBACK=%s" % (label, str(traceback.format_exc())))
        except Exception as e:
            function_logger.error("- something went bad sending to InfluxDB")
            function_logger.error("%s- Unexpected error:%s" % (label, str(sys.exc_info()[0])))
            function_logger.error("%s- Unexpected error:%s" % (label, str(e)))
            function_logger.error("%s- TRACEBACK=%s" % (label, str(traceback.format_exc())))
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.debug("%s - tt1-tt2=%s tt2-tt3=%s tt1-tt3=%s" % (label, str("{:.2f}".format(float(tt2 - tt1))), str("{:.2f}".format(float(tt3 - tt2))), str("{:.2f}".format(float(tt3 - tt1)))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)

        # manual garbage collection for multithreadded thing
        if t.minute == 0:
            if t.hour in {4, 8, 12, 16, 20, 0}:
                ####################################################################################################################################
                function_logger.critical("doing_garbage_collection")
                gc.collect()
                all_objects = muppy.get_objects()
                sum1 = summary.summarize(all_objects)
                # Prints out a summary of the large objects
                summary.print_(sum1)
                # Get references to certain types of objects such as dataframe
                dataframes = [ao for ao in all_objects if isinstance(ao, pd.DataFrame)]
                for d in dataframes:
                    function_logger.critical(d.columns.values)
                    function_logger.critical(len(d))
                ####################################################################################################################################

        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def child_tcp_ping_v6(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "tcp_ping_v6"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    if host_dictionary.get('TOS') is None:
        tos = host_dictionary['TOS']
    else:
        tos = 0
    if host_dictionary.get('port') is None:
        port = host_dictionary['port']
    else:
        port = 7
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("child_tcp_ping_v6 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
        packet = IPv6(dst=address_from_hostname, tc=int(tos)) / TCP(dport=port)
        drop_pc = 100
        latency_average = -1
        latency_total = 0
        latency_min = -1
        latency_max = -1
        success = 0
        fail = 0
        try:
            tt1 = time.time()
            for x in range(count):
                t1 = time.time()
                ans, unans = sr(packet, verbose=0, timeout=timeout, iface=interface)
                t2 = time.time()
                if str(ans).split(":")[4][0] == "1":
                    rx = ans[0][1]
                    tx = ans[0][0]
                    delta = rx.time - tx.sent_time
                    if delta < timeout:
                        latency = delta * 1000
                    else:
                        latency = -1
                    if not latency == -1:
                        latency_total += latency
                        success += 1
                        if latency > latency_max:
                            latency_max = latency
                        if latency_min == -1:
                            latency_min = latency
                        elif latency < latency_min:
                            if not latency == -1:
                                latency_min = latency
                    time.sleep(timeout / 2)
                elif str(unans).split(":")[4][0] == "1":
                    fail += 1

            if success > 0:
                latency_average = latency_total / success
            if fail > 0:
                drop_pc += fail * (100 / count)
        except Exception as e:
            function_logger.error("child_udp_ping_v4 " + label + "- something went bad sending to InfluxDB")
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(e))
            function_logger.error("child_udp_ping_v4 " + label + "- TRACEBACK=" + str(traceback.format_exc()))
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.info("child_tcp_ping_v6 - " + label + " -"
                    " tt1-tt2=" + str("{:.2f}".format(float(tt2 - tt1))) +
                    " tt2-tt3=" + str("{:.2f}".format(float(tt3 - tt2))) +
                    " tt1-tt3= " + str("{:.2f}".format(float(tt3 - tt1))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def child_tcp_ping_v4(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "tcp_ping_v4"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    if host_dictionary.get('TOS') is None:
        tos = host_dictionary['TOS']
    else:
        tos = 0
    if host_dictionary.get('port') is None:
        port = host_dictionary['port']
    else:
        port = 7
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("child_tcp_ping_v4 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
        packet = IP(dst=address_from_hostname, tos=int(tos)) / TCP(dport=port)
        drop_pc = 0
        latency_average = -1
        latency_total = 0
        latency_min = -1
        latency_max = -1
        success = 0
        fail = 0
        try:
            tt1 = time.time()
            for x in range(count):
                t1 = time.time()
                ans, unans = sr(packet, verbose=0, timeout=timeout, iface=interface)
                t2 = time.time()
                if str(ans).split(":")[4][0] == "1":
                    rx = ans[0][1]
                    tx = ans[0][0]
                    delta = rx.time - tx.sent_time
                    if delta < timeout:
                        latency = delta * 1000
                    else:
                        latency = -1
                    if not latency == -1:
                        latency_total += latency
                        success += 1
                        if latency > latency_max:
                            latency_max = latency
                        if latency_min == -1:
                            latency_min = latency
                        elif latency < latency_min:
                            if not latency == -1:
                                latency_min = latency
                    time.sleep(timeout / 2)
                elif str(unans).split(":")[4][0] == "1":
                    fail += 1
            if success > 0:
                latency_average = latency_total / success
            if fail > 0:
                drop_pc += fail * (100 / count)
        except Exception as e:
            function_logger.error("child_udp_ping_v4 " + label + "- something went bad sending to InfluxDB")
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(e))
            function_logger.error("child_udp_ping_v4 " + label + "- TRACEBACK=" + str(traceback.format_exc()))
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.info("child_tcp_ping_v4 - " + label + " -"
                    " tt1-tt2=" + str("{:.2f}".format(float(tt2 - tt1))) +
                    " tt2-tt3=" + str("{:.2f}".format(float(tt3 - tt2))) +
                    " tt1-tt3= " + str("{:.2f}".format(float(tt3 - tt1))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def child_udp_ping_v6(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    probe_name = "udp_ping_v6"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    if host_dictionary.get('TOS') is None:
        tos = host_dictionary['TOS']
    else:
        tos = 0
    if host_dictionary.get('port') is None:
        port = host_dictionary['port']
    else:
        port = 7
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']
    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)
    while True:
        function_logger.debug("child_udp_ping_v6 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
        packet = IPv6(dst=address_from_hostname, tc=int(tos)) / UDP(dport=port)
        drop_pc = 100
        latency_average = -1
        latency_total = 0
        latency_min = -1
        latency_max = -1
        success = 0
        fail = 0
        try:
            tt1 = time.time()
            for x in range(count):
                t1 = time.time()
                ans, unans = sr(packet, verbose=0, timeout=timeout, iface=interface)
                t2 = time.time()
                if str(ans).split(":")[4][0] == "1":
                    rx = ans[0][1]
                    tx = ans[0][0]
                    delta = rx.time - tx.sent_time
                    if delta < timeout:
                        latency = delta * 1000
                    else:
                        latency = -1
                    if not latency == -1:
                        latency_total += latency
                        success += 1
                        if latency > latency_max:
                            latency_max = latency
                        if latency_min == -1:
                            latency_min = latency
                        elif latency < latency_min:
                            if not latency == -1:
                                latency_min = latency
                    time.sleep(timeout / 2)
                elif str(unans).split(":")[4][0] == "1":
                    fail += 1
            if success > 0:
                latency_average = latency_total / success
            if fail > 0:
                drop_pc += fail * (100 / count)
        except Exception as e:
            function_logger.error("child_udp_ping_v4 " + label + "- something went bad sending to InfluxDB")
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(e))
            function_logger.error("child_udp_ping_v4 " + label + "- TRACEBACK=" + str(traceback.format_exc()))
        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.info("child_udp_ping_v6 - " + label + " -"
                    " tt1-tt2=" + str("{:.2f}".format(float(tt2 - tt1))) +
                    " tt2-tt3=" + str("{:.2f}".format(float(tt3 - tt2))) +
                    " tt1-tt3= " + str("{:.2f}".format(float(tt3 - tt1))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def child_udp_ping_v4(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "udp_ping_v4"
    function_logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    if host_dictionary.get('TOS') is None:
        tos = host_dictionary['TOS']
    else:
        tos = 0
    if host_dictionary.get('port') is None:
        port = host_dictionary['port']
    else:
        port = 7
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    if host_dictionary.get('interface') is None:
        interface = INTERFACE
    else:
        interface = host_dictionary['interface']

    t = datetime.datetime.now()
    if t.second < 29:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=30)
    elif t.second > 30:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
        future += datetime.timedelta(seconds=30)
    else:
        future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
        future += datetime.timedelta(seconds=90)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    time.sleep(time_to_sleep)

    while True:
        function_logger.debug("child_udp_ping_v4 - " + label + " - sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
        address_from_hostname = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
        packet = IP(dst=address_from_hostname, tos=int(tos)) / UDP(dport=port)
        drop_pc = 0
        latency_average = -1
        latency_total = 0
        latency_min = -1
        latency_max = -1
        success = 0
        fail = 0
        try:
            tt1 = time.time()
            # output = subprocess.check_output(['ping4', '-c', str(count), '-Q', str(tos), '-W', str(timeout), '-I', str(interface), str(hostname)], stderr=subprocess.STDOUT)
            # if not "100.0%" in str(output.splitlines()[-1]):
            #     drop_pc = float(str(output.splitlines()[-2]).split(" ")[5].replace("%", ""))
            #     latency_min = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[0])
            #     latency_average = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[1])
            #     latency_max = float(str(output.splitlines()[-1]).split(" ")[3].split("/")[2])
            # else:
            #     drop_pc = float(str(output.splitlines()[-1]).split(" ")[5].replace("%", ""))
            for x in range(count):
                t1 = time.time()
                ans, unans = sr(packet, verbose=0, timeout=timeout, iface=interface)
                t2 = time.time()
                if str(ans).split(":")[4][0] == "1":
                    rx = ans[0][1]
                    tx = ans[0][0]
                    delta = rx.time - tx.sent_time
                    if delta < timeout:
                        latency = delta * 1000
                    else:
                        latency = -1
                    if not latency == -1:
                        latency_total += latency
                        success += 1
                        if latency > latency_max:
                            latency_max = latency
                        if latency_min == -1:
                            latency_min = latency
                        elif latency < latency_min:
                            if not latency == -1:
                                latency_min = latency
                    time.sleep(timeout / 2)
                elif str(unans).split(":")[4][0] == "1":
                    fail += 1

            if success > 0:
                latency_average = latency_total / success
            if fail > 0:
                drop_pc += fail * (100 / count)
        except Exception as e:
            function_logger.error("child_udp_ping_v4 " + label + "- something went bad sending to InfluxDB")
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(sys.exc_info()[0]))
            function_logger.error("child_udp_ping_v4 " + label + "- Unexpected error:" + str(e))
            function_logger.error("child_udp_ping_v4 " + label + "- TRACEBACK=" + str(traceback.format_exc()))

        tt2 = time.time()
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyAvg", interface, str("{:.2f}".format(float(latency_average))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMin", interface, str("{:.2f}".format(float(latency_min))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyMax", interface, str("{:.2f}".format(float(latency_max))))
        results += 'Python_Monitor,__name__=PythonAssurance,host=PythonAssurance,instance=grafana-worker-02.greenbridgetech.co.uk:8050,job=PythonAssurance,service_name=PythonAssurance,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,measurement=%s,iface=%s value=%s\n' % (hostname, label, tos, dns, group, probe_name, "latencyDrop", interface, drop_pc)
        update_influx(results, future)
        tt3 = time.time()
        function_logger.info("child_udp_ping_v4 - " + label + " -"
                    " tt1-tt2=" + str("{:.2f}".format(float(tt2 - tt1))) +
                    " tt2-tt3=" + str("{:.2f}".format(float(tt3 - tt2))) +
                    " tt1-tt3= " + str("{:.2f}".format(float(tt3 - tt1))))
        t = datetime.datetime.now()
        if t.second < 29:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=30)
        elif t.second > 30:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 30)
            future += datetime.timedelta(seconds=30)
        else:
            future = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            future += datetime.timedelta(seconds=90)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            time.sleep(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def master_curl_v6_probe_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        child_thread_curl_v6 = []
        for key in HOSTS_DB['curl_v6'].keys():
            child_thread_curl_v6.append(threading.Thread(target=lambda: child_curl_v6(HOSTS_DB['curl_v6'][key])))
            child_thread_curl_v6[-1].start()
    except Exception as e:
        function_logger.error("master_curl_v6_probe_stats - something went bad with auto update")
        function_logger.error("master_curl_v6_probe_stats - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("master_curl_v6_probe_stats - Unexpected error:" + str(e))
        function_logger.error("master_curl_v6_probe_stats - TRACEBACK=" + str(traceback.format_exc()))


def master_curl_v4_probe_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    try:
        child_thread_curl_v4 = []
        for key in HOSTS_DB['curl_v4'].keys():
            child_thread_curl_v4.append(threading.Thread(target=lambda: child_curl_v4(HOSTS_DB['curl_v4'][key])))
            child_thread_curl_v4[-1].start()
    except Exception as e:
        function_logger.error("master_curl_v4_probe_stats - something went bad with auto update")
        function_logger.error("master_curl_v4_probe_stats - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("master_curl_v4_probe_stats - Unexpected error:" + str(e))
        function_logger.error("master_curl_v4_probe_stats - TRACEBACK=" + str(traceback.format_exc()))


def master_icmp_ping_v6_probe_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))

    try:
        child_thread_icmp_ping_v6 = []
        for key in HOSTS_DB['icmp_ping_v6'].keys():
            child_thread_icmp_ping_v6.append(threading.Thread(target=lambda: child_icmp_ping_v6(HOSTS_DB['icmp_ping_v6'][key])))
            child_thread_icmp_ping_v6[-1].start()
    except Exception as e:
        function_logger.error("master_icmp_ping_v6_probe_stats - something went bad with auto update")
        function_logger.error("master_icmp_ping_v6_probe_stats - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("master_icmp_ping_v6_probe_stats - Unexpected error:" + str(e))
        function_logger.error("master_icmp_ping_v6_probe_stats - TRACEBACK=" + str(traceback.format_exc()))


def master_icmp_ping_v4_probe_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        child_thread_icmp_ping_v4 = []
        for key in HOSTS_DB['icmp_ping_v4'].keys():
            child_thread_icmp_ping_v4.append(threading.Thread(target=lambda: child_icmp_ping_v4(HOSTS_DB['icmp_ping_v4'][key])))
            child_thread_icmp_ping_v4[-1].start()
    except Exception as e:
        function_logger.error("master_icmp_ping_v4_probe_stats - something went bad with auto update")
        function_logger.error("master_icmp_ping_v4_probe_stats - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("master_icmp_ping_v4_probe_stats - Unexpected error:" + str(e))
        function_logger.error("master_icmp_ping_v4_probe_stats - TRACEBACK=" + str(traceback.format_exc()))


def update_influx(raw_string, timestamp):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        string_to_upload = ""
        timestamp_string = str(int(timestamp.timestamp()) * 1000000000)
        for each in raw_string.splitlines():
            string_to_upload += each + " " + timestamp_string + "\n"
        upload_to_influx_sessions = requests.session()
        success = False
        attempts = 0
        attempt_error_array = []
        while attempts < 5 and not success:
            try:
                upload_to_influx_sessions_response = upload_to_influx_sessions.post(url=INFLUX_DB_Path, data=string_to_upload, timeout=(4, 2))
                success = True
            except requests.exceptions.ConnectTimeout as e:
                attempts += 1
                function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Timeout")
                function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.debug("update_influx - Unexpected error:" + str(e))
                function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                attempt_error_array.append(str(sys.exc_info()[0]))
                time.sleep(1)
            except requests.exceptions.ConnectionError as e:
                attempts += 1
                function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Error")
                function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.debug("update_influx - Unexpected error:" + str(e))
                function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                attempt_error_array.append(str(sys.exc_info()[0]))
                time.sleep(1)
            except Exception as e:
                function_logger.error("update_influx - attempted " + str(attempts) + " Failed")
                function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.error("update_influx - Unexpected error:" + str(e))
                function_logger.error("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                attempt_error_array.append(str(sys.exc_info()[0]))
                break
        upload_to_influx_sessions.close()
        if not success:
            function_logger.error("update_influx - FAILED after 5 attempts. Failed up update " + str(string_to_upload.splitlines()[0]))
            function_logger.error("update_influx - FAILED after 5 attempts. attempt_error_array: " + str(attempt_error_array))
            return
        else:
            function_logger.debug("update_influx - " + "string for influx is " + str(string_to_upload))
            function_logger.debug("update_influx - " + "influx status code is  " + str(upload_to_influx_sessions_response.status_code))
            function_logger.debug("update_influx - " + "influx response is code is " + str(upload_to_influx_sessions_response.text[0:1000]))
            return
    except Exception as e:
        function_logger.error("update_influx - something went bad sending to InfluxDB")
        function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("update_influx - Unexpected error:" + str(e))
        function_logger.error("update_influx - TRACEBACK=" + str(traceback.format_exc()))
    return


if __name__ == '__main__':
    # Create Logger
    logger = logging.getLogger("Python_Monitor")
    logger_handler = logging.handlers.TimedRotatingFileHandler(LOGFILE, backupCount=365, when='D')
    logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(thread)d:%(name)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)
    logger.setLevel(logging.INFO)
    logger.info("---------------------- STARTING ----------------------")
    logger.info("__main__ - " + "Python Monitor Logger")

    # GET_CURRENT_DB
    logger.info("__main__ - " + "GET_CURRENT_DB")
    HOSTS_DB = load_hosts_file_json()

    # thread per process
    master_thread_icmp_ping_v4 = threading.Thread(target=lambda: master_icmp_ping_v4_probe_stats())
    master_thread_icmp_ping_v4.start()
    master_thread_icmp_ping_v6 = threading.Thread(target=lambda: master_icmp_ping_v6_probe_stats())
    master_thread_icmp_ping_v6.start()
    master_thread_curl_v4 = threading.Thread(target=lambda: master_curl_v4_probe_stats())
    master_thread_curl_v4.start()
    master_thread_curl_v6 = threading.Thread(target=lambda: master_curl_v6_probe_stats())
    master_thread_curl_v6.start()

    # build flask instance.
    logger.info("__main__ - " + "starting flask")
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()
