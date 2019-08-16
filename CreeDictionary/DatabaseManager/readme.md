# Database Manager

A package that manages db.sqlite3 and imports xml files.

## Examples

- Import crkeng.xml to the database

    `python DatabaseManager import /res/dictionaries/crkeng.xml`
    
- Import crkeng.xml to the database with multi-process acceleration

    `python DatabaseManager import /res/dictionaries/crkeng.xml --multi-process 3`
    
- Help for sub-command `import`

    `python DatabaseManager import --help`

- Clear imported old data (normally unnecessary as `import` also clears data at start)

    `python DatabaseManager clear`