import numpy as np
from scipy import signal
from scipy.io.wavfile import write
import pyaudio
import wave
import sys
import matplotlib.pylab as plt
import math
import pdb

##########################################################################
## Bit-Rate = 44100 samples per second
## Laya = 90 beats per minute (1.6 Hz)
## Scale-> [1, (9/8), (5/4), (4/3), (3/2), (5/3), (15/8), 2]
## all_lower -> mandra saptak
## first_upper -> madhya saptak
## all_upper -> taar saptak
###########################################################################

SAMPLES_PER_SEC=44100
VOLUME_PC=100.0
BEATS_PER_SEC = 3.0
TONIC = 880 #10Hz

VOLUME_SCALE=(VOLUME_PC/100.0)*32768
SAMPLES_PER_BEAT = int(SAMPLES_PER_SEC * BEATS_PER_SEC/2)


SCALE = [(0.0),(3.0/4.0), (5.0/6.0), (15.0/16.0), (1.0), (9.0/8.0), (5.0/4.0), (4.0/3.0), (3.0/2.0), (5.0/3.0), (15.0/8.0), (2.0), (18.0/8.0), (10.0/4.0), (8.0/3.0), (6.0/4.0) ]
[__, pa, dha, ni, Sa, Re, Ga, Ma, Pa, Dha, Ni, SA, RE, GA, MA, PA]  = [i for i in range(0,len(SCALE))]

def decay_gen(Half, Num_Samples):
    decay = math.log(2) / Half
    return [math.exp(-decay*i) for i in range(0,Num_Samples)]
            
def noise_gen(Scaling, Num_Samples):
    return (np.random.uniform(-1,1,SAMPLES_PER_BEAT))/Scaling  

def swar_gen(Swar):
    if(Swar==0):
        return np.int16([0.0]*SAMPLES_PER_BEAT)
    else:
        freq = TONIC*SCALE[Swar]
        x = np.linspace(-freq*np.pi,freq*np.pi, SAMPLES_PER_BEAT)
        data = np.sin(x)
        #data = signal.sawtooth(2 * np.pi * 5 * x)
        return np.int16(( ( (data+noise_gen(100,SAMPLES_PER_BEAT)) *decay_gen(10000, SAMPLES_PER_BEAT)) / np.max(np.abs(data) ) ) *    VOLUME_SCALE)

def dhun_gen(dhun):
    phrase = swar_gen(dhun[0])#[0]*len(dhun)*SAMPLES_PER_BEAT
    for i in range(1, len(dhun)):
       phrase = np.int16(phrase.tolist() + swar_gen(dhun[i]).tolist())
    return np.int16(phrase)

#############################################
## Create your Dhun
#############################################

dhun = [ni, Re, Ga, ni, dha, ni, Re, Sa]

write("test.wave", SAMPLES_PER_SEC, dhun_gen(dhun))


wf = wave.open("test.wave", 'rb')
            
#Instantiate PyAudio
p = pyaudio.PyAudio()

#Open Stream
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

#Read Data
data = wf.readframes(SAMPLES_PER_BEAT*len(dhun))

# Play Stream
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(SAMPLES_PER_BEAT*len(dhun))

#Close Stream
stream.stop_stream()
stream.close()

#Close PyAudio
p.terminate()
plt.plot(dhun_gen(dhun))
plt.show()
