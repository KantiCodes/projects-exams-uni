# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pandas as pd
import DataHandlingLibrary.DataHandlingMethods as dataH
import pytz

# Date format that is used to cast date strings to dates
dateFormat = "%Y-%m-%dT%H:%M:%S"

def getERPDataForThePeroid(timeIntervalToLookBack):
    #        ERPurlEnd = "productionsbyinterval/"

    #        try:
    end = "";
    timeInterval = timeIntervalToLookBack
    timeInterval = timedelta(seconds=timeInterval)

    if end != "":
        endDateTime = datetime.strptime(end, dateFormat)
        tempBefTime = dataH.denmarkDateNow()
        beforeTime = tempBefTime - endDateTime
    else:
        beforeTime = timedelta(seconds=0)
    # print("beforeTime : " , beforeTime)
    now = dataH.offSetAware(dataH.denmarkDateNow())
    now = now - beforeTime
    past = now - timeInterval

    current_time = now.strftime(dateFormat)
    current_past = past.strftime(dateFormat)

    # constructing api url for time interval
    url = (dolleCoreApi + ERPurlEnd + current_past + ',' + current_time)
    # print("Searching in Interval :",current_past , "--", current_time)
    print(url)

    # requesting data from api

    response = dataH.authenticateToken(url)

    data = response.json()
    #        print ("the data is : " , data)
    print("time from get data from peroid  :", now)
    return data, current_time


# Method returns all of the ERP data
def getAllERPData():
    url = dolleCoreApi + "productions"
    # print("Searching in Interval :",current_past , "--", current_time)
    #print(url)
    # requesting data from api
    response = dataH.authenticateToken(url)

    data = response.json()
    #        print ("the data is : " , data)
    # print ("time from get data from peroid  :", now )
    return data



# Method returns ERP data of the product that is currently being produced, specify machine as an input parameter
# laddermachine1 = res 1405  /  laddermachine2 = res 1404
def get_latest_product_data(machine_name,erp):
    
    data = erp
    df = pd.DataFrame(data=data)
    df.drop(columns=['_id', '__v', 'pack_group_id'], inplace=True);

    df = df[df['starttime'] > df['stoptime']]

    df1 = df[(df['machine_id'] == '1405') & (df['active'])]
    df2 = df[(df['machine_id'] == '1404') & (df['active'])]
    df1 = df1.sort_values(by='starttime').tail()
    df2 = df2.sort_values(by='starttime').tail()

    if machine_name == "laddermachine1":
        return df1.iloc[-1]
    else:
        return df2.iloc[-1]


# these are the methods to return specific value of the erp data, that has to be supplemented with latest ERP data

# returns name of the product
def get_name(erp_data):
    return erp_data['name']


# returns the jobid
def get_jobid(erp_data):
    return erp_data['jobid']


# returns production type
def get_production_type(erp_data):
    return erp_data['production_type']


# returns production id
def get_production_id(erp_data):
    return erp_data['production_id']


# returns machine id
def get_laddermachine_id(erp_data):
    return erp_data['machine_id']


# returns the actual start time of the job
def get_actual_start_time(erp_data):
    actual_start = erp_data['starttime'][:-5]
    actual_start = datetime.strptime(actual_start, dateFormat) + timedelta(
        hours=dataH.current_time_difference())
    # actual_start=erp_data['starttime'] + timedelta(hours=dataH.current_time_difference())
    # actual_start=erp_data['starttime'] + timedelta(hours=dataH.current_time_difference())
    # print('[this is bullls sihet', actual_start)
    actual_start = datetime.strftime(actual_start, dateFormat)
    return actual_start


# returns scheduled work time in seconds
def get_scheduled_work_time(erp_data):
    start = datetime.strptime(get_planned_start_time(erp_data), dateFormat)
    stop = datetime.strptime(get_planned_stop_time(erp_data), dateFormat)
    scheduled_time = (stop - start).seconds / 60
    print(type(scheduled_time))
    print('scheduled time',scheduled_time)
    return scheduled_time


# returns the predicted stop time of the job
def get_predicted_stop_time(erp_data):
    actual_start = get_actual_start_time(erp_data)
    scheduled_time_minutes = get_scheduled_work_time(erp_data)
    # brake_time = get_brake_time(erp_data)
    predicted_stop = datetime.strptime(actual_start, dateFormat) \
            + timedelta(hours=scheduled_time_minutes/60)

    predicted_stop = datetime.strftime(predicted_stop,dateFormat)
    return predicted_stop


# returns the planned start time of the job
def get_planned_start_time(erp_data):
    planned_start = erp_data['from'][:-5]
    planned_start = datetime.strptime(planned_start, dateFormat) + timedelta(
        hours=dataH.current_time_difference())
    planned_start = datetime.strftime(planned_start, dateFormat)

    return planned_start


# returns the planned stop time of the job
def get_planned_stop_time(erp_data):
    planned_stop = erp_data['to'][:-5]
    planned_stop = datetime.strptime(planned_stop, dateFormat) + timedelta(
        hours=dataH.current_time_difference())
    planned_stop = datetime.strftime(planned_stop, dateFormat)

    return planned_stop


# returns the corrected start time of the job
def get_corrected_start_time(erp_data):
    return erp_data['c_start']


# returns the corrected stop time of the job
def get_corrected_stop_time(erp_data):
    return erp_data['c_stop']


# Method returns approx. time of the brakes scheduled for specific job
# def get_scheduled_brake_time(start_date, end_date):

# Method returns approx. time of the brakes scheduled for specific job
def get_scheduled_brake_time(planned_start, planned_stop):
    #
    regular_brakes = {
        'work-time': [],
        'morning': [9.00, 9.20],
        'noon': [12.00, 12.25],
        'afternoon': [18.30, 18.55],
        'evening': [21.30, 21.50]
    }
    # datetime(year, month, day)
    nineAM = ' date at nice am'
    twelveAM = ' date at twelve am'
    six_thirtyPM = 'date at six thirty pm'
    nine_thirtyPM = 'date at nine thirty pm'

    if planned_start < nineAM:
        if (planned_stop > nineAM & planned_stop < twelveAM):
            pass
        if (planned_stop > twelveAM & planned_stop < 'evening brake'):
            pass
        # if planned_stop > twelveAM



# data=getAllERPData()
# data = get_latest_product_data('laddermachine1',data)
# print(data)
# print (get_predicted_stop_time(data))
# date = get_corrected_start_time(data)
# print(datetime.strptime(date[:-5],"%Y-%m-%dT%H:%M:%S"))
