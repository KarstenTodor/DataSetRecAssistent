import time
import pylab as plt
import numpy as np
import thread
import os 
import sys

import scipy.io.wavfile as wav
import scipy.io.wavfile as wav



in_wav = "testdata/test2_32.wav"
out_wav = "testdata/test2_32_downs10.wav"
downscaling_factor = 10

in_rate, in_data = wav.read(in_wav)
l = len(in_data)
out_data = in_data[0:-1:downscaling_factor] 
out_data = np.int16(out_data)
wav.write(out_wav, in_rate/downscaling_factor, out_data)