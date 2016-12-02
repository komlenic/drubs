class yum_repos {
  yumrepo { "webtatic":
    baseurl => "http://uk.repo.webtatic.com/yum/el7/$architecture/",
    descr => "Webtatic repository",
    enabled => 1,
    gpgcheck => 0,
  }
  yumrepo { "epel":
    baseurl => "https://dl.fedoraproject.org/pub/epel/7/$architecture/",
    descr => "Extra packages for enterprise linux repository",
    enabled => 1,
    gpgcheck => 0,
  }
  yumrepo { "mysql":
     baseurl => "http://repo.mysql.com/yum/mysql-5.6-community/el/7/$architecture/",
     descr => "MySQL yum repository",
     enabled => 1,
     gpgcheck => 0
  }
  exec { "yum-makecache":
    command => "/usr/bin/yum makecache fast",
  }
}


class misc {
  package { "wget":
    ensure => present,
  }
  package { "git":
    ensure => present,
  }
  package { "patch":
    ensure => present,
  }
  package { "subversion":
    ensure => present,
  }
  package { "gcc":
    ensure => present,
  }
}


class httpd {
  file { ["/var/www", "/var/www/html"]:
    ensure => directory,
  }
  package { "httpd":
    ensure => present,
  }
  package { "httpd-devel":
    ensure => present,
  }
  service { "httpd":
    name      => "httpd",
    require   => [Package["httpd"],File["/var/www/html"]],
    ensure    => running,
    enable    => true,
  }
}


class php {
  package { "php55w":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-common":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-mysql":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-gd":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-xml":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-mbstring":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-pear":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-ldap":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-pecl-xdebug":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-mcrypt":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
  package { "php55w-mssql":
    ensure => present,
    require => Yumrepo["webtatic"],
  }
}


class mysql {
  package { "mysql-community-client":
    ensure => present,
    require => Yumrepo["mysql"],
  }
  package { "mysql-community-server":
    ensure => present,
    require => Yumrepo["mysql"],
  }
  service { "mysqld":
    name => "mysqld",
    require => Package["mysql-community-server"],
    ensure => running,
    enable => true,
  }
}

class python {
  package { "python":
    ensure => present,
  }
  package { "python-devel":
    ensure => present,
  }
  package { "python-setuptools":
    ensure => present,
  }
  package { "PyYAML":
    ensure => present,
  }
  package { "python-pip":
    ensure => present,
  }
  exec { "install-fabric":
    unless => "/usr/bin/command -v fab",
    command => "/usr/bin/pip install fabric",
    require => Package["python-pip"],
  }
}


class drush {
  exec { "install_drush":
    unless => "/usr/bin/command -v drush",
    command => "/bin/wget -P /tmp http://files.drush.org/drush.phar && /bin/chmod +x /tmp/drush.phar && /bin/mv /tmp/drush.phar /usr/local/bin/drush",
    require => [Package["php55w"],Package["wget"]],
  }
}


class drubs {
  exec { "install_drubs":
    command => "/usr/bin/pip install -I git+https://github.com/komlenic/drubs.git@0.3.3#egg=Drubs",
    require => [Package["python-pip"],Package["gcc"]],
  }
}


include yum_repos
include misc
include httpd
include php
include mysql
include python
include drush
include drubs
