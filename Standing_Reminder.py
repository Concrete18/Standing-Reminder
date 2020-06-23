from ctypes import Structure, windll, c_uint, sizeof, byref
from logging.handlers import RotatingFileHandler
from playsound import playsound
from tkinter import messagebox
import PySimpleGUIWx as sg
import datetime as dt
import logging as lg
import tkinter as tk
import configparser
import subprocess
import threading
import time
import os

Config = configparser.RawConfigParser()

def write_to_config():
    with open('Config.ini', 'w') as configfile:
        Config.write(configfile)

Config.read('Config.ini')

log_formatter = lg.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p')
logFile = f'{os.getcwd()}\\Standing_Reminder.log'

my_handler = RotatingFileHandler(logFile, maxBytes=5*1024*1024, backupCount=2)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(lg.INFO)

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)
logger.addHandler(my_handler)

root = tk.Tk()
root.withdraw()


class LASTINPUTINFO(Structure):
    _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]


def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


root = tk.Tk()
root.withdraw()

tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Standing.png', tooltip=f'Standing Reminder')

global time_left
time_left = 0

def main_func():
    with open('Config.ini', 'r') as configfile:
        Config.read(configfile)
        wait_till_idle = int(Config.get('Main', 'wait_till_idle'))
        check_frequency = int(Config.get('Main', 'check_frequency'))
        reminder_time = int(Config.get('Main', 'reminder_time'))
        non_idle_time = 0
        last_run = dt.datetime.now()
    print(f'Standing Reminder set with a {check_frequency} minute frequency and a idle detection set to {wait_till_idle} minutes.')
    while True:
        time.sleep(check_frequency * 60)
        idle_duration = get_idle_duration()
        if idle_duration > wait_till_idle * 60:
            non_idle_time = 0
            print('Computer is Idle')
        else:
            time_difference = dt.datetime.now() - last_run
            print(time_difference)
            if dt.datetime.now() - last_run >= wait_till_idle:
                print('Computer was asleep\nResetting timer.')
            non_idle_time += 1
            time_left = reminder_time - non_idle_time
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {time_left} minutes.')
            last_run = dt.datetime.now()
        print(f'PC has been used for {non_idle_time} minute(s).')
        if non_idle_time >= reminder_time:
            #  Todo set showmessage to replace old one and switch to bubble message if possible.
            # playsound('myfile.wav')
            tray.ShowMessage('Standing Reminder', f'PC has been used for {non_idle_time} minute(s).\nYou should stand up and stretch some.\n', time=10)
            print('You should stand up and stretch some.\n')
            non_idle_time = 0


main_thread = threading.Thread(target=main_func, daemon=True)
main_thread.start()

while True:
    event = tray.Read()
    print(event)
    if event == 'Exit':
        quit()
    elif event == '__DOUBLE_CLICKED__':
        non_idle_time = 0
        tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {time_left} minutes.')
