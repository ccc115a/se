	.file	"test_novolatile.c"
	.section	.text.unlikely,"x"
LCOLDB0:
	.text
LHOTB0:
	.p2align 4,,15
	.globl	_read_stream
	.def	_read_stream;	.scl	2;	.type	32;	.endef
_read_stream:
	movl	_buffer_full, %eax
	testl	%eax, %eax
	jne	L2
L4:
	jmp	L4
	.p2align 4,,10
L2:
	xorl	%eax, %eax
	ret
	.section	.text.unlikely,"x"
LCOLDE0:
	.text
LHOTE0:
	.comm	_buffer_full, 4, 2
	.ident	"GCC: (tdm-1) 5.1.0"
