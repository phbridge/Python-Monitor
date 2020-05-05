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
# Version 0.01 Date 06/05/19    Initial draft
# Version 0.1  Date 17/05/19    Improved Error handling
# Version 0.2  Date 18/05/19    Restructured some code to work better of various OS's
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
#

from flask import Flask             # Flask to serve pages
from flask import Response          # Flask to serve pages
import logging.handlers             # Needed for loggin
import time                         # Only for time.sleep
import wsgiserver                   # from gevent.wsgi
import paramiko                     # used for the SSH session
import socket                       # only used to raise socket exceptions
from multiprocessing import Pool    # trying to run in parallel rather than in sequence
import credentials
import traceback
import sys
import json
from scapy.all import Ether, IP, IPv6, ICMP, ICMPv6EchoRequest, sr
import pycurl

FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
LOGFILE = credentials.LOGFILE
LOGFILE_COUNT = credentials.LOGCOUNT
LOGFILE_MAX_SIZE = credentials.LOGBYTES
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH
HOSTS_DB = {}
flask_app = Flask('router_nat_stats')


def process_hosts_in_serial():
    logger.info("----------- Processing Serial -----------")
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
    logger.info("----------- Processing Parallel -----------")
    results = ""
    with Pool(processes=30) as pool:
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
        logger.info("----------- Workers all built Parallel -----------")
        for each in array_pingICMPv4:
            results += each
        for each in array_pingICMPv6:
            results += each
        for each in array_curlv4:
            results += each
        for each in array_curlv6:
            results += each
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
        logger.info("----------- Sending results Parallel -----------")
    return results


