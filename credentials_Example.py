ABSOLUTE_PATH = "/app/"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 8050
LOGFILE = ABSOLUTE_PATH + "/Python-Monitor_%s.log" % FLASK_PORT
LOGCOUNT = 16
LOGBYTES = 16777216
INTERFACE = "ens192"
INFLUX_DB_Path = "http://<hostname>:<port>/write?db=<DBNAME>&u=<USERNAME>&p=<password>"
