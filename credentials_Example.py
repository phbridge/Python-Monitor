ABSOLUTE_PATH = "/Users/phbridge/Documents/Git/Python-Monitor/"
FLASK_HOST = "::"
FLASK_PORT = 8050
LOGFILE = ABSOLUTE_PATH + "/Python-Monitor_%s.log" % FLASK_PORT
LOGCOUNT = 16
LOGBYTES = 16777216
INTERFACE = "ens192"
INFLUX_DB_Path = ["http://influx.co.uk:8086/write?db=PythonAssurance&u=<username>&p=<password>", "http://backup.co.uk:8086/write?db=PythonAssurance&u=<username>&p=<password>"]
FLASK_MODE = False
INFLUX_MODE = True