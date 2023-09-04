	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_foo                            ; -- Begin function foo
	.p2align	2
_foo:                                   ; @foo
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #16
	.cfi_def_cfa_offset 16
	str	w0, [sp, #12]
	str	x1, [sp]
	ldrsw	x8, [sp, #12]
	ldr	x9, [sp]
	add	x8, x8, x9
	mov	x0, x8
	add	sp, sp, #16
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_bar                            ; -- Begin function bar
	.p2align	2
_bar:                                   ; @bar
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #16
	.cfi_def_cfa_offset 16
	str	w0, [sp, #12]
	str	x1, [sp]
	ldrsw	x8, [sp, #12]
	ldr	x9, [sp]
	add	x8, x8, x9
	mov	x0, x8
	add	sp, sp, #16
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols
