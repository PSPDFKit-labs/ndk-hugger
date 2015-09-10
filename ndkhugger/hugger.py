#!/usr/bin/env python2
import click
import subprocess
import os
import sys

def push_gdb_server(gdbserver_path):
    click.echo("Pushing GDB server to device...")
    click.echo(gdbserver_path)
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

def attach_gdb_to_process(pid):
    click.echo("Attaching GDBserver to {}...".format(pid))
    subprocess.Popen(['adb', 'shell', '/data/local/tmp/gdbserver', ':5055', '--attach', str(pid)], stdout=subprocess.PIPE)

def forward_adb_socket():
    click.echo("Forwarding ADB socket...")
    subprocess.Popen(['adb', 'forward', 'tcp:5055', 'tcp:5055'])

gdb_paths = { 'armeabi': 'arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-gdb', \
              'x86': 'x86-4.9/prebuilt/darwin-x86_64/bin/i686-linux-android-gdb', \
              'arm64-v8a': 'aarch64-linux-android-4.9/prebuilt/darwin-x86_64/bin/aarch64-linux-android-gdb'}

# Add some aliases
gdb_paths["armeabi-v7a"] = gdb_paths["armeabi"]
gdb_paths["armeabi-v7a-hard"] = gdb_paths["armeabi"]

@click.command()
@click.option("--libs", default="libs")
@click.option("--obj", default="obj")
@click.argument("package")
@click.argument("soname")
@click.argument("arch")
def run(libs, obj, arch, soname, package):
    arch = "x86"
    package = "com.pspdfkit.pspdfcatalog"
    toolchain_path = "/Users/jernej/Development/android-ndk/toolchains"
    # Push GDB server binary to server
    push_gdb_server(os.path.join(libs, arch, "gdbserver"))

    # Figure out what PID the process has
    pids = get_pids_from_device()
    process_pid = None
    if package in pids:
        process_pid = pids[package]
        click.echo("Process PID for {} is {}.".format(package, process_pid))
    else:
        click.secho("Could not find PID for package {}.".format(package), fg='red')
        sys.exit(-1)

    attach_gdb_to_process(process_pid)
    forward_adb_socket()

    # Now start GDB
    gdb_path = os.path.join(toolchain_path, gdb_paths[arch])
    file_command = "file {}".format(os.path.join(obj, "local", arch, soname))

    click.echo("Starting GDB from {}....".format(gdb_path))
    gdb_call = "{} -ix {} -ex \"{}\" -ex \"{}\"".format(gdb_path, os.path.join(libs, arch, "gdb.setup"), file_command, "target remote :5055")
    click.echo("GDB call: " + gdb_call)
    os.system(gdb_call)


if __name__ == "__main__":
    run()