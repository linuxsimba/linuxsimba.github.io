---
title: "Stupid Things I Have Done On Linux"
tags: ['fun', 'linux']
---

1. **`rm -rf ./`**  
I wanted to delete all the contents in the current directory. I forgot the `"."`
and guess what happened?  Thank goodness I have a [restore pc Ansible
playbook](https://github.com/skamithi/restore_pc/)

2. **Edit files monitored by [Guard](http://guardgem.org/) in a VM from the host
PC**  
I recently started using [Vagrant](http://). I thought it would be cool to
change the files found in the `/vagrant` directory on the VM, from the host PC
but run [Guard](http://guardgem.org/) on the VM. Of cause, when I saved a file,
nothing happened. Why? After some time, I realized
[Guard](http://guardgem.org/) depends on [Linux
Inotify](http://linux.die.net/man/7/inotify). So, the host never sees
these events. Therefore, [Guard](http://guardgem.org/) never does anything when I change the file it should be
"watching".
3. **`git reset --hard` when I had important work I had not stashed**  
On this day, I truly was not thinking. I lost a lot of time and was very
frustrated regenerating the "important work".  I now remember - `git
stash` is your friend!
