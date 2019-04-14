from fnmatch import fnmatch
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict
import git
import subprocess
import sys

import click
import yaml

home = Path.home()
config_path = Path.joinpath(home, ".deployer")
config_file = Path.joinpath(config_path, "deployer.yaml")


@click.command()
@click.option("--create/--no-create", default=True,
              help="Should automatically create config file if it doesn't already exist. "
                   "Default is to automatically create.")
@click.option("-f", "--file", default=config_file, type=click.Path(exists=False, file_okay=True, dir_okay=False,
                                                                   writable=True, readable=True, resolve_path=True),
              help="Config file to use or create")
@click.option("--prompt", default=False, is_flag=True, help="Ask before running on each configured repository")
@click.option("-v", "--verbose", default=False, is_flag=True)
def main(create, file, prompt, verbose):
    if type(file) is str:
        file = Path(file)
    if Path.exists(file):
        with open(str(file), 'r') as cfg:
            run(yaml.safe_load(cfg), prompt, verbose)
    elif create:
        config_path.mkdir(parents=True, exist_ok=True)
        with open(str(file), 'w') as cfg:
            print(f"Creating example config file at {file}")
            yaml.safe_dump({"definitions": [
                {"repository": "https://github.com...",
                 "sourceDir": ".",
                 "outDir": "c:\\Users\\mikep\\Desktop\\test",
                 "ignore": [".*/*"],
                 "noOverwrite": []
                 }
            ]}, cfg)


def run(config: Dict, prompt: bool, verbose=False):
    for definition in config["definitions"]:
        out_dir = Path(definition["outDir"]).absolute()
        if prompt:
            if not query_yes_no(f"Run for {definition['repository']} to write into {out_dir}?"):
                continue
        try:
            # Get temp dir
            temp_dir = Path(tempfile.mkdtemp())

            # Clone requested repo with no history
            print(f"Cloning repo {definition['repository']}" +
                  (f" branch: {definition['branch']}" if "branch" in definition else "") +
                  (f" to {temp_dir}" if verbose else ""))
            if "branch" in definition:
                git.Repo.clone_from(definition["repository"], temp_dir, depth=1, branch=definition["branch"])
            else:
                git.Repo.clone_from(definition["repository"], temp_dir, depth=1)

            src_dir = temp_dir.joinpath(Path(definition.get("sourceDir", ".")))

            def ignorer(path, is_dir=False):
                path = str(Path(path).as_posix())
                path = path[len(str(src_dir)) + 1:]
                if is_dir and path and path[-1] != "/":
                    path += "/"

                return any(fnmatch(path, pat) for pat in definition.get("ignore", []))

            def non_overwriter(path):
                path = str(Path(path).as_posix())
                path = path[len(str(src_dir)) + 1:]
                return any(fnmatch(path, pat) for pat in definition.get("noOverwrite", []))

            cp(str(src_dir), str(out_dir), ignore=ignorer, no_overwrite=non_overwriter, verbose=verbose)
        finally:
            try:
                if verbose:
                    print(f"Cleaning up temporary directory {str(temp_dir)}")
                shutil.rmtree(str(temp_dir))
            except PermissionError:
                if verbose:
                    print(f"Failed to delete temporary directory {str(temp_dir)}")

        print("Running post install scripts if any")
        for command in definition.get("postInstall", []):
            print(command)
            subprocess.Popen(command, cwd=str(out_dir), stdout=sys.stdout, stderr=sys.stderr, shell=True).wait()
        print("=" * 30)
        print()


def cp(src, dest, ignore, no_overwrite, verbose):
    for src_dir, dirs, files in os.walk(src):
        dst_dir = src_dir.replace(src, dest)
        if not os.path.exists(dst_dir) and not ignore(src_dir, True):
            Path(dst_dir).mkdir(parents=True, exist_ok=True)
        for file in files:
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            if not ignore(src_file):
                allowed_to_overwrite = not no_overwrite(src_file)
                if not os.path.exists(dst_file) or allowed_to_overwrite:
                    try:
                        shutil.copy2(src_file, dst_dir)
                    except PermissionError as e:
                        print(e)
                elif not allowed_to_overwrite and verbose:
                    print(f"Skipping because file exists and not allowed to overwrite {dst_file}")
            elif verbose:
                print(f"Ignoring {src_file}")


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


if __name__ == "__main__":
    main()
