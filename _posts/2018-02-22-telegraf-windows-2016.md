---
title: "Windows 2016 Error when loading telegraf"
tags: ["windows", "telegraf"]
---

Playing with [telegraf](https://www.influxdata.com/time-series-platform/telegraf/) and loaded it onto a Windows 2016 evaluation server. Got the strangest
error when using [chocolatey](https://chocolatey.org/) to install telegraf.

```
Installing 64-bit telegraf..
Exception 0xc0000005 0x8 0x0 0x0", "PC=0x0
Microsoft.PowerShell.Commands.WriteErrorException
runtime.asmstdcall(0x410fcd, 0x1a4000, 0x0, 0x45b565, 0x412030, 0x23, 0x1a4000, 0x458170, 0x1a0000, 0x4023, ...)
/usr/local/go/src/runtime/sys_windows_amd64.s:60 +0x5e fp=0x211fd80 sp=0x211fd70 pc=0x45f03e
 rax     0x0
 rbx     0x1eec298
 rcx     0x1f15660
 rdi     0x21a000
 rsi     0x211fea0
 rbp     0x211fe68
 rsp     0x211fd68
 r8      0x4315bd
 r9      0x211fee0
 r10     0x0
 r11     0x246
 r12     0x119e083
 r13     0x0
 r14     0x0
 r15     0x0
 rip     0x0
 rflags  0x10293
 cs      0x33
 fs      0x53
 gs      0x2b

```

It looks like an assembly error. After some research I found someone else had [run into this](https://github.com/golang/go/issues/21060).
The go-erlang devs say that everything works for them. Then someone else said a fresh Windows 2016 install seems reproduce the problem.

On my setup, I use a fresh Windows 2016 VM but I have windows updates disabled. So I re-enabled Windows updates and voila, the problem
went away. So I suspect the problem has to do with the evaluation image with updates disabled.

So for any further Windows 2016 installs, I am building my base image with Windows updates enabled.
Long term I want to have [Packer](https://www.packer.io/intro/index.html) install all windows updates, then disable the updates after that.
I don't need Windows 2016 VMs, during development testing,  to be updated because these are short lived VMs and windows updates are disruptive and slow down development time.
