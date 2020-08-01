# Standing Reminder
This app allows you to set a reminder to stop using your computer after a configurable time period.
It is intelligent enough to detect inactivity after the reminder has gone off allowing you to simply walk away for your chosen time.
It will also reset the timer early if it detects inactivity past a configurable threshold.
The timer will also reset upon detecting a time gap in runs due to the computer going to sleep and then waking up a long enough time later.

## Features
* Tray Icon - Hover over the icon to see your next reminder time and a few other statuses.
* Timer Auto-reset on inactivity and wake from sleep.
* Tap Tray Icon to reset timer manually.

## Future Features
* Gamepad Detection

## Config
```ini
[Main]
check_frequency = 1 # Frequency of checks in minutes.
wait_till_idle = 10 # Idle time in minutes that resets timer.
reminder_time = 15 # Minutes of active computer use till Notification or sound goes off.
required_idle_time = 5 # Required minutes of inactivity to reset timer after it has gone off.
past_reminder_frequency = 5 # Frequency of notifications that you have passed your reminder time.
notification_popup = 1 # Determines if you will get a windows notification or just a sound.
```
## Requirements
Check the requirements.txt for modules to install or use the below command.
Run "pip install -r requirements.txt"

### Credits
* Icon: https://icons8.com/icons/set/standing-man--v1
* Notification Sound: https://notificationsounds.com/message-tones/juntos-607
