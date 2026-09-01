# debug

Valgrind: 偵測記憶體分配釋放問題

## sadstring.c -- 多釋放一次。

```
guest@localhost:~/sp/code/c/10-os2linux/01-c/debug$ gcc sadstring.c -o sadstring -g -Wall -std=gnu11 -O3
guest@localhost:~/sp/code/c/10-os2linux/01-c/debug$ valgrind --leak-check=yes ./sadstring
==7250== Memcheck, a memory error detector
==7250== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==7250== Using Valgrind-3.13.0 and LibVEX; rerun with -h for copyright info
==7250== Command: ./sadstring
==7250==
/lib64/ld-linux-x86-64.so.2
libc.so.6
__printf_chk
strlen
malloc
system
__snprintf_chk
__cxa_finalize
__libc_start_main
free
GLIBC_2.2.5
GLIBC_2.3.4
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
5B
%D
%B
%:
%2
%*
%"
%2
ATUI
X       Hc
AWAVI
AUATL
[]A\A]A^A_
strings %s
something went wrong running %s.
;*3$"
GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0
#__s
#__n
/usr/include/x86_64-linux-gnu/bits
/usr/lib/gcc/x86_64-linux-gnu/7/include
/usr/include
sadstring.c
stdio2.h
stddef.h
types.h
libio.h
stdio.h
sys_errlist.h
string.h
stdlib.h
<built-in>
__off_t
_IO_read_ptr
malloc
_chain
size_t
_shortbuf
_IO_2_1_stderr_
_IO_buf_base
long long unsigned int
free
long long int
_fileno
_IO_read_end
_flags
_IO_buf_end
_cur_column
__printf_chk
_old_offset
get_strings
_IO_marker
stdin
strlen
_IO_FILE_plus
_IO_write_ptr
sys_nerr
_sbuf
short unsigned int
_IO_save_base
_lock
_flags2
_mode
stdout
__builtin___snprintf_chk
_IO_2_1_stdin_
_IO_write_end
_IO_lock_t
_IO_FILE
GNU C11 7.5.0 -mtune=generic -march=x86-64 -g -O3 -std=gnu11 -fstack-protector-strong
/home/guest/sp/code/c/10-os2linux/01-c/debug
_pos
sys_errlist
_markers
unsigned char
short int
_vtable_offset
_IO_2_1_stdout_
_next
__off64_t
_IO_read_base
sadstring.c
_IO_save_end
__fmt
__pad1
__pad2
__pad3
__pad4
__pad5
snprintf
_unused2
stderr
argv
_IO_backup_base
system
argc
main
_IO_write_base
sadstring.c
crtstuff.c
deregister_tm_clones
__do_global_dtors_aux
completed.7698
__do_global_dtors_aux_fini_array_entry
frame_dummy
__frame_dummy_init_array_entry
__FRAME_END__
__init_array_end
_DYNAMIC
__init_array_start
__GNU_EH_FRAME_HDR
_GLOBAL_OFFSET_TABLE_
__libc_csu_fini
__snprintf_chk@@GLIBC_2.3.4
free@@GLIBC_2.2.5
_ITM_deregisterTMCloneTable
_edata
strlen@@GLIBC_2.2.5
system@@GLIBC_2.2.5
get_strings
__libc_start_main@@GLIBC_2.2.5
__data_start
__gmon_start__
__dso_handle
_IO_stdin_used
__libc_csu_init
malloc@@GLIBC_2.2.5
__bss_start
main
__printf_chk@@GLIBC_2.3.4
__TMC_END__
_ITM_registerTMCloneTable
__cxa_finalize@@GLIBC_2.2.5
.symtab
.strtab
.shstrtab
.interp
.note.ABI-tag
.note.gnu.build-id
.gnu.hash
.dynsym
.dynstr
.gnu.version
.gnu.version_r
.rela.dyn
.rela.plt
.init
.plt.got
.text
.fini
.rodata
.eh_frame_hdr
.eh_frame
.init_array
.fini_array
.dynamic
.data
.bss
.comment
.debug_aranges
.debug_info
.debug_abbrev
.debug_line
.debug_str
.debug_loc
.debug_ranges
==7250== Invalid free() / delete / delete[] / realloc()
==7250==    at 0x4C30D3B: free (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so) // 第一次釋放
==7250==    by 0x1086DB: main (sadstring.c:19)
==7250==  Address 0x522d040 is 0 bytes inside a block of size 20 free'd
==7250==    at 0x4C30D3B: free (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so) // 第二次釋放
==7250==    by 0x108869: get_strings (sadstring.c:14)
==7250==    by 0x1086DB: main (sadstring.c:19)
==7250==  Block was alloc'd at
==7250==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7250==    by 0x108819: get_strings (sadstring.c:11)
==7250==    by 0x1086DB: main (sadstring.c:19)
==7250==
==7250==
==7250== HEAP SUMMARY:
==7250==     in use at exit: 0 bytes in 0 blocks
==7250==   total heap usage: 1 allocs, 2 frees, 20 bytes allocated // 一次分配，兩次釋放！
==7250==
==7250== All heap blocks were freed -- no leaks are possible
==7250==
==7250== For counts of detected and suppressed errors, rerun with: -v
==7250== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0) // 有一個錯
```

