.syntax unified
.thumb

.macro JUMP_ABS addr
    push {r4}
    ldr r4, =\addr
    mov lr, r4
    pop {r4}
    bx lr
.endm

.global arceus_move_entry
.type arceus_move_entry,%function
.thumb_func
arceus_move_entry:
    push {r4}
    bl arceus_move_prepare_helper
    pop {r4}
    @ Replay BPEJ 0x08045DAC..0x08045DB3
    ldr r2, =0x02023FE0
    ldr r1, =0x02023EB0
    ldrb r3, [r1]
    lsls r0, r3, #4
    JUMP_ABS 0x08045DB5
.size arceus_move_entry, .-arceus_move_entry
