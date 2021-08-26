# Getting the maximum of your C compiler, for security

- [GCC TL;DR](#gcc-tldr)
- [Clang TL;DR](#clang-tldr)
- [Microsoft Visual Studio 2019 TL;DR](#microsoft-visual-studio-2019-tldr)
- [References](#references)

### Introduction

This guide is intended to help you determine which flags you should use to
compile your C Code using GCC, Clang or MSVC, in order to:

* detect the maximum number of bugs or potential security problems.
* enable security mitigations in the produced binaries.
* enable runtime sanitizers to detect errors (overflows, race conditions, etc.) and make fuzzing more efficient.


**Disclaimer**:

The flags selected and recommended here were chosen to *maximize* the number of
classes of detected errors which could have a security benefit when enabled.
Code generation options (such as `-fstack-protector-strong`) can also have
performance impacts.  It is up to you to assess the impact on your code base
and choose the right set of command line options.


Comments are of course [welcome](https://github.com/airbus-seclab/c-compiler-security/issues).


## GCC TL;DR

[Detailed page](./gcc_compilation.md)

Always use the following [warnings](./gcc_compilation.md#warnings) and [flags](./gcc_compilation.md#compilation-flags) on the command line:
```
-O2
-Wall -Wextra -Wpedantic -Wformat=2 -Wformat-overflow=2 -Wformat-truncation=2 -Wformat-security -Wnull-dereference -Wstack-protector -Wtrampolines -Walloca -Wvla -Warray-bounds=2 -Wimplicit-fallthrough=3 -Wtraditional-conversion -Wshift-overflow=2 -Wcast-qual -Wstringop-overflow=4 -Wconversion -Warith-conversion -Wlogical-op -Wduplicated-cond -Wduplicated-branches -Wformat-signedness -Wshadow -Wstrict-overflow=4 -Wundef -Wstrict-prototypes -Wswitch-default -Wswitch-enum -Wstack-usage=1000000 -Wcast-align=strict
-fstack-protector-strong -fstack-clash-protection -fPIE 
-Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -Wl,-z,separate-code
```

On legacy code bases, some of the warnings may produce some false positives. On
code where the behavior is intended, pragmas can be used to disable the specific
warning locally.

AddressSanitizer + UndefinedBehaviorSanitizer:
```
-fsanitize=address -fsanitize=pointer-compare -fsanitize=pointer-subtract -fsanitize=leak -fno-omit-frame-pointer -fsanitize=undefined -fsanitize=bounds-strict -fsanitize=float-divide-by-zero -fsanitize=float-cast-overflow
export ASAN_OPTIONS=strict_string_checks=1:detect_stack_use_after_return=1:check_initialization_order=1:strict_init_order=1:detect_invalid_pointer_pairs=2
```

If your program is multi-threaded, run with `-fsanitize=thread` (incompatible with ASan).

Finally, use [`-fanalyzer`](./gcc_compilation.md#code-analysis) to spot potential issues.

## Clang TL;DR

[Detailed page](./clang_compilation.md)

First compile with:

```
-O2
-Walloca -Wcast-qual -Wconversion -Wformat=2 -Wformat-security -Wlogical-op -Wnull-dereference -Wstack-protector -Wstrict-overflow=3 -Wvla -Warray-bounds -Warray-bounds-pointer-arithmetic -Wassign-enum -Wbad-function-cast -Wconditional-uninitialized -Wconversion -Wfloat-equal -Wformat-type-confusion -Widiomatic-parentheses -Wimplicit-fallthrough -Wloop-analysis -Wpointer-arith -Wshift-sign-overflow -Wshorten-64-to-32 -Wswitch-enum -Wtautological-constant-in-range-compare -Wunreachable-code-aggressive 
-fstack-protector-strong -fsanitize=safe-stack -fPIE -fstack-clash-protection
-Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -Wl,-z,separate-code
```

On legacy code bases, some of the warnings may produce some false positives. On
code where the behavior is intended, pragmas can be used to disable the specific
warning locally.

Run debug/test builds with sanitizers (in addition to the flags above):

AddressSanitizer + UndefinedBehaviorSanitizer:
```
-fsanitize=address -fsanitize=leak -fno-omit-frame-pointer -fsanitize=undefined -fsanitize=bounds-strict -fsanitize=float-divide-by-zero -fsanitize=float-cast-overflow -fsanitize=integer -fsanitize-no-recover
export ASAN_OPTIONS=strict_string_checks=1:detect_stack_use_after_return=1:check_initialization_order=1:strict_init_order=1:detect_invalid_pointer_pairs=2
```

If your program is multi-threaded, run with `-fsanitize=thread` (incompatible with ASan).

Finally, use [`scan-build`](./clang_compilation.md#code-analysis) to spot potential issues.

In addition, you can build production code with `-fsanitize=integer -fsanitize-minimal-runtime -fsanitize-no-recover` to catch integer overflows.


## Microsoft Visual Studio 2019 TL;DR

[Detailed page](./msvc_compilation.md)

* Compile with `/Wall /sdl /guard:cf /guard:ehcont`
* Use ASan with `/fsanitize=address`
* Analyze your code with `/fanalyze`

## Tips

* Check <https://github.com/pkolbus/compiler-warnings> to see which compiler version supports a given flag
* Use the [Compiler explorer](https://godbolt.org/) to experiment and check the impact on machine code produced
* If you have a doubt about the actual semantics of a flag, check the tests (for Clang, GCC)
* Use [checksec.py](https://github.com/Wenzel/checksec.py) to verify your binaries have mitigations

## References

* For [GCC](./gcc_compilation.md#references)
* For [Clang](./clang_compilation.md#references)
* For [MSVC](./msvc_compilation.md#references)
* <https://github.com/pkolbus/compiler-warnings>: GCC/Clang/XCode parsers for warnings definitions.
* <https://github.com/google/sanitizers/wiki/AddressSanitizerFlags>: ASan runtime options


Written by Raphaël Rigo and reviewed by Sarah Zennou @ [Airbus Security lab](https://airbus-seclab.github.io), 2021.


This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
