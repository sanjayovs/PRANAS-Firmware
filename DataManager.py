from datetime import datetime
import os
import pathlib

class LogFileManage:
        def __init__(self,currentService):
                #Creating and Initializing Log File to which all the session information is written.
                self.log_file_name=str(currentService.trialParameters.UID)+'_T'+str(currentService.trialParameters.TrialNo)+'_'+currentService.trialParameters.Mode+'.log'
                self.WriteLog('Started at '+ currentService.connectionTime)
                

        def WriteLog(self, writeString):
                # Writes any string passed as argument to the session's log file opened initially
                print(writeString)
                writeString=str(writeString)
                logFileFolder=os.path.abspath(os.getcwd())+'/logs'
                self.log_file = open(os.path.join(logFileFolder,self.log_file_name),"a")
                self.log_file.writelines(writeString+"\n")
                self.log_file.close()
        
class DataFileManage:
        def __init__(self):
                self


        #self.data_file_name="Data_"+str(UID)+'_T'+str(TrialNo)+'_'+Mode

class DataTransfer:
    def __init__(self):
        self