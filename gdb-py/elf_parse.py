
#Elf: lma address of section:
#Elf section headers don't contains LMA of sections, however 'objdump -h' shows its LMA.
#Elf segments headrs(== phdr) contains physical address (LMA) of segments. But elf don't contains the mapping (correspondence between segments and sections).

#https://stackoverflow.com/questions/23018496/where-is-the-section-to-segment-mapping-stored-in-elf-files
#    Readelf compute the mapping by looking at file offset and size of sections and segments.

#Objdump (source of binutils): /riscv-binutils-gdb/bfd/elf.c:
#    section_lma = p_paddr + sh_offset - p_offset


#Problem with import mudule 'struct' in gdb-py:
#    from _struct import *
#    ImportError: .../riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/python/lib/python3.7/lib-dynload/_struct.cpython-37m-x86_64-linux-gnu.so: undefined symbol: PyByteArray_Type
#About this problem:
#    https://github.com/sifive/freedom-tools/issues/71
#    https://github.com/vim/vim/issues/3629


'''
typedef uint16_t Elf64_Half;
typedef uint32_t Elf64_Word;
typedef uint64_t Elf64_Addr;
typedef uint64_t Elf64_Off;
typedef uint16_t Elf64_Section;
typedef uint64_t Elf64_Xword;

#define EI_NIDENT (16)

typedef struct
{
  unsigned char	e_ident[EI_NIDENT];	/* Magic number and other info */
  Elf64_Half	e_type;			/* Object file type */
  Elf64_Half	e_machine;		/* Architecture */
  Elf64_Word	e_version;		/* Object file version */
  Elf64_Addr	e_entry;		/* Entry point virtual address */
  Elf64_Off	    e_phoff;		/* Program header table file offset */
  Elf64_Off	    e_shoff;		/* Section header table file offset */
  Elf64_Word	e_flags;		/* Processor-specific flags */
  Elf64_Half	e_ehsize;		/* ELF header size in bytes */
  Elf64_Half	e_phentsize;	/* Program header table entry size */
  Elf64_Half	e_phnum;		/* Program header table entry count */
  Elf64_Half	e_shentsize;	/* Section header table entry size */
  Elf64_Half	e_shnum;		/* Section header table entry count */
  Elf64_Half	e_shstrndx;		/* Section header string table index: Index of section header of .shstrtab in shdr table */
} Elf64_Ehdr;

typedef struct
{
  Elf64_Word	p_type;			/* Segment type */
  Elf64_Word	p_flags;		/* Segment flags */
  Elf64_Off	    p_offset;		/* Segment file offset */
  Elf64_Addr	p_vaddr;		/* Segment virtual address */
  Elf64_Addr	p_paddr;		/* Segment physical address */
  Elf64_Xword	p_filesz;		/* Segment size in file */
  Elf64_Xword	p_memsz;		/* Segment size in memory */
  Elf64_Xword	p_align;		/* Segment alignment */
} Elf64_Phdr;

typedef struct
{
  Elf64_Word	sh_name;		/* Section name (string tbl index) */
  Elf64_Word	sh_type;		/* Section type */
  Elf64_Xword	sh_flags;		/* Section flags */
  Elf64_Addr	sh_addr;		/* Section virtual addr at execution */
  Elf64_Off	    sh_offset;		/* Section file offset */
  Elf64_Xword	sh_size;		/* Section size in bytes */
  Elf64_Word	sh_link;		/* Link to another section */
  Elf64_Word	sh_info;		/* Additional section information */
  Elf64_Xword	sh_addralign;	/* Section alignment */
  Elf64_Xword	sh_entsize;		/* Entry size if section holds table */
} Elf64_Shdr;
'''

import sys

