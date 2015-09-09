import serial 
import time
import pylab as plt
import numpy as np
import hickle as hkl
import thread
from random import randrange
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

def randomBasicAction():
	actions = ["tap - up - tap", "tap - down - tap", "tap - left - tap", "tap - right - tap"]
	return randomAction(actions)

def randomAction(actions):
	random_index = randrange(0,len(actions))
	return actions[random_index], random_index

def record(filename,plot=False,write_wav=False,write_raw=False):
	recording_time = 10
	verbose = True
	window_bytes = 600000

	ser = serial.Serial(
	   #port='/dev/tty.usbmodem14221',
	   #port='/dev/tty.usbmodem1d111',
	   port='/dev/tty.usbmodem1a121',
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
	action, action_id = randomBasicAction()
	print "Action: ", action
	print ser.readline()

	st = time.clock()
	data = ser.read(window_bytes)	# this number should be larger than the number of bytes that will actually be sent
	ser.close()			# close serial port
	time.sleep(8)
	et = time.clock() - st
	if verbose:
		print 'Elapsed time reading data (s): ', et
	print "len(data)", len(data)
	y = np.fromstring(data, dtype=np.uint16);
	print len(y), y
	# if np.little_endian: 
	# 	y = y.byteswap()
	# print y

	ch3 = y[0:-1:4]
	ch2 = y[1:-1:4]
	ch1 = y[2:-1:4]
	ch0 = y[3:-1:4]

	window_complete = 512*1920/2

	if write_raw:
		data0 = {'id':action_id,'data':ch0}
		hkl.dump(data0, filename+'_ch0.raw',compression="lzf")
		data1 = {'id':action_id,'data':ch1}
		hkl.dump(data1, filename+'_ch1.raw',compression="lzf")
		data2 = {'id':action_id,'data':ch2}
		hkl.dump(data2, filename+'_ch2.raw',compression="lzf")
		data3 = {'id':action_id,'data':ch3}
		hkl.dump(data3, filename+'_ch3.raw',compression="lzf")

	# file = open(filename+'_'+action_id+'_ch0.raw', 'w')
	# np.save(file,ch0)
	# file = open(filename+'_'+action_id+'_ch1.raw', 'w')
	# np.save(file,ch1)
	# file = open(filename+'_'+action_id+'_ch2.raw', 'w')
	# np.save(file,ch2)
	# file = open(filename+'_'+action_id+'_ch3.raw', 'w')
	# np.save(file,ch3)

	if write_wav:
		scaled0 = np.int16((np.double(ch0)-2047)/2048 * 32767)
		scaled1 = np.int16((np.double(ch1)-2047)/2048 * 32767)
		scaled2 = np.int16((np.double(ch2)-2047)/2048 * 32767)
		scaled3 = np.int16((np.double(ch3)-2047)/2048 * 32767)
		write(filename+'_ch0.wav', 8000, scaled0)
		write(filename+'_ch1.wav', 8000, scaled1)
		write(filename+'_ch2.wav', 8000, scaled2)
		write(filename+'_ch3.wav', 8000, scaled3)

	if plot:
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
		plt.figure("First subset ch0")
		plt.ylim(-100,4196);
		plt.xlim(0,window_subset);
		handle, = plt.plot(ch0[0:window_subset-1])
		plt.draw()

	raw_input("Press Enter to continue...")

#record("testdata/test",plot=True,write_wav=True,write_raw=True)

for i in range(10):
	record("testdata/elias"+str(i),write_raw=True)

