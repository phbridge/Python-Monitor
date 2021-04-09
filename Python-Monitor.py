# Copyright (c) 2021 Cisco and/or its affiliates.
#
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at
#
#                https://developer.cisco.com/docs/licenses
#
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

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

import logging.handlers             # Needed for logging
import time                         # Only for time.sleep
import credentials
import traceback
import sys
import json
import pycurl
import threading
import random
import requests
import datetime
import subprocess
import inspect


FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
FLASK_HOSTNAME = credentials.FLASK_HOSTNAME
LOGFILE = credentials.LOGFILE
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH

INFLUX_MODE = credentials.INFLUX_MODE
FLASK_MODE = credentials.FLASK_MODE

INTERFACE = credentials.INTERFACE
INFLUX_DB_PATH = credentials.INFLUX_DB_PATH
HOSTS_DB = {}

THREAD_TO_BREAK = threading.Event()


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


def load_hosts_file_json():
    function_logger = logger.getChild("%s.%s" % (inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        function_logger.debug("opening host file")
        user_filename = ABSOLUTE_PATH + "hosts.json"
        with open(user_filename) as host_json_file:
            return_db_json = json.load(host_json_file)
        function_logger.debug("closing host file")
        function_logger.debug("HOSTS_JSON=%s" % str(return_db_json))
        function_logger.info("host Records=%s" % str(len(return_db_json)))
        function_logger.debug("HOSTS=%s" % str(return_db_json.keys()))
        return return_db_json
    except Exception as e:
        function_logger.error("something went bad opening host file")
        function_logger.error("Unexpected error:%s" % str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:%s" % str(e))
        function_logger.error("TRACEBACK=%s" % str(traceback.format_exc()))
    return {}


def child_curl_v6(host_dictionary, offset=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "curl_v6"
    function_logger.debug(host_dictionary)
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    historical_upload = ""
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
    timestamp_string = str(int(future.timestamp()) * 1000000000)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    THREAD_TO_BREAK.wait(time_to_sleep)
    consecutive_error_count = 0
    while not THREAD_TO_BREAK.is_set():
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
                    consecutive_error_count = 0
                    c.close()
                    time.sleep(timeout / 4)
                else:
                    fail += 1
            except pycurl.error as e:
                function_logger.warning("catching pycurl.error")
                function_logger.warning("label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
                function_logger.warning("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.warning("Unexpected error:" + str(e))
                consecutive_error_count += 1
                if consecutive_error_count > 10:
                    function_logger.warning("consecutive errors on lable=%s error=%s" % (label, str(e)))
                    THREAD_TO_BREAK.wait(600)
                    consecutive_error_count = 0
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
        results = ""
        results += 'Python_Monitor,host=%s,target=%s,label=%s,dns=%s,group=%s,probe=%s,iface=%s ' \
                   'ConnectAvg=%s,ConnectMin=%s,ConnectMax=%s,LookupAvg=%s,LookupMin=%s,LookupMax=%s,' \
                   'PreTransferAvg=%s,PreTransferMin=%s,PreTransferMax=%s,TotalTransferAvg=%s,TotalTransferMin=%s,TotalTransferMax=%s,curlDrop=%s \n' % \
                   (FLASK_HOSTNAME, url, label, dns, group, probe_name, interface,
                    str("{:.2f}".format(float(curl_connect_average) * 1000)), str("{:.2f}".format(float(curl_connect_min) * 1000)), str("{:.2f}".format(float(curl_connect_max) * 1000)), str("{:.2f}".format(float(curl_lookup_average) * 1000)), str("{:.2f}".format(float(curl_lookup_min) * 1000)), str("{:.2f}".format(float(curl_lookup_max) * 1000)),
                    str("{:.2f}".format(float(curl_pre_transfer_average) * 1000)), str("{:.2f}".format(float(curl_pre_transfer_min) * 1000)), str("{:.2f}".format(float(curl_pre_transfer_max) * 1000)), str("{:.2f}".format(float(curl_total_transfer_average) * 1000)), str("{:.2f}".format(float(curl_total_transfer_min) * 1000)), str("{:.2f}".format(float(curl_total_transfer_max) * 1000)), drop_pc)
        to_send = ""
        for each in results.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.debug("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            historical_upload = ""
            function_logger.debug("adding to history")
            historical_upload += to_send
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
        timestamp_string = str(int(future.timestamp()) * 1000000000)

        time_to_sleep = (future - datetime.datetime.now()).seconds
        # if 30 > time_to_sleep > 0: # guess comit to fix timing thing
        if 29 > time_to_sleep > 0:  # guess comit to fix timing thing
            THREAD_TO_BREAK.wait(time_to_sleep)
        else:
            time.sleep(random.uniform(0, 1) * offset) # guess comit to fix timing thing
            THREAD_TO_BREAK.wait(90)
            function_logger.warning("had sleep time outside of valid range value was %s" % time_to_sleep)


def child_curl_v4(host_dictionary, offset=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "curl_v4"
    function_logger.debug(host_dictionary)
    url = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    historical_upload = ""
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
    timestamp_string = str(int(future.timestamp()) * 1000000000)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    THREAD_TO_BREAK.wait(time_to_sleep)
    consecutive_error_count = 0
    while not THREAD_TO_BREAK.is_set():
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
                    consecutive_error_count = 0
                    c.close()
                    time.sleep(timeout / 4)
                else:
                    fail += 1
            except pycurl.error as e:
                function_logger.warning("catching pycurl.error")
                function_logger.warning("label=" + label + " url=" + url + " count=" + str(count) + " timeout=" + str(timeout))
                function_logger.warning("Unexpected error:" + str(sys.exc_info()[0]))
                function_logger.warning("Unexpected error:" + str(e))
                consecutive_error_count += 1
                if consecutive_error_count > 10:
                    function_logger.warning("consecutive errors on lable=%s error=%s" % (label, str(e)))
                    THREAD_TO_BREAK.wait(600)
                    consecutive_error_count = 0
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
        results = ""
        results += 'Python_Monitor,host=%s,target=%s,label=%s,dns=%s,group=%s,probe=%s,iface=%s ' \
                   'ConnectAvg=%s,ConnectMin=%s,ConnectMax=%s,LookupAvg=%s,LookupMin=%s,LookupMax=%s,' \
                   'PreTransferAvg=%s,PreTransferMin=%s,PreTransferMax=%s,TotalTransferAvg=%s,TotalTransferMin=%s,TotalTransferMax=%s,curlDrop=%s \n' % \
                   (FLASK_HOSTNAME, url, label, dns, group, probe_name, interface,
                    str("{:.2f}".format(float(curl_connect_average) * 1000)), str("{:.2f}".format(float(curl_connect_min) * 1000)), str("{:.2f}".format(float(curl_connect_max) * 1000)), str("{:.2f}".format(float(curl_lookup_average) * 1000)), str("{:.2f}".format(float(curl_lookup_min) * 1000)), str("{:.2f}".format(float(curl_lookup_max) * 1000)),
                    str("{:.2f}".format(float(curl_pre_transfer_average) * 1000)), str("{:.2f}".format(float(curl_pre_transfer_min) * 1000)), str("{:.2f}".format(float(curl_pre_transfer_max) * 1000)), str("{:.2f}".format(float(curl_total_transfer_average) * 1000)), str("{:.2f}".format(float(curl_total_transfer_min) * 1000)), str("{:.2f}".format(float(curl_total_transfer_max) * 1000)), drop_pc)
        to_send = ""
        for each in results.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.debug("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            historical_upload = ""
            function_logger.debug("adding to history")
            historical_upload += to_send
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
        timestamp_string = str(int(future.timestamp()) * 1000000000)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        # if 30 > time_to_sleep > 0: guess comit to fix timing thing
        if 29 > time_to_sleep > 0: # guess comit to fix timing thing
            THREAD_TO_BREAK.wait(time_to_sleep)
        else:
            time.sleep(random.uniform(0, 1) * offset)  # guess comit to fix timing thing
            THREAD_TO_BREAK.wait(90)
            function_logger.warning("child_curl_v4 - had sleep time outside of valid range value was %s" % time_to_sleep)


def child_icmp_ping_v6(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "icmp_ping_v6"
    function_logger.debug(host_dictionary)
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    historical_upload = ""
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
    timestamp_string = str(int(future.timestamp()) * 1000000000)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    THREAD_TO_BREAK.wait(time_to_sleep)
    while not THREAD_TO_BREAK.is_set():
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
        results = ""
        results += 'Python_Monitor,host=%s,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,iface=%s latencyAvg=%s,latencyMin=%s,latencyMax=%s,latencyDroppc=%s \n' % \
                   (FLASK_HOSTNAME, hostname, label, tos, dns, group, probe_name, interface, str("{:.2f}".format(float(latency_average))), str("{:.2f}".format(float(latency_min))), str("{:.2f}".format(float(latency_max))), drop_pc)
        to_send = ""
        for each in results.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.debug("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            historical_upload = ""
            function_logger.debug("adding to history")
            historical_upload += to_send
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
        timestamp_string = str(int(future.timestamp()) * 1000000000)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)
        time.sleep(random.uniform(0, 1) * offset)


def child_icmp_ping_v4(host_dictionary, offset=10):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    probe_name = "icmp_ping_v4"
    function_logger.debug(host_dictionary)
    hostname = host_dictionary['address']
    count = int(host_dictionary['count'])
    timeout = int(host_dictionary['timeout'])
    tos = host_dictionary['TOS']
    label = host_dictionary['label']
    dns = host_dictionary['DNS']
    group = host_dictionary['group']
    historical_upload = ""
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
    timestamp_string = str(int(future.timestamp()) * 1000000000)
    time_to_sleep = (future - datetime.datetime.now()).seconds
    THREAD_TO_BREAK.wait(time_to_sleep)
    while not THREAD_TO_BREAK.is_set():
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
        results = ""
        results += 'Python_Monitor,host=%s,target=%s,label=%s,tos=%s,dns=%s,group=%s,probe=%s,iface=%s latencyAvg=%s,latencyMin=%s,latencyMax=%s,latencyDroppc=%s \n' % \
                   (FLASK_HOSTNAME, hostname, label, tos, dns, group, probe_name, interface, str("{:.2f}".format(float(latency_average))), str("{:.2f}".format(float(latency_min))), str("{:.2f}".format(float(latency_max))), drop_pc)
        to_send = ""
        for each in results.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.debug("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            historical_upload = ""
            function_logger.debug("adding to history")
            historical_upload += to_send
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
        timestamp_string = str(int(future.timestamp()) * 1000000000)
        time_to_sleep = (future - datetime.datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)
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


def update_influx(raw_string, timestamp=None):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    try:
        string_to_upload = ""
        if timestamp is not None:
            timestamp_string = str(int(timestamp.timestamp()) * 1000000000)
            for each in raw_string.splitlines():
                string_to_upload += each + " " + timestamp_string + "\n"
        else:
            string_to_upload = raw_string
        success_array = []
        upload_to_influx_sessions = requests.session()
        for influx_path_url in INFLUX_DB_PATH:
            success = False
            attempts = 0
            attempt_error_array = []
            while attempts < 5 and not success:
                try:
                    upload_to_influx_sessions_response = upload_to_influx_sessions.post(url=influx_path_url, data=string_to_upload, timeout=(2, 1))
                    if upload_to_influx_sessions_response.status_code == 204:
                        function_logger.debug("content=%s" % upload_to_influx_sessions_response.content)
                        function_logger.debug("status_code=%s" % upload_to_influx_sessions_response.status_code)
                        success = True
                    else:
                        attempts += 1
                        function_logger.warning("status_code=%s" % upload_to_influx_sessions_response.status_code)
                        function_logger.warning("content=%s" % upload_to_influx_sessions_response.content)
                except requests.exceptions.ConnectTimeout as e:
                    attempts += 1
                    function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Timeout")
                    function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.debug("update_influx - Unexpected error:" + str(e))
                    function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                except requests.exceptions.ConnectionError as e:
                    attempts += 1
                    function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Error")
                    function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.debug("update_influx - Unexpected error:" + str(e))
                    function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                except Exception as e:
                    function_logger.error("update_influx - attempted " + str(attempts) + " Failed")
                    function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.error("update_influx - Unexpected error:" + str(e))
                    function_logger.error("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                    break
            success_array.append(success)
        upload_to_influx_sessions.close()
        super_success = False
        for each in success_array:
            if not each:
                super_success = False
                break
            else:
                super_success = True
        if not super_success:
            function_logger.error("update_influx - FAILED after 5 attempts. Failed up update " + str(string_to_upload.splitlines()[0]))
            function_logger.error("update_influx - FAILED after 5 attempts. attempt_error_array: " + str(attempt_error_array))
            return False
        else:
            function_logger.debug("update_influx - " + "string for influx is " + str(string_to_upload))
            function_logger.debug("update_influx - " + "influx status code is  " + str(upload_to_influx_sessions_response.status_code))
            function_logger.debug("update_influx - " + "influx response is code is " + str(upload_to_influx_sessions_response.text[0:1000]))
            return True
    except Exception as e:
        function_logger.error("update_influx - something went bad sending to InfluxDB")
        function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("update_influx - Unexpected error:" + str(e))
        function_logger.error("update_influx - TRACEBACK=" + str(traceback.format_exc()))
    return False


if __name__ == '__main__':
    # Create Logger
    logger = logging.getLogger("Python_Monitor")
    logger_handler = logging.handlers.TimedRotatingFileHandler(LOGFILE, backupCount=30, when='D')
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
    if INFLUX_MODE:
        master_thread_icmp_ping_v4 = threading.Thread(target=lambda: master_icmp_ping_v4_probe_stats())
        master_thread_icmp_ping_v6 = threading.Thread(target=lambda: master_icmp_ping_v6_probe_stats())
        master_thread_curl_v4 = threading.Thread(target=lambda: master_curl_v4_probe_stats())
        master_thread_curl_v6 = threading.Thread(target=lambda: master_curl_v6_probe_stats())
        master_thread_icmp_ping_v4.start()
        master_thread_icmp_ping_v6.start()
        master_thread_curl_v4.start()
        master_thread_curl_v6.start()

