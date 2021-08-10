# Getting the maximum of your C compiler, for security


## GCC

Understanding GCC flags is a *pain*. Which are enabled by `Wall` or `Wextra` is
not very easy to untangle.
The most reliable way is to parse and analyze the `commont.opt` and `c.opt`
files, which define (partially) the command line options which are supported by GCC.

The format is decribed in the GCC internals
[manual](https://gcc.gnu.org/onlinedocs/gccint/Option-file-format.html#Option-file-format),
so I've written a partial [parser][./gcc_copt_inclusions.py] which can help
identify what flags are needed.

### Warnings

Note that some warnings **depend** on some optimizations to be enabled to be
effective, so I recommend to always use `-O2`.

#### Generic

* `-Wall`: enable "most" of warnings by default
* `-Wextra`: enable *more* warnings by default

#### Security warnings

* `-Wformat=2`: check for format string problems
* `-Wformat-overflow=2`: check for *printf overflow
* `-Wformat-truncation=2`: check for *nprintf potential truncation
* `-Wformat-security`: check for dangerous format specifiers in *printf (enabled by `-Wformat=2`)
* `-Wnull-dereference`: Warn if dereferencing a NULL pointer may lead to erroneous or undefined behavior
* `-Wimplicit-fallthrough`: 
* `-Wstack-protector`: Warn when not issuing stack smashing protection for some reason
* `-Wstrict-overflow=3`
* `-Wtrampolines`: Warn whenever a trampoline is generated (will probably create an executable stack)
* `-Walloca` or `-Walloca-larger-than=1048576`: don't use `alloca()`, or limit it to "small" sizes
* `-Wvla` or `-Wvla-larger-than=1048576`: don't use variable length arrays, or limit them to "small" sizes
* `-Warray-bounds=2`

#### Extra flags

* `-Wformat-signedness`: Warn about sign differences with format functions.
* `-Wpedantic`
* `-Wshadow`
* `-Wstrict-overflow=4` (or 5)

### Compilation flags

* `-fstack-protector-strong`: add stack cookie checks to functions with stack buffers or pointers
* `-fPIE`: generate position-independant code (needed for ASLR)
* `


### References
* <https://developers.redhat.com/blog/2017/02/22/memory-error-detection-using-gcc>

## Clang

### Warnings

* `-Wshorten-64-to-32`

### References

* <https://clang.llvm.org/docs/DiagnosticsReference.html>
