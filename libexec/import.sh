# 0005 was the basis of the import script in Database Manager
rm CreeDictionary/test_db.sqlite3 && pipenv migrate API 0005 && manage-db build-test-db