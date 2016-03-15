# Drubs

Drubs (short for "Drupal Build System") is a command-line tool for building,
deploying, and managing Drupal sites across multiple servers and environments
such as development, testing, staging, and production.  It is:

* free - open source, GNU GPL
* flexible - specify or script every detail of your project, however you want
* repeatable - add, update, remove, and rebuild exact copies of your project
* distributed - trigger builds and updates on any servers, from anywhere
* integratable - use Drubs with shell scripts, Jenkins/Hudson, Travis CI, or
    any other continuous integration tools

The "Drubs" name is a hat-tip to the indespensible Drush.  Drupal is a
registered trademark of Dries Buytaert.

## Installation

Drubs is presently in pre-alpha development and may not be suitable for use in
production environments.  Any API's, functions, and commands are not to be
considered stable and may change in later releases.

With that said, should you wish to try drubs:

1. Ensure that any system on which you would like to run drubs has python 2.7
    available.  On CentOS6/RHEL6 systems you can install python 2.7 by:

    ```bash
    wget https://centos6.iuscommunity.org/ius-release.rpm -v -O ius-install.rpm
    sudo rpm -Uvh ius-install.rpm
    sudo rm ius-install.rpm
    yum -y install python27 python27-devel python27-pip python27-setuptools python27-virtualenv --enablerepo=ius
    ```

    CentOS7/RHEL7 systems are likley to already have python 2.7 installed.

2. Clone this project and install using pip:

    ```bash
    git clone https://github.com/komlenic/drubs.git
    sudo pip2.7 install -e ./drubs
    ```

3. To effectively use drubs, you'll need some dependencies installed on nodes
    where you wish to install Drupal projects.  Generically this list includes:

    * apache 2
    * php 5.4+
    * mysql 5.5+
    * python 2.7 and fabric 2
    * drush 7+
    * git

    More documentation on installing and managing these dependencies will be
    included in future releases.  It is anticipated that an automated means of
    installing and managing dependencies will be provided.

## Usage

Run the command 'drubs' or 'drubs --help' for a listing of commands and usage
examples.

## Contact

For more information email drubs@drubs.org or follow
[@drubscli](https://twitter.com/drubscli) on twitter.
