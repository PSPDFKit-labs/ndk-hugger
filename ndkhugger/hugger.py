#!/usr/bin/env python2
import click
import subprocess
import os
import sys

from utilities import get_ndk_toolchain_path_or_fail

def push_gdb_server(gdbserver_path):
    click.secho("Pushing GDB server to device...", fg="yellow")
    subprocess.check_call(["adb", "push", gdbserver_path, "/data/local/tmp/gdbserver"])

def get_pids_from_device():     
    adb_proc = subprocess.Popen(['adb', 'shell', 'ps'], stdout=subprocess.PIPE)
    pids = {}

    while True:
      line = adb_proc.stdout.readline().strip()
      if line != '':
        # Take into account only lines with 9 items
        split_line = line.split()
        if len(split_line) != 9: continue

        try:
            pid = int(split_line[1])
            package = split_line[8]
        except ValueError as e:
            continue

        pids[package] = pid
      else:
        break

    return pids

def attach_gdb_to_process(pid, port):
    click.secho("Attaching GDBserver to {}...".format(pid), fg="yellow")
    subprocess.Popen(['adb', 'shell', '/data/local/tmp/gdbserver', ':' + str(port), '--attach', str(pid)], stdout=subprocess.PIPE)

def forward_adb_socket(port):
    click.secho("Forwarding ADB socket...", fg="yellow")
    subprocess.Popen(['adb', 'forward', 'tcp:' + str(port), 'tcp:' + str(port)])

gdb_paths = { 'armeabi': 'arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-gdb', \
              'x86': 'x86-4.9/prebuilt/darwin-x86_64/bin/i686-linux-android-gdb', \
              'arm64-v8a': 'aarch64-linux-android-4.9/prebuilt/darwin-x86_64/bin/aarch64-linux-android-gdb'}

# Add some aliases
gdb_paths["armeabi-v7a"] = gdb_paths["armeabi"]
gdb_paths["armeabi-v7a-hard"] = gdb_paths["armeabi"]

@click.command()
@click.option("--libs", default="libs")
@click.option("--obj", default="obj")
@click.option("--port", default=5055)
@click.argument("package")
@click.argument("soname")
@click.argument("arch")
def run(libs, obj, arch, soname, package, port):
    toolchain_path = get_ndk_toolchain_path_or_fail()

    gdbserver_path = os.path.realpath(os.path.join(libs, arch, "gdbserver")) 
    # Check for gdbserver path
    if not os.path.exists(gdbserver_path):
        click.secho("Could not find gdbserver binary in {}, did you forget to set --libs or NDK_DEBUG=1?".format(gdbserver_path), fg="red")
        sys.exit(-3)

    sofile_path = os.path.realpath(os.path.join(obj, "local", arch, soname))
    if not os.path.exists(sofile_path):
        click.secho("Could not find debuggable .so file in {}, did you forget to set --obj or wrong arch?".format(sofile_path), fg="red")
        sys.exit(-4)        

    gdb_path = os.path.join(toolchain_path, gdb_paths[arch])
    if not os.path.exists(gdb_path):
        click.secho("Could not find NDK gdb executable in {}, perhaps aliases have to be updated?".format(gdb_path))
        sys.exit(-5)

    # Figure out what PID the process has
    pids = get_pids_from_device()
    process_pid = None
    if package in pids:
        process_pid = pids[package]
        click.secho("Process PID for {} is {}.".format(package, process_pid), fg="yellow")
    else:
        click.secho("Could not find PID for package {}.".format(package), fg='red')
        sys.exit(-1)

    click.echo("==========")
    click.echo("[gdb] {}".format(gdb_path))
    click.echo("[gdbserver] {}".format(gdbserver_path))
    click.echo("[.so library] {}".format(sofile_path))
    click.echo("[PID] {}  [Port] {}".format(process_pid, port))
    click.echo("==========")

    # Push GDB server binary to server
    push_gdb_server(gdbserver_path)
    attach_gdb_to_process(process_pid, port)
    forward_adb_socket(port)

    # Now start GDB
    file_command = "file {}".format(sofile_path)
    gdb_call = "{} -ix {} -ex \"{}\" -ex \"{}\"".format(gdb_path, os.path.join(libs, arch, "gdb.setup"), file_command, "target remote :" + str(port))

    click.secho("Things look good, firing up GDB....", fg="green")
    os.system(gdb_call)

if __name__ == "__main__":
    run()