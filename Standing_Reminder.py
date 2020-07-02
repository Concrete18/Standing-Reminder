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
logFile = f'{os.getcwd()}\\script.log'

my_handler = RotatingFileHandler(logFile, maxBytes=5*1024*1024, backupCount=2)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(lg.DEBUG)

logger = lg.getLogger(__name__)
logger.setLevel(lg.DEBUG)
logger.addHandler(my_handler)

<<<<<<< HEAD
root = tk.Tk()
root.withdraw()
tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Media/Normal_Icon.png', tooltip=f'Standing Reminder')

=======
>>>>>>> dev
class LASTINPUTINFO(Structure):
    _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]


def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

Config = configparser.RawConfigParser()

<<<<<<< HEAD
=======
Config = configparser.RawConfigParser()


>>>>>>> dev
def write_to_config():
    with open('Config.ini', 'w') as configfile:
        Config.write(configfile)

<<<<<<< HEAD

def main_func():
    Config.read('Config.ini')
    wait_till_idle = int(Config.get('Main', 'wait_till_idle'))
    check_frequency = int(Config.get('Main', 'check_frequency'))
    reminder_time = int(Config.get('Main', 'reminder_time'))
    past_reminder_frequency = int(Config.get('Main', 'past_reminder_frequency')) * 60
    required_idle_time = int(Config.get('Main', 'required_idle_time'))
    notification_popup = int(Config.get('Main', 'notification_popup'))
    active_time = 0
    last_run = dt.datetime.now()
    print(f'Standing Reminder set with a {check_frequency} minute frequency and a idle detection set to {wait_till_idle} minutes.')
    tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {reminder_time} minutes.')
    # Main Loop
    while True:
        time.sleep(check_frequency * 60)
        if get_idle_duration() > wait_till_idle * 60:
            tray.update(filename='Media/Passed_Reminder.png')
            active_time = 0
            logger.info('Computer is Idle')
            tray.Update(tooltip=f'Standing Reminder\nComputer is Idle.', filename='Media/Idle_ Icon.png')
            while get_idle_duration() > wait_till_idle * 60:
                time.sleep(check_frequency * 60)
            tray.update(filename='Media/Normal_Icon.png')
            logger.info('Computer is no longer Idle')
        # Sleep Detection
        else:
            active_time += 1
            if dt.datetime.now() - last_run >= dt.timedelta(minutes=wait_till_idle):
                tray.update(filename='Media/Passed_Reminder.png')
                active_time = 0
                tray.ShowMessage('Standing Reminder', f'Computer was asleep for more then {wait_till_idle} minutes. Resetting timer.', time=10)
                logger.info(f'Computer was asleep for more then {wait_till_idle} minutes. Resetting timer.')
            time_left = reminder_time - active_time
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {time_left} minutes.')
        last_run = dt.datetime.now()
        print(f'PC has been used for {active_time} minute(s).    ', end="\r")
        # Check if passed reminder time.
        if active_time >= reminder_time:
            tray.Update(tooltip=f'Standing Reminder\nNext Reminder: {reminder_time} minutes.', filename='Media/Passed_Reminder.png')
            if notification_popup == 0:
                playsound('Media/juntos.mp3')
            logger.info(f'PC has passed active time limit of {reminder_time} minutes.')
            while get_idle_duration() < required_idle_time or active_time > reminder_time:
                tray.update(filename='Media/Passed_Reminder.png',tooltip='Standing Reminder\nStand up and stretch')
                if notification_popup == 1:
                    tray.ShowMessage('Standing Reminder', f'PC has been used for {active_time} minute(s).\nStop using the computer for {required_idle_time} minutes to reset this reminder.\n', time=10)
                time.sleep(past_reminder_frequency)
            logger.info(f'Inactivity Met - Resetting')
            tray.Update(tooltip=f'Standing Reminder\nInactivity Met: Wait for next check cycle for new reminder.', filename='Media/Normal_Icon.png')
            active_time = 0


