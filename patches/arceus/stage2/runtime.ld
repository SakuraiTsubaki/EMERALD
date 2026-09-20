ENTRY(arceus_move_entry)
SECTIONS
{
  . = 0x0891C000;
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.ARM.attributes*) *(.note*) }
}
