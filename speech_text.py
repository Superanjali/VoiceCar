# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 09:28:40 2018

@author: Sophia
"""
from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave
import json
import requests
#import cv2
import serial
import speech_recognition as sr

ARDUINO_SERIAL_PORT = 'COM10'

# Microphone to wav ###########################################################

#THRESHOLD = 500
THRESHOLD = 700
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r

def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')
    
    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()
    return sample_width

'''
if __name__ == '__main__':
    print("please speak a word into the microphone")
    record_to_file('demo.wav')
    print("done - result written to demo.wav")
'''
    
# AI (Speech to text) #########################################################

YOUR_API_KEY = '4e5c11ebf7e24e84ba8cdcd8a2a0d8fe'
YOUR_AUDIO_FILE = 'demo.wav'
REGION = 'westus' # westus, eastasia, northeurope 
MODE = 'interactive'
LANG = 'en-US'
cognitive_FORMAT = 'simple'


def handler():
    # 1. Get an Authorization Token
    token = get_token()
    # 2. Perform Speech Recognition
    results = get_text(token, YOUR_AUDIO_FILE)
    # 3. Print Results
    #print(results)
    key = 'DisplayText'
    return results.get(key)

def get_token():
    # Return an Authorization Token by making a HTTP POST request to Cognitive Services with a valid API key.
    url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': YOUR_API_KEY
    }
    r = requests.post(url, headers=headers)
    token = r.content
    return(token)

def get_text(token, audio):
    # Request that the Bing Speech API convert the audio to text
    url = 'https://{0}.stt.speech.microsoft.com/speech/recognition/{1}/cognitiveservices/v1?language={2}&format={3}'.format(REGION, MODE, LANG, cognitive_FORMAT)
    headers = {
        'Accept': 'application/json',
        'Ocp-Apim-Subscription-Key': YOUR_API_KEY,
        'Transfer-Encoding': 'chunked',
        'Content-type': 'audio/wav; codec=audio/pcm; samplerate=16000',
        'Authorization': 'Bearer {0}'.format(token)
    }
    r = requests.post(url, headers=headers, data=stream_audio_file(audio))
    results = json.loads(r.content)
    return results

def stream_audio_file(speech_file, chunk_size=1024):
    # Chunk audio file
    with open(speech_file, 'rb') as f:
        while 1:
            data = f.read(1024)
            if not data:
                break
            yield data
            
def sophsloop(com, rep, text, key, translation):    
    for elem in com:
        if translation.find(elem) >= 0:
            print('Executing:' + text)
            for i in range(rep):
                ser.write(key)
            continue
        
def check_active(command, car, names):
    valid = False
    for name in names:
        if command.find(name) >=0:
            car = name
            valid = True
            break
    if not valid:
        for name in ['move','go']:
            if command.find(name) >=0:
                valid = True
                break
        print('Please specify car name or keywords move, go')
    if car is None:
        valid = False
        print('Please set active car')
    return car, valid
    
# Main loop #################################################################

#if True:
try:
    ser = serial.Serial(ARDUINO_SERIAL_PORT, 9600, timeout=0)

    
    #back_left_list = ['reverse left'] #a
    #back_right_list = ['reverse right'] #d
    forward_list = ['forward', 'front', 'go'] #w
    back_list = ['reverse', 'back', 'mac'] #s
    forward_left_list = ['left'] #q
    forward_right_list = ['right'] #e
    active_car = None
    car_names = ['bob','jack']


    while True:
        r = sr.Recognizer()
        print("GREEN. Please speak a word into the microphone")
        ser.write(b'b')
        #record_to_file('demo.wav')
        with sr.Microphone() as source:
            audio = r.listen(source)
        print('RED. Processing your command')
        ser.write(b'r')
        #translation = handler()
        try:
            translation = r.recognize_google(audio)
        except:
            translation = None
            
        if translation is None:
            print('Sorry. I did not understand.')
            continue
        
        translation = translation.lower()
        print('Recieved:' + translation)
        
        active_car, valid = check_active(translation, active_car, car_names)
        if not valid:
            continue
            
        #print('Unrecognized command')
        #sophsloop(back_left_list, 10, 'reverse left', b'a', translation)
        #sophsloop(back_right_list, 10, 'reverse right', b'd', translation)
        sophsloop(forward_list, 1, 'front', b'w', translation)
        sophsloop(back_list, 1, 'back', b's', translation)
        sophsloop(forward_left_list, 1, 'left', b'q', translation)
        sophsloop(forward_right_list, 1, 'right', b'e', translation)

       
except Exception as error:
    print(error)
    ser.close()
