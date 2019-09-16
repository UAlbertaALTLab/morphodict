import argparse
import cProfile
import os
import subprocess
from os.path import dirname
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "script_name", help="py script name located at profiling folder"
    )

    args = parser.parse_args()

    script_name = args.script_name
    if not script_name.endswith(".py"):
        script_name += ".py"

    script_path = Path(dirname(__file__)) / script_name
    assert script_path.exists(), "script does not exist"

    pr = cProfile.Profile()
    pr.enable()

    # compile just so that there is script_name in the profiling graph
    exec(compile(script_path.read_text(), script_name, "exec"))

    pr.disable()

    prof_file = f"{os.path.splitext(script_name)[0]}.prof"

    pr.dump_stats(prof_file)

    subprocess.call(["snakeviz", prof_file])
