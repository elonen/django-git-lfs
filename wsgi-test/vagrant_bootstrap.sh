#!/bin/bash

set -e

echo "Installing APT packages..."

# Requirements
echo "deb http://deb.debian.org/debian buster main" >> /etc/apt/sources.list
apt-get update
apt-get -y -t stretch install python3-venv python3-pip apache2 libapache2-mod-wsgi-py3 curl
apt-get -y -t buster install git-lfs

echo "Creating virtualenv..."
VENV="/vagrant/_py_env"
rm -rf "$VENV"
pyvenv "$VENV"
test -e "$VENV/bin/pip" || { echo "FATAL: missing pip from venv!"; exit 1; }

echo "Installing dependencies..."
"$VENV/bin/pip" install -r /vagrant/djlfs_batch/requirements.txt

# Conveniences
apt-get -y -t stretch install joe bash-completion
echo '. /etc/bash_completion' >> /home/vagrant/.bashrc
echo 'alias ll="ls -lh"' >> /home/vagrant/.bashrc

echo "Configuring Git..."
# Make git complain less
git config --global user.name "Vagrant"
git config --global user.email vagrant_test@localhost

# Create test repositories

REPODIR=/opt/git_repos
mkdir -p $REPODIR

LFSDIR=/opt/lfs_storages
mkdir -p $LFSDIR	

for x in "repo1" "repo2" "repo3" ; do
  echo "Creating example repository: $x"
  if [ ! -d "$REPODIR/$x" ]; then
	  git init --bare "$REPODIR/$x.git" || { echo "Failed to init git repository."; exit 1; }
	  cd "$REPODIR/$x.git"
	  git lfs install || { echo "Failed to install LFS hooks."; exit 1; }
  fi
  if [ ! -d "$LFSDIR/$x" ]; then
	  mkdir "$LFSDIR/$x"  || { echo "Failed to create LFS storage dir."; exit 1; }
  fi
done

chown -R www-data:www-data "$REPODIR"
chown -R www-data:www-data "$LFSDIR"

echo "Configuring apache..."

cp /vagrant/wsgi-test/lfs_example_apache_site.conf /etc/apache2/sites-available/
a2enmod cgi
a2dissite 000-default
a2ensite lfs_example_apache_site
systemctl reload apache2

echo ""
echo "Provisioning done OK."
echo ""
