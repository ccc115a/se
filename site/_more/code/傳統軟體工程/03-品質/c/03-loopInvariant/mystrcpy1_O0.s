	.file	"mystrcpy1.c"
	.text
	.globl	_mystrcpy1
	.def	_mystrcpy1;	.scl	2;	.type	32;	.endef
_mystrcpy1:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$40, %esp
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	_strlen
	movl	%eax, -16(%ebp)
	movl	$0, -12(%ebp)
	jmp	L2
L3:
	movl	-12(%ebp), %edx
	movl	12(%ebp), %eax
	addl	%eax, %edx
	movl	-12(%ebp), %ecx
	movl	8(%ebp), %eax
	addl	%ecx, %eax
	movzbl	(%eax), %eax
	movb	%al, (%edx)
	addl	$1, -12(%ebp)
L2:
	movl	-12(%ebp), %eax
	cmpl	-16(%ebp), %eax
	jl	L3
	nop
	leave
	ret
	.globl	_mystrcpy2
	.def	_mystrcpy2;	.scl	2;	.type	32;	.endef
_mystrcpy2:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$40, %esp
	movl	$0, -12(%ebp)
	jmp	L5
L6:
	movl	-12(%ebp), %edx
	movl	12(%ebp), %eax
	addl	%eax, %edx
	movl	-12(%ebp), %ecx
	movl	8(%ebp), %eax
	addl	%ecx, %eax
	movzbl	(%eax), %eax
	movb	%al, (%edx)
	addl	$1, -12(%ebp)
L5:
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	_strlen
	movl	%eax, %edx
	movl	-12(%ebp), %eax
	cmpl	%eax, %edx
	ja	L6
	nop
	leave
	ret
	.ident	"GCC: (tdm-1) 5.1.0"
	.def	_strlen;	.scl	2;	.type	32;	.endef
