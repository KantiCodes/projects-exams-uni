# this file contains functionality shared among both classes-----------------------------
from datetime import datetime, timezone, timedelta
import DataHandlingLibrary.DataHandlingMethods as dataH
import pytz

# ----------------------CLASS INITIALIZATION-----------------------------------------------------


# -----------------------------------------------------------------------------
class LadderMachine:
    #    almostEndOfTheDay = datetime.time(23,45,00)
    # Dolles API parts
    dateFormat = "%Y-%m-%dT%H:%M:%S"

    # Used for resetting the port
    date2015 = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)

    

    # Initialize method

    def __init__(self, machineName, numberOfPorts, timeInterval):
        
        #Save machine string for later API requests
        self.machineName = machineName
        
        #assign basic values to the ports
        self.ports, self.currentStamps, self.latestStamps, self.diff, self.checkOutStamps = dataH._createDictionaries(
            numberOfPorts)
        
        #Refresh rate of the data
        self.timeInterval = timeInterval
        
        #Asssume machine is working
        self.currentPowerState = 1
        
        #Initial value of posting to the sql
        self.lastPostedToSql = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)



    # Creates 3 dictionaries to store values and stamps of each of the ports

    # Updates values to std dictionary
    def setSTD(self, lowerBorder, upperBorder):
        #        try:
        std = {
            "lowerBorder": 0,
            "upperBorder": 0
        }
        std['lowerBorder'] = lowerBorder
        std['upperBorder'] = upperBorder
        return std

    # Update for the entire ports dictionary to 0
    def _resetPortsValues(self):
        #        try:
        self.ports = dict.fromkeys(self.ports, 0)
        self.currentStamps = dict.fromkeys(self.currentStamps, self.date2015)
        self.latestStamps = dict.fromkeys(self.latestStamps, self.date2015)

    #        except:
    #            print("reseting ports valyes exception occured")
    #            logging.exception("%s reseting ports values exception occured",self.machineName)
    #            logging.warning('\n')
    #
    # Method handling the state of the machine - if its working or not
    def setCurrentPowerStateValue(self, value, timeStamp):
        print("value is ", value)
        if value == True:
            self.currentPowerState = 1
            print("true from def ")
        else:
            self.currentPowerState = 0
            print("false from def ")

    #        except:
    #            print("setting current state value failed")
    #            logging.exception("%s setCurrentStateValue exception occured",self.machineName)
    #            logging.warning('\n')

    # Traverse a data and updates the ports values
    def AssignValuesToPorts(self, dataFromNoSQL):
        pass

    # This method catches the number of ports triggered with value true in timeinterval
    def setTimeAndPort(self, portID, timStamp, action, value):
        #        print(self.ports)
        #        print("port id " , portID)

        if action == 'count':
            self.ports[portID] = self.ports.get(portID) + 1

        if action == 'update':
            if value == True:
                self.ports[portID] = 1
            elif value == False:
                self.ports[portID] = 0

        self.currentStamps[portID] = timStamp

    #
    def setLatestPort(self, port, timStamp):
        port = port[-1]
        self.checkOutStamps[port] = timStamp

    #
    #
    # Assigns headers to the row and changes the format of the data into json and assigns    

    def checkOutPut(self):
        try:
            ctd = dataH.current_time_difference()
            data, timeToPost = dataH.getDataForThePeroid(30, "", self.machineName)
            data = dataH.orderData(data, self.machineName)
            lastTurnOffStamp = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
            #        data, timeToPost= self.getDataForThePeroid(30,"")

            # print(data)

            for dat in data:

                port, value, timStamp = dataH.parseFromJson(dat)

                if value == True:
                    self.setLatestPort(port, datetime.strptime(timStamp.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                                                               "%Y-%m-%dT%H:%M:%S.%f%z") + timedelta(hours=ctd))

                if port[-1] == "1" and value == True:
                    lastTurnOffStamp = datetime.strptime(timStamp.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                                                         "%Y-%m-%dT%H:%M:%S.%f%z") + timedelta(hours=ctd)
        except :
            print("error")

        for i in self.checkOutStamps:
            try:
                if (lastTurnOffStamp - self.checkOutStamps[i]).total_seconds() > 0:
                    self.diff[i] = 0
                    self.checkOutStamps[i] = datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc)

                if self.checkOutStamps[i] != datetime(2015, 1, 1, 1, 1, 1, tzinfo=timezone.utc):
                    self.diff[i] = (dataH.offSetAware(dataH.denmarkDateNow()) - self.checkOutStamps[i]).total_seconds()
                else:
                    self.diff[i] = 0
                a = int(self.diff[i])
                print(a)

            except:
                print("error with: ")
