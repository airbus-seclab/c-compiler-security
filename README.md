# Getting the maximum of your C compiler, for security

## GCC 11

### tl;dr

Always use the following [warnings](./gcc_compilation.md#warnings) and [flags](./gcc_compilation.md#compilation-flags) on the command line, disable the warnings that have too much false positives, after considering the implications:
```
-O2 -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-overflow=2 -Wformat-truncation=2 -Wformat-security -Wnull-dereference -Wstack-protector -Wtrampolines -Walloca -Wvla -Warray-bounds=2 -Wimplicit-fallthrough=3 -Wtraditional-conversion -Wshift-overflow=2 -Wcast-qual -Wstringop-overflow=4 -Wconversion -Warith-conversion -Wlogical-op -Wduplicated-cond -Wduplicated-branches -Wformat-signedness -Wshadow -Wstrict-overflow=4 -Wundef -Wstrict-prototypes -Wswitch-default -Wswitch-enum -Wstack-usage=1000000 -Wcast-align=strict -fstack-protector-strong -fstack-clash-protection -fPIE
```

Run debug/test builds with [sanitizers](./gcc_compilation.md#runtime-sanitizers) (in addition to the flags above):

Address sanitizer:
```
-fsanitize=address -fsanitize=pointer-compare -fsanitize=pointer-substract -fsanitize=LeakSanitizer
export ASAN_OPTIONS=strict_string_checks=1:detect_stack_use_after_return=1:check_initialization_order=1:strict_init_order=1:detect_invalid_pointer_pairs=2
```

Detect undefined behaviour (dangerous), can sometimes misbehave when used in combination with ASan:
```
-fsanitize=undefined -fsanitize=bounds-strict -fsanitize=float-divide-by-zero -fsanitize=float-cast-overflow
```

If your program is multi-threaded, run with `-fsanitize=thread` (incompatible with ASan).

Finally, use [`-fanalyzer`](./gcc_compilation.md#code-analysis) to spot potential issues.

### Details

[Detailed page](./gcc_compilation.md)


## Clang 12

### tl;dr

Fist compile with:

```
-O2 -Weverything
```
and disable the warnings that have too much false positives, after considering the implications:

Run debug/test builds with sanitizers (in addition to the flags above):

Address sanitizer:



### Details

[Detailed page](./clang_compilation.md)

## Microsoft Visual Studio 2019

### tl;dr

TODO

### Details

[Detailed page](./msvc_compilation.md)

## References

* For [GCC](./gcc_compilation.md#references)
* For [Clang](./clang_compilation.md#references)
* <https://github.com/pkolbus/compiler-warnings>: GCC/Clang/XCode parsers for warnings definitions.

