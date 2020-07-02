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


log_formatter = lg.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p')
logFile = f'{os.getcwd()}\\Standing_Reminder.log'

my_handler = RotatingFileHandler(logFile, maxBytes=5*1024*1024, backupCount=2)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(lg.INFO)

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)
logger.addHandler(my_handler)

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

tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Standing.png')

class App:

    def __init__(self):
        Config.read('Config.ini')
        self.title = 'Standing Reminder'
        self.wait_idle = int(Config.get('Main', 'wait_till_idle'))
        self.check_freq = int(Config.get('Main', 'check_frequency'))
        self.remind_time = int(Config.get('Main', 'reminder_time'))
        self.req_idle_time = int(Config.get('Main', 'required_idle_time'))
        self.notif_popup = int(Config.get('Main', 'notification_popup'))
        self.time_left = 0
        self.non_idle_time = 0
        self.timer_reset = False
        self.last_run = dt.datetime.now()


    def idle_check(self):
        if get_idle_duration() > self.wait_idle * 60:
            self.non_idle_time = 0
            logger.info('Computer is Idle')
            while get_idle_duration() > self.wait_idle * 60:
                time.sleep(self.check_freq * 60)
            logger.info('Computer is no longer Idle')
        else:
            self.non_idle_time += 1
            if dt.datetime.now() - self.last_run >= dt.timedelta(minutes=self.wait_idle):
                self.non_idle_time = 0
                logger.info(f'Computer was asleep for more then {self.wait_idle} minutes. Resetting timer.')
            self.time_left = self.remind_time - self.non_idle_time
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {self.time_left} minutes.')


    def check_reminder(self):
        if self.non_idle_time >= self.remind_time:
            tray.Update(tooltip=f'{self.title}\nNext Reminder: {self.remind_time} minutes.')
        if self.notif_popup == 0:
            playsound('juntos.mp3')
        logger.info(f'PC has passed active time limit of {self.remind_time} minutes.')
        while get_idle_duration() < self.req_idle_time:
            if self.notif_popup == 1:
                tray.ShowMessage(self.title, f'PC has been used for {self.non_idle_time} minute(s).\nStop using the computer for {self.req_idle_time} minutes to reset this reminder.\n', time=10)
            time.sleep(self.check_freq)
            if dt.datetime.now() - self.last_run >= dt.timedelta(minutes=self.wait_idle):
                self.last_run = dt.datetime.now()
                break
            elif self.timer_reset is True:
                break
            print(self.last_run)
            self.update_last_run
        logger.info(f'Inactivity Met - Resetting')
        tray.Update(tooltip=f'{self.title}\nInactivity Met: Wait for next check cycle for new reminder.')
        self.non_idle_time = 0


    def run(self):
        tray.Update(tooltip=f'{main.title}\nNext Reminder: {self.remind_time} minutes.')
        self.last_run = dt.datetime.now()
        print(f'{main.title} has started with a {self.check_freq} minute frequency and a idle detection set to {self.wait_idle} minutes.')
        logger.info(f'remind_time set with a {self.check_freq} minute frequency and a idle detection set to {self.wait_idle} minutes.')
        while True:  # Main Loop
            time.sleep(self.check_freq * 60)
            self.idle_check
            self.last_run = dt.datetime.now()
            print(f'PC has been used for {self.non_idle_time} minute(s).           ', end="\r")
            self.check_reminder


if __name__ == '__main__':
    main = App()
    main_thread = threading.Thread(target=main.run, daemon=True)
    main_thread.start()

while True:
    event = tray.Read()
    # print(event)
    if event == 'Exit':
        quit()
