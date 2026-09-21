.syntax unified
.thumb

.macro JUMP_ABS addr
    push {r4}
    ldr r4, =\addr
    mov lr, r4
    pop {r4}
    bx lr
.endm

.global stance_entry
.type stance_entry,%function
.thumb_func
stance_entry:
    push {r4}
    bl stance_helper
    pop {r4}
    ldr r2, =0x02023FE0
    ldr r1, =0x02023EB0
    ldrb r3, [r1]
    lsls r0, r3, #4
    JUMP_ABS 0x08045DB5
.size stance_entry, .-stance_entry

.global ks_filter_entry
.type ks_filter_entry,%function
.thumb_func
ks_filter_entry:
    push {r4}
    bl ks_should_bypass
    pop {r4}
    cmp r0, #0
    bne 1f
    ldr r0, =0x02023E8E
    ldrh r3, [r0]
    cmp r3, #174
    bne 2f
    ldr r2, =0x02023D28
    ldr r0, =0x02023EAF
    JUMP_ABS 0x08045EF9
1:
    JUMP_ABS 0x08045FD1
2:
    JUMP_ABS 0x08045F15
.size ks_filter_entry, .-ks_filter_entry

.global ks_penalty_entry
.type ks_penalty_entry,%function
.thumb_func
ks_penalty_entry:
    push {r4}
    bl ks_contact_penalty
    pop {r4}

    @ Hooked after CancelMultiTurnMoves in the confirmed
    @ DEFENDER_IS_PROTECTED block. Replay the overwritten
    @ gMoveResultFlags |= MOVE_RESULT_MISSED setup, then resume.
    ldr r2, =0x02023F20
    ldrb r0, [r2]
    movs r1, #1
    orrs r0, r1
    JUMP_ABS 0x08045F4B

    @ Keep protect_chain_entry at its original runtime address
    @ 0x08917075 so the existing fourth trampoline remains valid.
    nop
    nop
    nop
    nop
    nop
.size ks_penalty_entry, .-ks_penalty_entry

.global protect_chain_entry
.type protect_chain_entry,%function
.thumb_func
protect_chain_entry:
    cmp r0, #182
    beq 1f
    cmp r0, #197
    beq 1f
    ldr r1, =354
    cmp r0, r1
    beq 1f
    JUMP_ABS 0x0804F9B9
1:
    JUMP_ABS 0x0804F9C9
.size protect_chain_entry, .-protect_chain_entry
