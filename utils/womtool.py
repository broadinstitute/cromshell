#!/usr/bin/env python
# handy utility to download and wrap womtool

import os
import sys
import subprocess
from requests import get
from shutil import which
from pathlib import Path

DefaultCacheDir = Path.home().joinpath('.config', 'womtool')

def get_womtool_jarpath(cache_dir=None, version=78):
    if cache_dir is None:
        cache_dir = DefaultCacheDir
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    target_path = cache_dir.joinpath('womtool.jar')
    if not target_path.exists():
        release_url = f'https://github.com/broadinstitute/cromwell/releases/download/{version}/womtool-{version}.jar'
        with get(release_url) as remote_fh:
            with open(target_path, 'wb') as local_fh:
                local_fh.write(remote_fh.content)
    return str(target_path)

def get_womtool_cmd():
    # is womtool available as a command?
    womtool_path = which('womtool')
    if womtool_path is not None:
        cmd = [womtool_path]
    else:
        # best effort
        java_path = which('java') or 'java'
        # is the jar where we expect?
        jar_path = get_womtool_jarpath()
        cmd = [java_path, '-jar', jar_path]
    return cmd

def main():
    cmd = get_womtool_cmd()
    cmd += sys.argv[1:]
    os.execv(cmd[0], cmd)

if __name__ == "__main__":
    main()