def dnspingipv4(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def udppingipv4(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def tcppingipv4(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def dnspingipv6(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def udppingipv6(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def tcppingipv6(host_dictionary):
    print(host_dictionary)
    results = ""
    results += "NOT YET IMPLEMENTED"
    return results


def pingipv4(host_dictionary):
    logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    logger.debug("sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
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
        ans, unans = sr(packet, verbose=0, timeout=timeout)
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


def pingipv6(host_dictionary):
    logger.debug(host_dictionary)
    results = ""
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    logger.debug("sending ping with attributes hostname=" + hostname + " count=" + str(count) + " timeout=" + str(timeout) + " DSCP=" + str(tos))
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
        ans, unans = sr(packet, verbose=0, timeout=timeout)
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


def curlv4(host_dictionary):
    logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
    curl_lookup_average = -1
    curl_connect_average = -1
    curl_app_connect_average = -1
    curl_pre_transfer_average = -1
    # curl_start_transfer_average = -1
    curl_total_transfer_average = -1

    curl_lookup_min = -1
    curl_connect_min = -1
    curl_app_connect_min = -1
    curl_pre_transfer_min = -1
    # curl_start_transfer_min = -1
    curl_total_transfer_min = -1

    curl_connect_max = -1
    curl_lookup_max = -1
    curl_app_connect_max = -1
    curl_pre_transfer_max = -1
    # curl_start_transfer_max = -1
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
                # if curl_start_transfer_max < c.getinfo(c.STARTTRANSFER_TIME):
                #     curl_start_transfer_max = c.getinfo(c.STARTTRANSFER_TIME)
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
                # if curl_start_transfer_min > c.getinfo(c.STARTTRANSFER_TIME):
                #     curl_start_transfer_min = c.getinfo(c.STARTTRANSFER_TIME)
                if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if curl_connect_min == -1:
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_min = c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if not curl_connect_average == -1:
                    curl_connect_average += c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_average += c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                else:
                    curl_connect_average = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_average = c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                c.close()
            else:
                fail += 1
        except pycurl.error as e:
            logger.error("curlv4 - catching pycurl.error")
            logger.error("sending curl url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
            logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            logger.error("curlv4 - Unexpected error:" + str(e))
            logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            drop_pc += 100 / count
            c.close()
        except Exception as e:
            logger.error("curlv4 - Curl'ing to host")
            logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            logger.error("curlv4 - Unexpected error:" + str(e))
            logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            drop_pc += 100 / count
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

    # results += 'curlv4_start_transfer_Avg{host="%s"} %s\n' % (url, str("{:.2f}".format(float(curl_start_transfer_average)*100)))
    # results += 'curlv4_start_transfer_Min{host="%s"} %s\n' % (url, str("{:.2f}".format(float(curl_start_transfer_min)*100)))
    # results += 'curlv4_start_transfer_Max{host="%s"} %s\n' % (url, str("{:.2f}".format(float(curl_start_transfer_max)*100)))

    results += 'curlv4_total_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_average)*1000)))
    results += 'curlv4_total_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_min)*1000)))
    results += 'curlv4_total_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.2f}".format(float(curl_total_transfer_max)*1000)))

    results += 'curlv4_drop{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, drop_pc)

    return results


def curlv6(host_dictionary):
    logger.debug(host_dictionary)
    results = ""
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']

    logger.debug("sending curl with attributes url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
    curl_lookup_average = -1
    curl_connect_average = -1
    curl_app_connect_average = -1
    curl_pre_transfer_average = -1
    # curl_start_transfer_average = -1
    curl_total_transfer_average = -1

    curl_lookup_min = -1
    curl_connect_min = -1
    curl_app_connect_min = -1
    curl_pre_transfer_min = -1
    # curl_start_transfer_min = -1
    curl_total_transfer_min = -1

    curl_connect_max = -1
    curl_lookup_max = -1
    curl_app_connect_max = -1
    curl_pre_transfer_max = -1
    # curl_start_transfer_max = -1
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
                # if curl_start_transfer_max < c.getinfo(c.STARTTRANSFER_TIME):
                #     curl_start_transfer_max = c.getinfo(c.STARTTRANSFER_TIME)
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
                # if curl_start_transfer_min > c.getinfo(c.STARTTRANSFER_TIME):
                #     curl_start_transfer_min = c.getinfo(c.STARTTRANSFER_TIME)
                if curl_total_transfer_min > c.getinfo(c.TOTAL_TIME):
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if curl_connect_min == -1:
                    curl_connect_min = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_min = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_min = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_min = c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_min = c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_min = c.getinfo(c.TOTAL_TIME)

                if not curl_connect_average == -1:
                    curl_connect_average += c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average += c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average += c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average += c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_average += c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_average += c.getinfo(c.TOTAL_TIME)
                else:
                    curl_connect_average = c.getinfo(c.CONNECT_TIME)
                    curl_lookup_average = c.getinfo(c.NAMELOOKUP_TIME)
                    curl_app_connect_average = c.getinfo(c.APPCONNECT_TIME)
                    curl_pre_transfer_average = c.getinfo(c.PRETRANSFER_TIME)
                    # curl_start_transfer_average = c.getinfo(c.STARTTRANSFER_TIME)
                    curl_total_transfer_average = c.getinfo(c.TOTAL_TIME)
                c.close()
            else:
                fail += 1

        except pycurl.error as e:
            logger.error("curlv4 - catching pycurl.error")
            logger.error("sending curl url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
            logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            logger.error("curlv4 - Unexpected error:" + str(e))
            logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            drop_pc += 100 / count
            c.close()
        except Exception as e:
            logger.error("curlv4 - Curl'ing to host")
            logger.error("curlv4 - Unexpected error:" + str(sys.exc_info()[0]))
            logger.error("curlv4 - Unexpected error:" + str(e))
            logger.error("curlv4 - TRACEBACK=" + str(traceback.format_exc()))
            drop_pc += 100 / count
            c.close()

    if success > 0:
        curl_connect_average = curl_connect_average / success
        curl_lookup_average = curl_lookup_average / success
        curl_pre_transfer_average = curl_pre_transfer_average / success
        # curl_start_transfer_average = curl_start_transfer_average / success
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

    # results += 'curlv6_start_transfer_Avg{host="%s"} %s\n' % (url, str("{:.4f}".format(float(curl_start_transfer_average))))
    # results += 'curlv6_start_transfer_Min{host="%s"} %s\n' % (url, str("{:.4f}".format(float(curl_start_transfer_min))))
    # results += 'curlv6_start_transfer_Max{host="%s"} %s\n' % (url, str("{:.4f}".format(float(curl_start_transfer_max))))

    results += 'curlv6_total_transfer_Avg{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_average)*1000)))
    results += 'curlv6_total_transfer_Min{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_min)*1000)))
    results += 'curlv6_total_transfer_Max{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, str("{:.4f}".format(float(curl_total_transfer_max)*1000)))

    results += 'curlv6_drop{host="%s",label="%s",dns="%s",group="%s"} %s\n' % (url, label, dns, group, drop_pc)

    return results


@flask_app.route('/probe_stats')
def get_stats():
    results = ""
    # results += process_hosts_in_serial()
    results += process_hosts_in_parallel()
    return Response(results, mimetype='text/plain')


def load_hosts_file_json():
    try:
        logger.debug("load_user_statistics_file_json - opening user statistics file")
        user_filename = ABSOLUTE_PATH + "hosts.json"
        with open(user_filename) as host_json_file:
            return_db_json = json.load(host_json_file)
        logger.debug("load_user_statistics_file_json - closing user statistics file")
        logger.debug("load_user_statistics_file_json - USERS_JSON =" + str(return_db_json))
        logger.info("load_user_statistics_file_json - " + "loaded USER JSON DB total EOL Records = " + str(len(return_db_json)))
        logger.debug("load_user_statistics_file_json - USERS_JSON =" + str(return_db_json.keys()))
        logger.debug("load_user_statistics_file_json - returning")
        return return_db_json
    except Exception as e:
        logger.error("load_user_statistics_file_json - something went bad opening user statistics file")
        logger.error("load_user_statistics_file_json - Unexpected error:" + str(sys.exc_info()[0]))
        logger.error("load_user_statistics_file_json - Unexpected error:" + str(e))
        logger.error("load_user_statistics_file_json - TRACEBACK=" + str(traceback.format_exc()))
    return {}


if __name__ == '__main__':
    # Create Logger
    logger = logging.getLogger("Python Monitor Logger")
    handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=LOGFILE_MAX_SIZE, backupCount=LOGFILE_COUNT)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("---------------------- STARTING ----------------------")
    logger.info("__main__ - " + "Python Monitor Logger")


    # GET_CURRENT_DB
    logger.info("__main__ - " + "GET_CURRENT_DB")
    HOSTS_DB = load_hosts_file_json()

    # build flask instance.
    logger.info("__main__ - " + "starting flask")
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()
