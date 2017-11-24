---
title: "Windows Active Directory LDAPS Setup using an External Certificate Authority"
tags: ['ldaps', 'windows']
---

  The procedures shown should work with Windows 2012 and Windows 2016.

The reason for writing this is because I use a trial version Windows 2012 server to test Active Directory integration with [Ansible Tower](https://www.ansible.com/tower) , [Netbox](https://netbox.readthedocs.io/en/latest/), and [Cumulus Linux Authentication](https://docs.cumulusnetworks.com/display/DOCS/LDAP+Authentication+and+Authorization).  In some cases I need to setup a secure LDAPS connection.

An Active Directory server requires a valid SSL certificate and the root certificate authority certificate placed on the server before Microsoft Windows automatically enables  LDAPS (_port 636_).

If you have limited compute and time resources on your Linux servers, like me, it is not possible to setup a Microsoft CA server and Microsoft Active directory Virtual Machines. So instead an external certificate authority (CA) is used. In this example the ancient [``CA.pl``](https://wiki.openssl.org/index.php/Manual:CA.pl(1)) perl script is used. Still works after all these years!  It is lightweight and requires only 1 Windows Server VM to be configured, i.e the Active Directory server.

> A Microsoft CA cannot coexist with Microsoft AD on the same Windows Server


## Workflow

<div class="flow-chart"><svg height="510" version="1.1" width="1039.53125" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="overflow: hidden; position: relative; top: -0.65625px;"><desc style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Created with Raphaël 2.1.2</desc><defs style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><path stroke-linecap="round" d="M5,0 0,2.5 5,5z" id="raphael-marker-block" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></path><marker id="raphael-marker-endblock33-obj1588" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1589" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1590" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1591" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1592" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1593" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj1594" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker></defs><rect x="0" y="0" width="52.6875" height="39" rx="20" ry="20" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="st" transform="matrix(1,0,0,1,152.2734,4)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="stt" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,152.2734,4)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Start</tspan></text><rect x="0" y="0" width="162.078125" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op2" transform="matrix(1,0,0,1,97.5781,97)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op2t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,97.5781,97)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create the External CA </tspan></text><rect x="0" y="0" width="237.34375" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op3" transform="matrix(1,0,0,1,369.6016,97)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op3t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,369.6016,97)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Set the Windows Server Hostname</tspan></text><rect x="0" y="0" width="308.28125" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op4" transform="matrix(1,0,0,1,334.1328,190)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op4t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,334.1328,190)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Setup Active Directory on the Windows Server</tspan></text><rect x="0" y="0" width="292.046875" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op5" transform="matrix(1,0,0,1,342.25,283)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op5t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,342.25,283)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create the Certificate Signing Request(CSR)</tspan></text><rect x="0" y="0" width="349.234375" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op6" transform="matrix(1,0,0,1,688.2969,283)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op6t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,688.2969,283)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Sign the CSR on the External CA creating a certificate</tspan></text><rect x="0" y="0" width="347.046875" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op7" transform="matrix(1,0,0,1,689.3906,376)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op7t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,689.3906,376)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Install the server certificate into the Windows Server</tspan></text><rect x="0" y="0" width="194.875" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op8" transform="matrix(1,0,0,1,765.4766,469)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op8t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,765.4766,469)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Reboot the Windows Server</tspan><tspan dy="18" x="10" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></tspan></text><path fill="none" stroke="#000000" d="M178.6171875,43C178.6171875,43,178.6171875,82.65409994125366,178.6171875,94.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1588)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M259.65625,116.5C259.65625,116.5,348.9827271774411,116.5,366.6037705268973,116.5" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1589)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M488.2734375,136C488.2734375,136,488.2734375,175.65409994125366,488.2734375,187.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1590)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M488.2734375,229C488.2734375,229,488.2734375,268.65409994125366,488.2734375,280.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1591)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M634.296875,302.5C634.296875,302.5,673.9509749412537,302.5,685.2973140846007,302.5" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1592)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M862.9140625,322C862.9140625,322,862.9140625,361.65409994125366,862.9140625,373.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1593)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M862.9140625,415C862.9140625,415,862.9140625,454.65409994125366,862.9140625,466.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj1594)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path></svg></div>


## Create the External Certificate Authority (CA)
Install the openssl  package containing the ``CA.pl`` script onto the Linux hypervisor.

```
yum install openssl-perl (Centos/RHEL)

dnf install openssl-perl (Fedora 25+)

apt-get install openssl (Debian/Ubuntu)
```

Create the Certificate Authority. Review the ``CA.pl`` to see where the certificates are installed. The variable is called ``$CATOP``.

```
% sudo /usr/lib/ssl/misc/CA.pl -newca
CA certificate filename (or enter to create)

Making CA certificate ...
Generating a 2048 bit RSA private key
......+++
........+++
writing new private key to './demoCA/private/cakey.pem'
Enter PEM pass phrase: [enter password]
Verifying - Enter PEM pass phrase: [enter matching password]
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:North Carolina
Locality Name (eg, city) []:Durham
Organization Name (eg, company) [Internet Widgits Pty Ltd]:LinuxSimba
Organizational Unit Name (eg, section) []:Dept of Work
Common Name (e.g. server FQDN or YOUR name) []:Server Admin
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []: [blank hit return]
An optional company name []: [blank hit return]
Using configuration from /usr/lib/ssl/openssl.cnf
Enter pass phrase for ./demoCA/private/cakey.pem:
Check that the request matches the signature
Signature ok
Certificate Details:
        Serial Number: 12757355171169984766 (0xb10b3aefd31460fe)
        Validity
            Not Before: May 13 01:03:32 2017 GMT
            Not After : May 12 01:03:32 2020 GMT
        Subject:
            countryName               = US
            stateOrProvinceName       = North Carolina
            organizationName          = LinuxSimba
            organizationalUnitName    = Dept of Work
            commonName                = Server Admin
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                E9:97:DD:5D:EE:92:94:31:6F:A1:72:03:9B:CB:9B:94:85:72:74:54
            X509v3 Authority Key Identifier:
                keyid:E9:97:DD:5D:EE:92:94:31:6F:A1:72:03:9B:CB:9B:94:85:72:74:54

            X509v3 Basic Constraints:
                CA:TRUE
Certificate is to be certified until May 12 01:03:32 2020 GMT (1095 days)

Write out database with 1 new entries
Data Base Updated

```

## Set the Windows Server Name

This step assumes that Active directory is not configured yet. If it is, delete the server VM and start from scratch. Changing the hostname after installing Active Directory is not an easy thing.

Use Powershell to set the Windows Server name.

```powershell
$ Rename-Computer -NewName linuxsimbaAD"
$ Restart-Computer -Force
```


## Install Windows Active Directory

Install the Active Directory and DNS Windows Features. PowerShell commands shown below:

```
$ install-windowsfeature -name "ad-domain-services" -IncludeAllSubFeature -IncludeManagementTools -ComputerName "linuxsimbaAD"

$ install-windowsfeature -name "dns" -IncludeAllSubFeature -IncludeManagementTools -ComputerName "linuxsimbaAD"

```

Then install Active Directory Services.  After that the server reboots.

```
$  Import-Module ADDSDeployment
$  Install-ADDSForest `
        -CreateDnsDelegation:$false `
        -DatabasePath "C:\Windows\NTDS" `
        -DomainMode "Win2012R2" `
        -DomainName "linuxsimba.local" `
        -DomainNetbiosName "LINUXSIMBA" `
        -ForestMode "WIN2012R2" `
        -InstallDns:$true `
        -safemodeadministratorpassword (convertto-securestring 1q2w3e4r5t! -asplaintext -force) `
        -LogPath "C:\Windows\NTDS" `
        -NoRebootOnCompletion:$false `
        -SysvolPath "C:\Windows\SYSVOL" `
        -Force:$true
```


## Create the Windows Server CSR

From the [Microsoft Technet article about using external CAs](https://support.microsoft.com/en-us/help/321051/how-to-enable-ldap-over-ssl-with-a-third-party-certification-authority), create a ``request.inf`` file. In this example, the CSR looks like this:

```
;----------------- request.inf -----------------

[Version]

Signature="$Windows NT$

[NewRequest]

Subject = "CN=linuxsimbaAD.linuxsimba.local" ; replace with the FQDN of the DC
KeySpec = 1
KeyLength = 2048
; Can be 1024, 2048, 4096, 8192, or 16384.
; Larger key sizes are more secure, but have
; a greater impact on performance.
Exportable = TRUE
MachineKeySet = TRUE
SMIME = False
PrivateKeyArchive = FALSE
UserProtected = FALSE
UseExistingKeySet = FALSE
ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
ProviderType = 12
RequestType = PKCS10
KeyUsage = 0xa0

[EnhancedKeyUsageExtension]

OID=1.3.6.1.5.5.7.3.1 ; this is for Server Authentication

;-----------------------------------------------
```

Then create a Certificate Signing Request(CSR) from the ``request.inf`` file.

```
$ certreq -new request.inf newreq.pem
```

Copy the newreq.pem file back to the Linux hypervisor where the Certificate authority resides.

## Sign the Windows Server CSR

Use the new CA on the Linux hypervisor to sign the certificate. The name of the CSR should be ``newreq.pem``.

```
$ sudo /usr/lib/ssl/misc/CA.pl -signreq

Using configuration from /usr/lib/ssl/openssl.cnf
Enter pass phrase for ./demoCA/private/cakey.pem:
Check that the request matches the signature
Signature ok
Certificate Details:
        Serial Number: 12757355171169984767 (0xb10b3aefd31460ff)
        Validity
            Not Before: May 13 02:54:29 2017 GMT
            Not After : May 13 02:54:29 2018 GMT
        Subject:
            commonName                = linuxsimbaAD.linuxsimba.local
        X509v3 extensions:
            X509v3 Basic Constraints:
                CA:FALSE
            Netscape Comment:
                OpenSSL Generated Certificate
            X509v3 Subject Key Identifier:
                0F:6E:E7:20:5A:53:4D:93:82:6A:A8:9F:41:39:1A:92:A5:60:23:9F
            X509v3 Authority Key Identifier:
                keyid:E9:97:DD:5D:EE:92:94:31:6F:A1:72:03:9B:CB:9B:94:85:72:74:54

Certificate is to be certified until May 13 02:54:29 2018 GMT (365 days)
Sign the certificate? [y/n]:y


1 out of 1 certificate requests certified, commit? [y/n]y
Write out database with 1 new entries
Data Base Updated
Signed certificate is in newcert.pem

$ cp newcert.pem ldapcert.pem
$ cp demoCA/cacert.pem cacert.pem
```

## Copy the Server Certificate and Root Certificate back into the Windows Servers

Copy ``ldapcert.pem`` (_LDAP Server SSL Certificate_)  and ``cacert.pem`` (_CA SSL Certificate_) to the Windows Server Virtual Machine. Then use the following Powershell command to install the Root certificate

``` powershell

Import-Certificate -FilePath C:\users\vagrant\cacert.pem -CertStoreLocation Cert:\LocalMachine\Root
```

Next install the server certificate into the servers personal SSL store

``` powershell

Import-Certificate -FilePath C:\users\vagrant\ldapcert.pem -CertStoreLocation Cert:\LocalMachine\My
```


> Make sure to check the time on the server. Wrong time could result in the certificate becoming invalid and LDAPS will not work.


Finally Restart the Server

## Verify LDAPS connection

After the Windows Server restart LDAPs should be working. Here are some steps to verify if its working.

* Start ``ldp.exe`` on the Windows server

![enter image description here](https://lh3.googleusercontent.com/-qoOKIk4kzJg/WRZ8-JnVK_I/AAAAAAAAOUQ/tbXyXxYMlpUx4UmRn59C3TbJI4iUoM0nQCLcB/s0/ldap_connect.png "ldap_connect.png")

*  Output from a working server
![enter image description here](https://lh3.googleusercontent.com/-vuzQaGSzjt4/WRZ9OEOYchI/AAAAAAAAOUY/0ABcUmrgI6sKu_Ycc_N40oMEon1pb6VBwCLcB/s0/ldp+output_working.png "ldp output_working.png")

* View of the valid Server Certificate
![enter image description here](https://lh3.googleusercontent.com/-eUNoHLOQmqQ/WRZ9hN33C6I/AAAAAAAAOUg/0HAQgmJr6_IegmZAZfKnrb6784rjWLSOwCLcB/s0/view_of_working_cert.png "view_of_working_cert.png")

## Reference

* [Adding a Certificate Using Powershell](https://mcpmag.com/articles/2014/11/18/certificate-to-a-store-using-powershell.aspx)
* [How to enable LDAP over SSL with a 3rd Party CA](https://support.microsoft.com/en-us/help/321051/how-to-enable-ldap-over-ssl-with-a-third-party-certification-authority)

> Written with [StackEdit](https://stackedit.io/).
