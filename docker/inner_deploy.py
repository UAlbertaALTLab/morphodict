def run(call):
    """Perform post-git-pull deploy operations"""

    call(["./helper.py", "setup"])
    call(["docker-compose", "pull"])
    call(["docker-compose", "up", "-d", "--remove-orphans"])
    call(["./helper.py", "manage", "all", "migrate"])
