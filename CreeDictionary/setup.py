from setuptools import find_packages, setup

setup(
    name="CreeDictionary",
    packages=find_packages(),
    entry_points={"console_scripts": ["manage-db=DatabaseManager.__main__:cmd_entry",]},
)