## sadstring2.c 沒釋放

```
guest@localhost:~/sp/code/c/10-os2linux/01-c/debug$ gcc sadstring2.c -o sadstring2 -g -Wall -std=gnu11 -O3
guest@localhost:~/sp/code/c/10-os2linux/01-c/debug$ valgrind --leak-check=yes ./sadstring2
==7321== Memcheck, a memory error detector
==7321== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==7321== Using Valgrind-3.13.0 and LibVEX; rerun with -h for copyright info
==7321== Command: ./sadstring2
==7321==
/lib64/ld-linux-x86-64.so.2
libc.so.6
__printf_chk
strlen
malloc
system
__snprintf_chk
__cxa_finalize
__libc_start_main
GLIBC_2.2.5
GLIBC_2.3.4
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
%z
%r
%j
=9
ATUI
X       Hc
[]A\
]A\1
AWAVI
AUATL
[]A\A]A^A_
strings %s
something went wrong running %s.
;*3$"
GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0
#__s
#__n
/usr/include/x86_64-linux-gnu/bits
/usr/lib/gcc/x86_64-linux-gnu/7/include
/usr/include
sadstring2.c
stdio2.h
stddef.h
types.h
libio.h
stdio.h
sys_errlist.h
string.h
stdlib.h
<built-in>
__off_t
_IO_read_ptr
malloc
_chain
size_t
_shortbuf
_IO_2_1_stderr_
_IO_buf_base
sadstring2.c
long long unsigned int
long long int
_fileno
_IO_read_end
_flags
_IO_buf_end
_cur_column
__printf_chk
_old_offset
get_strings
_IO_marker
stdin
strlen
_IO_FILE_plus
_IO_write_ptr
sys_nerr
_sbuf
short unsigned int
_IO_save_base
_lock
_flags2
_mode
stdout
__builtin___snprintf_chk
_IO_2_1_stdin_
_IO_write_end
_IO_lock_t
_IO_FILE
GNU C11 7.5.0 -mtune=generic -march=x86-64 -g -O3 -std=gnu11 -fstack-protector-strong
/home/guest/sp/code/c/10-os2linux/01-c/debug
_pos
sys_errlist
_markers
unsigned char
short int
_vtable_offset
_IO_2_1_stdout_
_next
__off64_t
_IO_read_base
_IO_save_end
__fmt
__pad1
__pad2
__pad3
__pad4
__pad5
snprintf
_unused2
stderr
argv
_IO_backup_base
system
argc
main
_IO_write_base
sadstring2.c
crtstuff.c
deregister_tm_clones
__do_global_dtors_aux
completed.7698
__do_global_dtors_aux_fini_array_entry
frame_dummy
__frame_dummy_init_array_entry
__FRAME_END__
__init_array_end
_DYNAMIC
__init_array_start
__GNU_EH_FRAME_HDR
_GLOBAL_OFFSET_TABLE_
__libc_csu_fini
__snprintf_chk@@GLIBC_2.3.4
_ITM_deregisterTMCloneTable
_edata
strlen@@GLIBC_2.2.5
system@@GLIBC_2.2.5
get_strings
__libc_start_main@@GLIBC_2.2.5
__data_start
__gmon_start__
__dso_handle
_IO_stdin_used
__libc_csu_init
malloc@@GLIBC_2.2.5
__bss_start
main
__printf_chk@@GLIBC_2.3.4
__TMC_END__
_ITM_registerTMCloneTable
__cxa_finalize@@GLIBC_2.2.5
.symtab
.strtab
.shstrtab
.interp
.note.ABI-tag
.note.gnu.build-id
.gnu.hash
.dynsym
.dynstr
.gnu.version
.gnu.version_r
.rela.dyn
.rela.plt
.init
.plt.got
.text
.fini
.rodata
.eh_frame_hdr
.eh_frame
.init_array
.fini_array
.dynamic
.data
.bss
.comment
.debug_aranges
.debug_info
.debug_abbrev
.debug_line
.debug_str
.debug_loc
.debug_ranges
==7321== 
==7321== HEAP SUMMARY:
==7321==     in use at exit: 21 bytes in 1 blocks
==7321==   total heap usage: 1 allocs, 0 frees, 21 bytes allocated
==7321==
==7321== 21 bytes in 1 blocks are definitely lost in loss record 1 of 1
==7321==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7321==    by 0x1087C9: get_strings (sadstring2.c:11)
==7321==    by 0x10868B: main (sadstring2.c:19)
==7321==
==7321== LEAK SUMMARY:
==7321==    definitely lost: 21 bytes in 1 blocks
==7321==    indirectly lost: 0 bytes in 0 blocks
==7321==      possibly lost: 0 bytes in 0 blocks
==7321==    still reachable: 0 bytes in 0 blocks
==7321==         suppressed: 0 bytes in 0 blocks
==7321==
==7321== For counts of detected and suppressed errors, rerun with: -v
==7321== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0)
```