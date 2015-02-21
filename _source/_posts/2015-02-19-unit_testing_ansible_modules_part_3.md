---
title: Unit Testing Ansible Modules Part 3
---

In [part 1]({% post_url 2015-02-17-unit_testing_ansible_modules_part_1 %}), 
I discuss the basic Ansible module structure and what I like to unit test in Ansible
modules.


In [part 2]({% post_url 2015-02-18-unit_testing_ansible_modules_part_2 %}),  I
went over the actual test cases in a sample module and discussed some of the
mocking techniques to use with [python-mock](https://pypi.python.org/pypi/mock)

Ansible modules <strike>has a quirk</strike> had a quirk
where modules required to not have a suffix.

Looks like in 1.8.0 and higher, you can name python modules with the `.py` suffix. Makes
testing modules easier now.

This is the tree structure of the module directory
> Do not forget the empty `__init__.py` in the library folder. otherwise the tests will fail.

```
.
├── ansible.cfg
├── library
│   ├── __init__.py
│   └── prefix_check.py
└── tests
    └── test_prefix_check.py

```

In this directory, I run `nosetests` to execute the tests.

```
$ nosetests -v
prefix_check - test module arguments ... ok
prefix_check - test_main_exit_functionality - success ... ok
prefix_check - test_main_exit_functionality - failure ... ok
prefix_check - test action when prefix is found ... ok
prefix_check - test action when prefix not found. timeout occurs ... ok
prefix_check - test ip route show execution ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.021s

OK

```

The code is all available on my [Github blog
site]('https://github.com/skamithi/linuxsimba/asample_configs/ansible_testing')
