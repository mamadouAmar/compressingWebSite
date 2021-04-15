# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 20:47:37 2020
@author: Shayan
"""
import numpy as np
import pylab as py
from scipy.fftpack import fft,ifft,rfft,irfft
from scipy.signal import blackman,hamming,chebwin,resample,stft,butter,lfilter
from scipy.signal import freqz
import soundfile as sf
import os
import time



def inputwav(filename):
    """
        Decodes input file using "soundfile" library. Determines if file is
        mono or stereo and converts data to dB.
        Parameters
        ----------
        filename: string
            Name of the input <audio> file. Uses the soundfile python library
            to decode the input.
        Returns
        -------
        n: length of audio in samples
        
        data: array containing the signal in bits.
        
        data_dB: array containing the signal in dB.
        
        sr: sample rate
        
        ch: number of audio channels. 1 = mono, 2 = stereo
        """
    data, sr = sf.read(filename)
    print('Decoding "'+filename+'"...')
    print('Sample rate is '+str(sr)+'...')
    try:
        ch=len(data[0,])
    except:
        ch=1
    print('File contains '+str(ch)+' audio channel(s)...')
        #Reshape the data so other functions can interpret the array if mono.
        #basically transposing the data
    if ch==1:
        data=data.reshape(-1,1)
    n=len(data)
        #This prevents log(data) producing nan when data is 0
    data[np.where(data==0)]=0.00001
        #convert to dB
    data_dB=20*np.log10(abs(data))
    return n, data,data_dB,sr, ch
       
def compress(filename,threshold,ratio,makeup,attack,release,wout=True,plot=False):
    """
        Reduces dynamic range of input signal by reducing volume above threshold.
        The gain reduction is smoothened according to the attack and release.
        Makeup gain must be added manually.
        Parameters
        ----------
        filename: string
            Name of the input *.wav file.
        threshold: scalar (dB)
            value in dB of the threshold at which the compressor engages in
            gain reduction.
        ratio: scalar
            The ratio at which volume is reduced for every dB above the threshold
            (i.e. r:1)
            For compression to occur, ratio should be above 1.0. Below 1.0, you
            are expanding the signal.
            
        makeup: scalar (dB)
            Amount of makeup gain to apply to the compressed signal
        
        attack: scalar (ms)
            Characteristic time required for compressor to apply full gain
            reduction. Longer times allow transients to pass through while short
            times reduce all of the signal. Distortion will occur if the attack
            time is too short.
        
        release: scalar (ms)
            Characteristic time that the compressor will hold the gain reduction
            before easing off. Both attack and release basically smoothen the gain
            reduction curves.
            
        wout: True/False, optional, default=True
            Writes the data to a 16 bit *.wav file. Equating to false will suppress
            *.wav output, for example if you want to chain process.
            
        plot: True/False, optional, default=True
            Produces plot of waveform and gain reduction curves.
        
            
        Returns
        -------
        data_Cs: array containing the compressed waveform in dB
        data_Cs_bit: array containing the compressed waveform in bits.
    """
    start = time.time()
    if ratio < 1.0:
        print('Ratio must be > 1.0 for compression to occur! You are expanding.')
    if ratio==1.0:    
        print('Signal is unaffected.')
    n, data, data_dB,sr,ch= inputwav(filename)
        #Array for the compressed data in dB
    dataC=data_dB.copy()
    #attack and release time constant
    a=np.exp(-np.log10(9)/(44100*attack*1.0E-3))
    re=np.exp(-np.log10(9)/(44100*release*1.0E-3))
        #apply compression
    print('Compressing...')
    for k in range(ch):
        for i in range (n):
            if dataC[i,k]>threshold:
                dataC[i,k]=threshold+(dataC[i,k]-threshold)/(ratio)
        #gain and smooth gain initialization
    gain=np.zeros(n)
    sgain=np.zeros(n)
        #calculate gain
    gain=np.subtract(dataC,data_dB)
    sgain=gain.copy()
        #smoothen gain
    print('Smoothing...')
    for k in range(ch):
        for i in range (1,n):
            if sgain[i-1,k]>=sgain[i,k]:
                sgain[i,k]=a*sgain[i-1,k]+(1-a)*sgain[i,k]
            if sgain[i-1,k]<sgain[i,k]:
                sgain[i,k]=re*sgain[i-1,k]+(1-re)*sgain[i,k]    
        #Array for the smooth compressed data with makeup gain applied
    dataCs=np.zeros(n)
    dataCs=data_dB+sgain+makeup
        #Convert our dB data back to bits
    dataCs_bit=10.0**((dataCs)/20.0)
        #sign the bits appropriately:
    for k in range (ch):
        for i in range (n):
            if data[i,k]<0.0:
                dataCs_bit[i,k]=-1.0*dataCs_bit[i,k]
        #Plot the data:
    if plot==True:
        print('Plotting...')
        t=np.linspace(0,n/(1.0*sr),n)
        py.close()
        fig, (ax1, ax2) = py.subplots(nrows=2)  
        ax2.plot(t,gain,'k-',linewidth=0.1,label='Gain Reduction')
        ax2.plot(t,sgain,'r-',linewidth=1, label='Gain Reduction Smooth')
        ax1.plot(t,data,'k-',linewidth=1,label=filename)
        ax1.plot(t,dataCs_bit,'m-',linewidth=0.1,
                    label=filename+' compressed')
        ax1.axhline(10**(threshold/20.0),linestyle='-',
                        color='cyan',linewidth=1)
        ax1.axhline(-10**(threshold/20.0),linestyle='-',
                        color='cyan',linewidth=1)
        ax1.legend()
        ax2.legend()
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Gain Reduction (dB)')
        ax1.set_ylabel('Amplitude (Rel. Bit)')
        ax1.set_xlabel('Time (s)')
        #write data to 16 bit file
    if wout==True:
        print('Exporting...')
    sf.write(filename[0:len(filename)-4]+'_compressed.wav',dataCs_bit,
                    sr,'PCM_16')
    end=time.time()
    elapsed=int(1000*(end-start))
    print('Done!')
    print('...............................')
    print('Completed in '+str(elapsed)+' milliseconds.')    
    return dataCs,dataCs_bit
    
##a, b = compress("tictac.wav",0,2,0,1000,1000,wout=True,plot=True)
