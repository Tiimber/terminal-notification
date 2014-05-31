Terminal Notification
=====================

[**Project home**] [1]

This project aims to be a highly configurable notification handler for any terminal commands in Mac OS X (10.8+).

All notifications are sent out using Mac OS Notification Center, and you can specify quite a few things:

- What pattern to listen for in the output
- Configure title, subtitle and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on termination

Project requirements:

- Mac OS X (10.8 or later)
- Python 2.7
- [terminal-notifier] [2] (Installation instructions are included in this file)

Version
-------

1.0

Installation
------------

**Clone**

First you need to clone this project. If you haven't already, visit [Project home] [1] and follow instructions for how to clone the project.

**Install terminal-notifier**

```
[sudo] gem install terminal-notifier
```

or if you prefer to install using brew

```
brew install terminal-notifier
```


Usage
-----

**Run Custom Terminal Notification**

Enter the folder of the project in a terminal, then run

```
python Notifier.py --config resources/example_setup.txt
```

This will run with the included example, which is just as stated, an example configuration.

To run with a lot of debug outputting:

```
python Notifier.py --config resources/example_setup.txt --debug True
```

If you desire to not mirror the standard console output, run with the mute option:

```
python Notifier.py --config resources/example_setup.txt --mute True
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

- **SUBTITLE** - The subtitle to display in the notification

- **MESSAGE** - The text to display in the notification

- **GROUP** - A group ID for the notification. Is supposed to be limited to one per ID, but seems to have no effect (known bug).

- **SOUND** - The sound to play when the notification is shown (available sounds listed below) 

If you want to have a range of sounds to either play in order of appearance or randomly, these can be specified as such:

```
[SOUND]{cycle}Basso,Blow
[SOUND]{random}Frog,Sosumi
```

All of the NOTIFICATION fields can use values from the capturing groups in both PATTERN and HISTORYPATTERN. First group from PATTERN is written as **$1** and the first group from HISTORYPATTERN is written as **$H1**. 

---

There is also one other special CONFIGURATION:

```
[CONFIGURATION:{QUIT}]
    [NOTIFICATION][TITLE]QUIT[MESSAGE]All commands have terminated[SOUND]Basso[GROUP]group1
[/CONFIGURATION:{QUIT}]
```

This is simply put a special configuration which only triggers when all commands have finished running, no matter if successful or interrupted. There are no patterns, historyPatterns or graceTime settings for this one.

Sounds
------

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

It's possible to add your own sounds to this setup, follow [this guide] [3] to add your own.


Future plans
------------

- Fix so that groups isn't needed in patterns
- Figure out why group ID isn't working for the notifications
- Figure out if it's possible to configure how long time to show notifications
- More configuration options, eg. choose which configuration should apply to what command
- Windows notifications
- Linux notifications(?)

License
-------

Do whatever you want with the sources, fork it out, put it on a golden chip, totally break it... or develop cool features and give them to me.


[1]:https://bitbucket.org/rtapper/terminalnotifier
[2]:https://github.com/alloy/terminal-notifier
[3]:https://bitbucket.org/rtapper/terminalnotifier/src/c02e5a25960fdbc873370511c8b7d136e00f5c89/resources/sounds/README.md?at=master

---

# Differences with notify-send
time-parameter only for Linux
sound, group, not for Linux
subtitle and title merged as title for Linux
Linux issues with queueing notifications