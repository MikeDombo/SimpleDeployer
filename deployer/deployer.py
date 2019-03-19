from fnmatch import fnmatch
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict
import git
import subprocess
import sys

import yaml


def main():
    home = Path.home()
    config_path = Path.joinpath(home, ".deployer")
    config_file = Path.joinpath(config_path, "deployer.yaml")

    if Path.exists(config_file):
        with open(str(config_file), 'r') as cfg:
            run(yaml.safe_load(cfg))
    else:
        config_path.mkdir(parents=True, exist_ok=True)
        with open(str(config_file), 'w') as cfg:
            yaml.safe_dump({"definitions": [
                {"repository": "https://github.com...",
                 "sourceDir": ".",
                 "outDir": "c:\\Users\\mikep\\Desktop\\test",
                 "ignore": [".*/*"],
                 "noOverwrite": []
                 }
            ]}, cfg)


def run(config: Dict):
    for definition in config["definitions"]:
        try:
            # Get temp dir
            temp_dir = Path(tempfile.mkdtemp())

            # Clone requested repo with no history
            git.Repo.clone_from(definition["repository"], temp_dir, depth=1)

            src_dir = temp_dir.joinpath(Path(definition.get("sourceDir", ".")))
            out_dir = Path(definition["outDir"]).absolute()

            def ignorer(path, isDir=False):
                path = str(Path(path).as_posix())
                path = path[len(str(src_dir))+1:]
                if isDir and path and path[-1] != "/":
                    path += "/"

                return any(fnmatch(path, pat) for pat in definition.get("ignore", []))

            def nonOverwriter(path):
                path = str(Path(path).as_posix())
                path = path[len(str(src_dir)) + 1:]
                return any(fnmatch(path, pat) for pat in definition.get("noOverwrite", []))

            cp(str(src_dir), str(out_dir), ignore=ignorer, noOverwrite=nonOverwriter)
        finally:
            try:
                shutil.rmtree(str(temp_dir))
            except PermissionError:
                pass

        for command in definition.get("postInstall", []):
            print(command)
            subprocess.Popen(command, cwd=str(out_dir), stdout=sys.stdout, stderr=sys.stderr, shell=True).wait()


def cp(src, dest, ignore, noOverwrite):
    for src_dir, dirs, files in os.walk(src):
        dst_dir = src_dir.replace(src, dest)
        if not os.path.exists(dst_dir) and not ignore(src_dir, True):
            os.mkdir(dst_dir)
        for file in files:
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            if not ignore(src_file):
                if not os.path.exists(dst_file) or not noOverwrite(src_file):
                    try:
                        shutil.copy2(src_file, dst_dir)
                    except PermissionError as e:
                        print(e)


if __name__ == "__main__":
    main()
