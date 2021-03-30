try:
    # Import GUI stuff and whatnot
    import wx
    import sys
    import importlib
    import configparser

    # Import Google stuff
    import concurrent.futures
    import json
    import logging
    import os
    import os.path
    import pathlib2 as pathlib
    import sys
    import time
    import uuid

    import click
    import grpc
    import google.auth.transport.grpc
    import google.auth.transport.requests
    import google.oauth2.credentials
    import subprocess

    from google.assistant.embedded.v1alpha2 import (
        embedded_assistant_pb2,
        embedded_assistant_pb2_grpc
    )

    from tenacity import retry, stop_after_attempt, retry_if_exception

    # Import buttons and other stuff
    import RPi.GPIO as GPIO
    import time
    
    import math
    import pyaudio # sudo apt-get install python{,3}-pyaudio
    import wave
    import configparser
    
except Exception as e:
    print("Error:\n" + str(e))
    print("\n\nAre you sure you installed all the libraries correctly?")
    exit(1)

# Initialise configparser
config = configparser.ConfigParser()

os.system("cp /media/*/*/config.ini /home/pi/Universal-IoT-Control-Panel/config.ini")

try:
    print("Reading Config...")
    config.read('/home/pi/Universal-IoT-Control-Panel/config.ini')
    assistantModelID = config["assistant"]["modelID"]
    assistantProjectID = config["assistant"]["projectID"]
except Exception as e:
    print("Config read failed...")

if os.geteuid() == 0:
    with open("/etc/rc.local", "w") as rcLocal:
        rcLocal.write("""
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

python3 /home/pi/Universal-IoT-Control-Panel/main.py &
exit 0
""")
       
        rcLocal.close()
    time.sleep(3)
    input("Installation complete! Press enter to reboot")
    os.system("sudo reboot")

print("Setting up sound...")
os.system('pacmd set-default-sink "alsa_output.usb-Generic_USB2.0_Device_20130100ph0-00.analog-stereo"')
os.system('pacmd set-default-source "alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono"')
os.system('pactl set-source-volume "alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono" 100%')
print("Done!\n\n")

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range

def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()


input("Press enter when ready...")

print("Testing buttons:")

GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

inputA = True
inputB = True
inputC = True

print("Please Press Button 1")
while inputA != False:
    inputA = GPIO.input(16)
    time.sleep(0.2)

print("Please Press Button 2")
while inputB != False:
    inputB = GPIO.input(20)
    time.sleep(0.2)

print("Please Press Button 3")
while inputC != False:
    inputC = GPIO.input(21)
    time.sleep(0.2)

input("Buttons are functional, press enter to test the speaker")

sine_tone(
    frequency=440.00,
    duration=1,
    volume=1,
    sample_rate=22050
)

soundCheck = input("Did you hear the sound? (y/N): ")
if soundCheck != "y":
    print("Please check your speaker and try again")
    exit(1)

# Microphone test
try:
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    input('Press enter and say something to test your microphone...')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    filename = 'output.wav'

    # Set chunk size of 1024 samples per data frame
    chunk = 1024  

    # Open the sound file 
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while data != b'' and data != '':
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()
except Exception as e:
    print("Error:\n" + str(e))
    print("\n\nPlease check your installation and try again")
    exit(1)

soundCheck = input("Did you hear what you said? (y/N): ")
if soundCheck != "y":
    print("Please check your speaker and/or microphone and try again")
    exit(1)

input("Press enter to initialise Google Assistant Instalation")

os.system("cp /media/*/*/client_secret_*-*.apps.googleusercontent.com.json /home/pi/Universal-IoT-Control-Panel/client_secrets.json")

time.sleep(1)

command = "google-oauthlib-tool --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless --client-secrets /home/pi/Universal-IoT-Control-Panel/client_secrets.json"
authentication = os.system(command)
if (authentication != 0):
    print("Error with Authentication: Did you enter the correct code?")
    exit(1)

os.system('sudo python3 /home/pi/Universal-IoT-Control-Panel/install.py')
