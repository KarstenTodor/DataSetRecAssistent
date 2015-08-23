import serial 
import time
import pylab as plt
import numpy as np
import thread
from scipy.io.wavfile import write


def handshake(verbose,serialinst):
	""" Send/receive pair of bytes to synchronize data gathering """
	nbytes = serialinst.write('A') # can write anything here, just a single byte (any ASCII char)		
	if verbose:
		print 'Wrote bytes to serial port: ', nbytes
	#wait for byte to be received before returning
	st = time.clock()
	byte_back = serialinst.readline()
	et = time.clock()
	if verbose:
		print 'Received handshake data from serial port: ',byte_back
		print 'Time between send and receive: ',et-st


recording_time = 10
verbose = True
window_bytes = 1000000

ser = serial.Serial(
   port='/dev/tty.usbmodem14221',
   baudrate=115200,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS
)

if ser.isOpen() == False :
   ser.open()
   if ser.isOpen() == False :
      print "Can't open serial port"
      sys.exit(1)

handshake(verbose,ser)
print ser.readline()

st = time.clock()
data = ser.read(window_bytes)	# this number should be larger than the number of bytes that will actually be sent
ser.close()				# close serial port
et = time.clock() - st
if verbose:
	print 'Elapsed time reading data (s): ', et
print "len(data)", len(data)
y = np.fromstring(data, dtype=np.uint16);
print len(y), y
# if np.little_endian: 
# 	y = y.byteswap()
# print y

ch0 = y[0:-1:4]
ch1 = y[1:-1:4]
ch2 = y[2:-1:4]
ch3 = y[3:-1:4]

print ch0
print ch1
print ch2
print ch3

window_complete = 512*1920/2

sel0 = ch0[0:window_complete]
plt.ion()
plt.figure("Complete window channel 0")
plt.ylim(-100,4196);
plt.xlim(0,len(sel0));
handle, = plt.plot(sel0)
plt.draw()

sel1 = ch1[0:window_complete]
plt.ion()
plt.figure("Complete window channel 1")
plt.ylim(-100,4196);
plt.xlim(0,len(sel1));
handle, = plt.plot(sel1)
plt.draw()

sel2 = ch2[0:window_complete]
plt.ion()
plt.figure("Complete window channel 2")
plt.ylim(-100,4196);
plt.xlim(0,len(sel2));
handle, = plt.plot(sel2)
plt.draw()

sel3 = ch3[0:window_complete]
plt.ion()
plt.figure("Complete window channel 3")
plt.ylim(0,4096);
plt.xlim(0,len(sel3));
handle, = plt.plot(sel3)
plt.draw()

window_subset = 2000
plt.figure("First subset ch1")
plt.ylim(-100,4196);
plt.xlim(0,window_subset);
handle, = plt.plot(ch1[0:window_subset-1])
plt.draw()

raw_input("Press Enter to continue...")

file = open('testdata/ch0.raw', 'w')
np.save(file,ch0)
file = open('testdata/ch1.raw', 'w')
np.save(file,ch1)
file = open('testdata/ch2.raw', 'w')
np.save(file,ch2)
file = open('testdata/ch3.raw', 'w')
np.save(file,ch3)

scaled0 = np.int16((np.double(ch0)-2047)/2048 * 32767)
scaled1 = np.int16((np.double(ch1)-2047)/2048 * 32767)
scaled2 = np.int16((np.double(ch2)-2047)/2048 * 32767)
scaled3 = np.int16((np.double(ch3)-2047)/2048 * 32767)
write('ch0.wav', 40000, scaled0)
write('ch1.wav', 40000, scaled1)
write('ch2.wav', 40000, scaled2)
write('ch3.wav', 40000, scaled3)


#message id