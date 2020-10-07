Migrations are not used to migrate database on production
The only times migrations are needed are when we re-build the database and
create empty tables with `manage.py migrate`

This includes when we manually build test database, 
and when our unit tests build test in memory database. 

0000_initial.py migration is re-generated based on models.py everytime when the database is rebuilt.  

This directory is managed by the rebuild script and does not require manual intervention: