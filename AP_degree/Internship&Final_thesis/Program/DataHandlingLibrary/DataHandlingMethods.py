import requests
import json
from datetime import datetime, timezone, timedelta
import pandas as pd
import pytz

dateFormat = "%Y-%m-%dT%H:%M:%S"

# ------------------Methods for handling data and creating environment to manipulate data----------------------
def _createDictionaries(numberOfPorts):
    portsNames = []
    for i in range(numberOfPorts):
        portsNames.append(str(i + 1))
        # Dictionary for holding the ports that are supposed to be count in given interval
    ports = {}
    # Dictionary for holding the ports that are supposed to be updated ( wont be reset after the main method)
    # Dictionary for the newset occurence of the specific port
    currentStamps = {}
    # Dictionary for the oldest occurence of the specific port
    latestStamps = {}
    # Dictionary for difference between machine on occurrence
    diff = {}

    checkOutStamps = {}

    for i in portsNames:
        ports[i] = 0
        currentStamps[i] = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
        latestStamps[i] = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
        diff[i] = 0
        checkOutStamps[i] = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    return ports, currentStamps, latestStamps, diff, checkOutStamps


# -------------------Call API to get sensor data from the desired time period-------------------------
def getDataForThePeroid(timeIntervalToLookBack, rightSearchTimeInterval, machineName):
    #        try:
    end = rightSearchTimeInterval
    timeInterval = timeIntervalToLookBack
    timeInterval = timedelta(seconds=timeInterval)
    #        except:
    #            print ('invalid timeinterval')
    #            #logging.exception("%s time interval exception",self.machineName)
    #            logging.warning('\n')

    # end = self.constructDate(2019,9,2,9,30,0)
    if end != "":
        endDateTime = datetime.strptime(end, dateFormat)
        tempBefTime = denmarkDateNow()
        beforeTime = tempBefTime - endDateTime
    else:
        beforeTime = timedelta(seconds=0)
    # print("beforeTime : " , beforeTime)
    now = offSetAware(denmarkDateNow())
    now = now - beforeTime
    past = now - timeInterval

    current_time = now.strftime(dateFormat)
    current_past = past.strftime(dateFormat)

    # constructing api url for time interval
    url = (dolleCoreApi + machineName + urlEnd + current_past + ',' + current_time)
    # print("Searching in Interval :",current_past , "--", current_time)
    #print(url)

    # requesting data from api

    response = authenticateToken(url)

    data = response.json()
    #        print ("the data is : " , data)
    #print("time from get data from peroid  :", now)
    return data, current_time


def get_all_sensor_data(machineName):
    url = (dolleCoreApi + machineName + "/inputreadings")
    # print("Searching in Interval :",current_past , "--", current_time)
    print(url)

    # requesting data from api

    response = authenticateToken(url)

    data = response.json()


def authenticateToken(url):
    myToken = 'DASHBOARDKEY'
    myUrl = url
    head = {'Authorization': 'token {}'.format(myToken)}
    response = requests.get(myUrl, headers=head)
    return response


def getDataFromAlreadyLoadedData(data, endTime, newInterval):
    # take already loaded data
    newInterval = timedelta(seconds=newInterval)
    df = pd.DataFrame.from_records(data)
    selectedData = [dat for dat in df if dat['timestamp'] > (endTime - newInterval)]
    # take end time when interval was called
    # (End time - selectedSeconds) = newTs
    # newdata = data where timestamp > newTs
    return selectedData


# -------------------Call API to get ERP data from the desired time period-------------------------

# ---------------Convert Json format into variables that can be handled by python-----------

def parseFromJson(data):
    # Parsing requested json format
    convertToJson = json.dumps(data)
    parseJson = json.loads(convertToJson)
    port = parseJson["port"]
    value = parseJson["value"]
    timeStamp = parseJson["timestamp"]
    # Making timestamp format from string
    timStamp = datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    # Selecting data for specific sensor
    return port, value, timStamp


# ------------------Convert dataframe elements to Json-------------------

def fromRowToJson(row, HEADER):
    data_raw = []
    data_raw.append(row)
    data_df = pd.DataFrame(data_raw, columns=HEADER)
    data_json = bytes(data_df.to_json(orient='records'), encoding='utf-8')
    return data_json


# ----------------Convert offset aware datetime to offset naive datetime----------

def offSetAware(date):
    string = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    datetimeOffsetAware = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return datetimeOffsetAware


# this method posts to certain powerBI api using Json formatted data
def pushToPowerBI(BIURL, data_json):
    req = requests.post(BIURL, data_json)


# Returns a date string , required fields : year,month,day,hour,minute,second
def constructDate(year, month, day, hour, minute, second):
    if month < 10:
        month = "0" + str(month)
    if day < 10:
        day = "0" + str(day)
    if hour < 10:
        hour = "0" + str(hour)
    if minute < 10:
        minute = "0" + str(minute)
    if second < 10:
        second = "0" + str(second)
    dateString = str(year) + "-" + str(month) + "-" + str(day) + "T" + str(hour) + ":" + str(minute) + ":" + str(second)
    return dateString


def orderData(data, machineName):
    if machineName == "laddermachine1":
        return data
    else:
        return reversed(data)


def checkTrueFalseOrder(listOfTrueFalses):
    indexOfBad = []
    for index, element in enumerate(listOfTrueFalses):

        if listOfTrueFalses[index] == listOfTrueFalses[index - 1]:
            indexOfBad.append(index)

    if len(indexOfBad) > 0:
        return False, indexOfBad, 'Incorrect'
    else:
        return True, indexOfBad, 'Correct'


def denmarkDateNow():
    ddate = datetime.now(pytz.timezone('Europe/Copenhagen'))
    return ddate


def dateToDenmarkDate(date):
    tz = pytz.timezone('Europe/Copenhagen')
    z = offSetAware(date)
    z = tz.localize(z)
    return z


def current_time_difference():
    now = denmarkDateNow()
    utcnow = datetime.now(pytz.timezone('Etc/Greenwich'))
    timediff = (now.hour-utcnow.hour)
    return timediff
