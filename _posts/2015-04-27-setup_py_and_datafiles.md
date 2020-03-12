---
title: Setup.py, Wheels, and Data files
---

Building a python package where I want to install a text file outside of
``site-packages`` directory. In my case in under the
``{sys.prefix}/share/netshow-lib`` directory.

### Setup.py config

```
import netshowlib._version import get_version

setup(
    name='netshow-linux-lib',
    version=get_version(),
    url="[website]",
    description="Python Library to Abstract Linux Networking Data",
    author='[author]',
    author_email='[author email]',
    packages=find_packages(),
    zip_safe=False,
    license='GPLv2',
    cmdclass={"install_data": PostInstall,
              "build": BuildWithI18n},
    namespace_packages=['netshowlib', 'netshowlib.linux'],
    classifiers=[
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux'
    ],
    data_files=[('share/netshow-lib/providers', ['data/provider/linux'])]
)

```

The trick here was to specify the install directory
``share/netshow-lib/providers`` as a **relative** path, not absolute.

To know this works look out for the following message in ``python setup.py
bdist_wheel`` output

```
# python setup.py bdist_wheel
...
......
copying data/provider/linux ->
build/bdist.linux-x86_64/wheel/netshow_linux_lib-0.9.data/data/share/netshow-lib/providers

```

The file should get installed into the <span
style="color:green">*[project_name].data/data*</span> folder.
When that happens and you install the wheel using ``pip install`` you should see
a file listing like this. Notice that the data file is going to installed
outside of the ``site-packages`` folder and right under the ``sys.prefix``
folder.

```
# pip show netshow-linux-lib -f
...
....
Files:
  ../../../share/netshow-lib/providers/linux
  netshow/__init__.py
  netshow/__pycache__/__init__.cpython-34.pyc
  netshow/linux/__init__.py
```

Figured out this behavior by following the logic in the [python wheels source
code](https://bitbucket.org/pypa/wheel).

### References

[Python Packaging Guide](https://packaging.python.org/en/latest/) **(Read this first!)**


