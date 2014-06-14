Terminal Notification
=====================

[**Project home**] [1]

**This is the Linux Only Guide - for other platforms, see: [README] (README.md)**

*Currently supporting most Linux variants with more or less native notifications*

*There is also support for additional systems by using Growl (but this normally requires a bit more manual install)*

---

When used, notifications will be displayed like this:

Ubuntu 14.04 - notify-send:

![Ubuntu notify-send] (resources/screenshots/UbuntuNotifySend.png)


Ubuntu 14.04 - Growl:

![Ubuntu Growl] (resources/screenshots/UbuntuGrowl.png)

notify-send
-----------

This project supports most Linux flavours, where notify-send and the ALSA drivers are installed (bundled with many distributions).

All notifications will be sent out using notify-send, and you can specify the following:

- What pattern to listen for in the output
- Configure title and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination

Project requirements:

- Linux system with notify-send installed
- Python 2.7 or 3.4
- aplay (for sounds)

Growl
-----

With Growl, you get the benefit of being able to see the notifications on all systems that have support for Growl. However there are a few requirements, which may be a bit complex to setup, and it will not end up in as tight integration as the system default implementations.

All notifications will be sent out over the gntp protocol, and you can specify the following:

- What pattern to listen for in the output
- Configure title and message (including using above mentioned regexp variables)
- Choose what sound to play with the message
- Set a max frequency for messages of each type
- Send notifications on startup and termination

Project requirements:

- Growl installed
- pip (python package manager, used for installing GNTP)
- GNTP installed (python layer for Growl Network Transfer Protocol)

Version
-------

2.0

Installation
------------

**Clone**

First you need to clone this project. If you haven't already, visit [Project home] [1] and follow instructions for how to clone the project.

**Install notify-send**

If notify-send isn't installed, install it with your favourite package manager, eg:

```
sudo apt-get install notify-osd
```

If you are lacking aplay in your system, I can't really help you. What I know is that it's bundled with ALSA sound card drivers. So google it, and if you figure it out, send instructions to me and I will add them. I haven't used a flavour of Linux that don't bundle it yet.

*For Growl implementation*

Download and install Growl for [Linux] [5]

Download and install GNTP for your system, by using your package manager to install python-pip:

```
sudo apt-get install python-pip
```

Now we just need to install gntp through pip:

```
sudo pip install gntp
```

---

Usage
-----

**Run Custom Terminal Notification**

Enter the folder of the project in a terminal, then the shortest way to start the application is as such:

```
python notifier.py --config resources/example.txt
```

The config file may be either a local configuration file with the file suffix .txt or a zip-package. The zip-package may be either a local file on your hard-drive or one distributed on the Internet. There are some specific rules to follow if you use the zip-packages, which is explained in a section below.

The rest of the parameters to the application can be defined in two ways. The first way is to put them inside of the configuration file itself, which will be described later in this file. The other way is to add them as arguments when starting the application. The following parameters are available:

--debug

Will output a lot of debug text, which may help eg. when trying to setup configurations on your own

--mute

This option will make sure to not output the standard console output

--no-sound

Use this one to not play any sounds for the notifications (some systems may still play a system default sound instead)

--only-sound

This one will only play the sound, and make sure to not display any notifications

--growl

Will use Growl to display notifications 

--color COLOR

Here you may specify a color to use for all the console output. Replace COLOR with one of the following values: **black**, **gray**, **white**, **red**, **green**, **yellow**, **blue**, **magenta**, **cyan** and last but not least **rainbow**

--no-override-settings

Normally, settings written inside of a configuration takes priority over ones entered manually, use this option to not accept any of the settings in the configuration file


Configuration
-------------

There are three major types of blocks that can be configured:

- SETTINGS
- COMMANDS
- CONFIGURATION:

---

SETTINGS is a list of settings that will apply during runtime, unless the *--no-override-settings* was entered manually when starting the application, other than that, these are the same parameters. Each setting should be on it's own line, and to negate the value of it, simply prefix it with an exclamation mark (!).

```
[SETTINGS]
    !--growl
    --color green
    --debug
    !--mute
[/SETTINGS]
```

The above list of settings means roughly: *Do not use Growl for notifications. Color all output in green text, use debug mode and also make sure to not mute the script output*

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

