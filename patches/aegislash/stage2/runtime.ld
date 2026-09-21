ENTRY(stance_entry)
SECTIONS
{
  . = 0x08917000;
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.ARM.attributes*) *(.note*) }
}
