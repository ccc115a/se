	.file	"loop_invariant.c"
	.section	.text.unlikely,"x"
LCOLDB0:
	.text
LHOTB0:
	.p2align 4,,15
	.globl	_fsum
	.def	_fsum;	.scl	2;	.type	32;	.endef
_fsum:
	pushl	%esi
	pushl	%ebx
	movl	12(%esp), %esi
	movl	16(%esp), %ebx
	testl	%esi, %esi
	jle	L4
	imull	%ebx, %ebx
	xorl	%edx, %edx
	xorl	%eax, %eax
	.p2align 4,,10
L3:
	movl	%edx, %ecx
	imull	%edx, %ecx
	addl	$1, %edx
	addl	%ebx, %ecx
	addl	%ecx, %eax
	cmpl	%edx, %esi
	jne	L3
L2:
	popl	%ebx
	popl	%esi
	ret
L4:
	xorl	%eax, %eax
	jmp	L2
	.section	.text.unlikely,"x"
LCOLDE0:
	.text
LHOTE0:
	.ident	"GCC: (tdm-1) 5.1.0"
