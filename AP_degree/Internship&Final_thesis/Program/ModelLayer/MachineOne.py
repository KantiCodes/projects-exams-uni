#this is a class for handling internal logic of laddermachine nr 2

from ModelLayer.BasicFunctionality import LadderMachine
import DataHandlingLibrary.DataHandlingMethods as dataH
import DataHandlingLibrary.ERPHandling as erpH
from datetime import datetime,timedelta,timezone
import pandas as pd


class MachineOne(LadderMachine):
    """ Class representing first machine of the production"""
    std = {}
    HEADER = []
    
    
    
    def __init__(self,timeInterval):
    
        #Parent contructor
        super(MachineOne, self).__init__("laddermachine1",6,timeInterval)
        
        #Gauge ranges
        #TODO find out specific values from ERP and sensor
        self.std= self.setSTD(8*4,12*4)
        
        #Port names
        self.HEADER = ["MachineOn","PaceIn","PaceOut","StringError","ScrewError",
                      "Allarm","DateNow","lowerBorder","upperBorder"]
                      
        #
        self.erp,self.cr = erpH.getERPDataForThePeroid(60*60*24*1)
        if len(self.erp) > 0:
            self.latestJobid = erpH.get_jobid(erpH.get_latest_product_data("laddermachine1",self.erp))
        else:
            self.latestJobid = '111111'
        self.lastEndTime = datetime(2015,1,1,1,1,1)
        self.output,self.firstEndTime = 0,datetime(2015,1,1,1,1,1)
        self.lastError = datetime(2015,1,1,1,1,1)
        self.last_error_type = 'none'
        self.onOrOff = "empty"
        self.output_recent = datetime(2015,1,1,1,1,1)
    

    

    def AssignValuesToPorts(self,dataFromNoSQL):
            if len(dataFromNoSQL) > 0:
                dataFromNoSQL = dataH.orderData(dataFromNoSQL,self.machineName)
                for dat in  (dataFromNoSQL):
                    #print("helo from firstfor" )
                    port,value,timStamp = dataH.parseFromJson(dat)
    #               Keep track of machine power status
                    portID = str(port[-1])
#                    print("port id from machine 1" , portID)
#                    print (self.ports )
                    if portID == '1'or portID == '4' or portID == '5' or portID == '6':
                        self.setTimeAndPort(portID,timStamp,'update',value)
                    
                    elif value:
                        self.setTimeAndPort(portID,timStamp,'count',value)
            else:
                print("no data has be found in given peroid")
            
 
            

    def output_cj(self,data):
        erp = data
        latestJobId = erpH.get_jobid(erpH.get_latest_product_data("laddermachine1",erp))
        
        
        if latestJobId == self.latestJobid:
            #first time the script runs
#            print('first if')
            if self.lastEndTime == datetime(2015,1,1,1,1,1):
#                print('second if')
                self.output,self.firstEndTime = self.outPutForCurrentJobOnce(erp)
                dNow = dataH.denmarkDateNow()
                tempTimeToLook = (dNow-self.firstEndTime).total_seconds()
                data,cr = dataH.getDataForThePeroid(tempTimeToLook,"","laddermachine1")
                
#                print('first time')
            else:
#                print('first else')
                dNow = dataH.denmarkDateNow()
                tempTimeToLook = (dNow-self.lastEndTime).total_seconds()
                data,cr = dataH.getDataForThePeroid(tempTimeToLook,"","laddermachine1")
                
#                print('not first time')
            df = pd.DataFrame(data,columns=['_id','timestamp','port','value','__v'])
            newdf = df[((df['port']=='0103') & (df['value']==True))]
            self.output = self.output + len(newdf)
            print('output:' ,self.output,'dflength:', len(newdf))
            self.lastEndTime = dNow
            return self.output
            
        else:
#            print('seconds else')
            self.latestJobid = latestJobId
            self.output,self.firstEndTime = self.outPutForCurrentJobOnce(erp)
            dNow = dataH.denmarkDateNow()
            tempTimeToLook = (dNow-self.firstEndTime).total_seconds()
            data,cr = dataH.getDataForThePeroid(tempTimeToLook,"","laddermachine1")
            df = pd.DataFrame(data,columns=['_id','timestamp','port','value','__v'])
            newdf = df[((df['port']=='0103') & (df['value']==True))]
            self.output = self.output + len(newdf)
            self.lastEndTime = dNow
            return self.output
        
    def outPutForCurrentJobOnce(self,data_erp):

        erp = erpH.get_latest_product_data("laddermachine1",data_erp)
        startOfJobDateString = erpH.get_actual_start_time(erp)
        startDate = datetime.strptime(startOfJobDateString, "%Y-%m-%dT%H:%M:%S")
        startDate = dataH.dateToDenmarkDate(startDate)
        d = dataH.denmarkDateNow()
        timeToLook = (d - startDate).total_seconds()
        data, cr = dataH.getDataForThePeroid(timeToLook, "", "laddermachine1")
        dataForLatestJob = pd.DataFrame(data)
        dataForLatestJob = dataForLatestJob[((dataForLatestJob['port'] == '0103') & (dataForLatestJob['value'] == True))]
        outputOfCurrentJob = len(dataForLatestJob)
        return outputOfCurrentJob, d
            
    def searchForMachineDowntime(self,data,timeInterval1):
    #print("search started")
        
