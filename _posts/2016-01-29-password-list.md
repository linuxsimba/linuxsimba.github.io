---
title: "Python Script for Generating Password Word Dictionaries"
tags: ['hacking', 'password']
---

A friend forgot that their most recent IPhone backup to Itunes was
encrypted. Apple says, [you are basically
screwed](s://support.apple.com/en-us/HT205220) and have to guess your
password.

With [Opensource hacking software](http://hashcat.net/oclhashcat), and a little Python script, we managed to
figure out the password. The python script below takes a sequence of characters
and tries all permutations of those sequences and varies the length of the
permutations.

My friend, said that their password had a bunch of sequences, and it would
have about 4-6 of these sequences, but was not sure of the order. My friend
also had some clue what the first sequence of characters in the password was, so
we coded for that too.

First time doing something like this. Felt like being in a movie and playing the
part of the ace hacker :)

This is the Python script we came up with.


{% gist 8b9ea48b755964823047 %}



