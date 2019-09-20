# Database Manager

A package that manages db.sqlite3 and imports xml files.

If installed as a package, command `manage-db` will be added to python environment and should be accessible from a terminal cross-platform. In case `manage-db` is not accessible, use `python -m DatabaseManager` instead. 

## Examples

- Import crkeng.xml and engcrk.xml to the database

    `manage-db import /res/dictionaries/`
    
- Use multi-process acceleration

    `manage-db import /res/dictionaries/ --multi-process 2`
    
- Help for sub-command `import`

    `manage-db import --help`

- Clear imported old data (normally unnecessary as `import` also clears data at start)

    `manage-db clear`

## My word isn't imported to the database :(

- `cd DatabaseManager/logs`
- search and find out what happened to your word