	.file	"jumpTable.c"
	.globl	_R
	.bss
	.align 4
_R:
	.space 4
	.text
	.globl	_f0
	.def	_f0;	.scl	2;	.type	32;	.endef
_f0:
	pushl	%ebp
	movl	%esp, %ebp
	movl	$0, _R
	nop
	popl	%ebp
	ret
	.globl	_f1
	.def	_f1;	.scl	2;	.type	32;	.endef
_f1:
	pushl	%ebp
	movl	%esp, %ebp
	movl	$1, _R
	nop
	popl	%ebp
	ret
	.globl	_f2
	.def	_f2;	.scl	2;	.type	32;	.endef
_f2:
	pushl	%ebp
	movl	%esp, %ebp
	movl	$2, _R
	nop
	popl	%ebp
	ret
	.globl	_f3
	.def	_f3;	.scl	2;	.type	32;	.endef
_f3:
	pushl	%ebp
	movl	%esp, %ebp
	movl	$3, _R
	nop
	popl	%ebp
	ret
	.globl	_f4
	.def	_f4;	.scl	2;	.type	32;	.endef
_f4:
	pushl	%ebp
	movl	%esp, %ebp
	movl	$4, _R
	nop
	popl	%ebp
	ret
	.globl	_table
	.data
	.align 4
_table:
	.long	_f0
	.long	_f1
	.long	_f2
	.long	_f3
	.long	_f4
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "R=%d\12\0"
	.text
	.globl	_main
	.def	_main;	.scl	2;	.type	32;	.endef
_main:
	pushl	%ebp
	movl	%esp, %ebp
	andl	$-16, %esp
	subl	$32, %esp
	call	___main
	movl	$0, 28(%esp)
	jmp	L7
L8:
	movl	28(%esp), %eax
	movl	_table(,%eax,4), %eax
	call	*%eax
	movl	_R, %eax
	movl	%eax, 4(%esp)
	movl	$LC0, (%esp)
	call	_printf
	addl	$1, 28(%esp)
L7:
	cmpl	$4, 28(%esp)
	jle	L8
	movl	$0, %eax
	leave
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
	.def	_printf;	.scl	2;	.type	32;	.endef
