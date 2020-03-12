---
title: Ansible Filter Plugin for network interfaces
tags:
  - ansible
---

Building out a large virtual topology and ran into an interesting problem with Centos. Configuring LLDP in Centos is not straightforward. To configure it correctly I wanted to apply a set of steps on the appropriate interfaces.

The interface names are different depending on whether the virtual  setup uses Virtualbox or Libvirt/KVM. So a filter is needed on the `ansible_interfaces` fact to say if a port begins with either 'em' or 'eth' then apply the LLDP config.

This was achieved using a filter plugin. There may be one already in Ansible, but I could not find it.

### filter\_plugins/filter\_ints.py

```
#!/usr/bin/python

import re
import unittest


def filter_ints(_ifacelist, _regex_str):
    """
    filter list of interfaces based on a regex string
    """
    _regex = re.compile(_regex_str)
    return [iface for iface in _ifacelist
            if _regex.match(iface)]


class FilterModule(object):
    """ Ansible custom filter plugin """

    def filters(self):
        return {
            'filter_ints': filter_ints
        }


class TestFilterInt(unittest.TestCase):
    """
    Test case for this filter plugin. Run python script to run test
    e.g python filter_ints.py
    """
    def test_filter_ints(self):
        self.assertEqual(filter_ints(
            ['eth1', 'lo', 'em0'], 'eth|em'), ['eth1', 'em0'])


if __name__ == '__main__':
    unittest.main()
```

###roles/centos_lldp/tasks/main.yml
<pre><code>
# vim:ft=ansible:
{% raw %}
- name: create new list of intefaces only include physical ports based on the name
  set_fact:
    phy_ints: "{{ ansible_interfaces | <strong>filter_ints('eth|em')</strong> }}"
  tags: config_lldp_centos
{% endraw %}
- name: install lldpad
  yum:  name=lldpad
  tags: install_lldp_centos

- name: enable lldpad service
  service: name=lldpad.service enabled=yes state=started
  register: lldpad_started
  tags: install_lldp_centos

- name: enable lldpad on all interfaces. One time when first configured.
  command: lldptool set-lldp -i {{ item }} adminStatus=rxtx
  with_items: phy_ints
  when: lldpad_started.changed == True
  tags: config_lldp_centos

- name: enable sending system name via lldpad. One time.
  command: lldptool -T -i {{ item }} -V sysName enableTx=yes
  with_items: phy_ints
  when: lldpad_started.changed == True
  tags: config_lldp_centos

- name: enable sending port description via lldpad. One time.
  command: lldptool -T -i {{ item }} -V portDesc enableTx=yes
  with_items: phy_ints
  when: lldpad_started.changed == True
  tags: config_lldp_centos
```
</code></pre>
