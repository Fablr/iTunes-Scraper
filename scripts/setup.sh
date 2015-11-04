#!/bin/bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python3
brew install unixodbc
brew install freetds --with-unixodbc
export WORKON_HOME=$HOME/.virtualenvs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv --python=/usr/local/bin/python3 VFABLER_ITUNESSCRAPER
pip install virtualenv
pip install virtualenvwrapper
echo source ~/.bashrc >> ~/.profile
echo source /usr/local/bin/virtualenvwrapper.sh >> ~/.bashrc
echo export WORKON_HOME=$HOME/.virtualenvs >> ~/.bashrc
