
# overlay_demo

----

This project provides demonstration of using overlays.
As the example used embedded RISC-V.

Project contains simple target overlay-manager ovlymgr.cpp (similar to the example from /gdb/testsuite/gdb.base).  
GDB supports overlay debugging (GDB-doc: 14. Debugging Programs That Use Overlays).
In addition, this project contains custom instruments (GDB-commands implemented with Python-GDB-API) for working with overlays.  
These ideas can be used in full-size project that uses overlays.
Details in the Wiki.


### Custom GDB-commands for working with overlays

* 'ovreplace ovlymgr_name' - class ReplaceOverlayManager(gdb.Command):    Replace target overlay-manager mode.
* 'ovload ovlyno' - class OverlayLoadManually(gdb.Command):   Load specified overlay manually.
* 'getmapped' - class GetNumMappedOverlay(gdb.Command):   Print numbers of mapped overlays.


### Quick start

Get project:

        $ git clone ...
        $ cd overlay_demo
        $ git submodule update --init --recursive

Set actual paths in file '/overlay_demo/paths'.

Build project:

        make

There are two launch configurations for demonstration (setting in file '/overlay_demo/paths'):

        GDB_SCRIPT="../gdb-py/gdb_launch.py"   =>  Launch with target overlay-manager (part of C++ program)
        GDB_SCRIPT="../gdb-py/gdb_ovmgr_replace.py"    =>   Launch in replace target overlay-manager mode

Launch with hardware:

        cd ./launch-sh/
        ./openocd_gdb_launch.sh ../Debug/overlay_demo.elf

Launch with Spike:

        cd ./launch-sh/
        ./spike_openocd_gdb_launch.sh ../Debug/overlay_demo.elf

Example of using custom GDB-commands 'ovload ovlyno' and 'getmapped':

        (gdb) ovload 0
        section_name = .ovly0; lma = 0x10080400; size = 0x44
        Restoring binary file /home/user/workspace/overlay_demo/Debug/overlay_demo.elf into memory (0x10000060 to 0x100000a4)
        (gdb) getmapped
        Overlay #0 is mapped

----
