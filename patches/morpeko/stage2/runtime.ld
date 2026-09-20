SECTIONS
{
    . = 0x0891B000;
    .text : {
        *(.text*)
        *(.rodata*)
    }
    /DISCARD/ : {
        *(.comment*)
        *(.ARM.attributes*)
        *(.eh_frame*)
    }
}
