---
title: "Handling Unreachable Ansible Hosts"
tags: ["ansible"]
---

Got two use cases for handling Ansible unreachable hosts.  Ansible devs [have made it clear](https://github.com/ansible/ansible/issues/18075) that
``ignore_erros`` and ``any_errors_fatal`` does not handle the unreachable host condition.

So what to do if you want to perform some action when a host is unreachable?

## Case 1: Disabling Insecure WinRM on Windows , then proceeding with the playbook.

When you try to disable the insecure WinRM(port 5985) using a modified Ansible remoting script, the connection fails and the play ends on that host.
Below is a solution.

```
- hosts: adserver
  gather_facts: no
  connection: local
  tasks:
    - block:
        - name: test basic auth is working on port 5985
          wait_for_connection:
            timeout: 10
        - name: copy winrm setup for ansible
          win_copy:
            src: ConfigureRemotingForAnsible.ps1.txt
            dest: C:\users\vagrant\ConfigureRemoteForAnsible.ps1
        - block:
            - name: enable credssp and disable basic auth and port 5985
              win_shell: C:\users\vagrant\ConfigureRemoteForAnsible.ps1 -enablecredssp -disablebasicauth -disableinsecureport
          rescue:
            - debug:
                msg: "Insecure WinRM is now disabled"
      rescue:
        - debug:
            msg: "Insecure WinRM already disabled.. move on!"

        - name: clear any host unreachable error messages.
          meta: clear_host_errors
      vars:
        ansible_winrm_transport: basic
        ansible_connection: winrm

- hosts: adserver
  gather_facts: no
  vars:
    ansible_winrm_transport: credssp
    ansible_port: 5986
  roles:
    - role: manage-hostname
    - role: install-ad
    - role: ad-users-and-groups
    - role: install-rds

```

## Case 2: Got multiple plays affecting the same hosts but need to weed out the unreachables first before running on the remaining plays

This is a theoretical  scenario for me. I was wondering how do you weed out all the unreachable hosts at the beginning
of the first play and make sure that subsequent plays not to connect to the unreachable hosts.

```
---
- hosts: web
  connection: local
  gather_facts: no
  tasks:
    - block:
        - name: check to see if the port is open
          wait_for_connection:
            timeout: 10
          vars:
            ansible_connection: ssh
        -  name: add devices with connectivity to the "working_hosts" group
            group_by:
            key: "working_hosts"
      rescue:
        - debug: msg="cannot connect to {{ inventory_hostname }}"

- hosts: working_hosts
  gather_facts: no
  tasks:
    - shell: date
    - debug:
        msg: "host {{inventory_hostname }} is working"

```
