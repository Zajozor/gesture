import numpy as np
import matplotlib.pyplot as plt
'''
t = np.arange(8)
print('time: ', t)
sp = np.fft.fft([1,0,0,0,0,0,0,0])
print('values :', sp)
freq = np.fft.fftfreq(t.shape[-1])
print('freqs :', freq)

x = np.arange(0, 7, 0.1)
sines = [np.absolute(sp[i])*np.sin(2*np.pi*(freq[i])*x+np.angle(sp[i])) for i in range(len(sp))]

print(x)
print(sines)

ss = np.sum(sines[:len(sines)], axis=0)



# plt.plot(freq, sp.real, freq, sp.imag)

for i in range(len(sines)):
    plt.plot(x, sines[i], color=['red','green','blue','orange','yellow','cyan','magenta','purple'][i])

plt.plot(x,ss, color='0')
plt.show()
'''

import matplotlib.pyplot as plt
import numpy as np
# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

Fs = 100.0  # sampling rate
Ts = 1.0/Fs # sampling interval
t = np.arange(0,10,Ts) # time vector

ff = 2/np.pi   # frequency of the signal
ff2 = 1/np.pi
y = np.sin(2*np.pi*ff*t) + np.sin(2*np.pi*ff2*t)

n = len(y) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = np.pi*frq[:n//2] # one side frequency range

Y = np.fft.fft(y)/n # fft computing and normalization
Y = Y[:n//2]

fig, ax = plt.subplots(2, 1)
ax[0].plot(t,y)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Amplitude')
ax[1].plot(frq,Y.real,'r') # plotting the spectrum
ax[1].plot(frq,Y.imag,'b') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('|Y(freq)|')


plt.show()
#plot_url = py.plot_mpl(fig, filename='mpl-basic-fft')