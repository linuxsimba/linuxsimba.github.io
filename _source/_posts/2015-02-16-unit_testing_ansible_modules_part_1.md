---
title: Unit Testing Ansible Modules Part 1
---

I love [Ansible](http://ansible.com). I started creating Ansible modules for [Cumulus Networks](http://cumulusnetworks.com) about a year ago.

Unit testing [Ansible](http://ansible.com) modules is important to me. I
realized writing unit tests reduced the time I spent performing integration
tests.

I will show a simple module and discuss how I configured unit tests for it. 


## Module structure

Ansible modules produce 3 main types of exit signals:

* `AnsibleModule.exit_json(changed=True)`:  This activates the notify action,
also if available

* `AnsibleModule.exit_json(changed=False)`: Nothing changed

* `AnsibleModule.fail_json(msg="Something bad")`:  This exits the playbook. No
further tasks should be run.

In this example, the module uses the following arguments:

* _prefix_ - can be something like '10.1.1.0/24'

* _timeout_ - how long to run the check before quitting.

### Pseudo code for the module
1. Create Ansible module instance
2. Check if route exists.
 - If route exists, return "report no change"
 - If route doesn't exist, "Fail"
 - module does not have a "changed" option

> It is common for modules to report a change if something happens. This is
one of those few examples where reporting a change doesn't make sense.

The common use case for this module is when configuring a routing protocol on
the switch or server, you want to confirm that the routes are been exchanged. So
the prefix_check module, ensures that routing is working as expected. If the
route is missing, then **Fail**.  

Having wrongly configured routing is a bad thing for any network.

## Time for some code

Below is the `main()` function. Notice that `main()` is split out

<script src="https://gist.github.com/skamithi/a8ee451d6faf0e28ad5c.js"></script>

### What to perform unit testing on?
1. main()
	- Check AnsibleModule variable inputs. In case someone fat fingered something. 
	- Perform basic integration test. That is, if route check fails, run the `exit_json()` function. If it passes run the `fail_json` function.

2. check\_if\_route_exists()
	- Mock ip route calls and if the route exists, return true
	- Mock ip route calls and if the route doesn't exist, function should return false
	- Mock the timeout, and ensure it returns false if the timeout is reached

The next blog post goes into test details and how I performed mocking.

Unit tests eliminated a lot of the common coding errors I would otherwise
encounter during integration testing on real switches. It truly has saved me a
lot of time, and adds some dependability to the module.
