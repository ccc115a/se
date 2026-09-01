	.file	"constant_folding2.c"
	.data
	.align 4
_a:
	.long	3
	.text
	.globl	_f
	.def	_f;	.scl	2;	.type	32;	.endef
_f:
	pushl	%ebp
	movl	%esp, %ebp
	movl	_a, %edx
	movl	%edx, %eax
	sall	$2, %eax
	addl	%edx, %eax
	leal	8(%eax), %edx
	movl	8(%ebp), %eax
	addl	%edx, %eax
	popl	%ebp
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
