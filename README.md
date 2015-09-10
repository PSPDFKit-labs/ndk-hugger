# ndk-hugger
Alternative GDB server setup script to ndk-gdb.

## Installation

```
python setup.py install
```

## Usage

```
nhgr <package name> <native library .so name> <architecture>
```

examples:

```
nhgr com.pspdfkit.pspdfcatalog libpspdfkit.so x86
```

The script should be run from the directory of the project that contains `libs` and `obj` directories. If those directories were renamed, use `--libs` to set new libs directory name, and `--obj` to set new object file directory name.
