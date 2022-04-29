import gdb
from elf_parse import parse_elf

class Field():
    '''Fields of _ovly_table'''
    VMA = 0
    SIZE = 1
    LMA = 2
    MAPPED = 3
#********************************************************************************

class ReplaceOverlayManager(gdb.Command):
    '''Enable replace target overlay-manager mode.
    Each call of specified target overlay manager will be replaced with this imitation of overlay manager.
    This imitation of overlay manager takes overlay-section directly from elf.
    usage:
    ovreplace target_overlay_manager_name'''
    ovly_mgr_name = ''

    def __init__(self):
        super(ReplaceOverlayManager, self).__init__("ovreplace", gdb.COMMAND_USER)

    @classmethod
    def get_ovly_table(cls, ovlyno):
        '''Get overlay section from elf.'''
#        print('get_ov_sect_from_elf :') #
        novlys = gdb.parse_and_eval('_novlys')
        if (ovlyno < 0) or (ovlyno > novlys-1):
            raise gdb.GdbError('Argument "ovlyno" must be in 0.._novlys-1.')

        ovly_table = gdb.parse_and_eval(f'*_ovly_table@{novlys}')
#        print(f'_novlys = {novlys}') #
#        print(f'_ovly_table = {ovly_table}') #
#        print(f'_ovly_table[0] = {hex(ovly_table[0][0])}, {hex(ovly_table[0][1])}, {hex(ovly_table[0][2])}, {hex    (ovly_table[0][3])}') #
#        print(f'_ovly_table[1] = {hex(ovly_table[1][0])}, {hex(ovly_table[1][1])}, {hex(ovly_table[1][2])}, {hex(ovly_table[1][3])}') #

#        print(f' {hex(ovly_table[ovlyno][Field.VMA])}, {hex(ovly_table[ovlyno][Field.SIZE])}, {hex(ovly_table[ovlyno][Field.LMA])}, {hex(ovly_table[ovlyno][Field.MAPPED])}') #

        return (ovly_table[ovlyno][Field.VMA], ovly_table[ovlyno][Field.SIZE], ovly_table[ovlyno][Field.LMA], ovly_table[ovlyno][Field.MAPPED])

    @classmethod
    def set_ovly_mapped(cls, ovlyno, section_name):
        '''Set overlay mapped flags.'''
        novlys = gdb.parse_and_eval('_novlys')
        if (ovlyno < 0) or (ovlyno > novlys-1):
            raise gdb.GdbError('Argument "ovlyno" must be in 0.._novlys-1.')

        #Field _ovly_table[ovlyno][MAPPED]:
        #_ovly_table[ovlyno][MAPPED] = 1: mapped overlay № ovlyno
        #_ovly_table[ecxept ovlyno][MAPPED] = 0: unmapped all overlays except № ovlyno (according to OverlayLoad(...))
        for i in range(novlys):
            if i == ovlyno:
                gdb.parse_and_eval(f'*(*(_ovly_table + {i}) + {Field.MAPPED}) = 1')
            else:
                gdb.parse_and_eval(f'*(*(_ovly_table + {i}) + {Field.MAPPED}) = 0')

        #Mapped status for GDB-client:
        #Map current overlay (by name of overlay section)
        #Unmap all overlays except current #?
        #gdb.execute(f'overlay map {section_name}') #?
        #gdb.execute(f'overlay unmap {...}') #?

    @classmethod
    def stop_event_handler(cls, bp_event):
#        print('\nstop event handler:') #
#        print(bp_event.breakpoints[0].number) #
#        print(bp_event.breakpoints[0].location) #

        #If stop on breakpoint event is gdb.BreakpointEvent
        #If stop by step event is gdb.StopEvent. Which has not attribute 'breakpoints'
        if isinstance(bp_event, gdb.BreakpointEvent):
            if(bp_event.breakpoints[0].location == ReplaceOverlayManager.ovly_mgr_name):
