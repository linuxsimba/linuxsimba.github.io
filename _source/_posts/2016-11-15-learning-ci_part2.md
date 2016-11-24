---
title: Learning Continuous Integration - Part 2
tags: ['ci', 'gitlab']
---

[Continuous integration](https://en.wikipedia.org/wiki/Continuous_integration) (CI) is the hot new thing in the computer infrastructure world. To learn CI I'm going to practise it using one of my favorite python projects - netshow.

This article covers how to setup CI on the [netshow-core](https://github.com/linuxsimba/netshow-core) project. For details on how to setup Gitlab, review [Part 1 of this series]({% post_url 2016-11-14-learning-ci_part1 %})

## Configure gitlab-ci.yml
Gitlab provides builtin CI support. Much like Github supports Travis CI by default. To activate CI support, create a ``.gitlab-ci.yml`` file in the root of the Git repo.

#### Defining gitlab-ci.yml
Below is the ``.gitlab-ci.yml`` for the netshow-core project.

{% gist linuxsimba/8756d4d5fc0d7ee64b0624a26c9b4722 %}

It says it will run 2 jobs. The first is using a python 2.7 container, and the second will use a python 3.4 container.
This is done to ensure that the code is compatible with both established python versions and the upcoming python
release set to take over.

#### Activating gitlab-ci.yml

* Add SSH Key so passwordless access to the Git repository is possible
![ssh key settings](https://lh3.googleusercontent.com/-xgNuQL0Xu-c/WDWtc6hAvqI/AAAAAAAAMPw/2Qi-1-mBvfUOZDvPGziWo9suFH2YeRkTwCLcB/s0/ssh_key_setting_1.png "ssh_key_setting_1.png")

* If you are using MacOS or Linux modify the $HOME/.ssh/config to include the gitlab SSH connection info

```
Host gitlab.linuxsimba.test
  Hostname localhost
  Port 9022
  User git
```

*  git clone netshow-core from the local gitlab server

```
% git clone git@gitlab.linuxsimba.test:demo/netshow-core     

Cloning into 'netshow-core'...
remote: Counting objects: 1227, done.
remote: Compressing objects: 100% (459/459), done.
remote: Total 1227 (delta 712), reused 1227 (delta 712)
Receiving objects: 100% (1227/1227), 239.22 KiB | 0 bytes/s, done.
Resolving deltas: 100% (712/712), done.
Checking connectivity... done.
```

* Create a branch add the ``.gitlab-ci.yml`` file along with other necessary changes
to make Gitlab CI work

```
wget https://goo.gl/0jfMmJ -o $HOME/add_ci.diff
git checkout -b add_ci_stuff
patch -p0 < $HOME/add_ci.diff
git add .
git commit -m "add CI"
git push origin add_ci_stuff
```

#### Create a Pull Request
Then in the Gitlab UI, create a [Pull request](https://help.github.com/articles/about-pull-requests/) and watch the Gitlab runner execute
the tests defined in ``.gitlab-ci.yml``

![new merge request](https://lh3.googleusercontent.com/5BfSn849d77dSC624sFrOLWq-tPVgPNZplxFEiOodGx_Z1K0FrjzvMdB_E2yNneBMqaikz-x=s0 "new_merge_request.png")

#### Observe the Status of the tests
One of the tests failed. The build of  netshow-core using python-3.5. Details can be seen by
clicking on the failed test. Gitlab will move to the pipeline section showing the docker container output
of the failed build.
![details of merge result](https://lh3.googleusercontent.com/-e1bqHHSUTnE/WDZTgzuSLjI/AAAAAAAAALM/B6GP513jgCMSraIOS9_mckUyGzWt51gpQCLcB/s0/details_of_merge_result.png "details_of_merge_result.png")

#### Iterate on the Pull Request. Fix the failed build
Here is the beauty of CI. When a test fails, all that needs to be done is to fix the code in the ``add_gitlab_ci`` branch. Commit this code and the tests will automatically run again. The fix was to disable pylint tests on the
``netshow.netshow`` module.

```
diff --git a/netshow/tox.ini b/netshow/tox.ini
index a9f6123..ab3f374 100644
--- a/netshow/tox.ini
+++ b/netshow/tox.ini
@@ -13,4 +13,3 @@ commands=
   python setup.py bdist_wheel
   pip install --find-links=./dist netshow-core
   nosetests --first-package-wins
-  pylint -E netshow
```

The build passed. Gitlab was set with desktop notifications so a desktop alert was issue
when the build finished.

#### Rebase the request, before the request is committed

Rebasing means taking all the patches in the Pull request and reducing it down on just one gigantic patch.

```
git rebase -i origin/master
```
An editor will open. Keep the ``pick`` setting for only the first commit. Change all other commit settings to ``squash`` and save. The commits will be squashed down to 1 commit. Then force the new single commit to overwrite the branch

```
git push origin add_gitlab_ci -f
```

#### Submit the Pull Request
![ submit the merge](https://lh3.googleusercontent.com/-iGzg9S10LUI/WDZiii9Vt_I/AAAAAAAAALo/34jlA5_S7_AjXL5SSnnlw6eCbxo5AD1NACLcB/s0/merge_is_allowed.png "merge_is_allowed.png")

The next part of the series is work with multiple branches and how CI can be used to ensure the stability of the application. Specifically how to commit to a develop branch simulating a dev release. Then at some point, merging the dev release changes back to master to simulate creating a new production release.
