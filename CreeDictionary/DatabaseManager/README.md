# Database Manager

A package that manages db.sqlite3 and imports xml files.

If installed as a package, command `manage-db` will be added to python environment and should be accessible from a terminal cross-platform. In case `manage-db` is not accessible, use `python -m DatabaseManager` instead. 

## Examples

- Unlink the database and import crkeng.xml to the database (migrations will also be applied)

    `manage-db import res/dictionaries/`
    
- Help for sub-command `import`

    `manage-db import --help`


## My word isn't imported to the database :(

- `cd DatabaseManager/logs`
- search and find out what happened to your word
