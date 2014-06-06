Terminal Notification
=====================

[**Project home**] [1]

*Currently supporting Mac OS X 10.8+, Windows and most Linux variants with more or less native notifications*

*There is also support for older systems or additional ones by using Growl (but this normally requires a bit more manual install)*

---

When used, notifications will be displayed like this:

Mac OS X - Notification Center:

![Mac OS X Notification Center] (resources/screenshots/MacOSXNotificationCenter.png)

Mac OS X - Growl:

![Mac OS X Growl] (resources/screenshots/MacOSXGrowl.png)

Ubuntu 14.04 - notify-send:

![Ubuntu notify-send] (resources/screenshots/UbuntuNotifySend.png)


Ubuntu 14.04 - Growl:

![Ubuntu Growl] (resources/screenshots/UbuntuGrowl.png)


Windows 7 - notifu:

![Windows notifu] (resources/screenshots/WindowsNotifu.png)


Windows 7 - Growl:

![Windows Growl] (resources/screenshots/WindowsGrowl.png)


Mac OS X
--------

This project aims to be a highly configurable notification handler for any terminal commands in Mac OS X (10.8+).

All notifications are sent out using Mac OS Notification Center, and you can specify quite a few things:

- What pattern to listen for in the output
- Configure title, subtitle and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination

Project requirements:

- Mac OS X (10.8 or later)
- Python 2.7
- [terminal-notifier] [2] (Installation instructions are included below)

Linux
-----

This project also supports most Linux flavours, where notify-send and the ALSA drivers are installed (bundled with many distributions).

All notifications will be sent out using notify-send, and you can specify the following:

- What pattern to listen for in the output
- Configure title and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination

Project requirements:

- Linux system with notify-send installed
- Python 2.7
- aplay (for sounds)

Windows
-------

This project also supports Windows, if you have installed notifu on it. For playing sounds, supported application is sounder.exe.

All notifications will be sent out using notifu, and you can specify the following:

- What pattern to listen for in the output
- Configure title and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination
- Choose how long the notification can be visible

Project requirements:

- Windows system with [notifu] [7] installed
- Python 2.7
- [sounder.exe] [6] (for sounds)

Growl
-----

With Growl, you get the benefit of being able to see the notifications on all systems that have support for Growl. However there are a few requirements, which may be a bit complex to setup, and it will not end up in as tight integration as the system default implementations. For playing sounds, there is a requirement of an additional external sound player.

All notifications will be sent out over the gntp protocol, and you can specify the following:

- What pattern to listen for in the output
- Configure title and message (including using above mentioned regexp variables)
- *Linux and Windows* - Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination

Project requirements:

- System with growl installed
- pip (python package manager, used for installing GNTP)
- GNTP installed (python layer for Growl Network Transfer Protocol)

Version
-------

1.6

Installation
------------

**Clone**

First you need to clone this project. If you haven't already, visit [Project home] [1] and follow instructions for how to clone the project.

---

*For Mac OS X*

**Install terminal-notifier**

```
[sudo] gem install terminal-notifier
```

or if you prefer to install using brew

```
brew install terminal-notifier
```

---

*For Linux*

If notify-send isn't installed, install it with your favourite package manager, eg:

```
sudo apt-get install notify-osd
```

If you are lacking aplay in your system, I can't really help you. What I know is that it's bundled with ALSA sound card drivers. So google it, and if you figure it out, send instructions to me and I will add them. I haven't used a flavour of Linux that don't bundle it yet.

---

*For Windows*

If notifu isn't installed, download it [here] [7]. You will also need to add the path of it to your path environment variable.

If sounder.exe isn't installed, download it [here] [6]. You will also need to add the path of it to your path environment variable.

In order for color output to work for Windows, a handy python-tool is required, called colorama. To install it on your system, follow the instructions to install pip just below, then run the following command as Administrator in a command prompt:

```
pip install colorama
```

---

*For Growl implementation*

Download and install Growl for [Windows] [3], [Mac] [4] or [Linux] [5]

