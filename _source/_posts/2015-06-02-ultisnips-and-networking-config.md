---
title: Vim Ultisnips and Computer Network Templates
tags: ['vim', 'computer_networking', 'cumulus']
---
[Vim Ultisnips](http://vimawesome.com/plugin/ultisnips-forever-and-always) is a very cool snippet plugin for VIM. Yes I'm a [VIM](http://www.vim.org/) user. Still not an expert, but getting better every day.

Cumulus Linux, as a programmatic way of entering repeatable config using [Mako](https://support.cumulusnetworks.com/hc/en-us/articles/202868023-Configuring-etc-network-interfaces-with-Mako).

But I though, nah, I don't want do that. I wanted to use the [Cumulus Ansible modules](https://galaxy.ansible.com/list#/roles/1875) and  wrote variable config in the ``host_vars/[hostname]`` location

So I wanted to configure 100 bridges, and I wanted to do it on a switch to switch basis. So each switch gets a different set of 100 vlans. _(its for a test for a real network)_

```
cl_bonds:
  bond0:
    slaves: ['swp17-18']
    ipv4: '10.1.1.0/31'

cl_interfaces:
  swp52:
    ipv4: ['10.1.3.1/24']

cl_bridges:
  br0:
    ports: ['swp49-50', 'swp51']
  br1:
    ports: ["swp49-50.1", "swp51.1"]
  ...
  ....
  ......
  br99:
    ports:["swp49-50.99, "swp51.99"]
```

So I managed to get the Ultisnip snippet for this section of the code.

```
br1:
    ports: ["swp49-50.1", "swp51.1"]
...
....
......
br99:
    ports:["swp49-50.99, "swp51.99"]

```

The Ultisnip snippet below creates 100 entries of "br" entry config, iterated from 1 to 99.

```
snippet br
`!p
for i in range(1,100):
  snip.rv += 'br%(foo)s:\n' % {'foo': i}
  snip.rv += '  ports: ["swp49-50.%(foo)s", "swp51.%(foo)s"]\n' % {'foo': i}
`
endsnippet
```

Just typed ``br[tab]`` , at the beginning of the line under the ``br0`` port config.
Then from the end of the document

* ``Ctrl-Shift-V`` - Visual Line. Start the highlight line at the bottom of the document
* ``/br1[enter]`` - Search to line with ``br11`` and Vim selection highlighting will move from the bottom of the page to that ``br1`` line
* ``1>x`` to shift the selection one "tab" over so its inline with the rest of the YAML config

So many keystrokes to remember. But with VIM, the more you practise, the more it becomes natural.
