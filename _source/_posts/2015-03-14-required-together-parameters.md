---
title: Required Together Parameters in Ansible and Puppet
tags: ['ansible', 'puppet']
---

I could not figure out what the _correct_ term for these types of parameters
are. These are parameters or attributes that must be defined together.
For example, defining an IP address on a router. If you specify an IP one
must also include the subnet mask.

> *Today's Fun Fact*: <br/>
In Linux, specifying the IP address **only** sets the subnet mask to all Fs(/32)

In a puppet custom type,  how you say, these 2 parameters are _"required together"_ ?
I will use the IP address and subnet mask example

```ruby

Puppet::Type.newtype(:ip_host_info) do
  desc 'describe basic ip host info'
  newparam(:ip) do
    desc 'ip address'
    isnamevar
  end

  newparam(:mask) do
    desc 'subnet mask'
  end

  validate do

    if self[:ip].nil?
      fail Puppet::Error, 'ip address must be configured'
    end

    # found an actual use case of XOR. Always wondered in college
    # what you use XOR for :)
    if self[:ip].nil? ^ self[:mask].nil?
      fail Puppet::Error, 'subnet mask and ip are required together'
    end
```

In an Ansible module it would look like this

```python

def main():
  module = AnsibleModule(
    argument_spec=dict(
      ip=dict(required=True, type='str'),
      mask=dict(type='str')
    ),
    required_together=[['ip', 'mask']]
  )

```

