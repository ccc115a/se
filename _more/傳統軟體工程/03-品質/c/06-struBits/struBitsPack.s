	.file	"struBits.c"
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "sizeof(iA)=%d\12\0"
LC1:
	.ascii "sizeof(Instr)=%d\12\0"
LC2:
	.ascii "sizeof(iC)=%d\12\0"
	.text
	.globl	_main
	.def	_main;	.scl	2;	.type	32;	.endef
_main:
	pushl	%ebp
	movl	%esp, %ebp
	andl	$-16, %esp
	subl	$32, %esp
	call	___main
	movl	$2, 4(%esp)
	movl	$LC0, (%esp)
	call	_printf
	movl	$2, 4(%esp)
	movl	$LC1, (%esp)
	call	_printf
	movl	$2, 4(%esp)
	movl	$LC2, (%esp)
	call	_printf
	movzbl	28(%esp), %eax
	orl	$8, %eax
	movb	%al, 28(%esp)
	movzwl	28(%esp), %eax
	andw	$-1009, %ax
	orl	$48, %eax
	movw	%ax, 28(%esp)
	movl	$0, %eax
	leave
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
	.def	_printf;	.scl	2;	.type	32;	.endef
