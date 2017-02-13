---
title: "Merging Git Upstream changes"
tags: ['git']
---

This has been a challenge for a while. Different web postings say to do different things. This is the way I solve it

This article uses the example of [Kargo - a Kubernetes installer](https://github.com/kubernetes-incubator/kargo)


### Fork the project
From the Github UI, fork the Kargo project. The new repo will be in called ``linuxsimba/kargo``


### Add a Upstream Repo to the Forked project
From CLI type:

```
cd kargo
git remote add upstream https://github.com/kubernetes-incubator/kargo
```

### Fetch the upstream branches

Update the ``upstream`` branches

```
git fetch upstream
```

### Call the main branch of the upstream repo "upstream_master"

```
git checkout -b upstream_master --track upstream/master
```

### When upstream is changed

When upstream master branch is updated, this is the steps taken to update the Linuxsimba fork master branch

```
git checkout upstream_master
git pull upstream master
git checkout master
git merge upstream_master
```