Download and install GNTP for your system, instructions based on system.

---

*For Windows*

If you are having troubles doing this, for Windows the suggested solution is to do the following:

- Run this in a terminal (it will install pip):

```
python -c "exec('try: from urllib2 import urlopen \nexcept: from urllib.request import urlopen');f=urlopen('https://raw.github.com/pypa/pip/master/contrib/get-pip.py').read();exec(f)"
```

- Add pip to your path (environment variable). It will be put in a subfolder to Python itself. Search for pip.exe among your files to find it.

---

*For Linux*

Use your package manager to install pip, eg:

```
sudo apt-get install python-pip
```

--- 

*For Mac OS X*

Use easy_install to install pip, it should be bundled with Python:

```
sudo easy_install pip
```

---

*For all systems*

Now we just need to install gntp through pip:

```
pip install gntp
```

You will need to run this command as administrator, for Mac OS X and Linux it means prefixing the command with sudo and for Windows by opening the command prompt as Administrator.

---

Usage
-----

**Run Custom Terminal Notification**

Enter the folder of the project in a terminal, then run

```
python notifier.py --config resources/example_setup.txt
```

This will run with the included example, which is just as stated, an example configuration.

To run with a lot of debug outputting:

```
python notifier.py --config resources/example_setup.txt --debug
```

If you desire to not mirror the standard console output, run with the mute option:

```
python notifier.py --config resources/example_setup.txt --mute
```

If you don't want sounds to play (Mac OS X will eg. play a default sound if none is entered in configuration):

```
python notifier.py --config resources/example_setup.txt --no-sound
```

If you are of the opposite kind you might only want the sounds to play, no notifications *Not in Mac OS X*:

```
python notifier.py --config resources/example_setup.txt --only-sound
```

If you would like to force the notifications to use growl, run with this option:

```
python notifier.py --config resources/example_setup.txt --growl
```

*Mac Only*

Even if you're using Notification Center for displaying notifications, you might want to use the external sound player (afplay). Do this by running with this option:

```
python notifier.py --config resources/example.txt --mac-afplay
```

Of course, this will mean that you will have to enter the relative or full path to the sound instead of using the shorthands available in the system.

*Windows Only*

For Windows, there seem to be some issues with sounder.exe not being recognized automatically, even if put on the environment path. To solve this issue, you may enter the full search path to this executable:

```
python notifier.py --config resources/example_setup.txt --growl --win-sounder C:\\sounder.exe
```

*BONUS (Windows need additional installation for this to work)*

If you feel like controlling the color of the output during runtime of this application, you can specify color as such:

```
python notifier.py --config resources/example_setup.txt --color green
```

Accepted values for color is **black**, **gray**, **white**, **red**, **green**, **yellow**, **blue**, **magenta** and **cyan**.


Configuration
-------------

There are two major types of blocks that can be configured:

- COMMANDS
- CONFIGURATION:

---

COMMANDS is simply a list of terminal commands to trigger in sequence in the Terminal. Inside of this block, simply write a list of commands, one command per line, eg:

```
[COMMANDS]
    pwd
    cd
    echo "Name:`whoami`:"
    echo "Hello world"
    date
    sleep 5
[/COMMANDS]
```

if many COMMANDS-blocks are entered, the last one will be used.

---

CONFIGURATION: takes a name directly after the colon (still unused, but is planned for). This one have a bit more complex setup, so let's start by looking at an example:

```
[CONFIGURATION:HELLOWORLD]
    [PATTERN](Hello world)
    [HISTORYPATTERN]Name:(.*?):
    [GRACETIME]1000
    [NOTIFICATION][TITLE]$H1[SUBTITLE]$1[MESSAGE]This triggers when Hello world is outputted[SOUND]Glass[GROUP]group1
[/CONFIGURATION:HELLOWORLD]
```

Some explanations for each part:

**PATTERN** - *REQUIRED* - is followed by a regexp pattern. It **MUST** contain at least one capturing group (known bug). This pattern will match only on a line by line basis.

