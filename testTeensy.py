import serial 
from AutoDetectSerial import AutoDetectSerial
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import hickle as hkl
import thread
import sys
from random import randrange
from scipy.io.wavfile import write
from distutils.util import strtobool

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

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
	#actions = ["tap - up - tap", "tap - down - tap", "tap - left - tap", "tap - right - tap"]
	actions = ["wijsvinger - 1", "middelvinger - 2", "ringvinger - 3", "pink - 4"]
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

	# file = open(filename+'_'+action_id+'_ch0.raw', 'w')
	# np.save(file,ch0)
	# file = open(filename+'_'+action_id+'_ch1.raw', 'w')
	# np.save(file,ch1)
	# file = open(filename+'_'+action_id+'_ch2.raw', 'w')
	# np.save(file,ch2)
	# file = open(filename+'_'+action_id+'_ch3.raw', 'w')
	# np.save(file,ch3)

	f = None
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
		plt.pause(1e-9)
		#Put figure window on top of all other windows
		f.canvas.manager.window.attributes('-topmost', 1)
		#After placing figure window on top, allow other windows to be on top of it later
		f.canvas.manager.window.attributes('-topmost', 0)

	written = True
	query = False
	if write_raw or write_wav:
		query = query_yes_no("Sample good enough to save?")

	if write_raw and query:
		data0 = {'id':action_id,'data':ch0}
		hkl.dump(data0, filename+'_ch0.raw',compression="lzf")
		data1 = {'id':action_id,'data':ch1}
		hkl.dump(data1, filename+'_ch1.raw',compression="lzf")
		data2 = {'id':action_id,'data':ch2}
		hkl.dump(data2, filename+'_ch2.raw',compression="lzf")
		data3 = {'id':action_id,'data':ch3}
		hkl.dump(data3, filename+'_ch3.raw',compression="lzf")
	else:
		written = False

	if write_wav and query:
		scaled0 = np.int16(np.double(ch0)-32767)
		scaled1 = np.int16(np.double(ch1)-32767)
		scaled2 = np.int16(np.double(ch2)-32767)
		scaled3 = np.int16(np.double(ch3)-32767)
		write(filename+'_ch0.wav', 12000, scaled0)
		write(filename+'_ch1.wav', 12000, scaled1)
		write(filename+'_ch2.wav', 12000, scaled2)
		write(filename+'_ch3.wav', 12000, scaled3)

	#raw_input("Press Enter to continue...")

	if f != None:
		plt.close(f)

	return written


def recordDataSet(basename, numberOfSamples):
	it=0
	while it<numberOfSamples:
		successful = record(basename+"_"+str(it),plot=True, write_raw = True, write_wav = True)
		if successful:
			it += 1

#record("testdata/test",plot=True,write_wav=True)

# for i in range(10):
#     record("testdata/test_"+str(i),plot=True)

recordDataSet("testdata/session20151021/elias1_L",1000)


