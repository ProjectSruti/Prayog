from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import pdb
from itertools import chain

C_sharp=440
scale=C_sharp
note_resolution=scale/7.0
sa=C_sharp+0*note_resolution
re=C_sharp+1*note_resolution
ga=C_sharp+2*note_resolution
ma=C_sharp+3*note_resolution
pa=C_sharp+4*note_resolution
dha=C_sharp+5*note_resolution
ni=C_sharp+6*note_resolution

y=[re,ga,ma,ni,re,ga,ma,pa,dha,ni,re,ga]
#y=[ga,ni,re,ga]

x = np.linspace(0, len(y), num=len(y), endpoint=True)
f = interp1d(x, y)
f2 = interp1d(x, y, kind='cubic')

N=20
note_frequency = 100/60 #100 beats/minute
note_frequency = 100.0/60 #100 beats/minute
pdb.set_trace()
note_time_period=1.0/note_frequency
note_time_period_hold_instant=note_time_period/N
freq_curve_sampling_rate=N*note_frequency

xnew = np.linspace(0, len(y), num=N*len(y), endpoint=True)
freq_list=f2(xnew)
plt.subplot(211)
plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew,freq_list, '--')
plt.legend(['data', 'linear', 'cubic'], loc='best')
#plt.show()

audio_sample=[]
for i in range(len(freq_list)):
    fs=N*freq_list[i]
    Ts=1.0/fs
    k=np.linspace(0,int(note_time_period_hold_instant/Ts),int(note_time_period_hold_instant/Ts))
    audio_sample.append(np.sin(2*np.pi*freq_list[i]*k*Ts))

plt.subplot(212)
plt.plot(list(chain.from_iterable(audio_sample)))
plt.show()