**HISTORYPATTERN** - *OPTIONAL* - just as above a regexp pattern. However this is only used towards the history output (since last match), and is only used for adding additional capturing groups for the notification.

**GRACETIME** - *OPTIONAL* - will only allow this notification to be triggered once during this period of time. Time is written in milliseconds. Default value is 500.

**NOTIFICATION** - *REQUIRED* - This is the actual contents of the Notification. What follows on this line is the different fields for the notification:

- **TITLE** - The title to display in the notification

- **SUBTITLE** - The subtitle to display in the notification - *MAC ONLY* - If entered in a Linux system or when using Growl, it will be appended to the title

- **MESSAGE** - The text to display in the notification

- **GROUP** - A group ID for the notification. Is supposed to be limited to one per ID, but seems to have no effect (known bug) - *MAC ONLY* - Will not work at all for Linux or Growl

- **TIME** - If entered, the notification will be requested to be removed after this amount of milliseconds - *LINUX ONLY* - Will be ignored for Mac OS X and Growl

- **SOUND** - The sound to play when the notification is shown. A list of default available sounds for Mac OS X is listed below. More sounds may be added to this list. For Linux systems, all sounds that can be played with aplay is supported, and have to be written with the full path. If you're using windows, this application have integrated support with [sounder.exe] [6], and the sounds have to be written with the full path.

If you want to have a range of sounds to either play in order of appearance or randomly, these can be specified as such:

```
[SOUND]{cycle}Basso,Blow
[SOUND]{random}Frog,Sosumi
```

All of the NOTIFICATION fields can use values from the capturing groups in both PATTERN and HISTORYPATTERN. First group from PATTERN is written as **$1** and the first group from HISTORYPATTERN is written as **$H1**. 

---

There is also three additional, special CONFIGURATIONs:

```
[CONFIGURATION:{STARTUP}]
    [NOTIFICATION][TITLE]START[MESSAGE]Application has started[SOUND]Pop
[/CONFIGURATION:{STARTUP}]
```

This is simply put a special configurations which only triggers before the commands are started. There are no patterns, historyPatterns or graceTime settings for this one.

```
[CONFIGURATION:{QUIT}]
    [EXITCODE]{not}0
    [RESTART]True
    [NOTIFICATION][TITLE]QUIT[MESSAGE]All commands have terminated[SOUND]Basso
[/CONFIGURATION:{QUIT}]
```

Just like the above one, this is configurations which only triggers when the commands execution have been finished. The big difference towards the startup configuration is these two available fields:

- **EXITCODE** - *OPTIONAL* - Will only trigger if the exitcode is or is not equal to the specified exit code. If {not} is put at the beginning, it will negate the error code check, otherwise it will only check for equality - If not entered, default behaviour is to always trigger this notification
- **RESTART** - *OPTIONAL* - Set this to True in order to restart the chain of the commands all over (eg. upon detecting a crash) - If not given, no restart will be made

```
[CONFIGURATION:{HANGING}]
    [PATTERN]{ifnot:1}(Start)
    [TIMEOUT]8000
    [RESTART]True
    [NOTIFICATION][TITLE]Hanging app?[MESSAGE]The application haven't responded in 8 seconds[SOUND]Sosumi
[/CONFIGURATION:{HANGING}]
```

These kind of configurations may be used to give a message when nothing have outputted for a certain time. The setup on this one is a bit complex, so bare with me here. First of all, you may have as many of this configuration as you like.

The parts you can have inside of this one is:

- **NOTIFICATION** - Exactly same syntax as the above mentioned configurations
- **TIMEOUT** - If nothing have outputted after this amount of milliseconds, 1/1000 of a second (8000 = 8s), this configuration will be triggered.
- **RESTART** - *OPTIONAL* - Same as description for {QUIT}
- **PATTERN** - *OPTIONAL* - If no pattern are given, the only criteria will be the timeout for this notification to trigger. If entered, the following is the format:

```
[ {[ [ IF / IF NOT ]: ][ NUMBER OF LINES BACK IN THE OUTPUT ]} ]PATTERN
```