CONFIGURATION: takes a name directly after the colon (three names are reserved, the others are still unused, but is planned for the future). This one have a bit more complex setup, so let's start by looking at an example:

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

- **SUBTITLE** - The subtitle to display in the notification - This is intended for Mac OS Native Notifications. If entered in a Linux system, it will be appended to the title

- **MESSAGE** - The text to display in the notification

- **TIME** - If entered, the notification will be requested to be removed after this amount of milliseconds

- **SOUND** - The sound to play when the notification is shown. All sounds that can be played with aplay is supported, and have to be written with the full path

If you want to have a range of sounds to either play in order of appearance or randomly, these can be specified as such:

```
[SOUND]{cycle}resources/sounds/alien.wav,resources/sounds/beep.wav
[SOUND]{random}resources/sounds/click.wav,resources/sounds/flute.wav
```

All of the NOTIFICATION fields can use values from the capturing groups in both PATTERN and HISTORYPATTERN. First group from PATTERN is written as **$1** and the first group from HISTORYPATTERN is written as **$H1**. 

---

There is also three additional, special CONFIGURATIONs:

```
[CONFIGURATION:{STARTUP}]
    [NOTIFICATION][TITLE]START[MESSAGE]Application has started[SOUND]resources/sounds/shutter.wav
[/CONFIGURATION:{STARTUP}]
```

This is simply put a special configurations which only triggers before the commands are started. There are no patterns, historyPatterns or graceTime settings for this one.

```
[CONFIGURATION:{QUIT}]
    [EXITCODE]{not}0
    [RESTART]True
    [NOTIFICATION][TITLE]QUIT[MESSAGE]All commands have terminated[SOUND]resources/sounds/swirl.wav
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

For the NOTIFICATION > SOUND, these sounds should be sounds that can play with aplay (all sounds bundled with this project should work). They are entered with the relative or full path to the file.

Zip Packages
------------

Zip Packages was implemented for one reason; to be able to share configurations without needing to manually keep a configuration up to date. A Zip Package also have the benefit that you may bundle sounds and multiple configurations (one for each of the three supported Operating Systems). If you only need one configuration, the simplest file structure in the ZIP-file is as follows:

```
example.zip
-example.txt 
```

In this case the application will automatically load the .txt-file with the same name as the .zip-package, as the configuration.

If you would like to have different configurations depending on platform, do like this:
 
```
example.zip
-platform-route.txt
-configuration-macosx.txt
-configuration-linux.txt
-configuration-windows.txt
```

The file *platform-route.txt* will be used to decide the configuration file to use for the current Operating System, and the contents of the file in this case would be:

```
mac:zip:configuration-macosx.txt
lin:zip:configuration-linux.txt
win:zip:configuration-windows.txt
```

The first part is the short name of the Operating System; **mac**, **lin** or **win**, followed by a colon. The second part, **zip:** just tells the application that the file is embedded within the Zip Package, and what the filename it has inside it.

Let's say you want to bundle a wave-file within the package, looking like this:

```
example.zip
-example.txt
-mySound.wav
```

In order to define this sound in the configuration, simply put **zip:** before the definition of the sound file for the NOTIFICATION, as such:

```
[NOTIFICATION][TITLE]Title[MESSAGE]Message[SOUND]zip:mySound.wav
```

Future plans
------------

**General**

- Create an interactive guide
- Fix so that groups isn't needed in patterns
- More configuration options, eg. choose which configuration should apply to what command

**Linux**

- Try to see if queueing issues for notifications can be fixed
- Try to see if time of showing notifications can be fixed

Reservations
------------

Please note that I've only tested this on a limited set of systems and combinations. If you want support for more systems or features, please ask and I might be able to help out. Known working combinations for Linux variants are:

- Ubuntu 14.04 with notify-send and aplay
- Ubuntu 14.04 with Growl and aplay
- Fedora 20 with notify-send and aplay
- Linux Mint 17 "Qiana" with notify-send and aplay
- Linux Mint 17 "Qiana" with Growl and aplay

License
-------

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

For full license see [LICENSE.txt] (LICENSE.txt)

[1]:https://bitbucket.org/rtapper/terminal-notification
[5]:http://mattn.github.io/growl-for-linux/