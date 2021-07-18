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

* Game pad Detection
* Tray right click reset

## Config

```json
{
    "config":
    {
        "check_frequency": 1,
        "wait_till_idle": 10,
        "reminder_time": 50,
        "required_idle_time": 5,
        "notification_popup": 1
    }
}
```

## Requirements

Check the requirements.txt for modules to install or use the below command.
Run "pip install -r requirements.txt"

### Credits

* [Tray Icon](https://icons8.com/icons/set/standing-man--v1)
* [Notification Sound](https://notificationsounds.com/message-tones/juntos-607)
