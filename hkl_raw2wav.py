import time
import pylab as plt
import numpy as np
import thread
import os 
import sys
import hickle as hkl

from scipy.io.wavfile import write


def read(filename):
	lib = hkl.load(filename)
	return lib['data'], lib['id'] 

def find(path, extension):
	files = []
	for f in os.listdir(path):
		if f.endswith(extension):
				files.append(f)
	return files 

#input guards
argc = len(sys.argv)

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: Source Path %s was not found!' % sys.argv[1])
if not os.path.exists(sys.argv[2]):
    sys.exit('ERROR: Sink Path %s was not found!' % sys.argv[2])

src_path = sys.argv[1]
dest_path = sys.argv[2]
sample_freq = 8000

files = find(src_path,".raw")
for f in files:
	data, id = read(src_path+"/"+f)
	print "data, ", data[0:50]
	scaled = np.int16((np.float64(data)-2047)/2048 * 32767)
	print "scaled, ", scaled[0:50]
	out_wav = dest_path+"/"+f.rstrip(".raw")+".wav"
	write(out_wav, sample_freq, scaled)