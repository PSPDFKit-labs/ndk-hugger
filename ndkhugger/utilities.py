import os
import click
import sys

def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def get_ndk_toolchain_path_or_fail():
    ndk_build_path = which('ndk-build')
    if ndk_build_path is None:
        click.secho("Could not find ndk-build in path, please add it.", fg="red")
        sys.exit(-2)

    path,filename = os.path.split(ndk_build_path)
    return os.path.join(path, "toolchains")