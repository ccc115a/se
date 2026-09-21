	.file	"goto.c"
	.globl	_x
	.data
	.align 4
_x:
	.long	3
	.text
	.globl	_test
	.def	_test;	.scl	2;	.type	32;	.endef
_test:
	pushl	%ebp
	movl	%esp, %ebp
	movl	_x, %eax
	cmpl	$4, %eax
	jle	L5
	movl	$100, _x
	jmp	L3
L5:
	nop
L3:
	nop
	popl	%ebp
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
