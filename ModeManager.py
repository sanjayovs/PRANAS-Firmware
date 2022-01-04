from DAQManager import DAQManager
import time
import os
import threading
import requests
class ModeManager():

    global nebState
    nebState=0
    def __init__(self,modeData,logFile):
        global nebState
        nebState=0
        self.logFile=logFile
        if modeData.BUFFER_SIZE==None:
            modeData.BUFFER_SIZE='-1'
        self.DAQ=DAQManager(modeData.SAMPLING_RATE,int(modeData.BUFFER_SIZE),logFile)
        
        self.RecordDataFolder=os.path.join(os.getcwd(),'RecordedData')
        self.RecordFileName='Data_'+modeData.FILE_NAME+'.csv'
        self.modeData=modeData

    def ModeRun(self):
        global nebState
        self.logFile.WriteLog('Record Duration:'+str(self.modeData.RECORD_DURATION))
        self.total_samples_read=0
        startTime=time.time()
        endTime=startTime+self.modeData.RECORD_DURATION
        currentTime=time.time()
        self.logFile.WriteLog('Recording Started at '+self.logFile.GetCurrentTime()[0])
        while currentTime<=endTime and self.modeData.StopFlag==False: #0.2 is the compensation for delays
            msg,self.total_samples_read=self.DAQ.ScanDAQ(self.total_samples_read,nebState)
            self.logFile.WriteLog('Time Elapsed (s):'+str(int(currentTime-startTime)+1)+' of '+str(self.modeData.RECORD_DURATION),True)
            if msg=='HardwareOvr':
                self.logFile.WriteLog('Hardware Over Run')
                break
            elif msg=='BuffOvr':
                self.logFile.WriteLog('Buffer Over Run')
                break
            else:
                currentTime=time.time()
                continue
        self.logFile.WriteLog('Recording Ended at '+self.logFile.GetCurrentTime()[0])
        self.logFile.WriteLog('Data Recording Complete for a Duration of '+str(int(self.modeData.RECORD_DURATION))+'s')
        self.logFile.WriteLog('Final Data Frame Size:'+str(self.DAQ.recDataFrame.shape))
        self.DAQ.recDataFrame.index.name='Samples'
        self.DAQ.recDataFrame.to_csv(self.RecordDataFolder+self.RecordFileName,index=True,header=True)

class RunThread(threading.Thread):
    def __init__(self,threadID,logFile,MethodToRun):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.logFile=logFile
        self.MethodToRun=MethodToRun
    def run(self):
        self.logFile.WriteLog('Started Thread:'+str(self.threadID))    
        self.MethodToRun()

class RecordMode(ModeManager):
    def __init__(self,modeData,logFile):
        ModeManager.__init__(self,modeData,logFile)
    def Run(self):
        self.ModeRun()

class BreathEmulationMode(ModeManager):
    def __init__(self,modeData,logFile):
        self.nebControl={'NebStatus':True,'StepDurations':list(map(int,modeData.SEQUENCE_DURATION.split(','))),'NebStates':list(map(int,modeData.SEQUENCE.split(',')))}
        modeData.RECORD_DURATION=sum(self.nebControl['StepDurations'])
        ModeManager.__init__(self,modeData,logFile)
        self.logFile.WriteLog('Step Durations:'+(modeData.SEQUENCE_DURATION))
        self.logFile.WriteLog('Nebulizer States:'+modeData.SEQUENCE)
    def NebulizerControl(self):
        if(self.nebControl['NebStatus']):
            stepDurations=self.nebControl['StepDurations']
            nebStates=self.nebControl['NebStates']
            cycleNo=1
            for stepValue in stepDurations:
                startTime=time.time()
                endTime=startTime+stepValue
                currentTime=startTime
                self.SwitchControl(nebStates[cycleNo-1])
                self.logFile.WriteLog('Nebulizer Switched at '+self.logFile.GetCurrentTime()[0]+', State:'+str('Off' if nebStates[cycleNo-1]==0 else 'On'))
                while currentTime<=endTime:
                    currentTime=time.time()
                    continue
                realDuration=int(time.time()-startTime)
                self.logFile.WriteLog('State Duration Actual Time:' +str(realDuration) +' off '+str(stepValue))
                if realDuration!=stepValue:
                    self.logFile.WriteLog('Error!! Missing Time Steps Detected! Rerun the experiment!')
                cycleNo+=1
            self.SwitchControl(0)    # Switch off nebulizer in the end
    
    def SwitchControl(self,nebstate):
        global nebState
        nebState=nebstate
        if nebstate==0:
            
            requests.post("https://maker.ifttt.com/trigger/off_switch/with/key/bQbEEqB8H2G9oAy3ndl-aK")
            #print('Nebulizer Off')
        elif nebstate==1:    
            requests.post("https://maker.ifttt.com/trigger/on_switch/with/key/bQbEEqB8H2G9oAy3ndl-aK")
            #print('Nebulizer On')
    
    def Run(self):
        thread2=RunThread('Nebulizer Control',self.logFile,self.NebulizerControl)
        thread2.start()
        self.ModeRun()
        thread2.join()