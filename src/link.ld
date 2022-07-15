OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
  RAM_MEM 				: ORIGIN = 0x10000000, LENGTH = 0x7FFFF
  OVERLAY_AREA			: ORIGIN = 0x10080400, LENGTH = 0x1FFF
}

SECTIONS
{
 .init :
{
  KEEP (*(SORT_NONE(.init)))
} >RAM_MEM

  OVERLAY ALIGN(8) : NOCROSSREFS
  {
    .ovly0 { *foobar.o(.text .text.* .data .data.* .sdata .sdata.*) }
    .ovly1 { *demo_class.o(.text .text.* .data .data.* .sdata .sdata.*) }
  } >RAM_MEM AT>OVERLAY_AREA

.text ALIGN(8) :
{
  *(.text)
} >RAM_MEM

.interrupt_handler ALIGN(8) :
{
  *(.interrupt_handler)
} >RAM_MEM

.data ALIGN(8) :
{
    *(.rodata)
    *(.data)
    . = ALIGN(8);
    PROVIDE(__global_pointer$ = . + 0x800);
    . = ALIGN(8);
    *(.sdata)
    *(.srodata)

    . = ALIGN(8);
    _ovly_table = .;	    
	    QUAD(ABSOLUTE(ADDR(.ovly0)));
	    QUAD(SIZEOF(.ovly0));
	    QUAD(LOADADDR(.ovly0));
	    QUAD(0);

	    QUAD(ABSOLUTE(ADDR(.ovly1)));
	    QUAD(SIZEOF(.ovly1));
	    QUAD(LOADADDR(.ovly1));
        QUAD(0);
    _novlys = .; LONG((_novlys - _ovly_table) / 32);

} >RAM_MEM
PROVIDE(_edata = .);
PROVIDE(edata = .);

.preinit_array ALIGN(8) :
{
  PROVIDE_HIDDEN (__preinit_array_start = .);
  KEEP (*(.preinit_array))
  PROVIDE_HIDDEN (__preinit_array_end = .);
} >RAM_MEM

.init_array ALIGN(8) :
{
  PROVIDE_HIDDEN (__init_array_start = .);
  KEEP (*(SORT_BY_INIT_PRIORITY(.init_array.*) SORT_BY_INIT_PRIORITY(.ctors.*)))
  KEEP (*(.init_array EXCLUDE_FILE (*crtbegin.o *crtbegin?.o *crtend.o *crtend?.o ) .ctors))
  PROVIDE_HIDDEN (__init_array_end = .);
} >RAM_MEM

PROVIDE(__bss_start = .);
.bss ALIGN(8) :
{
  *(.sbss)
  *(.sbss.*)
  *(.bss)
  *(.bss.*)
  *(COMMON)
} >RAM_MEM
PROVIDE(__bss_end = .);

  PROVIDE(exit = .);
  PROVIDE(_exit = exit);

  PROVIDE(_end = .);
  PROVIDE(end = .);

  PROVIDE(_sp = 0x10080000);  /*stack*/
}
