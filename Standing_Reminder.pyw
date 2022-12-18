from ctypes import Structure, windll, c_uint, sizeof, byref
from logging.handlers import RotatingFileHandler
from win10toast import ToastNotifier
import threading, json, time, os
from playsound import playsound
import PySimpleGUIWx as sg
import datetime as dt
import logging as lg


class Settings:

    debug = 0
    if debug:
        title = "Standing Reminder"
        wait_idle = 1
        check_freq = 1
        remind_time = 5
        req_idle_time = 2
        enable_win_notif = True
        enable_audio_notif = True
    else:
        with open("config.json") as config:
            data = json.load(config)
        title = "Standing Reminder"
        wait_idle = data["config"]["wait_till_idle"]
        check_freq = data["config"]["check_frequency"]
        remind_time = data["config"]["reminder_time"]
        req_idle_time = data["config"]["required_idle_time"]
        notif_popup = data["config"]["notification_popup"]
        enable_win_notif = True
        enable_audio_notif = True


class Notification(Settings):

    toaster = ToastNotifier()

    def win_notif(self, notif_msg, icon_img, notif_dur=5):
        self.toaster.show_toast(
            title=self.title,
            msg=notif_msg,
            # icon_path=icon_img,
            duration=notif_dur,
            threaded=True,
        )

    def restarting(self):
        if self.enable_win_notif:
            msg = "Restarting timer."
            self.win_notif(msg, "Media/Normal_Icon.png")
        if self.enable_audio_notif:
            path = "Media\Restarting.wav"
            if os.path.exists(path):
                playsound("Media\Restarting.wav")

    def time_to_stand(self):
        if self.enable_win_notif:
            msg = "Restarting timer."
            self.win_notif(msg, "Media/Normal_Icon.png")
        if self.enable_audio_notif:
            path = "Media\Time to stand up.wav"
            if os.path.exists(path):
                playsound("Media/Time to stand up.wav")


class Reminder(Settings):

    # check if new code for this is better
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Notif = Notification()
    # misc
    time_left = 0
    active_time = 0
    early_cancel = 0
    last_run = dt.datetime.now()
    icon = "Media/Normal_Icon.png"
    # logger setup
    log_formatter = lg.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%m-%d-%Y %I:%M:%S %p"
    )
    logger = lg.getLogger(__name__)
    logger.setLevel(lg.DEBUG)  # Log Level
    my_handler = RotatingFileHandler(
        "script.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    my_handler.setFormatter(log_formatter)
    logger.addHandler(my_handler)
    # tray setup
    tray = sg.SystemTray(menu=["menu", ["Exit"]], filename="Media/Normal_Icon.png")
    # debug
    debug = 1

    @staticmethod
    def get_idle_duration():
        """
        Gets the total idle time.
        """

        class LASTINPUTINFO(Structure):
            _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]

        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0

    def idle_check(self):
        """
        ph
        """
        if self.get_idle_duration() > self.wait_idle * 60:
            self.active_time = 0
            self.logger.debug("Computer is Idle")
            self.tray.Update(
                tooltip=f"{self.title}\nComputer is Idle.",
                filename="Media/Idle_ Icon.png",
            )
            while self.get_idle_duration() > self.wait_idle * 60:
                self.last_run = dt.datetime.now()
                time.sleep(self.check_freq * 60)
            self.tray.update(filename="Media/Normal_Icon.png")
            self.logger.debug("Computer is no longer Idle")
        else:
            self.active_time += 1
            if dt.datetime.now() - self.last_run >= dt.timedelta(
                minutes=self.wait_idle
            ):
                self.tray.update(filename="Media/Normal_Icon.png")
                self.active_time = 0
                msg = (
                    f"{self.title}",
                    f"Computer was asleep for more then {self.wait_idle} minutes. Resetting timer.",
                )
                self.tray.ShowMessage(msg, time=10)
                self.logger.debug(
                    f"Computer was asleep for more then {self.wait_idle} minutes. Resetting timer."
                )
            self.time_left = self.remind_time - self.active_time
            self.tray.Update(
                tooltip=f"{self.title}\nNext Reminder: {self.time_left} minutes.",
                filename="Media/Normal_Icon.png",
            )

    def start_tray(self):
        """
        Starts try icon interaction checking loop.
        """
        while True:
            event = self.tray.Read()
            if self.debug:
                print(event)
            if event == "Exit":
                exit()
            elif event == "__ACTIVATED__" or "__MESSAGE_CLICKED__":
                self.early_cancel = 1
                self.Notif.restarting()
                self.tray.Update(
                    tooltip=f"{self.title}\nNext Reminder: {self.remind_time} minutes.",
                    filename=self.icon,
                )

    def check_reminder(self):
        """
        ph
        """
        self.last_run = dt.datetime.now()
        if self.active_time >= self.remind_time:
            self.tray.update(
                tooltip=f"{self.title}\nStand up and stretch",
                filename="Media/Passed_Reminder.png",
            )
            self.Notif.time_to_stand()
            self.logger.debug(
                f"PC has exceeded active time limit of {self.remind_time} minutes."
            )
            while self.get_idle_duration() < self.req_idle_time:
                if self.early_cancel == 1:
                    self.early_cancel = 0
                    # Check on self.tray.update response after manual loop 1.
                    break
                self.tray.ShowMessage(
                    self.title,
                    f"PC has been used for {self.active_time} minute(s)."
                    "\nStop using the computer for {self.req_idle_time} minutes to reset this reminder."
                    "\nTap Icon to Cancel Early.",
                )
                time.sleep(self.check_freq * 60)
                if dt.datetime.now() - self.last_run >= dt.timedelta(
                    minutes=self.wait_idle
                ):
                    self.last_run = dt.datetime.now()
                    break
            self.Notif.restarting()
            self.logger.debug(f"Inactivity Met - Resetting")
            self.tray.Update(
                tooltip=f"{self.title}\nInactivity Met: Resetting within 1 minute.",
                filename="Media/Normal_Icon.png",
            )
            self.active_time = 0

    def run_loop(self):
        """
        Run loops main loop in a thread.
        """

        def callback():
            self.tray.Update(
                tooltip=f"{self.title}\nNext Reminder: {self.remind_time} minutes."
            )
            self.last_run = dt.datetime.now()
            self.logger.debug(
                f"{self.title} set with a {self.check_freq} minute frequency"
                "and a idle detection set to {self.wait_idle} minutes."
            )
            while True:
                time.sleep(self.check_freq * 60)
                self.last_run = dt.datetime.now()
                self.idle_check()
                if self.debug:
                    print(
                        f"PC has been used for {self.active_time} minute(s).       ",
                        end="\r",
                    )
                self.check_reminder()

        threading.Thread(target=callback, daemon=True).start()


if __name__ == "__main__":
    App = Reminder()
    App.run_loop()
    App.start_tray()
