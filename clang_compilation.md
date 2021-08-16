## Clang (12)

Clang compiler flags are described by a domain specific language call
[TableGen](https://llvm.org/docs/TableGen/index.html), and LLVM includes a tool
called `llvm-tblgen` which parses the definition files, `DiagnosticsGroups.td` in particular.

### Warnings

Clang thankfully provides a `-Weverything` option which enables *all* warnings.
So, I recommend using `-Weverything` and then selectively disable the warnings
which are not really relevant for your code base.

Clang supports the following warnings which are compatible with GCC:

`-Walloca`,`-Wcast-qual`,`-Wconversion`,`-Wformat=2`,`-Wformat-security`,`-Wlogical-op`,`-Wnull-dereference`,`-Wstack-protector`,`-Wstrict-overflow=3`,`-Wvla`

Some other warnings are of interest for security:

* `-Wconversion`: which enables a lot of warning related to implicit conversions, with some which are particularly interesting:
    * `-Wshorten-64-to-32`: warn on 64 bit truncation (`long` to `int` for example)
* `-Warray-bounds`: which does not take an argument, contrary to GCC (enabled by default).
* `-Warray-bounds-pointer-arithmetic`: a more advanced version which takes pointer arithmetic into account.
* `-Wimplicit-fallthrough`: does not take an argument. Note that Clang does not parse comments and only supports `[[clang::fallthrough]]` and `__attribute__((fallthrough))` annotations.
* `-Wconditional-uninitialized`: warn if a variable may be uninitialized depending on a conditional branch
* `-Wloop-analysis`: warn about loop variable misuse (double increment, etc.)
* `-Wshift-sign-overflow`: warn when left shift overflows into sign bit
* `-Wswitch-enum`: warn when a switch statement does not handle all enum values
* `-Wtautological-constant-in-range-compare`: warn about pathological comparisons

### Compiler flags


Clang supports various options for stack based buffer overflow protection:
* `-fstack-protector-strong` (or `-fstack-protector-all)`: enable stack cookies
* `-fsanitize=safe-stack`: use two stacks ("safe" and "unsafe"), should not impact perfs and can be combined with `-fstack-protector` [Doc](https://clang.llvm.org/docs/SafeStack.html)
* `-fsanitize=shadow-call-stack`: stronger protection which specific arch support (currently only `Aarch64`)

Clang support several mitigations against control flow attacks:
* `-fcf-protection=full|return|branch`: Generate code for [Intel CET](https://i.blackhat.com/asia-19/Thu-March-28/bh-asia-Sun-How-to-Survive-the-Hardware-Assisted-Control-Flow-Integrity-Enforcement.pdf)

Other compilation flags:
* `-fPIE`: generate position-independant code (needed for ASLR)
* `-fstack-clash-protection`: Insert code to probe each page of stack space as it is allocated to protect from [stack-clash](https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt) style attacks.
* `-ftrivial-auto-var-init=pattern`: Auto initialize variables with a random pattern (can be costly ?). `=zero` option is not supported.

### Runtime sanitizers

LLVM support of sanitizers is first class, besides `AddressSanitizer`, `ThreadSanitizer`, `LeakSanitizer` and `UndefinedBehaviorSanitizer`, which are included in GCC, the following are available:

* `MemorySanitizer`: MemorySanitizer is a detector of uninitialized reads.

* `-fsanitize=integer`
* `-fsanitize=cfi`

#### In production

* `-fsanitize=integer`
* `-fsanitize-minimal-runtime`
* `-fsanitize-no-recover`

### Code analysis

* `scan-build`
* `DataFlowSanitizer` can be used to develop your own, application specific, code analyzer

### References

* <https://releases.llvm.org/12.0.0/tools/clang/docs/DiagnosticsReference.html>
* <https://releases.llvm.org/12.0.0/tools/clang/docs/index.html>
* <https://copperhead.co/blog/memory-disclosure-mitigations/>
* <https://source.android.com/devices/tech/debug/intsan>
* <https://security.googleblog.com/2019/05/queue-hardening-enhancements.html>
* <https://clang-analyzer.llvm.org/>
