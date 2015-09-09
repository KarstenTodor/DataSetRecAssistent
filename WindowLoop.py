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
   port='/dev/tty.usbmodem1d111',
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

window_complete = 512*1920/2
z = y[0:window_complete]
plt.ion()
plt.figure("Complete window")
plt.ylim(0,4096);
plt.xlim(0,len(z));
handle, = plt.plot(z)
plt.draw()

window_subset = 2000
plt.figure("First subset")
plt.ylim(0,4096);
plt.xlim(0,window_subset);
handle, = plt.plot(y[0:window_subset-1])
plt.draw()

raw_input("Press Enter to continue...")

file = open('temp.nparray.dat', 'w')
np.save(file,z)

a = np.double(z)
scaled = np.int16((a-2047)/2048 * 32767)
print "scaled", scaled
write('test.wav', 40000, scaled)


#message id