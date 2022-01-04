from DataManager import LogFileManage
from ConnectionManager import ConnectionManager
from ModeManager import RecordMode 
from DataClasses import TrialParameters,DeviceFlags
from datetime import datetime

class ServiceManager:

        def __init__ (self):
                
                while True:
                        self.trialParameters=TrialParameters()
                        self.deviceFlags=DeviceFlags()
                        
                        
                        self.thisConnection=ConnectionManager(self)
                        self.thisConnection.Run_ConnectionHandlerThread()
                        #thisConnection.Connection_Thread.start()
                        # This loop waits for connection
                        while True:
                                if self.deviceFlags.CONNECTION_FLAG:
                                        self.connectionTime=self.GetCurrentTime()
                                        print('Connected!')
                                        break

                        while True:
                                if self.deviceFlags.CONNECTION_FLAG:
                                        print('Config Complete')
                                        self.logFileManage=LogFileManage(self)
                                        self.logFileManage.WriteLog()

                                if self.deviceFlags.STOP_FLAG:
                                        self.thisConnection.Stop_ConnectionHandlerThread()
                                        break
                        

        def GetCurrentTime(self):
                #Gets current time and returns in string and integer format
                dt_now=datetime.now()
                return str(10000000000*dt_now.year+100000000*dt_now.month+1000000*dt_now.day+10000*dt_now.hour+100*dt_now.minute+dt_now.second)                



                """ while True:
                        if thisConnection.ConnectionStatus==False:
                                thisConnection=ConnectionManager(self.PORT_Server,self.IP_Server,self.thisLogFile) # Making a new connection if there was a fault
                                self.thisConnection=thisConnection
                        else:
                                if   thisConnection.ConfigureFlag:
                                        thisConnection.ConfigureFlag=False
                                        thisConnection.StopFlag=False
                                        print("Configuration Complete Waiting for Start")
                                elif thisConnection.StartFlag:
                                        self.thisLogFile.WriteLog("Configured at "+self.thisLogFile.GetCurrentTime(),True)
                                        if thisConnection.MODE == 'Breath' or thisConnection.MODE=='Static':
                                                self.AnalyzeMode(thisConnection.MODE,thisConnection.TRIAL)
                                elif thisConnection.StopFlag:
                                        print("Stop Received")

        def AnalyzeMode(self,ModeType,trials):
                if ModeType=="Breath":
                        self.thisConnection.RECORD_DURATION=180 # 180 seconds for each trial
                elif ModeType=="Static":
                        self.thisConnection.RECORD_DURATION=180 # 180 seconds of recording
                        #self.FILE_NAME=str(self.UID)+'_T'+str(self.TRIAL)+'_'+self.MODE
                self.thisConnection.NameFile(str(trials),ModeType)
                self.thisMode=RecordMode(self.thisConnection,self.thisLogFile)
                self.thisConnection.StartFlag=False
                self.thisMode.Run()                     

 """



                    






