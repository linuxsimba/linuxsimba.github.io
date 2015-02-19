---
title: Unit Testing Ansible Modules Part 2
---

In [part 1]({% post_url 2015-02-17-unit_testing_ansible_modules_part_1 %}), 
I went over the basic module structure of a simple module, and a summary of the unit tests I would execute. 
In this post, I cover the actual [nose](https://nose.readthedocs.org/en/latest/) tests.

## Test module arguments

{% gist skamithi/68907267a14e45015daa %}


Mocking is important to unit testing 
Ansible modules. It took me a while and several videos to understand how 
[Python Mock](http://mock.readthedocs.org/en/latest/patch.html) works.

`mock.patch` has a quirk that took a while to get used to. Notice that `check_if_route_exists` and `AnsibleModule` is mocked in that order. But in the `test_module_args` call, variables holding those mocks are in reverse order. the order is reversed, that is `mock_modules` first, followed by `mock_route_check`..Weird!

## Test Exit functionality

{% gist skamithi/aa57667544c305e8044d %}

In these tests, the "check route found" mocked function has a `return value`.
This needs to be set before the `prefix_check.main()` function is called.

I broke out the success and failure test case into 2 separate functions, just
to make it clear what I'm doing. Normally, I'm lazy and just keep my test cases
in the same function and use `reset_mock()` to reinitialize the mocks before each use case. Probably bad practise though :)

## Test route check function

{% gist skamithi/afc31a5286f5e1a30f17 %}

The hardest trick in these tests was mocking the `time.sleep` function. Wanted to be
sure that it polls `ip route show` correctly.

The final test, ensures that future modifications don't mess up the `ip route show` call.

In [part 3]({% post_url 2015-02-19-unit_testing_ansible_modules_part_3 %}), I show how I run the tests.
