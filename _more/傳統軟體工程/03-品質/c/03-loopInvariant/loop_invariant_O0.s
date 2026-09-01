	.file	"loop_invariant.c"
	.text
	.globl	_fsum
	.def	_fsum;	.scl	2;	.type	32;	.endef
_fsum:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
	movl	$0, -4(%ebp)
	movl	$0, -8(%ebp)
	jmp	L2
L3:
	movl	12(%ebp), %eax
	imull	12(%ebp), %eax
	movl	%eax, %edx
	movl	-8(%ebp), %eax
	imull	-8(%ebp), %eax
	addl	%edx, %eax
	addl	%eax, -4(%ebp)
	addl	$1, -8(%ebp)
L2:
	movl	-8(%ebp), %eax
	cmpl	8(%ebp), %eax
	jl	L3
	movl	-4(%ebp), %eax
	leave
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
