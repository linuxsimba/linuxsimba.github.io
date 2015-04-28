---
title: Linux Terminal in Chrome Browser - Chromecast
---

At work we have Chromecast setup in all conference rooms. Chromecast for Linux
does not cast the whole screen, just to a Chrome browser tab. How do I show my
terminal during a presentation?


### Solution

Install [butterfly](https://github.com/paradoxxxzero/butterfly), a python based terminal emulation program.

Install it via ``pip install butterfly`` and follow the instructions on the
[website](https://github.com/paradoxxxzero/butterfly)

### Upstart script for Ubuntu 14.04

Butterfly provides a systemd startup script, which will be great for Jessie and
other distros running systemd. Unfortunately 14.04 still uses Upstart. Here is
the ``/etc/init.d/butterfly`` startup script I use

```
# Butterfly - Python Web Terminal Emulator
# https://github.com/paradoxxxzero/butterfly

description     "Web Terminal Emulator"

stop on runlevel [016]

exec  /usr/local/bin/butterfly.server.py

```
I am experimenting with using ``tmux`` in this terminal emulator browser tab and
then only have 1 window open on my laptop to do web searches and write code.
Let us see how that goes.


