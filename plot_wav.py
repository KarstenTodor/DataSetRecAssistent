from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import sys
import math
import numpy as np

#TODO write a decent input guard
filename = sys.argv[1]
peak_detection = (sys.argv[2] == True) or (sys.argv[2] == "1")
print "Arguments: ", sys.argv[1], sys.argv[2]


# read audio samples
input_data = read(filename)
audio = input_data[1]
# plot the first 1024 samples
plt.plot(audio)
plt.ylim(-32767,32767);
# label the axes
plt.ylabel("Amplitude")
plt.xlabel("Time")
# set the title  
plt.title(filename)

if peak_detection:
	peak_detected = False
	peak_value = 0
	peak_pos = -1
	for i in range(1,len(audio)):
		moving_avg = -1
		if i<(5000):
			moving_avg = np.sum(np.abs(1.0*audio[0:i]))/i
		else:
			moving_avg = np.sum(np.abs(1.0*audio[i-5000:i]))/5000
		abs_value = np.abs(audio[i])
		if abs_value >(15*moving_avg):
			if peak_detected:
				if peak_value < abs_value:
					peak_value = abs_value
					peak_pos = i
			else:
				peak_value = abs_value
				peak_pos = i
				peak_detected = True
		else:
			if peak_detected:
				print "peak detected at ", peak_pos, " with a value of ", peak_value
				plt.plot((peak_pos, peak_pos), (-32767, 32767), 'y', alpha=.5)
				peak_detected = False

# display the plot
plt.show()

plt.draw()

#raw_input("Press Enter to continue...")