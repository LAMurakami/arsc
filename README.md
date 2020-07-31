# Lawrence A. Murakami at ARSC

[arsc.lam1.us](http://arsc.lam1.us/)
[arsc.lamurakami.com](http://arsc.lamurakami.com/)

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
