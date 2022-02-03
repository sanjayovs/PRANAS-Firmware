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
        if self.currentService.trialParameters.MODE=="BreathEmulate":
            self.paraData=self.currentService.trialParameters
            self.nebControl={'NebStatus':True,'StepDurations':list(map(int,self.paraData.SEQUENCE_DURATION.split(','))),'NebStates':list(map(int,self.paraData.SEQUENCE.split(',')))}
            self.currentService.trialParameters.RECORD_DURATION=sum(self.nebControl['StepDurations'])
            self.logFile.WriteLog('Step Durations:'+self.paraData.SEQUENCE_DURATION,0)
            self.logFile.WriteLog('Nebulizer States:'+self.paraData.SEQUENCE,0)
            self.stepDurations=self.nebControl['StepDurations']
            self.nebStates=self.nebControl['NebStates']
            self.thisState=-1
            self.stateSet=True
        self.DAQ=DAQManager(self.currentService)
        self.modeData=self.currentService.deviceFlags



    def SwitchControl(self,nebstate1):
        global nebState
        nebState=nebstate1
        print(nebstate1)
        if nebstate1==0:
            requests.post("https://maker.ifttt.com/trigger/off_switch/with/key/bQbEEqB8H2G9oAy3ndl-aK")
            print('Nebulizer Off')
        elif nebstate1==1:    
            requests.post("https://maker.ifttt.com/trigger/on_switch/with/key/bQbEEqB8H2G9oAy3ndl-aK")
            print('Nebulizer On')  

    def RegularModeRun(self):
        self.total_samples_read=0
        startTime=time.time()
        endTime=startTime+self.currentService.trialParameters.RECORD_DURATION
        currentTime=time.time()
        self.logFile.WriteLog('Recording Started',1)
        self.DAQ.StartDAQ()
        while currentTime<=endTime and self.modeData.STOP_FLAG==False and self.modeData.CONNECTION_FLAG: #0.2 is the compensation for delays
            msg,self.total_samples_read=self.DAQ.ScanDAQ(self.total_samples_read,nebState)

            if self.currentService.trialParameters.MODE=="BreathEmulate":
                if self.stateSet:
                    print(self.stateSet)
                    self.stateSet=False
                    self.thisState+=1
                    self.SwitchControl(self.nebStates[self.thisState])
                    if self.thisState<=len(self.stepDurations):
                        endDuration=self.stepDurations[self.thisState]
                        curDuration=0
                else:
                    curDuration+=1
                    if curDuration>=endDuration-1:
                        self.stateSet=True
                        curDuration=0
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
                continue
        self.DAQ.ResetDAQ()
        if self.modeData.CONNECTION_FLAG:
            self.currentService.thisConnection.SendData2Server('Recording Complete!')
        
        self.logFile.WriteLog('Recording Ended ',1)
        self.logFile.WriteLog('Data Recording Complete for a Duration of '+str(int(timeElapsed))+'s',0)
        self.logFile.WriteLog('Final Data Frame Size:'+str(self.DAQ.recDataFrame.shape),0)
        self.DAQ.recDataFrame.index.name='Samples'

        self.currentService.dataFileManage.Write2CSV(self.DAQ.recDataFrame)
        

class RecordMode(ModeManager):
    def __init__(self,currentService):
        ModeManager.__init__(self,currentService)
    def Run(self):
        self.RegularModeRun()

class BreathEmulationMode(ModeManager):
    def __init__(self,currentService):
        ModeManager.__init__(self,currentService)
        #self.Nebulizer_Thread=threading.Thread(target=self.NebulizerControl,args=())
    def Run(self):
        self.RegularModeRun()
        
    
   
