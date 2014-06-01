Terminal Notification
=====================

[**Project home**] [1]

*Currently supporting Mac OS X 10.8+, Windows and most Linux variants, or by using Growl on most systems (but requires a bit more manual install)*

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

1.2

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

If you don't want sounds to play (Mac OS X will eg. play a default sound if none is entered):

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

*Windows Only*

For Windows, there seem to be some issues with sounder.exe not being recognized automatically, even if put on the environment path. To solve this issue, you may enter the full search path to this executable:

```
python notifier.py --config resources/example_setup.txt --growl --win-sounder C:\\sounder.exe
```


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

There is also two more special CONFIGURATIONs:

```
[CONFIGURATION:{STARTUP}]
    [NOTIFICATION][TITLE]START[MESSAGE]Application has started[SOUND]Pop
[/CONFIGURATION:{STARTUP}]

[CONFIGURATION:{QUIT}]
    [NOTIFICATION][TITLE]QUIT[MESSAGE]All commands have terminated[SOUND]Basso
[/CONFIGURATION:{QUIT}]
```

These are simply put special configurations which only triggers before the commands are started and after commands have finished running, no matter if successful or interrupted. There are no patterns, historyPatterns or graceTime settings for this one.

Sounds
------

**Mac OS X**

*Note!* - These sounds described here are only for Notification Center. See below for Growl variant.

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

**Note!** - If you are using Growl for Mac, the sounds will be played with afplay, which is bundled with Mac OS X 10.5+. The sounds bundled with this project should work. They are not entered with the short names mentioned above, but with the relative or full path to the file.

**Linux**

For the NOTIFICATION > SOUND, these sounds should be sounds that can play with aplay (all sounds bundled with this project should work). They are entered with the relative or full path to the file.

**Windows**

For the NOTIFICATION > SOUND, these sounds should be sounds that can play with sounder.exe (all sounds bundled with this project should work). They are entered with the relative or full path to the file.

Future plans
------------

**General**

- Fix so that groups isn't needed in patterns
- More configuration options, eg. choose which configuration should apply to what command
- Try and mute much more output (sound playing in external players should be ignored from an terminal output point of view)

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
- Ubuntu 14.04 with notify-send and aplay
- Ubuntu 14.04 with Growl and aplay
- Windows 7 with notifu and sounder.exe
- Windows 7 with Growl, GNTP and sounder.exe

License
-------

Do whatever you want with the sources, fork it out, put it on a golden chip, totally break it... or develop cool features and give them to me.


[1]:https://bitbucket.org/rtapper/terminalnotifier
[2]:https://github.com/alloy/terminal-notifier
[3]:http://www.growlforwindows.com/gfw/default.aspx
[4]:http://growl.info/downloads
[5]:http://mattn.github.io/growl-for-linux/
[6]:http://www.elifulkerson.com/projects/commandline-wav-player.php
[7]:http://www.paralint.com/projects/notifu/download.html