Some examples:

```
1. (Hello)
2. {if}(Hello)
3. {if:0}(Hello)
4. {0}(Hello)

5. {ifnot}(Hello)
6. {ifnot:0}(Hello)

7. {if:3}(Old line)
8. {3}(Old line)

9. {ifnot:3)(New line)
```

All of lines 1-4 means the exact same thing: **If** the **latest** outputted line matches the regex pattern **(Hello)**, then trigger this notification.

That is due to 'if' and '0' being the default values for *condition* and *lines back in history*.

Lines 5 and 6 also mean the same thing: **If** the **latest** outputted value does **not** match the regex pattern **(Hello)**, then trigger this notification.

In this case, only *lines back in history* can be ommited, since the last one will be checked.

Just like below, lines 7 and 8 have the same meaning as each other: **If** the **third last** outputted line match the regex pattern **(Old line)**, then trigger this notification.

Line 9 have the meaning: **If** the **third last** outputted line does **not** match the regex pattern **(New line)**, then trigger this notification.



Sounds
------

**Mac OS X**

*Note!* - These sounds described here are only for Notification Center and if you haven't set the override flag for --mac-afplay. See below for this override flag and Growl variant of sound play.

For the NOTIFICATION > SOUND, these should be the names on the sounds bundled with Mac OS X. Too see the names available for your computer, open System Preferences > Sound > Sound Effects. The names of the sounds there are also available for this application. The list of my computer is as follows:

- Basso
- Blow
- Bottle
- Frog
- Funk
- Glass
- Hero
- Morse
- Ping
- Pop
- Purr
- Sosumi
- Submarine
- Tink

It's possible to add your own sounds to this setup, follow [this guide] (resources/sounds/mac/README.md) to add your own.

**Note!** - If you are using Growl for Mac or have set the override flag --mac-afplay, the sounds will be played with afplay, which is bundled with Mac OS X 10.5+. The sounds bundled with this project should work. They are not entered with the short names mentioned above, but with the relative or full path to the file.

**Linux**

For the NOTIFICATION > SOUND, these sounds should be sounds that can play with aplay (all sounds bundled with this project should work). They are entered with the relative or full path to the file.

**Windows**

For the NOTIFICATION > SOUND, these sounds should be sounds that can play with sounder.exe (all sounds bundled with this project should work). They are entered with the relative or full path to the file.

Future plans
------------

**General**

- Fix so that groups isn't needed in patterns
- More configuration options, eg. choose which configuration should apply to what command

**Mac OS X**

- Figure out why group ID isn't working for the notifications
- Figure out if it's possible to configure how long time to show notifications

**Linux**

- Try to see if queueing issues for notifications can be fixed
- Try to see if time of showing notifications can be fixed

Reservations
------------

Please note that I've only tested this on a limited set of systems and combinations. If you want support for more systems or features, please ask and I might be able to help out. Known working combinations is:

- Mac OS X 10.9.3 with Notification Center
- Mac OS X 10.9.3 with Growl and afplay
- Mac OS X 10.8.5 with Notification Center
- Ubuntu 14.04 with notify-send and aplay
- Ubuntu 14.04 with Growl and aplay
- Fedora 20 with notify-send and aplay
- Linux Mint 17 "Qiana" with notify-send and aplay
- Linux Mint 17 "Qiana" with Growl and aplay
- Windows 7 with notifu and sounder.exe
- Windows 7 with Growl, GNTP and sounder.exe

License
-------

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

For full license see [LICENSE.txt] (LICENSE.txt)

[1]:https://bitbucket.org/rtapper/terminal-notification
[2]:https://github.com/alloy/terminal-notifier
[3]:http://www.growlforwindows.com/gfw/default.aspx
[4]:http://growl.info/downloads
[5]:http://mattn.github.io/growl-for-linux/
[6]:http://www.elifulkerson.com/projects/commandline-wav-player.php
[7]:http://www.paralint.com/projects/notifu/download.html