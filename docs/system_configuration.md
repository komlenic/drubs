# System configuration

## Adding a 'drubs' user

At this time, the best way that we've found to manage connecting to, and
managing Drupal sites on remote nodes using Drubs, is to create and configure a
'drubs' user.

### CentOS 7

Execute the following as root:

```bash
# Create the user.
useradd drubs

# Assign 'apache' user to the 'drubs' group.
usermod -a -G drubs apache

# Setup ssh keys for the 'drubs' user.
su drubs
ssh-keygen -t rsa -C "drubs@<hostname>"
# Go back to being 'root'.
exit

# Add public keys from other nodes which will be used to trigger builds on this
# node, to the 'drubs' user's 'authorized_keys' file.

# Make sure the 'drubs' user account is locked.
passwd -l drubs
```

At this point, you should be able to ssh to this node as 'drubs' from other
nodes which will be used to trigger builds on this node - without password,
using ssh keys.

You may need to modify the login access control table located at
`/etc/security/access.conf` to allow the 'drubs' user to login.  Generally this
involves editing this file and adding an entry for 'drubs' similar to the other
entries that will be present.

Finally, set the 'apache' user's umask, such that files created by Drupal in
`sites/default/files` have sufficient permissions to be deleted upon site
rebuild, etc:

```bash
# Set apache umask.
mkdir /etc/systemd/system/httpd.service.d
printf "[Service]\nUMask=0002" >> /etc/systemd/system/httpd.service.d/umask.conf

# Reboot the server.
reboot
```
