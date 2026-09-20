.syntax unified
.thumb

.macro JUMP_ABS addr
    push {r4}
    ldr r4, =\addr
    mov lr, r4
    pop {r4}
    bx lr
.endm

.global morpeko_endturn_entry
.type morpeko_endturn_entry,%function
.thumb_func
morpeko_endturn_entry:
    push {r4}
    bl morpeko_endturn_bridge
    pop {r4}
    JUMP_ABS 0x080406C9
.size morpeko_endturn_entry, .-morpeko_endturn_entry

.global morpeko_switch_entry
.type morpeko_switch_entry,%function
.thumb_func
morpeko_switch_entry:
    push {r4}
    bl morpeko_reset_switch
    pop {r4}

    @ Replay overwritten HandleAction_Switch instructions at 0x0803E4B8.
    ldr r0, =0x02022AC8
    movs r2, #0
    strh r2, [r0]
    ldr r0, =0x02022ACA
    ldr r3, =0x02023EAF
    JUMP_ABS 0x0803E4C1
.size morpeko_switch_entry, .-morpeko_switch_entry
