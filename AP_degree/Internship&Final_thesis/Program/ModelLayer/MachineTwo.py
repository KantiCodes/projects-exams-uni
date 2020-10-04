# this is a class for handling internal logic of laddermachine nr 2


from ModelLayer.BasicFunctionality import LadderMachine
import DataHandlingLibrary.DataHandlingMethods as dataH
import DataHandlingLibrary.ERPHandling as erpH


class MachineTwo(LadderMachine):
    """Class representing second machine of production"""
    std = {}
    HEADER = []

    def __init__(self, timeInterval):
        super(MachineTwo, self).__init__("laddermachine2", 8, timeInterval)
        self.std = self.setSTD(20 * 4 / 3, 30 * 4 / 3)
        self.HEADER = ["MachineOn", "AlarmMachine", "BufferTreadsOk", "StringsPresentAtGlueStation",
                       "PaceOut", "PaceTreads", "Pacs", "AlaramDowelSurvilance",
                       "DateNow", "lowerBorder", "upperBorder"]

    def main(self, rightSearchTimeInterval):

        self.postToDashboard(rightSearchTimeInterval)
        self.checkOutPut()

    #           print('M2 :' self.std)

    def postToDashboard(self, rightSearchTimeInterval):

        dataFromNoSQL, timeToPost = dataH.getDataForThePeroid(self.timeInterval, rightSearchTimeInterval
                                                              , self.machineName)
        self.AssignValuesToPorts(dataFromNoSQL)

        MachineOn, AlarmMachine, BufferTreadsOk, StringsPresentAtGlueStation, PaceOut, PaceTreads, Pacs, AlaramDowelSurvilance = self.ports.values()
        PaceOut = PaceOut * 4 / 3
        row = [MachineOn, AlarmMachine, BufferTreadsOk, StringsPresentAtGlueStation,
               PaceOut, PaceTreads, Pacs, AlaramDowelSurvilance, timeToPost, self.std["lowerBorder"]
            , self.std["upperBorder"]]

        print(" TIme to post = :", timeToPost)
        data_json = dataH.fromRowToJson(row, self.HEADER)
        print("data json : ", data_json)
        dataH.pushToPowerBI(genericApi, data_json)

        latestErp = erpH.getLatestProducts(self.machineName)
        print(latestErp)

        self._resetPortsValues()

    def AssignValuesToPorts(self, dataFromNoSQL):
        if len(dataFromNoSQL) > 0:
            dataFromNoSQL = dataH.orderData(dataFromNoSQL, self.machineName)
            for dat in (dataFromNoSQL):
                # print("helo from firstfor" )
                port, value, timStamp = dataH.parseFromJson(dat)
                #               Keep track of machine power status
                portID = port[-1]
                if (portID == '2' or portID == '8' or portID == '3'):
                    self.setTimeAndPort(portID, timStamp, 'update', value)

                elif value == True:
                    self.setTimeAndPort(portID, timStamp, 'count', value)
        else:
            print("no data has be found in given peroid")
