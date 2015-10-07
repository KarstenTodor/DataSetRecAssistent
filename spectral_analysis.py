import serial 
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import hickle as hkl
import thread
from random import randrange
from scipy.io.wavfile import write

def subsequences(a, window, overlap):
    #for 1D arrays
    shape = ((a.size - window)/(window-overlap) + 1, window)
    strides = list(a.strides * 2)
    strides[0] = strides[0]*overlap
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def rolling_window(a, window):
	#for 2d arrays
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    print strides
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def read(filename):
	lib = hkl.load(filename)
	return lib['data'], lib['id'] 

def test_def_subsequences():
	original = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16])
	print original
	print subsequences(original,4,2)
	print rolling_window(original,4) 



def test_sel():
	original = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16])
	print original
	fourbyfour = original.reshape(4,4)
	print fourbyfour
	print fourbyfour.strides
	print fourbyfour[0:2,0:2]

def plot_amplitude(filename):
	data, action =  read(filename)
	plt.figure("elias5_ch3.raw")
	plt.ylim(-100,4196);
	plt.xlim(0,len(data));
	handle, = plt.plot(data)
	plt.draw()

def plot_builtin_spectogram(filename,window,overlap,Fs=8000,offset=2048):
	data, action =  read(filename)
	plt.figure("built-in spectogram")
	plt.ylim(-100,500);
	Pxx, freqs, bins, im = plt.specgram(data-offset, NFFT=window, Fs=Fs, noverlap=window-overlap,
	                                cmap=plt.get_cmap('Greys'), window=np.hamming(window))
	plt.draw()

def plot_spectogram(filename,window,overlap):
	data, action =  read(filename)
	print "action", action
	data = data[0:56000]
	windows = subsequences(data,window,overlap)

	dft = np.fft.fft(windows*np.hamming(window))

	plt.ion()

	magnitude = np.abs(dft)
	#print 'histogram', np.histogram(magnitude,100)
	#print magnitude.max().max()
	#print magnitude.min().min()
	plt.figure("Magnitude_w"+str(window)+"_o"+str(overlap)+" "+filename)
	im1 = plt.imshow(magnitude[:,window-1-(window/10):window-1].transpose(),vmin=100 , vmax=1000, aspect='auto')
	plt.colorbar(im1, orientation='horizontal')
	plt.show()

	angle = np.angle(dft)
	#print 'histogram', np.histogram(angle,20)
	#print angle.max().max()
	#print angle.min().min()
	plt.figure("Angle_w"+str(window)+"_o"+str(overlap)+" "+filename)
	im2 = plt.imshow(angle.transpose(), aspect='auto')
	plt.colorbar(im2, orientation='horizontal')
	plt.show()

def plot_angle(filename,window,overlap):
	data, action =  read(filename)
	print "action", action
	data = data[0:56000]
	windows = subsequences(data,window,overlap)

	dft = np.fft.fft(windows*np.hamming(window))
	plt.ion()
	angle = np.angle(dft)
	#print 'histogram', np.histogram(angle,20)
	#print angle.max().max()
	#print angle.min().min()
	plt.figure("Angle_w"+str(window)+"_o"+str(overlap)+" "+filename)
	im2 = plt.imshow(angle.transpose(), aspect='auto')
	plt.colorbar(im2, orientation='horizontal')
	plt.show()

mpl.rcParams['figure.max_open_warning'] = 40

for i in range(3):
	plot_spectogram("testdata/elias3_ch3.raw",128*(2**i),64*(2**i))


raw_input("Press Enter to continue...")