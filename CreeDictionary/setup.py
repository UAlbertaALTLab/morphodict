from setuptools import setup, find_packages

setup(
    name="CreeDictionary",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "manage-db=DatabaseManager.__main__:cmd_entry",
            "update-layouts=utils.update_layouts:update",
        ]
    },
)
