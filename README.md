# vteam-bike-brain

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/p0ntan/vteam-bike-brain/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/p0ntan/vteam-bike-brain/?branch=main)
[![Build Status](https://scrutinizer-ci.com/g/p0ntan/vteam-bike-brain/badges/build.png?b=main)](https://scrutinizer-ci.com/g/p0ntan/vteam-bike-brain/build-status/main)
[![codecov](https://codecov.io/gh/p0ntan/vteam-bike-brain/graph/badge.svg?token=PQLIP59BOW)](https://codecov.io/gh/p0ntan/vteam-bike-brain)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

## Introduction
First of all, welcome! And you might be wondering, what is a bike-brain? Well, this repo is part of a system where you can rent electric scooters a.k.a. bikes. Here you can find the code intended to be run inside each bike, and also for simulating multiple bikes inside the system. You can see the full system [here](https://github.com/p0ntan/vteam-root), where you also can find the other subsystems of our project. This comprehensive system encompasses various components, such as the bike brain, server and API, an administrative frontend GUI, a user-oriented frontend GUI, and a progressive web app for users.

## Setup
To use this repo, you'll need an .env file with the variables you find in the .env.example. But as you read above, this is a part of a bigger system and needs other components to work as intened.

But if you want to try the repo locally inside a docker-container, just run the command and it will throw you right in after setting everything up. 

Set up the repo with:
```
./setup.bash up
```

In the container tests and linters can be executed with pytest, pytlint or flake8. But the program (app.py) itself is depending on the server to be running and won't work properly without it.

## Teardown
Above command will start a container and keep it in the shell. To remove images when container is closed, run:

```
./setup.bash down
```

And it will clean everything up.
