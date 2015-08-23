import time
import pylab as plt
import numpy as np
import thread
import os 
import sys

from scipy.io.wavfile import write



#input guards
argc = len(sys.argv)
if argc < 3 or argc > 4:
    sys.exit('Usage: <raw input filename> <wav output filename> <sample frequency (integer)>')

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: Raw input file %s was not found!' % sys.argv[1])

in_raw = sys.argv[1]
out_wav = sys.argv[2]
sample_freq = 44000
if argc == 4:
	if not sys.argv[3].isdigit():
		sys.exit('ERROR: Expecting a integer value for the sample frequency, but received %s instead! \nUsage: <raw input filename> <wav output filename> <sample frequency (integer)>' % sys.argv[1])
	else:
		sample_freq = int(sys.argv[3])

print "Reading ", in_raw, "..."
f = open(in_raw,'r')
f.close()
z = np.load(in_raw)
a = np.double(z)
scaled = np.int16((a-2047)/2048 * 32767)
print "scaled", scaled
write(out_wav, sample_freq, scaled)