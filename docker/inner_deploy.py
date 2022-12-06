def run(call):
    """Perform post-git-pull deploy operations"""

    call(["./helper.py", "setup"])
    call(["docker-compose", "pull"])
    call(["docker-compose", "up", "-d"])
    call(["./helper.py", "manage", "all", "migrate"])
