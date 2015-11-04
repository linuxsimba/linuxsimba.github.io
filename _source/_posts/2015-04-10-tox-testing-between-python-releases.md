---
title: Testing between Python Releases
---

Recently completed research on how to properly setup a python project
and run continuous integration between multiple python versions.
From the ``#pypa`` IRC channel, I was told
to try out [tox](https://pypi.python.org/pypi/tox)

> **Note**:
  I do have python3.4 installed beforehand on the debian VM that
I use for python development. So I built it manually [from
source](https://www.python.org/downloads/release/python-343/)


Here is my ``tox.ini`` so I can test between python2.7 and python3.4

```

[tox]
envlist = py27,py34
[testenv]
deps=
  mock
  nose      # install pytest in the venvs
commands=nosetests  # or 'nosetests' or ..

```

> **Note**: For ``tox`` to work you need a working ``setup.py``

Here is the output from my python project

```
# tox
GLOB sdist-make: /root/git/linux-netshow-lib/setup.py
py27 inst-nodeps:
/root/git/linux-netshow-lib/.tox/dist/linux-netshow-lib-0.9.zip
py27 runtests: PYTHONHASHSEED='2240461829'
py27 runtests: commands[0] | nosetests
............................................................
----------------------------------------------------------------------
Ran 60 tests in 0.069s

OK
py34 inst-nodeps:
/root/git/linux-netshow-lib/.tox/dist/linux-netshow-lib-0.9.zip
py34 runtests: PYTHONHASHSEED='2240461829'
py34 runtests: commands[0] | nosetests
............................................................
----------------------------------------------------------------------
Ran 60 tests in 0.093s

OK
_____________________________________________________________________________________________________________
summary
_____________________________________________________________________________________________________________
  py27: commands succeeded
  py34: commands succeeded
  congratulations :)
```
