# Copyright (c) 2015
# Author: Janne Posio

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# This script is intended to use with Adafruit DHT22 temperature and humidity sensors
# and with sensor libraries that Adafruit provides for them. This script alone, without
# sensor/s to provide data for it doesn't really do anyting useful.
# For guidance how to create your own temperature logger that makes use of this script,
# Adafruit DHT22 sensors and raspberry pi, visit :
# http://www.instructables.com/id/Raspberry-PI-and-DHT22-temperature-and-humidity-lo/

#!/usr/bin/python2
#coding=utf-8

import os
# import re
import sys
import datetime
from datetime import timedelta
import json
# import subprocess
import MySQLdb
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
# import DS18B20read
from w1thermsensor import W1ThermSensor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# function for converting sensor type name to sensor type numerical designation.
# Only needed because the w1thermsensor library doesn't let you pass the type
# name to __init__...
def getSensorTypeNum(typeString):
    conversion = {"DS18S20" : 0x10,
        "DS1822" : 0x22,
        "DS18B20" : 0x28,
        "DS1825" : 0x3B,
        "DS28EA00" : 0x42,
        "MAX31850K" : 0x3B}

    return conversion[typeString]

# function for getting weekly average temperatures.
def getWeeklyAverageTemp(sensor):

    weekAverageTemp = ""

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta = (datetime.date.today() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")

    try:
        sqlCommand = "SELECT AVG(temperature) FROM temperaturedata WHERE dateandtime BETWEEN '%s' AND '%s' AND sensor='%s'" % (delta,date,sensor)
        data = databaseHelper(sqlCommand,"Select")
        weekAverageTemp = "%.2f" % data
    except:
        pass

    return weekAverageTemp

# function that sends emails, either warning or weekly averages in order to see that pi is alive
def emailWarning(msg, msgType):

    configurations = getConfigurations()

    fromaddr = configurations["mailinfo"]["from_address"]
    toaddrs = configurations["mailinfo"]["to_address"]
    username = configurations["mailinfo"]["username"]
    password = configurations["mailinfo"]["password"]
    subj = configurations["mailinfo"]["subjectwarning"]

    if msgType is 'Info':
        subj = configurations["mailinfo"]["subjectmessage"]

    # Message to be sended with subject field
    message = 'Subject: %s\n\n%s' % (subj,msg)

    # The actual mail sending
    if configurations["mailinfo"]["enabled"]:
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()

    return

# helper function for database actions. Handles select, insert and sqldumpings. Update te be added later
def databaseHelper(sqlCommand,sqloperation):

    configurations = getConfigurations()

    host = configurations["mysql"]["host"]
    user = configurations["mysql"]["user"]
    password = configurations["mysql"]["password"]
    database = configurations["mysql"]["database"]
    backuppath = configurations["sqlbackuppath"]

    data = ""

    db = MySQLdb.connect(host,user,password,database)
        cursor=db.cursor()

    if sqloperation == "Select":
        try:
            cursor.execute(sqlCommand)
            data = cursor.fetchone()
          except:
            db.rollback()
    elif sqloperation == "SelectMany":
        try:
            cursor.execute(sqlCommand)
            data = cursor.fetchall()
        except:
            db.rollback()
    elif sqloperation == "Insert":
            try:
            cursor.execute(sqlCommand)
                    db.commit()
            except:
                    db.rollback()
                    emailWarning("Database insert failed", "")
            sys.exit(0)

    elif sqloperation == "Backup":
        # Getting current datetime to create seprate backup folder like "12012013-071334".
        date = datetime.date.today().strftime("%Y-%m-%d")
        backuppathoftheday = backuppath + date

        # Checking if backup folder already exists or not. If not exists will create it.
        if not os.path.exists(backuppathoftheday):
            os.makedirs(backuppathoftheday)

        # Dump database
        db = database
        dumpcmd = "mysqldump -u " + user + " -p" + password + " " + db + " > " + backuppathoftheday + "/" + db + ".sql"
        os.system(dumpcmd)

    return data

# function for checking log that when last warning was sended, also inserts new entry to log if warning is sent
def checkWarningLog(sensor, sensortemp):

    currentTime = datetime.datetime.now()
    currentTimeAsString = datetime.datetime.strftime(currentTime,"%Y-%m-%d %H:%M:%S")
    lastLoggedTime = ""
    lastSensor = ""
    triggedLimit = ""
    lastTemperature = ""
    warning = ""
    okToUpdate = False
    # sql command for selecting last send time for sensor that trigged the warning

    sqlCommand = "select * from mailsendlog where triggedsensor='%s' and mailsendtime IN (SELECT max(mailsendtime)FROM mailsendlog where triggedsensor='%s')" % (sensor,sensor)
    data = databaseHelper(sqlCommand,"Select")

    # If there weren't any entries in database, then it is assumed that this is fresh database and first entry is needed
    if data == None:
               sqlCommand = "INSERT INTO mailsendlog SET mailsendtime='%s', triggedsensor='%s', triggedlimit='%s' ,lasttemperature='%s'" % (currentTimeAsString,sensor,"0.0",sensortemp)
        databaseHelper(sqlCommand,"Insert")
        lastLoggedTime = currentTimeAsString
        lastTemperature = sensortemp
        okToUpdate = True
    else:
        lastLoggedTime = data[0]
        lastSensor = data[1]
        triggedLimit = data[2]
        lastTemperature = data[3]

    # check that has couple of hours passed from the time that last warning was sended.
    # this check is done so you don't get warning everytime that sensor is trigged. E.g. sensor is checked every 5 minutes, temperature is lower than trigger -> you get warning every 5 minutes and mail is flooded.
    try:
        delta = (currentTime - lastLoggedTime).total_seconds()
        passedTime = delta // 3600

        if passedTime > 2:
            okToUpdate = True
        else:
            pass
    except:
        pass

    # another check. If enough time were not passed, but if temperature has for some reason increased or dropped 5 degrees since last alarm, something might be wrong and warning mail is needed
    # TODO: Add humidity increase / decrease check as well...requires change to database as well.
    if okToUpdate == False:
        if "conchck" not in sensor:
            if sensortemp > float(lastTemperature) + 5.0:
                okToUpdate = True
                warning = "NOTE: Temperature increased 5 degrees"
            if sensortemp < float(lastTemperature) - 5.0:
                okToUpdate = True
                warning = "NOTE: Temperature decreased 5 degrees"

    return okToUpdate, warning

    # Function for checking limits. If temperature is lower or greater than limit -> do something
def checkLimits(sensor,sensorTemperature,sensorhighlimit,sensorlowlimit):

    check = True
    warningmsg = ""

    # check temperature measurements against limits
    if float(sensorTemperature) < float(sensorlowlimit):
        warningmsg = "Temperature low on sensor: {0}\nTemperature: {1}\nTemperature limit: {2}".format(sensor,sensorTemperature,sensorlowlimit)
        check = False
    elif float(sensorTemperature) > float(sensorhighlimit):
        warningmsg = "Temperature high on sensor: {0}\nTemperature: {1}\nTemperature limit: {2}".format(sensor,sensorTemperature,sensorhighlimit)
        check = False

    return check,warningmsg

    # helper function for getting configurations from config json file
def getConfigurations():

    path = os.path.dirname(os.path.realpath(sys.argv[0]))

    #get configs
    configurationFile = path + '/config.json'
    configurations = json.loads(open(configurationFile).read())

    return configurations

def main():

    configurations = getConfigurations()

    # Sensors
    sensors = [W1ThermSensor(getSensorTypeNum(s["type"]),s["id"]) for s in configurations["sensors"]]
    for i, s in enumerate(sensors):
        s.tag = configurations["sensors"][i]["tag"]
        s.id = configurations["sensors"][i]["id"]
        s.high_limit = float(configurations["sensors"][i]["high_limit"])
        s.low_limit = float(configurations["sensors"][i]["low_limit"])


    # Backup enabled
    backupEnabled = configurations["sqlBackupDump"]["backupDumpEnabled"]
    backupHour = configurations["sqlBackupDump"]["backupHour"]

    # Connection check enabled
    connectionCheckEnabled = configurations["connectionCheck"]["connectionCheckEnabled"]
    connectionCheckDay = configurations["connectionCheck"]["connectionCheckDay"]
    connectionCheckHour = configurations["connectionCheck"]["connectionCheckHour"]

    # Default value for message type, not configurable
    msgType = "Warning"

    d = datetime.date.weekday(datetime.datetime.now())
    h = datetime.datetime.now()

    # check if it is 5 o clock. If yes, take sql dump as backup
    if backupEnabled:
        if h.hour == int(backupHour):
            databaseHelper("","Backup")

    # check if it is sunday, if yes send connection check on 23.00
    if connectionCheckEnabled:
        if str(d) == str(connectionCheckDay) and str(h.hour) == str(connectionCheckHour):
            for sensor in sensors:
                okToUpdate = False
                #For better accuracy, or use mysql timestamp DEFAULT CURRENT_TIMESTAMP
                currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    sensorWeeklyAverage = getWeeklyAverageTemp(sensor.tag)
                    if sensorWeeklyAverage != None and sensorWeeklyAverage != '':
                        checkSensor = sensor.tag+" conchck"
                        okToUpdate, tempWarning = checkWarningLog(checkSensor,sensorWeeklyAverage)
                        if okToUpdate == True:
                            msgType = "Info"
                            Message = "Connection check. Weekly average from {0} is {1}".format(sensor.tag,sensorWeeklyAverage)
                            emailWarning(Message, msgType)
                            sqlCommand = "INSERT INTO mailsendlog SET mailsendtime='%s', triggedsensor='%s', triggedlimit='%s' ,lasttemperature='%s'" % (currentTime,checkSensor,sensor.low_limit,sensorWeeklyAverage)
                            databaseHelper(sqlCommand,"Insert")
                except:
                    emailWarning("Couldn't get average temperature to sensor: {0} from current week".format(sensor.tag),msgType)
                    pass

    # default message type to send as email. DO NOT CHANGE
    msgType = "Warning"


    # Sensor readings and limit check
    for sensor in sensors:
        okToUpdate = False
        sensorError = False
        #For better accuracy, or use mysql timestamp DEFAULT CURRENT_TIMESTAMP
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # only works for DS18B20...add some of the old code back in if you want to mix sensor types
            sensorTemperature = sensor.get_temperature(sensor.DEGREES_C)
            sensorTemperatureF = sensorTemperature * 1.8 + 32;

            print sensor.tag,"temp:",sensorTemperature,"tempF:",sensorTemperatureF
            limitsOk,warningMessage = checkLimits(sensor.tag,sensorTemperature,sensor.high_limit,sensor.low_limit)
        except:
            print sensor.tag,"failed to read"
            emailWarning("Failed to read {0} sensor".format(sensor.tag),msgType)
            sensorError = True
            pass

        if sensorError == False:
            try:
                # if limits were trigged
                if limitsOk == False:
                    # check log when was last warning sended
                    okToUpdate, tempWarning = checkWarningLog(sensor.tag,sensorTemperature)
            except:
                # if limits were triggered but something caused error, send warning mail to indicate this
                emailWarning("Failed to check/insert log entry from mailsendlog. Sensor: {0}".format(sensor.tag),msgType)
                sys.exit(0)

            if okToUpdate == True:
                # enough time has passed since last warning or temperature has increased/decreased by 5 degrees since last measurement
                warningMessage = warningMessage + "\n" + tempWarning
                # send warning
                emailWarning(warningMessage, msgType)
                try:
                # Insert line to database to indicate when warning was sent
                    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sqlCommand = "INSERT INTO mailsendlog SET mailsendtime='%s', triggedsensor='%s', triggedlimit='%s' ,lasttemperature='%s'" % (currentTime,sensor.tag,sensor.low_limit,sensorTemperature)
                    databaseHelper(sqlCommand,"Insert")
                except:
                    # if database insert failed, send warning to indicate that there is some issues with database
                    emailWarning("Failed to insert from {0} to mailsendlog".format(sensor.tag),msgType)

            # insert values to db
            try:
                sqlCommand = "INSERT INTO temperaturedata SET dateandtime='%s', sensor='%s', temperature='%s', temperature_f='%s'" % (currentTime,sensor.tag,sensorTemperature,sensorTemperatureF)
                # This row below sets temperature as fahrenheit instead of celsius. Comment above line and uncomment one below to take changes into use
                #sqlCommand = "INSERT INTO temperaturedata SET dateandtime='%s', sensor='%s', temperature='%s'" % (currentTime,sensor.tag,(sensorTemperatureF)
                databaseHelper(sqlCommand,"Insert")

               except:
                #sys.exit(0)
                #don't exit because of for loop
                print "Database error"

    sqlCommand = "SELECT dateandtime, temperature_f FROM temperaturedata WHERE dateandtime >= (NOW() - INTERVAL 12 HOUR) ORDER BY dateandtime"
    data = databaseHelper(sqlCommand,"SelectMany")
    outtimes = np.array([i[0] for i in data])
    output = np.array([i[1] for i in data])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(outtimes,output)
    xfmt = matplotlib.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(xfmt)
    ax.grid(True)
    fig.savefig('/var/www/html/test.svg')

if __name__ == "__main__":
    main()
