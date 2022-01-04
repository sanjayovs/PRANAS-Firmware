#  -*- coding: utf-8 -*-
from __future__ import print_function
from sys import stdout
from time import sleep
from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask
import numpy as np
import sys
import pandas as pd

class DAQManager():
    def __init__(self,samplingRate,sampleBuffer,logFile):
        self.logFile=logFile
        self.timeout=5.0
        self.total_samples_read=0
        self.channels=[0,1,2] #X,Y,Power
        self.channel_mask=chan_list_to_mask(self.channels)
        self.num_channels=len(self.channels)
        self.samples_per_channel=0
        self.options=OptionFlags.CONTINUOUS
        self.scan_rate=samplingRate
        self.recDataFrame=pd.DataFrame()
        self.READ_ALL_AVAILABLE=sampleBuffer
        self.ConfigureDAQ()




    def ConfigureDAQ(self):
        try:
            self.address=select_hat_device(HatIDs.MCC_118)
            self.hat=mcc118(self.address)
            self.logFile.WriteLog('Selected MCC 118 HAT device at address:'+str(self.address))
            self.actual_scan_rate=self.hat.a_in_scan_actual_rate(self.num_channels,self.scan_rate)
            self.logFile.WriteLog('Device in continous scan mode')
            self.logFile.WriteLog('Channels: '+(''.join([str(chan)+', ' for chan in self.channels]))+' ')
            self.logFile.WriteLog('Requested Scan Rate: '+str(self.scan_rate)+' ')
            self.logFile.WriteLog('Actual Scan Rate: '+str(self.actual_scan_rate)+' ')
            self.hat.a_in_scan_start(self.channel_mask,self.samples_per_channel
                                            ,self.scan_rate,self.options)
        except (HatError, ValueError) as err:
            self.logFile.WriteLog(err)

    
    def ScanDAQ(self,total_samples_read,nebMode):
        read_result=self.hat.a_in_scan_read(self.READ_ALL_AVAILABLE,self.timeout)
        
        if read_result.hardware_overrun:
            self.logFile.WriteLog('Hardware Overrun')
            return 'HardwareOvr'
        elif read_result.buffer_overrun:
            self.logFile.WriteLog('Buffer Overrun')
            return 'BuffOvr'
        samples_read_per_channel = int(len(read_result.data) / self.num_channels)
        total_samples_read += samples_read_per_channel
        #print('\r{:12}'.format(samples_read_per_channel),
        #      ' {:12} '.format(total_samples_read), end='')    
        Xpos=[read_result.data[i] for i in range(0,len(read_result.data),3)]
        Ypos=[read_result.data[i] for i in range(1,len(read_result.data),3)]
        Pow=[read_result.data[i] for i in range(2,len(read_result.data),3)]

        currentDF=pd.DataFrame({'Xpos':Xpos,'Ypos':Ypos,'Pow':Pow,'NebMode':nebMode})
        self.recDataFrame=self.recDataFrame.append(currentDF,ignore_index=True)
        if samples_read_per_channel > 0:
            endIndex = samples_read_per_channel * self.num_channels - self.num_channels

            #print(np.shape(read_result.data))

            # Enable the following code to print the data on screen. Should also check the time function for disorderly print
            #for i in range(self.num_channels):
            #    print('{:10.5f}'.format(read_result.data[index+i]), 'V ',
            #          end='')
            stdout.flush()
            sleep(0.1)
        return 'Success',total_samples_read
        
        

        
        
        






