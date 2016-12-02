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
* python 2.7+ and fabric 1.x
* drush 8+
* git

Distribution/version-specific installation instructions are provided below.

---

## CentOS 7 / RHEL 7

### Installing Drubs using Puppet

1.  Install puppet in standalone mode (recommended).

    ```bash
    sudo rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm
    yes | sudo yum -y install puppet
    ```

2.  Install all dependencies and the latest release of Drubs using the provided
    [CentOS 7 puppet manifest](puppet/drubs_centos7.pp).  Please note that
    additional configuration will be necessary for secure operation on publicly
    available and/or production nodes.  This manifest is supplied to ease
    installation of Drubs - it is not a complete server setup solution.

    ```bash
    sudo puppet apply drubs_centos7.pp
    ```

### Installing Drubs manually

1.  Install dependencies.

2.  Install or update using pip:

    ```bash
    # To install or update to the latest release:
    sudo pip install -I git+https://github.com/komlenic/drubs.git@0.3.3#egg=Drubs

    # To install or update to the latest commit or "tip":
    sudo pip install -I git+https://github.com/komlenic/drubs.git#egg=Drubs
    ```

---

## CentOS 6 / RHEL 6

1.  Install dependencies.

    *Important:* Ensure that python 2.7 is available.  On CentOS6/RHEL6 systems
    you can install python 2.7 by:

    ```bash
    wget https://centos6.iuscommunity.org/ius-release.rpm -v -O ius-install.rpm
    sudo rpm -Uvh ius-install.rpm
    sudo rm ius-install.rpm
    sudo yum -y install python27 python27-devel python27-pip python27-setuptools python27-virtualenv --enablerepo=ius
    ```

2. Install or update using pip2.7:

    ```bash
    # To install or update to the latest release:
    sudo pip2.7 install -I git+https://github.com/komlenic/drubs.git@0.3.3#egg=Drubs

    # To install or update to the latest commit or "tip":
    sudo pip2.7 install -I git+https://github.com/komlenic/drubs.git#egg=Drubs
    ```

---

## All others

1.  Install dependencies.

2.  Install or update using pip:

    ```bash
    # To install or update to the latest release:
    sudo pip install -I git+https://github.com/komlenic/drubs.git@0.3.3#egg=Drubs

    # To install or update to the latest commit or "tip":
    sudo pip install -I git+https://github.com/komlenic/drubs.git#egg=Drubs
    ```
