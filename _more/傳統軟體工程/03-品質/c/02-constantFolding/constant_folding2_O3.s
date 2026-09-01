	.file	"constant_folding2.c"
	.section	.text.unlikely,"x"
LCOLDB0:
	.text
LHOTB0:
	.p2align 4,,15
	.globl	_f
	.def	_f;	.scl	2;	.type	32;	.endef
_f:
	movl	4(%esp), %eax
	addl	$23, %eax
	ret
	.section	.text.unlikely,"x"
LCOLDE0:
	.text
LHOTE0:
	.ident	"GCC: (tdm-1) 5.1.0"
