# Database Manager

A package that manages db.sqlite3 and imports xml files.

If installed as a package, command `manage-db` will be added to python environment and should be accessible from a terminal cross-platform. In case `manage-db` is not accessible, use `python -m DatabaseManager` instead. 

## Examples

- Import crkeng.xml to the database

    `manage-db import /res/dictionaries/crkeng.xml`
    
- Import crkeng.xml to the database with multi-process acceleration

    `manage-db import /res/dictionaries/crkeng.xml --multi-process 3`
    
- Help for sub-command `import`

    `manage-db import --help`

- Clear imported old data (normally unnecessary as `import` also clears data at start)

    `manage-db clear`

## My word isn't imported to the database :(

- `cd DatabaseManager/logs`
- search and find out what happened to your word