#!/bin/bash

set -e

echo "Installing APT packages..."

# Requirements
echo "deb http://deb.debian.org/debian buster main" > /etc/apt/sources.list.d/buster.list
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y -t stretch install python3-venv python3-pip nginx openssl apache2-utils fcgiwrap curl supervisor
apt-get -y -t buster install git-lfs

echo "Creating virtualenv..."
VENV="/vagrant/_py_env"
rm -rf "$VENV"
pyvenv "$VENV"
test -e "$VENV/bin/pip" || { echo "FATAL: missing pip from venv!"; exit 1; }

echo "Installing pip dependencies..."
"$VENV/bin/pip" install -r /vagrant/djlfs_batch/requirements.txt

echo "Installing (system wide) uWSGI..."
pip3 install uwsgi
test -e "/usr/local/bin/uwsgi" || { echo "uWSGI failed to install."; exit 1; }

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

HTPASSWD=/opt/htpasswd
touch $HTPASSWD
chown www-data:www-data "$HTPASSWD"


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

	echo "Creating htpasswd Basic credentials: USER$x / PASS$1 ..."
	htpasswd -b "$HTPASSWD" USER$x PASS$x
done

chown -R www-data:www-data "$REPODIR"
chown -R www-data:www-data "$LFSDIR"

# Creating SSL keys
echo "Creating SSL key & cert"
openssl genrsa -des3 -passout pass:xyz123 -out /root/server.pass.key 2048
openssl rsa -passin pass:xyz123 -in /root/server.pass.key -out /root/server.key
rm /root/server.pass.key
openssl req -new -key /root/server.key -out /root/server.csr \
  -subj "/C=UK/ST=Example/L=Example/O=Example/OU=Example/CN=example.com"
openssl x509 -req -days 365 -in /root/server.csr -signkey /root/server.key -out /root/server.crt


echo "Configuring nginx..."
rm -f /etc/nginx/sites-enabled/*
ln -s /vagrant/wsgi-test/lfs_example_nginx_site /etc/nginx/sites-enabled/
service nginx reload

echo "Configuring Supervisor..."
rm -f /etc/supervisor/conf.d/*
ln -s /vagrant/wsgi-test/supervisord_uwsgi.conf /etc/supervisor/conf.d/
service supervisor restart


echo ""
echo "Provisioning done OK."
echo ""
