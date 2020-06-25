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

tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Standing.png', tooltip=f'Standing Reminder')

class App:

    def __init__(self):
        Config.read('Config.ini')
        self.title = 'Standing Reminder'
        self.wait_idle = Config.get('Main', 'wait_till_idle')
        self.check_freq = Config.get('Main', 'check_frequency')
        self.remind_time = Config.get('Main', 'reminder_time')
        self.req_idle_time = Config.get('Main', 'required_idle_time')
        self.notif_popup = Config.get('Main', 'notification_popup')
        self.time_left = 0
        self.non_idle_time = 0
        self.timer_reset = False
        self.last_run = dt.datetime.now()

    def increase_idle(self):
        self.non_idle_time += 1


    def update_last_run(self):
        self.last_run = dt.datetime.now()

    main = App()
    print(main.title)


    def check_reminder(self):
        if App.non_idle_time >= App.remind_time:
            tray.Update(tooltip=f'{App.title}\nNext Reminder: {App.remind_time} minutes.')
        if App.notif_popup == 0:
            playsound('juntos.mp3')
        logger.info(f'PC has passed active time limit of {App.remind_time} minutes.')
        while get_idle_duration() < App.req_idle_time:
            if App.notif_popup == 1:
                tray.ShowMessage(App.title, f'PC has been used for {App.non_idle_time} minute(s).\nStop using the computer for {App.req_idle_time} minutes to reset this reminder.\n', time=10)
            time.sleep(App.check_freq)
            if sleep_check(App.last_run, App.wait_idle):
                break
            elif timer_reset is True:
                break
            print(App.last_run)
            App.update_last_run

        logger.info(f'Inactivity Met - Resetting')
        tray.Update(tooltip=f'{App.title}\nInactivity Met: Wait for next check cycle for new reminder.')
        non_idle_time = 0


    def sleep_check(self):
        if dt.datetime.now() - App.last_run >= dt.timedelta(minutes=App.wait_idle):
            result = True
        App.update_last_run
        return result


    def idle_check(self):
        if get_idle_duration() > App.wait_idle * 60:
            non_idle_time = 0
            logger.info('Computer is Idle')
            while get_idle_duration() > App.wait_idle * 60:
                time.sleep(App.check_freq * 60)
            logger.info('Computer is no longer Idle')
        else:
            non_idle_time += 1
            if dt.datetime.now() - App.last_run >= dt.timedelta(minutes=App.wait_idle):
                non_idle_time = 0
                logger.info(f'Computer was asleep for more then {App.wait_idle} minutes. Resetting timer.')
            time_left = App.remind_time - non_idle_time
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {time_left} minutes.')


    def main_func(self):
        last_run = dt.datetime.now()
        title = 'Standing Reminder'
        print(f'remind_time set with a {App.check_freq} minute frequency and a idle detection set to {App.wait_idle} minutes.')
        logger.info(f'remind_time set with a {App.check_freq} minute frequency and a idle detection set to {App.wait_idle} minutes.')
        tray.Update(tooltip=f'remind_time\nNext Reminder: {App.remind_time} minutes.')
        while True:  # Main Loop
            time.sleep(App.check_freq * 60)
            idle_duration = get_idle_duration()
            idle_check()
            last_run = dt.datetime.now()
            print(f'PC has been used for {non_idle_time} minute(s).           ', end="\r")
            check_reminder()


    main_thread = threading.Thread(target=main_func, daemon=True)
    main_thread.start()

while True:
    event = tray.Read()
    # print(event)
    if event == 'Exit':
        quit()
    # elif event == '__ACTIVATED__':
    #     tray.Update(icon='PH')
    elif event == '__DOUBLE_CLICKED__':
        timer_reset = True
        non_idle_time = 0
        tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {App.time_left} minutes.')
