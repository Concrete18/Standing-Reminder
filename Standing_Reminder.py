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

tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Normal_Icon.png', tooltip=f'Standing Reminder')
time_left = 0
non_idle_time = 0
stop_command = 0
timer_reset = 0

class LASTINPUTINFO(Structure):
    _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]


def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

Config = configparser.RawConfigParser()

def write_to_config():
    with open('Config.ini', 'w') as configfile:
        Config.write(configfile)


def main_func():
    Config.read('Config.ini')
    wait_till_idle = int(Config.get('Main', 'wait_till_idle'))
    check_frequency = int(Config.get('Main', 'check_frequency'))
    reminder_time = int(Config.get('Main', 'reminder_time'))
    past_reminder_frequency = int(Config.get('Main', 'past_reminder_frequency')) * 60
    required_idle_time = int(Config.get('Main', 'required_idle_time'))
    notification_popup = int(Config.get('Main', 'notification_popup'))
    non_idle_time = 0
    last_run = dt.datetime.now()
    print(f'Standing Reminder set with a {check_frequency} minute frequency and a idle detection set to {wait_till_idle} minutes.')
    logger.info(f'Standing Reminder set with a {check_frequency} minute frequency and a idle detection set to {wait_till_idle} minutes.')
    tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {reminder_time} minutes.')
    while True:
        time.sleep(check_frequency * 60)
        idle_duration = get_idle_duration()
        if idle_duration > wait_till_idle * 60:
            tray.update(filename='Passed_Reminder.png')
            non_idle_time = 0
            logger.info('Computer is Idle')
            while idle_duration > wait_till_idle * 60:
                idle_duration = get_idle_duration()
                time.sleep(check_frequency * 60)
            logger.info('Computer is no longer Idle')
        else:
            non_idle_time += 1
            if dt.datetime.now() - last_run >= dt.timedelta(minutes=wait_till_idle):
                tray.update(filename='Passed_Reminder.png')
                non_idle_time = 0
                logger.info(f'Computer was asleep for more then {wait_till_idle} minutes. Resetting timer.')
            time_left = reminder_time - non_idle_time
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {time_left} minutes.')
        last_run = dt.datetime.now()
        print(f'PC has been used for {non_idle_time} minute(s).    ', end="\r")
        if non_idle_time >= reminder_time:
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {reminder_time} minutes.', filename='Passed_Reminder.png')
            if notification_popup == 0:
                playsound('juntos.mp3')
            logger.info(f'PC has passed active time limit of {reminder_time} minutes.')
            while idle_duration < required_idle_time or non_idle_time > reminder_time:
                idle_duration = get_idle_duration()
                if notification_popup == 1:
                    tray.update(filename='Passed_Reminder.png')
                    tray.ShowMessage('Standing Reminder', f'PC has been used for {non_idle_time} minute(s).\nStop using the computer for {required_idle_time} minutes to reset this reminder.\n', time=10)
                time.sleep(past_reminder_frequency)
            logger.info(f'Inactivity Met - Resetting')
            tray.Update(tooltip=f'Standing Reminder\nInactivity Met: Wait for next check cycle for new reminder.', filename='Normal_Icon.png')
            non_idle_time = 0


main_thread = threading.Thread(target=main_func, daemon=True)
main_thread.start()

while True:
    event = tray.Read()
    print(event)
    if event == 'Exit':
        quit()
        tray.update(filename='Passed_Reminder.png')
        tray.update(filename='Normal_Icon.png')
