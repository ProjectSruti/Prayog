# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
from scipy import signal
from scipy.interpolate import CubicSpline
from scipy.io.wavfile import write
from scipy.interpolate import interp1d
import pyaudio
import wave
import sys
import matplotlib.pylab as plt
import math
import pdb
import os
import sys
from itertools import chain
from pylab import cumsum

##########################################################################
## Bit-Rate = 44100 samples per second
## Laya = 90 beats per minute (1.6 Hz)
## Scale-> [1, (9/8), (5/4), (4/3), (3/2), (5/3), (15/8), 2]
## all_lower -> mandra saptak
## first_upper -> madhya saptak
## all_upper -> taar saptak
###########################################################################

SAMPLES_PER_SEC=44100
VOLUME_Pc=75.0
BEATS_PER_SEC = 2.5
TONIC = 261.6
SAMPLES_PER_BEAT = int(SAMPLES_PER_SEC * BEATS_PER_SEC/2)

VOLUME_SCALE=(VOLUME_Pc/100.0)*32768

SCALE = {"__":(0.0), "pa":(3.0/4.0), "dha":(5.0/6.0), "ni":(15.0/16.0),
         "Sa":(1.0), "Re":(9.0/8.0), "Ga":(5.0/4.0), "Ma":(4.0/3.0),
         "Pa":(3.0/2.0), "Dha":(5.0/3.0), "Ni":(15.0/8.0), "SA":(2.0),
         "RE":(18.0/8.0), "GA":(10.0/4.0), "MA":(8.0/3.0), "PA":(6.0/4.0) }

def decay_gen(Half, Num_Samples, Time_Value):
    decay = math.log(2) / Half
    return [math.exp(-decay*i) for i in range(0,Num_Samples)]
    #FACTOR=((SAMPLES_PER_BEAT*Time_Value)/2)
    #return [(((i-FACTOR)*(i-FACTOR))*(0.5/(FACTOR*FACTOR))+0.5) for i in range(0,Num_Samples)]
    #return [(0.25*np.cos(2.0*np.pi*i/(2.0*FACTOR)) + 0.5) for i in range(0,Num_Samples)]

def noise_gen(Scaling, Num_Samples):
    return (np.random.uniform(-1,1,Num_Samples))/Scaling  

def swar_gen(Swar, Time_Value):
    #pdb.set_trace()
    if(Swar.split("'")[0]=="__"):
        return np.int16([0.0]*int(SAMPLES_PER_BEAT*Time_Value))
    else:
        freq = TONIC*SCALE[Swar]
        x = np.linspace(-(Time_Value/2.0*BEATS_PER_SEC),(Time_Value/2.0*BEATS_PER_SEC), int(SAMPLES_PER_BEAT*Time_Value)) #TBD make sure that fractions of times per beat are not missed due to truncation with int
        #pdb.set_trace()
        data = np.sin(2*np.pi*freq*x)
        #data = signal.sawtooth(2 * np.pi * 5 * x)
        
        return np.int16(( ( (data+noise_gen(100,int(SAMPLES_PER_BEAT*Time_Value)))
                            *decay_gen(10000, int(SAMPLES_PER_BEAT*Time_Value),Time_Value)
                            ) / np.max(np.abs(data) ) ) *    VOLUME_SCALE)

def dhun_gen(dhun):

    if(dhun[0].count("'")==0):
        TIME_VALUE=1
    else:
        TIME_VALUE=1.0/(np.power(2,dhun[0].count("'")))
    print (TIME_VALUE)
    phrase = swar_gen(dhun[0].split("'")[0],TIME_VALUE)#[0]*len(dhun)*SAMPLES_PER_BEAT
    print (dhun[0])
    print (dhun[0].count("'"))
    for i in range(1, len(dhun)):
        if(dhun[i].count("'")==0):
            TIME_VALUE=1
        else:
            TIME_VALUE=1.0/(np.power(2, dhun[i].count("'")))
        print (TIME_VALUE)
        print (dhun[i])
        print (dhun[i].count("'"))
        phrase = np.int16(phrase.tolist() + swar_gen(dhun[i].split("'")[0],TIME_VALUE).tolist())

    return np.int16(phrase)

def dhun_gen_new(dhun):
    time_unit=4.0
    frequency_list=[]
    BEAT_COUNT=0
    for i in range(len(dhun)):
        TIME_VAL=int((1.0/(2**dhun[i].count("'")))*time_unit)
        
        print i,TIME_VAL
        freq = TONIC*SCALE[dhun[i].split("'")[0]]
        BEAT_COUNT=BEAT_COUNT+TIME_VAL/time_unit
        for j in range(TIME_VAL):
            frequency_list.append(freq)
    x=np.linspace(0,BEAT_COUNT*SAMPLES_PER_BEAT-1,len(frequency_list))
    ft=CubicSpline(x,frequency_list,bc_type ='clamped')
    fs=10*max(frequency_list)
    Ts=1.0/fs
    xs=np.linspace(0,SAMPLES_PER_BEAT*BEAT_COUNT-1,BEAT_COUNT*SAMPLES_PER_BEAT)
    plt.plot(xs, ft(xs))
    plt.show()


    signal=np.sin(2*np.pi*np.abs(ft(xs))*(1/(SAMPLES_PER_BEAT*BEATS_PER_SEC))*xs)
    plt.plot(signal)
    plt.show()
    return np.int16(signal*VOLUME_SCALE)
##    plt.plot(signal)
##    plt.show()
##    
##    xs = np.arange(0, len(frequency_list), 0.01)
##    dt = xs[1] - xs[0]
##    f_inst=ft(xs)
##    signal=np.sin(2*np.pi*ft(xs)*xs)
##    plt.plot(signal)
##    plt.show()
##    
##    
##    #plt.plot(x, frequency_list, 'o', label='data')
##    #plt.plot(xs, f_inst, label="S")
##    phi = 2 * np.pi * cumsum(f_inst) * dt
##    signal=np.sin(phi)
##    plt.plot(xs,signal)
##    plt.show()
    
    

#############################################
## Create your Dhun
#############################################

dhun= "Ga'',Ma'',Re',Ga'',Ma,Ga'',Pa'',Ma',__',Dha'',Dha'',Dha',SA'',Pa,Ga'',Pa'',Ma''"
#dhun= "Ga'',Ma'',Re',Ga'',Ma,Ga''"
#(Ni,)

list_dhun = dhun.split(",")

list_dhun_x=dhun_gen_new(list_dhun)
#dhun = [Sa, Sa, Sa, Sa, Sa, Sa, Sa, Sa, Sa]
write("test.wave", SAMPLES_PER_SEC, list_dhun_x)

#write("test.wave", SAMPLES_PER_SEC, dhun_gen(list_dhun))

wf = wave.open("test.wave", 'rb')
            
#Instantiate PyAudio
p = pyaudio.PyAudio()

#Open Stream
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

#Read Data
data = wf.readframes(SAMPLES_PER_BEAT*len(list_dhun_x)) #TBD total frames to be picked equals the time duration of all the notes in dhun
    
# Play Stream
while len(data) > 0:
    stream.write(data)
    #data = wf.readframes(1024)
    data = wf.readframes(SAMPLES_PER_BEAT*len(list_dhun_x))

#Close Stream
stream.stop_stream()
stream.close()

#Close PyAudio
p.terminate()
plt.plot(dhun_gen(list_dhun))
plt.show()
