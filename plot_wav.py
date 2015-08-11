from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import sys


filename = sys.argv[1]

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
# display the plot
plt.show()

#raw_input("Press Enter to continue...")