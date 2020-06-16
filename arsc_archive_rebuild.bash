#!/bin/bash

<<PROGRAM_TEXT

This script will rebuild an archive of /var/www/arsc resources
 if any of the resources have been changed or added.

The archive is extracted on a new instance with:

tar -xvzf /mnt/efs/aws-lam1-ubuntu/arsc.tgz --directory /var/www

The following will list files changed since the archive was last rebuilt:

if [ $(find /var/www/arsc -newer /mnt/efs/aws-lam1-ubuntu/arsc.tgz -print \
 | sed 's|^/var/www/arsc/||' | grep -v '.git/' | grep -v '.git$' | wc -l) \
 -gt 0 ]
then
  find /var/www/arsc -newer /mnt/efs/aws-lam1-ubuntu/arsc.tgz \
  | grep -v '.git/' | grep -v '.git$' \
  | xargs ls -ld --time-style=long-iso  | sed 's|/var/www/arsc/||' 
fi

PROGRAM_TEXT

if [ $(find /var/www/arsc -newer /mnt/efs/aws-lam1-ubuntu/arsc.tgz -print \
| sed 's|^/var/www/arsc/||' | grep -v '.git/' \
| grep -v '.git$' | wc -l) -gt 0 ]; then

  echo Recreating the aws-lam1-ubuntu/arsc.tgz archive

  rm -f /mnt/efs/aws-lam1-ubuntu/arsc.t{gz,xt}

  tar -cvzf /mnt/efs/aws-lam1-ubuntu/arsc.tgz \
  --exclude='arsc/.git' \
  --exclude='arsc/html/RCS' \
  --directory /var/www arsc 2>&1 \
  | tee /mnt/efs/aws-lam1-ubuntu/arsc.txt

fi
