#!/bin/bash
xcode-select --install
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install pyenv
brew install pyenv-virtualenv
pyenv install 3.4.3
pyenv rehash
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
exec $SHELL
pyenv global 3.4.3
pyenv virtualenv VFABLER_ITUNESCRAPER
pip install -r requirements.txt