main_thread = threading.Thread(target=main_func, daemon=True)
main_thread.start()
=======
root = tk.Tk()
root.withdraw()
tray = sg.SystemTray(menu= ['menu',['E&xit']], filename='Media/Normal_Icon.png')

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
        self.active_time = 0
        self.early_cancel = 0
        self.timer_reset = False
        self.last_run = dt.datetime.now()


    def idle_check(self):
        if get_idle_duration() > self.wait_idle * 60:
            self.active_time = 0
            logger.debug('Computer is Idle')
            tray.Update(tooltip=f'{self.title}\nComputer is Idle.', filename='Media/Idle_ Icon.png')
            while get_idle_duration() > self.wait_idle * 60:
                self.last_run = dt.datetime.now()
                time.sleep(self.check_freq * 60)
            tray.update(filename='Media/Normal_Icon.png')
            logger.debug('Computer is no longer Idle')
        else:
            self.active_time += 1
            if dt.datetime.now() - self.last_run >= dt.timedelta(minutes=self.wait_idle):
                tray.update(filename='Media/Normal_Icon.png')
                self.active_time = 0
                tray.ShowMessage(f'{self.title}', f'Computer was asleep for more then {self.wait_idle} minutes. Resetting timer.', time=10)
                logger.debug(f'Computer was asleep for more then {self.wait_idle} minutes. Resetting timer.')
            self.time_left = self.remind_time - self.active_time
            tray.Update(tooltip=f'{self.title}\nNext Reminder: {self.time_left} minutes.',\
            filename='Media/Normal_Icon.png')


    def check_reminder(self):
        self.last_run = dt.datetime.now()
        if self.active_time >= self.remind_time:
            tray.update(tooltip=f'{self.title}\nStand up and stretch', filename='Media/Passed_Reminder.png')
            if self.notif_popup == 0:
                playsound('Media/juntos.mp3')
            logger.debug(f'PC has passed active time limit of {self.remind_time} minutes.')
            while get_idle_duration() < self.req_idle_time:
                if self.early_cancel == 1:
                    self.early_cancel = 0
                    break
                if self.notif_popup == 1:
                    tray.ShowMessage(self.title, f'PC has been used for {self.active_time} minute(s).\nStop using the computer for {self.req_idle_time} minutes to reset this reminder.\nTap Icon to Cancel Early.')
                time.sleep(self.check_freq * 60)
                if dt.datetime.now() - self.last_run >= dt.timedelta(minutes=self.wait_idle):
                    self.last_run = dt.datetime.now()
                    break
            logger.debug(f'Inactivity Met - Resetting')
            tray.Update(tooltip=f'{self.title}\nInactivity Met: Resetting within 1 minute.',\
            filename='Media/Normal_Icon.png')
            self.active_time = 0


    def run(self):
        tray.Update(tooltip=f'{main.title}\nNext Reminder: {self.remind_time} minutes.')
        self.last_run = dt.datetime.now()
        print(f'{main.title} has started with a {self.check_freq} minute frequency and a idle detection set to {self.wait_idle} minutes.')
        logger.debug(f'{self.title} set with a {self.check_freq} minute frequency and a idle detection set to {self.wait_idle} minutes.')
        while True:
            time.sleep(self.check_freq * 60)
            self.last_run = dt.datetime.now()
            self.idle_check()
            print(f'PC has been used for {self.active_time} minute(s).       ', end="\r")
            self.check_reminder()


if __name__ == '__main__':
    main = App()
    main_thread = threading.Thread(target=main.run, daemon=True)
    main_thread.start()
>>>>>>> dev

while True:
    event = tray.Read()
    # print(event)
    if event == 'Exit':
        quit()
<<<<<<< HEAD
=======
    elif event == '__ACTIVATED__' or '__MESSAGE_CLICKED__':
        main.early_cancel = 1
        tray.Update(tooltip=f'{main.title}\nNext Reminder: {main.remind_time} minutes.', filename='Media/Normal_Icon.png')
>>>>>>> dev