def parse_elf(path, arg_lma):
    '''Returns (section_name, sh_offset, sh_size) of section by its LMA.'''

    #elf header
    with open(path, 'rb') as f:
        ehdr = f.read(64)

    #fields of elf header
    e_ident = ehdr[0:16]
    #...
    e_phoff = int.from_bytes(ehdr[32:40], 'little')
    e_shoff = int.from_bytes(ehdr[40:48], 'little')
    #...
    e_phentsize = int.from_bytes(ehdr[54:56], 'little')
    e_phnum = int.from_bytes(ehdr[56:58], 'little')
    e_shentsize = int.from_bytes(ehdr[58:60], 'little')
    e_shnum = int.from_bytes(ehdr[60:62], 'little')
    e_shstrndx = int.from_bytes(ehdr[62:64], 'little')

    segments = []
    with open(path, 'rb') as f:
        f.seek(e_phoff)
        for i in range(e_phnum):
            phdr = f.read(e_phentsize)
            p_offset = int.from_bytes(phdr[8:16], 'little')
            p_vaddr = int.from_bytes(phdr[16:24], 'little')
            p_paddr = int.from_bytes(phdr[24:32], 'little')
            p_filesz = int.from_bytes(phdr[32:40], 'little')
            segments.append((p_offset, p_vaddr, p_paddr, p_filesz))
#            segments.append((hex(p_offset), hex(p_vaddr), hex(p_paddr), hex(p_filesz)))
#    print(segments)

    #section names (.shstrtab)
    with open(path, 'rb') as f:
        f.seek(e_shoff + e_shstrndx * e_shentsize)
        shstrtab_shdr = f.read(e_shentsize) #shdr of .shstrtab
        shstrtab_sh_name = int.from_bytes(shstrtab_shdr[0:4], 'little')
        shstrtab_sh_addr = int.from_bytes(shstrtab_shdr[16:24], 'little')
        shstrtab_sh_offset = int.from_bytes(shstrtab_shdr[24:32], 'little')
        shstrtab_sh_size = int.from_bytes(shstrtab_shdr[32:40], 'little')
        f.seek(shstrtab_sh_offset)
        shstrtab = f.read(shstrtab_sh_size)

    sections = []
    with open(path, 'rb') as f:
        f.seek(e_shoff)
        for i in range(e_shnum): #first shdr = 0
            shdr = f.read(e_shentsize)
            sh_name = int.from_bytes(shdr[0:4], 'little')
            sh_addr = int.from_bytes(shdr[16:24], 'little')
            sh_offset = int.from_bytes(shdr[24:32], 'little')
            sh_size = int.from_bytes(shdr[32:40], 'little')
            section_name = shstrtab[sh_name:].split(b'\x00', 1)[0].decode('utf-8')
            section_lma = sh_addr
            for j in range(e_phnum):
                if sh_addr != 0: #ignore auxiliary sections
                    #if p_vaddr != p_paddr
                    if segments[j][1] != segments[j][2]:
                        #if p_offset <= sh_offset <= (p_offset + p_filesz)
                        if segments[j][0] <= sh_offset <= (segments[j][0] + segments[j][3]):
                            #section_lma = p_paddr + sh_offset - p_offset
                            section_lma = segments[j][2] + sh_offset - segments[j][0]

            sections.append((section_name, sh_addr, sh_offset, sh_size, section_lma))
#            sections.append((section_name, hex(sh_addr), hex(sh_offset), hex(sh_size), hex(section_lma)))
#    print(sections)

    #find section with specified lma (section_lma == arg_lma)
    found_sect = [sect for sect in sections if sect[4] == arg_lma]

    return(found_sect[0][0], found_sect[0][2], found_sect[0][3]) #(section_name, sh_offset, sh_size)


def main():
    elf_path = sys.argv[1]
    print(elf_path)

    #test
    (section_name, sh_offset, sh_size) = parse_elf(elf_path, 0x10080400) #0x10080400 ; 0x10080444
    print(section_name, hex(sh_offset), hex(sh_size)) #(.ovly0, 0x2060, 0x44); (.ovly1, 0x3060, 0x18c)


if __name__ == "__main__":
	main()
