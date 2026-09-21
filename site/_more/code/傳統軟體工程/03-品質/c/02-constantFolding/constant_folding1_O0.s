	.file	"constant_folding1.c"
	.text
	.globl	_f
	.def	_f;	.scl	2;	.type	32;	.endef
_f:
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax
	addl	$23, %eax
	popl	%ebp
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
