import gdb
import os.path

sys.path.append('../')   # For import /modules/
from modules.gdb_connection import BeginSession
from modules.gdb_connection import Shutdown
from modules.gdb_connection import Output

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ovlymgr_imit import OverlayLoadManually
from ovlymgr_imit import ReplaceOverlayManager
from ovlymgr_imit import GetNumMappedOverlay

def main():
    print(f'GDB-client version = {gdb.VERSION}\n')

    # Elf-file taken as argument of gdb-client
    elf = gdb.objfiles()[0]
    if elf == None:
        raise gdb.GdbError('Elf-file is not found.')
    elf = elf.filename
    print(f'Elf-file = {elf}\n')

    # Preparing:
    BeginSession.invoke(elf, False) # CLI: (gdb) begin <path-to-elf>
    # State: stop at _start

    # Breakpoint on trap for exception/interrupt
    gdb.Breakpoint('trap')

    # Start execution:
    gdb.Breakpoint('main')
    gdb.execute('continue')
    # State: stop at main()

    gdb.execute('set verbose on')
    gdb.execute('overlay auto')

    gdb.execute('overlay list')
    GetNumMappedOverlay.invoke('', False) # CLI: (gdb) getmapped

    ReplaceOverlayManager.invoke('OverlayLoad', False) # CLI: (gdb) ovreplace OverlayLoad

    gdb.Breakpoint('35')
    gdb.execute('continue')
    # State: stop at end of main()

    gdb.execute('overlay list')
    GetNumMappedOverlay.invoke('', False) # CLI: (gdb) getmapped

    print('_ovly_table = ')
    gdb.execute('print/x *_ovly_table@2')

    print(f"\nisErr = {gdb.parse_and_eval('isErr')}")

    # Output text message to GDB-console:
    if gdb.parse_and_eval('isErr') == False:
        Output.invoke('Ok: Result is Ok!', False)
    else:
        Output.invoke('Err: Result is Failure!', False)

    # End:
    print('\n')
    Output.invoke(f'Info: {" End of python-GDB-script ":*^80}', False)
    Shutdown.invoke('', False)  # CLI: (gdb) shutdown


if __name__ == "__main__":
	main()
