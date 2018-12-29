# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 09:23:30 2018

@author: Anjali
"""

import speech_recognition as sr


while True:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say Something")
        audio = r.listen(source)
        print("Processing")

        try:
            print("You Said " + r.recognize_google(audio));
        except:
            print('UNRECOGNIZED')

'''
try:
    print("You Said" + r.recognise_google(audio));
except:
    print('Call failed ? ')
'''