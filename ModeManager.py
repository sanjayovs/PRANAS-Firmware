from DAQManager import DAQManager
import time
import os
import threading
import requests
class ModeManager():

    global nebState
    nebState=0
    def __init__(self,currentService):
        self.currentService=currentService
        self.logFile=self.currentService.logFileManage
        self.DAQ=DAQManager(self.currentService)
        self.modeData=self.currentService.deviceFlags
        

    def ModeRun(self):
        self.total_samples_read=0
        startTime=time.time()
        endTime=startTime+self.currentService.trialParameters.RECORD_DURATION
        currentTime=time.time()
        self.logFile.WriteLog('Recording Started',1)
        self.DAQ.StartDAQ()
        while currentTime<=endTime and self.modeData.STOP_FLAG==False: #0.2 is the compensation for delays
            msg,self.total_samples_read=self.DAQ.ScanDAQ(self.total_samples_read,nebState)
            self.logFile.WriteLog('Time Elapsed (s):'+str(int(currentTime-startTime)+1)+' of '+str(self.currentService.trialParameters.RECORD_DURATION),True)
            if msg=='HardwareOvr':
                self.logFile.WriteLog('Hardware Over Run')
                break
            elif msg=='BuffOvr':
                self.logFile.WriteLog('Buffer Over Run')
                break
            else:
                currentTime=time.time()
                timeElapsed=currentTime-startTime
                #self.currentService.thisConnection.portalConnection.sendall(str(timeElapsed).encode('ascii'))
                #self.currentService.thisConnection.portalConnection.settimeout(5)
                """ try:
                    self.tokenRcv=self.currentService.thisConnection.portalConnection.recv(1024).decode('ascii')
                    print(self.tokenRcv)
                except:                   
                    self.modeData.STOP_FLAG=True
                    self.currentService.thisConnection.portalConnection.settimeout(None) """
                continue
        self.DAQ.ResetDAQ()
        self.logFile.WriteLog('Recording Ended ',1)
        self.logFile.WriteLog('Data Recording Complete for a Duration of '+str(int(timeElapsed))+'s',0)
        self.logFile.WriteLog('Final Data Frame Size:'+str(self.DAQ.recDataFrame.shape),0)
        self.DAQ.recDataFrame.index.name='Samples'
        self.currentService.dataFileManage.Write2CSV(self.DAQ.recDataFrame)
        

class RecordMode(ModeManager):
    def __init__(self,currentService):
        ModeManager.__init__(self,currentService)
    def Run(self):
        self.ModeRun()

   
