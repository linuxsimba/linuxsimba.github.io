---
title: Unit Testing Ansible Modules Part 1
---

I started creating and maintaining [Ansible](http://ansible.com) modules for
[Cumulus
Networks](http://github.com/CumulusNetworks/cumulus-linux-ansible-modules) about
a year ago, and love it.

Unit testing [Ansible](http://ansible.com) modules is important to me. I
realized writing unit tests reduced the time I spent performing integration
tests on real switches.

I will show a simple module and discuss how I configured unit tests for it. 


## Module structure

Ansible modules produce 3 main types of exit signals:

* `AnsibleModule.exit_json(changed=True)`: This means something changed. This activates the notify action, also if available

* `AnsibleModule.exit_json(changed=False)`: Nothing changed

* `AnsibleModule.fail_json(msg="Something bad")`:  This exits the playbook. No
further tasks should be run.

In this example, the module uses the following arguments:

* _prefix_ - can be something like '10.1.1.0/24'

* _timeout_ - how long to run the check before quitting.

### Pseudo code for the module
1. Create Ansible module instance
2. Check if route exists.
 - If route exists, return "no change"
 - If route doesn not exist, "Fail"
 - module does not have a **"changed"** option

> It is common for modules to report a change if something happens. This is
one of those few examples where reporting a change doesn't make sense.

The common use case for this module is when configuring a routing protocol on
the switch or server, you want to confirm that the routes are been exchanged. So
the `prefix_check` module, ensures that routing is working as expected. If the
route is missing, then **Fail**.  

## Time for some code

Below is the `main()` function. Notice that `main()` is split out

{% gist skamithi/a8ee451d6faf0e28ad5c %}

### What to perform unit testing on?
1. **main()**
	- *Check AnsibleModule variable inputs*. In my experience I fat finger stuff in the `main()` function all the time. This adds a basic sanity check to ensure 
I don't make any mistakes with the module arguments. 
This kind of error is easily detected in live system testing. 
I feel it saves me time during live testing to have this unit test in place.
	- *Module exits correctly under different conditions*. That is, if route check fails, run the `exit_json()` function. 
If it passes run the `fail_json` function. When making changes in the `main()`, 
I sometimes mess up the exit logic. This makes sure to catch any errors in the basic outcome logic of the module

2. **check\_if\_route_exists()**
  - *Mock ip route calls* and if the route exists, return true
  - *Mock the timeout*, and ensure it returns false if the timeout is reached  
  
3. **Test that the ip route call is correct** 
  - This ensures that future modifications of the module 
don't accidentally change the important system calls of
this module.

The [next blog post]({% post_url 2015-02-18-unit_testing_ansible_modules_part_2 %}) goes into test details and how I performed mocking.

Unit tests eliminate a lot of the common coding errors, I would otherwise
encounter during integration testing on real switches. It  has saved me a
lot of time, and adds some dependability to modules I work on.
