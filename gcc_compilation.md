- [Warnings](#warnings)
- [Compilation flags](#compilation-flags)
- [Runtime sanitizers](#runtime-sanitizers)
- [Code analysis](#code-analysis)
- [Fuzzing](#fuzzing)
- [Test files](#test-files)
- [References](#references)

## GCC

*Note: this guide is valid for GCC 11*

Understanding GCC flags is a *pain*. Which ones are enabled by `-Wall` or `-Wextra` is
not very easy to untangle.
The most reliable way is to parse and analyze the `commont.opt` and `c.opt`
files, which define (partially) the command line options supported by GCC.

The format is decribed in the GCC internals
[manual](https://gcc.gnu.org/onlinedocs/gccint/Option-file-format.html#Option-file-format),
so I've written a partial [parser][./gcc_copt_inclusions.py] which can help
identify what flags are needed.
You *should* also check the
[compiler-warnings](https://github.com/pkolbus/compiler-warnings) project, which has a real parser
for GCC, Clang and XCode.

### Warnings

Note that some warnings **depend** on some optimizations to be enabled, so I
recommend to always use `-O2`.

#### Generic

* `-Wall`: enable "most" of warnings by default
* `-Wextra`: enable *more* warnings by default
* `-Wpedantic`: and even more.

#### Security warnings

* `-Wformat=2`: check for format string problems
* `-Wformat-overflow=2`: check for *printf overflow
* `-Wformat-truncation=2`: check for *nprintf potential truncation
* `-Wformat-security`: check for dangerous format specifiers in *printf (enabled by `-Wformat=2`)
* `-Wnull-dereference`: Warn if dereferencing a NULL pointer may lead to erroneous or undefined behavior
* `-Wstack-protector`: Warn when not issuing stack smashing protection for some reason
* `-Wstrict-overflow=3`: Warn when the compiler optimizes based on the assumption that signed overflow does not occur.
* `-Wtrampolines`: Warn whenever a trampoline is generated (will probably create an executable stack)
* `-Walloca` or `-Walloca-larger-than=1048576`: don't use `alloca()`, or limit it to "small" sizes
* `-Wvla` or `-Wvla-larger-than=1048576`: don't use variable length arrays, or limit them to "small" sizes
* `-Warray-bounds=2`: Warn if an array is accessed out of bounds. Note that it is very limited and will not catch some cases which may seem obvious.
* `-Wimplicit-fallthrough=3`: already added by `-Wextra`, but mentioned for reference.
* `-Wtraditional-conversion`: Warn of prototypes causing type conversions different from what would happen in the absence of prototype.
* `-Wshift-overflow=2`: Warn if left shift of a signed value overflows.
* `-Wcast-qual`: Warn about casts which discard qualifiers.
* `-Wstringop-overflow=4`: Under the control of Object Size type, warn about buffer overflow in string manipulation functions like memcpy and strcpy.
* `-Wconversion`: Warn for implicit type conversions that may change a value. *Note*: will probably introduce lots of warnings.
* `-Warith-conversion`: Warn if conversion of the result of arithmetic might change the value even though converting the operands cannot. *Note*: will probably introduce lots of warnings.

Those are not really security options per se, but will catch some logical errors:

* `-Wlogical-op`: Warn when a logical operator is suspiciously always evaluating to true or false.
* `-Wduplicated-cond`: Warn about duplicated conditions in an if-else-if chain.
* `-Wduplicated-branches`: Warn about duplicated branches in if-else statements.

#### Extra flags

* `-Wformat-signedness`: Warn (in format functions) about sign mismatches between the format specifiers and actual parameters.
* `-Wshadow`: Warn when one variable shadows another.  Same as `-Wshadow=global`.
* `-Wstrict-overflow=4` (or 5): Warn in more cases.
* `-Wundef`: Warn if an undefined macro is used in an `#if` directive.
* `-Wstrict-prototypes`: Warn about unprototyped function declarations.
* `-Wswitch-default`: Warn about enumerated switches missing a `default:` statement.
* `-Wswitch-enum`: Warn about all enumerated switches missing a specific case.
* `-Wstack-usage=<byte-size>`: Warn if stack usage might exceed `<byte-size>`.
* `-Wcast-align=strict`: Warn about pointer casts which increase alignment.
* `-Wjump-misses-init`: Warn when a jump misses a variable initialization.

### Compilation flags

* `-fstack-protector-strong`: add stack cookie checks to functions with stack buffers or pointers.
* `-fstack-clash-protection`: Insert code to probe each page of stack space as it is allocated to protect from [stack-clash](https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt) style attacks.
* `-fPIE`: generate position-independant code (needed for ASLR).
* `-fcf-protection=full|return|branch`: Generate code for [Intel CET](https://i.blackhat.com/asia-19/Thu-March-28/bh-asia-Sun-How-to-Survive-the-Hardware-Assisted-Control-Flow-Integrity-Enforcement.pdf).

#### Linker flags

* `-Wl,-z,relro`: make the GOT read-only ([Ref](https://www.redhat.com/en/blog/hardening-elf-binaries-using-relocation-read-only-relro)).
* `-Wl,-z,now`: disable lazy binding, making the PLT read-only.
* `-Wl,-z,noexecstack`: Marks the object as not requiring executable stack.
* `-Wl,-z,separate-code`: separate code from data (default on since binutils 2.31).

### Runtime sanitizers

GCC supports various *runtime* sanitizers, which are enabled by the `-fsanitize` flags, which are often not compatible and thus must be run separately.

* `address`: AddressSanitizer, with extra options available:
    * `pointer-compare`: Instrument comparison operation with pointer operands. Must be enabled at runtime by using `detect_invalid_pointer_pairs=2` in the `ASAN_OPTIONS` env var.
    * `pointer-subtract`: Instrument subtraction with pointer operands. Must be enabled at runtime by using `detect_invalid_pointer_pairs=2` in the `ASAN_OPTIONS` env var.
    * `ASAN_OPTIONS=strict_string_checks=1:detect_stack_use_after_return=1:check_initialization_order=1:strict_init_order=1`
* `thread`: ThreadSanitizer, a data race detector.
* `leak`: memory leak detector for programs which override `malloc` and other allocators.
* `undefined`: UndefinedBehaviorSanitizer. Checks not enabled by default (GCC 11):
    * `-fsanitize=bounds-strict`
    * `-fsanitize=float-divide-by-zero`
    * `-fsanitize=float-cast-overflow`

`kernel-address` also exists and enables AddressSanitizer for the Linux kernel.

### Code analysis

GCC 10 [introduced](https://developers.redhat.com/blog/2020/03/26/static-analysis-in-gcc-10)
the `-fanalyzer` static code analysis tool, which was vastly [improved](https://developers.redhat.com/blog/2021/01/28/static-analysis-updates-in-gcc-11) in GCC 11.

It tries to detect memory management issues (double free, use after free,
etc.), pointers-related problems, etc.

It *is* costly and slows down compilation and also exhibits false positives, so
its use may not always be practical.


### Fuzzing

While fuzzing is out of scope, you should use [AFL++](https://aflplus.plus/) to
fuzz your code, with [sanitizers][#runtime-sanitizers] enabled.

### Test files

Test files are a great way to understand in detail what is and what is not
covered by a specific command line flag.

They are located in the
[gcc/testsuite](https://gcc.gnu.org/git/?p=gcc.git;a=tree;f=gcc/testsuite;hb=HEAD)
directory, and in the
[gcc/testsuite/c-c++-common](https://gcc.gnu.org/git/?p=gcc.git;a=tree;f=gcc/testsuite/c-c%2B%2B-common;hb=HEAD)
and
[gcc/testsuite/gcc.dg](https://gcc.gnu.org/git/?p=gcc.git;a=tree;f=gcc/testsuite/gcc.dg;hb=HEAD)
subdirectories in particular.

For example, the test suite for the `-Walloca-larger-than` flag can be found in the following files:
```
gcc.dg/Walloca-larger-than-2.c
gcc.dg/Walloca-larger-than-3.c
gcc.dg/Walloca-larger-than-3.h
gcc.dg/Walloca-larger-than.c
```


`Walloca-larger-than.c` gives some insights on how the option behaves in practice:

```C
/* PR middle-end/82063 - issues with arguments enabled by -Wall
   { dg-do compile }
   { dg-require-effective-target alloca }
   { dg-options "-O2 -Walloca-larger-than=0 -Wvla-larger-than=0 -ftrack-macro-expansion=0" } */

extern void* alloca (__SIZE_TYPE__);

void sink (void*);

#define T(x) sink (x)

void test_alloca (void)
{
  /* Verify that alloca(0) is diagnosed even if the limit is zero.  */
  T (alloca (0));   /* { dg-warning "argument to .alloca. is zero" } */
  T (alloca (1));   /* { dg-warning "argument to .alloca. is too large" } */
}

void test_vla (unsigned n)
{
  /* VLAs smaller than 32 bytes are optimized into ordinary arrays.  */
  if (n < 1 || 99 < n)
    n = 1;

  char a[n];        /* { dg-warning "argument to variable-length array " } */
  T (a);
}
```


### References
* <https://developers.redhat.com/blog/2020/03/26/static-analysis-in-gcc-10>
* <https://developers.redhat.com/blog/2021/01/28/static-analysis-updates-in-gcc-11>
* <https://developers.redhat.com/blog/2017/02/22/memory-error-detection-using-gcc>
* <https://codeforces.com/blog/entry/15547>
* <https://github.com/google/sanitizers/wiki/AddressSanitizerFlags>
* <https://sudonull.com/post/6959-ld-z-separate-code>
