	.file	"test_volatile.c"
	.comm	_buffer_full, 4, 2
	.text
	.globl	_read_stream
	.def	_read_stream;	.scl	2;	.type	32;	.endef
_read_stream:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
	movl	$0, -4(%ebp)
	jmp	L2
L3:
	addl	$1, -4(%ebp)
L2:
	movl	_buffer_full, %eax
	testl	%eax, %eax
	je	L3
	movl	-4(%ebp), %eax
	leave
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
