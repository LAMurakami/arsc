# Lawrence A. Murakami at ARSC

[arsc.lam1.us](http://arsc.lam1.us/)
[arsc.lamurakami.com](http://arsc.lamurakami.com/)

This is one of the additional-sites of the Linux Apache MariaDB in the cloud
AWS EC2 instance described in the
[aws repo README.md](https://github.com/LAMurakami/aws#readme)

The main page is a copy of what was at people.arsc.edu/~murakami with
broken links changed.  Some of the links were changed to point to pages
captured by The Internet Archive as part of the Internet Archive Wayback
Machine.

I started with
[Arctic Region Supercomputing Center](https://en.wikipedia.org/wiki/Arctic_Region_Supercomputing_Center)
(ARSC) Monday, August 31, 2009 and created the people.arsc.edu/~murakami
page by the end of the year when I created an ARSC HPC Users Newsletter
contribution.

My time with ARSC ended August 31, 2015 when I retired, not coincidentally,
the same day
[Arctic Region Supercomputing Center ceased to exist](http://arsc.lam1.us/About).

This repo contains content in the html folder and an apache2 configuration
that can be implemented with:

<pre>sudo ln -s /var/www/arsc/arsc_apache2.conf \
/etc/apache2/sites-available/060_arsc.conf

sudo a2ensite 060_arsc
sudo systemctl reload apache2</pre>

If the repo contents are installed in a location other than /var/www
the path in the configuration and in the instuctions would have to be modified.

The arsc_archive_rebuild.bash script will Rebuild an archive of /var/www/arsc
resources when they change.  It is intended to be run daily with:

<pre>ln -s /var/www/arsc/arsc_archive_rebuild.bash /mnt/efs/aws-lam1-ubuntu/arsc</pre>

This would then be picked up by the Daily cron job to backup
/mnt/efs/aws-lam1-ubuntu archives.

<pre>$ cat /etc/cron.daily/Bk-20-aws-changes
#!/bin/bash
run-parts --report /mnt/efs/aws-lam1-ubuntu
[19:34:30 Sunday 06/14/2020] ubuntu@aws</pre>


See Also:
* [aws repo README.md](https://github.com/LAMurakami/aws#readme)
* [no-ssl repo README.md](https://github.com/LAMurakami/no-ssl#readme)
* [ubuntu-etc repo README.md](https://github.com/LAMurakami/ubuntu-etc#readme) Ubuntu Server 20.04 configuration changes for LAM AWS VPC EC2 instances

