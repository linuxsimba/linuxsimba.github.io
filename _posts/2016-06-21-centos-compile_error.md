---
title: "AM_PROG_AR Compile Error on Centos 6"
tags: ['compile', 'centos']
---

Had to recently compile  the latest version of  [nss-pam-ldapd](https://arthurdejong.org/nss-pam-ldapd/) - 	version 0.9.6 on CentOS6 and encountered a compilation error.

### Problem

Experienced the following error:

<pre>
rpmbuild -ba nss-pam-ldapd.spec
Executing(%prep): /bin/sh -e /var/tmp/rpm-tmp.XpF5ON
+ umask 022
+ cd /home/vagrant/rpmbuild/BUILD
+ LANG=C
+ export LANG
+ unset DISPLAY
+ cd /home/vagrant/rpmbuild/BUILD
+ rm -rf nss-pam-ldapd-0.9.6
+ /bin/tar -xf -
+ /usr/bin/gzip -dc /home/vagrant/rpmbuild/SOURCES/nss-pam-ldapd-0.9.6.tar.gz
+ STATUS=0
+ '[' 0 -ne 0 ']'
+ cd nss-pam-ldapd-0.9.6
+ /bin/chmod -Rf a+rX,u+w,g-w,o-w .
+ autoreconf -f -i
<strong>
configure.ac:64: warning: macro `AM_PROG_AR' not found in library
configure.ac:64: error: possibly undefined macro: AM_PROG_AR
      If this token and others are legitimate, please use m4_pattern_allow.
      See the Autoconf documentation.
configure:10941: error: possibly undefined macro: m4_ifnblank
autoreconf: /usr/bin/autoconf failed with exit status: 1
error: Bad exit status from /var/tmp/rpm-tmp.XpF5ON (%prep)
</strong>
</pre>

### Fix:

Upgrade [automake](ftp://ftp.pbone.net/mirror/ftp5.gwdg.de/pub/opensuse/repositories/home:/monkeyiq:/centos6updates/CentOS_CentOS-6/noarch/automake-1.13.4-3.2.noarch.rpm) and [autoconf](ftp://ftp.pbone.net/mirror/ftp5.gwdg.de/pub/opensuse/repositories/home:/monkeyiq:/centos6updates/CentOS_CentOS-6/noarch/autoconf-2.69-12.2.noarch.rpm) using updated packages from a  SUSE repo.


```
wget ftp://ftp.pbone.net/mirror/ftp5.gwdg.de/pub/opensuse/repositories/home:/monkeyiq:/centos6updates/CentOS_CentOS-6/noarch/automake-1.13.4-3.2.noarch.rpm

wget ftp://ftp.pbone.net/mirror/ftp5.gwdg.de/pub/opensuse/repositories/home:/monkeyiq:/centos6updates/CentOS_CentOS-6/noarch/autoconf-2.69-12.2.noarch.rpm

sudo yum install autoconf-2.69-12.2.noarch.rpm
sudo yum install automake-1.13.4-3.2.noarch.rpm
```

