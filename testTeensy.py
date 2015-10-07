import serial 
from AutoDetectSerial import AutoDetectSerial
import time
import pylab as plt
import numpy as np
import hickle as hkl
import thread
from random import randrange
from scipy.io.wavfile import write

def handshake(verbose,con):
	con.write("start\n")
	st = time.clock()
	if verbose:
		print "Connection %s" % con
		print 'Received handshake data from serial port: '
		print con.readline(),
		print con.readline(),
	else:
		con.readline()
		con.readline()
	et = time.clock()
	if verbose:
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
	window_bytes = 512*512

	ad = AutoDetectSerial()
	ad.open(115200)

	action, action_id = randomBasicAction()
	print "Action: ", action
	
	handshake(verbose,ad.con)

	while ad.con.inWaiting() == 0:
		time.sleep(1)
		if verbose: 
			print ad.con.inWaiting()

	st = time.clock()
	data = ad.con.read(window_bytes)	# this number should be larger than the number of bytes that will actually be sent
	ad.con.close()			# close serial port
	et = time.clock() - st
	# time.sleep(1)
	if verbose:
		print 'Elapsed time reading data (s): ', et
		print "len(data)", len(data)
	y = np.fromstring(data, dtype=np.uint16);
	if verbose:
		print len(y), y
	# if np.little_endian: 
	# 	y = y.byteswap()
	# print y

	ch3 = y[0:-1:4]
	ch2 = y[1:-1:4]
	ch1 = y[2:-1:4]
	ch0 = y[3:-1:4]

	window_complete = 512*512/2

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
		scaled0 = np.int16(np.double(ch0)-32767)
		scaled1 = np.int16(np.double(ch1)-32767)
		scaled2 = np.int16(np.double(ch2)-32767)
		scaled3 = np.int16(np.double(ch3)-32767)
		write(filename+'_ch0.wav', 12000, scaled0)
		write(filename+'_ch1.wav', 12000, scaled1)
		write(filename+'_ch2.wav', 12000, scaled2)
		write(filename+'_ch3.wav', 12000, scaled3)

	if plot:
		# sel0 = ch0[0:window_complete]
		# plt.ion()
		# plt.figure("Complete window channel 0")
		# plt.ylim(-100,65536);
		# plt.xlim(0,len(sel0));
		# handle, = plt.plot(sel0)
		# plt.draw()

		# sel1 = ch1[0:window_complete]
		# plt.ion()
		# plt.figure("Complete window channel 1")
		# plt.ylim(-100,65536);
		# plt.xlim(0,len(sel1));
		# handle, = plt.plot(sel1)
		# plt.draw()

		# sel2 = ch2[0:window_complete]
		# plt.ion()
		# plt.figure("Complete window channel 2")
		# plt.ylim(-100,65536);
		# plt.xlim(0,len(sel2));
		# handle, = plt.plot(sel2)
		# plt.draw()

		# sel3 = ch3[0:window_complete]
		# plt.ion()
		# plt.figure("Complete window channel 3")
		# plt.ylim(0,65536);
		# plt.xlim(0,len(sel3));
		# handle, = plt.plot(sel3)
		# plt.draw()

		# window_subset = 2000
		# plt.figure("First subset ch0")
		# plt.ylim(-100,65536);
		# plt.xlim(0,window_subset);
		# handle, = plt.plot(ch0[0:window_subset-1])
		# plt.draw()

		# row and column sharing
		plt.ion()
		f, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2, sharex='col', sharey='row')
		ax0.plot(ch0)
		ax0.set_title('ch0')
		ax0.set_ylim([-100,65536]);
		ax1.plot(ch1)
		ax1.set_title('ch1')
		ax1.set_ylim([-100,65536]);
		ax2.plot(ch2)
		ax2.set_title('ch2')
		ax2.set_ylim([-100,65536]);
		ax3.plot(ch3)
		ax3.set_title('ch3')
		ax3.set_ylim([-100,65536]);

	raw_input("Press Enter to continue...")

#record("testdata/test",plot=True,write_wav=True)

for i in range(10):
    record("testdata/elias_"+str(i),plot=True)