#        print(data)
        end = dataH.denmarkDateNow().strftime("%Y-%m-%dT%H:%M:%S")
        if len(data) > 0:
    
            listOfDowntimes = []
            row = []
            
            for dat in data:
                
                port,value,timStamp = dataH.parseFromJson(dat)
                row = self.getDownTime(port,value,timStamp)
                if len(row) != 0:
                    
                    listOfDowntimes.append(row)
    
            tempL = []
            tempTimeDt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
            begin = tempTimeDt-timedelta(seconds=timeInterval1)
            beginString = begin.strftime("%Y-%m-%dT%H:%M:%S")
            for l in listOfDowntimes:
                tempL.append(l)
            #print(tempL)
            if len(tempL) > 0:
                if tempL[0][1] == True:
                    tempL.insert(0,[beginString,False])
                if tempL[-1][1] == False:
                    tempL.insert(len(tempL),[end,True])
            i = 0
            j = 1
            newList = []
            newRow = []
            size = len(tempL)
            rangeOfLoop = size//2
            #print(rangeOfLoop)
            for x in range(rangeOfLoop):
                newRow = [tempL[i][0],tempL[j][0]]
                newList.append(newRow)
                i = i+2
                j = j+2
    
            return newList,tempL
        else:
            return 0,0
        
    def searchForMachineDowntimeMorningStart(self,data,timeInterval1):
        #print("search started")
        
#        print(data)
        end = dataH.denmarkDateNow().strftime("%Y-%m-%dT%H:%M:%S")
        if len(data) > 0:

            listOfDowntimes = []
            row = []
            
            for dat in data:
                
                port,value,timStamp = dataH.parseFromJson(dat)
                row = self.getDownTime(port,value,timStamp)
                if len(row) != 0:
                    
                    listOfDowntimes.append(row)

            tempL = []
            #tempTimeDt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
            #begin = tempTimeDt-timedelta(seconds=timeInterval1)
           # beginString = begin.strftime("%Y-%m-%dT%H:%M:%S")
            for l in listOfDowntimes:
                tempL.append(l)
            #print(tempL)
            if len(tempL) > 1:
                if tempL[0][1] == True:
                    del tempL[:1]
                if tempL[-1][1] == False:
                    tempL.insert(len(tempL),[end,True])
            i = 0
            j = 1
            newList = []
            newRow = []
            size = len(tempL)
            rangeOfLoop = size//2
            #print(rangeOfLoop)
            for x in range(rangeOfLoop):
                newRow = [tempL[i][0],tempL[j][0]]
                newList.append(newRow)
                i = i+2
                j = j+2

            return newList,tempL
            
    def getDownTime(self,port,value,timestamp):
        timediff = dataH.current_time_difference()
        row = []
        if port == "0101" and value == True :
            gmtTs = timestamp + timedelta(hours=timediff)
            ts = gmtTs.strftime("%Y-%m-%dT%H:%M:%S")
            row = [ts,value]
            return row
        if port == "0101" and value == False :
            gmtTs = timestamp + timedelta(hours=timediff)
            ts = gmtTs.strftime("%Y-%m-%dT%H:%M:%S")
            row = [ts,value]
            return row
        else:
            return row
        
    def getDtFromTimeInterval(self,TimeInterval,listOf):
        sumOf = 0
        if listOf is not None:
            for l in listOf:
                tim1 = l[0]
                tim2 = l[1]
                tim1date = datetime.strptime(tim1, "%Y-%m-%dT%H:%M:%S")
                tim2date = datetime.strptime(tim2, "%Y-%m-%dT%H:%M:%S")
                sumOf = sumOf + (tim2date - tim1date).total_seconds()
                #print((tim2date - tim1date).total_seconds())

        #print("The percentage of time the machine was down in the given interval is:",(sumOf/TimeInterval)*100,"%")
        #print("The percentage the machine was down deducting the planned breaks: ",((sumOf-3600)/TimeInterval)*100,"%")
        return sumOf
                
    def time_since_last_error(self,dataS):
        timedif = dataH.current_time_difference()
        data = dataS
        df= pd.DataFrame(data,columns=['_id','timestamp','port','value','__v'])
        df_fail = df[(df['port']=='0104') | (df['port']=='0105')]
        if len(df_fail) > 0:
            last_fail_time = df_fail['timestamp'].iloc[-1]
            self.last_error_type = df_fail['port'].iloc[-1]
            self.lastError = datetime.strptime(last_fail_time,"%Y-%m-%dT%H:%M:%S.%fZ")
        if self.lastError == datetime(2015,1,1,1,1,1):
            time_since_last_error = 'IKKE TIL'
        else:
            time_since_last_error = str((dataH.denmarkDateNow()-dataH.dateToDenmarkDate(self.lastError)-timedelta(hours=timedif)).total_seconds())
        if self.last_error_type == '0104' :
            a = 'String fejl'
        if self.last_error_type == '0105':
            a = 'Skrue fejl'
        if self.last_error_type == 'none':
            a = 'Ingen fejl'
        return time_since_last_error,a
    
    def check_machine(self,data):
        df= pd.DataFrame(data,columns=['_id','timestamp','port','value','__v'])
        df_machineOff = df[df['port']=='0101']
        if len(df_machineOff) > 0:
            self.onOrOff = df_machineOff['value'].iloc[-1]
            b = self.onOrOff
        else:
            b = self.onOrOff
        return b
    
    def is_output(self,data):
        df = pd.DataFrame(data,columns=['_id','timestamp','port','value','__v'])
        df_out = df[(df['port']=='0103') & (df['value']==True)]
        if len(df_out) > 0:
            output_ts = df_out['timestamp'].iloc[-1]
            if output_ts == self.output_recent:
                return False
            else:
                self.output_recent = output_ts
                return True
        else:
            return False
        print("LOOOOOOOOOK: ", self.output_recent)
        
            