#                print('ok')             #Убрать
#                gdb.execute('frame')    #Убрать
                for sym in gdb.selected_frame().block(): #get ovlyno argument symbol
                    if sym.is_argument:
                        ovlyno_arg = sym
                ovlyno = int(gdb.parse_and_eval(str(ovlyno_arg)))
                print(f'Overlay #{ovlyno}')
                (s_vma, s_size, s_lma, s_mapped) = ReplaceOverlayManager.get_ovly_table(ovlyno)
                if s_mapped:
                    print(f'Overlay #{ovlyno} is already mapped')
                    gdb.execute('continue')
                    return
                elf = gdb.objfiles()[0].filename
                (section_name, sh_offset, sh_size) = parse_elf(elf, s_lma)
                print(f'section_name = {section_name}; lma = {hex(s_lma)}; size = {hex(sh_size)}')
                gdb.execute(f'restore {elf} binary {s_vma - sh_offset} {sh_offset} {sh_offset + sh_size}')
                ReplaceOverlayManager.set_ovly_mapped(ovlyno, section_name)
                gdb.execute('jump overstep_ovly_load') #includes continue

    @classmethod
    def invoke(cls, argument, from_tty):
        argv = gdb.string_to_argv(argument)
        len_argv = len(argv)
        if len_argv != 1:
            raise gdb.GdbError('Command "ovreplace" takes 1 argument. Try "help ovreplace".')
        ReplaceOverlayManager.ovly_mgr_name = argv[0]

        gdb.events.stop.connect(ReplaceOverlayManager.stop_event_handler)

        bp = gdb.Breakpoint(ReplaceOverlayManager.ovly_mgr_name)
        bp.silent = True

ReplaceOverlayManager()
#********************************************************************************

class OverlayLoadManually(gdb.Command):
    '''Load specified overlay manually.
    May be used as replacement of target overlay manager if it is absent.
    usage:
    ovload ovlyno'''

    def __init__(self):
        super(OverlayLoadManually, self).__init__("ovload", gdb.COMMAND_USER)

    @classmethod
    def invoke(cls, argument, from_tty):
        argv = gdb.string_to_argv(argument)
        len_argv = len(argv)
        if len_argv != 1:
            raise gdb.GdbError('Command "ovload" takes 1 argument. Try "help ovload".')
        ovlyno = int(argv[0])

        (s_vma, s_size, s_lma, s_mapped) = ReplaceOverlayManager.get_ovly_table(ovlyno)
        elf = gdb.objfiles()[0].filename
        (section_name, sh_offset, sh_size) = parse_elf(elf, s_lma)
        print(f'section_name = {section_name}; lma = {hex(s_lma)}; size = {hex(sh_size)}')
        gdb.execute(f'restore {elf} binary {s_vma - sh_offset} {sh_offset} {sh_offset + sh_size}')
        ReplaceOverlayManager.set_ovly_mapped(ovlyno, section_name)
        gdb.parse_and_eval('FlushCache()')

OverlayLoadManually()
#********************************************************************************

class GetNumMappedOverlay(gdb.Command):
    '''Print numbers of mapped overlays.
    This command is similar to "overlay list".
    usage:
    getmapped'''

    def __init__(self):
        super(GetNumMappedOverlay, self).__init__("getmapped", gdb.COMMAND_USER)

    @classmethod
    def invoke(cls, argument, from_tty):
        argv = gdb.string_to_argv(argument)
        len_argv = len(argv)
        if len_argv != 0:
            raise gdb.GdbError('Command "getmapped" takes no arguments. Try "help getmapped".')

        novlys = gdb.parse_and_eval('_novlys')
        ovly_table = gdb.parse_and_eval(f'*_ovly_table@{novlys}')
        no_mapped = True
        for i in range(novlys):
            if ovly_table[i][Field.MAPPED]:
                no_mapped = False
                print(f'Overlay #{i} is mapped\n')
        if no_mapped:
            print('No mapped overlays\n')

GetNumMappedOverlay()
#********************************************************************************
#********************************************************************************

class EntryOvMgrBreakpoint(gdb.Breakpoint):
    '''Breakpoint on entry of overlay manager for overstep its body.'''

    def __init__(self, *arg):
        super().__init__(*arg)
        self.silent = True
        self.flag = True        ##

    def stop(self):
        print('stop at overlay manager:')
        print(f'return T')
        return True

'''
    def stop(self):
        print('stop at overlay manager')
        if self.flag == True:
            print('pre call stop()')
            self.flag = False
            self.stop() #exit with True
            gdb.execute('frame')    #Dont work!
#            gdb.execute('jump overstep_ovly_load')   #Dont work (not stopped)!
            #'overstep_ovly_load' - label in OverlayLoad(ovlyno) before call FlushCache();
            #Load overlay section from elf
            self.flag = True    #for next call
            print('return F')
            return False    #continue execution
        else:
            print(f'return T')
            return True
'''
#********************************************************************************
