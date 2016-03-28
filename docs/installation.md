# Installation

Drubs is presently in pre-alpha development and may not be suitable for use in
production environments.  Any API's, functions, and commands are not to be
considered stable and may change in later releases.

With that said, should you wish to try drubs, instructions are provided below.

## Dependencies

Generically, drubs requires the following:

* apache 2+
* php 5.5+
* mysql 5.6+ (MariaDB should work also, untested)
* python 2.7+ and fabric 2
* drush 8+
* git

Distribution/version-specific installation instructions are provided below.

### CentOS 7 / RHEL 7

1.  Install dependencies.  A [puppet manifest](puppet/drubs_centos7.pp) exists
    for CentOS 7 / RHEL 7, which you can use to quickly install all dependencies
    (recommended).  Please note that additional configuration may be necessary
    for secure operation on publicly available and/or production nodes.

2.  Clone drubs project and install using pip:

    ```bash
    git clone https://github.com/komlenic/drubs.git
    sudo pip install -e ./drubs
    ```

### CentOS 6 / RHEL 6

1.  Install dependencies.

    *Important:* Ensure that python 2.7 is available.  On CentOS6/RHEL6 systems
    you can install python 2.7 by:

    ```bash
    wget https://centos6.iuscommunity.org/ius-release.rpm -v -O ius-install.rpm
    sudo rpm -Uvh ius-install.rpm
    sudo rm ius-install.rpm
    ```

2. Clone this project and install using pip2.7:

    ```bash
    git clone https://github.com/komlenic/drubs.git
    sudo pip2.7 install -e ./drubs
    ```

### All others

1.  Install dependencies.

2.  Clone drubs project and install using pip:

    ```bash
    git clone https://github.com/komlenic/drubs.git
    sudo pip install -e ./drubs
    ```
