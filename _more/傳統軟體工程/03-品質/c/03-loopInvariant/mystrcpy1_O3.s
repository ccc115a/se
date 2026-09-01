	.file	"mystrcpy1.c"
	.section	.text.unlikely,"x"
LCOLDB0:
	.text
LHOTB0:
	.p2align 4,,15
	.globl	_mystrcpy1
	.def	_mystrcpy1;	.scl	2;	.type	32;	.endef
_mystrcpy1:
	pushl	%ebp
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	subl	$28, %esp
	movl	48(%esp), %ebx
	movl	52(%esp), %esi
	movl	%ebx, (%esp)
	call	_strlen
	testl	%eax, %eax
	jle	L8
	leal	4(%ebx), %edx
	cmpl	%edx, %esi
	leal	4(%esi), %edx
	setnb	%cl
	cmpl	%edx, %ebx
	setnb	%dl
	orl	%ecx, %edx
	movl	%ebx, %ecx
	orl	%esi, %ecx
	andl	$3, %ecx
	sete	%cl
	testb	%cl, %dl
	je	L10
	cmpl	$9, %eax
	jbe	L10
	leal	-4(%eax), %ecx
	xorl	%edx, %edx
	shrl	$2, %ecx
	addl	$1, %ecx
	leal	0(,%ecx,4), %edi
L4:
	movl	(%ebx,%edx,4), %ebp
	movl	%ebp, (%esi,%edx,4)
	addl	$1, %edx
	cmpl	%edx, %ecx
	ja	L4
	cmpl	%edi, %eax
	je	L8
	movzbl	(%ebx,%ecx,4), %edx
	movb	%dl, (%esi,%ecx,4)
	leal	1(%edi), %edx
	cmpl	%edx, %eax
	jle	L8
	movzbl	1(%ebx,%edi), %edx
	movb	%dl, 1(%esi,%edi)
	leal	2(%edi), %edx
	cmpl	%edx, %eax
	jle	L8
	movzbl	2(%ebx,%edi), %eax
	movb	%al, 2(%esi,%edi)
L8:
	addl	$28, %esp
	xorl	%eax, %eax
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
	.p2align 4,,10
L10:
	xorl	%edx, %edx
	.p2align 4,,10
L3:
	movzbl	(%ebx,%edx), %ecx
	movb	%cl, (%esi,%edx)
	addl	$1, %edx
	cmpl	%edx, %eax
	jne	L3
	addl	$28, %esp
	xorl	%eax, %eax
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
	.section	.text.unlikely,"x"
LCOLDE0:
	.text
LHOTE0:
	.section	.text.unlikely,"x"
LCOLDB1:
	.text
LHOTB1:
	.p2align 4,,15
	.globl	_mystrcpy2
	.def	_mystrcpy2;	.scl	2;	.type	32;	.endef
_mystrcpy2:
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	xorl	%ebx, %ebx
	subl	$16, %esp
	movl	32(%esp), %esi
	movl	36(%esp), %edi
	jmp	L25
	.p2align 4,,10
L26:
	movzbl	(%esi,%ebx), %eax
	movb	%al, (%edi,%ebx)
	addl	$1, %ebx
L25:
	movl	%esi, (%esp)
	call	_strlen
	cmpl	%ebx, %eax
	ja	L26
	addl	$16, %esp
	popl	%ebx
	popl	%esi
	popl	%edi
	ret
	.section	.text.unlikely,"x"
LCOLDE1:
	.text
LHOTE1:
	.ident	"GCC: (tdm-1) 5.1.0"
	.def	_strlen;	.scl	2;	.type	32;	.endef
