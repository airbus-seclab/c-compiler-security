## Clang (12)

Clang compiler flags are described by a domain specific language call
[TableGen](https://llvm.org/docs/TableGen/index.html), and LLVM includes a tool
called `llvm-tblgen` which parses the definition files, `DiagnosticsGroups.td` in particular.


### Warnings

Clang thankfully provides a `-Weverything` option which enables *all* warnings.
So, I recommend using `-Weverything` and then selectively disable the warnings
which are too not relevant for your code base.

Clang supports the following warnings which are compatible with GCC:

`-Walloca`,`-Wcast-qual`,`-Wconversion`,`-Wformat=2`,`-Wformat-security`,`-Wlogical-op`,`-Wnull-dereference`,`-Wstack-protector`,`-Wstrict-overflow=3`,`-Wvla`

Some other warnings are of interest for security:

* `-Wconversion`: which enables a lot of warning related to implicit conversions, with some which are interesting: 
    * `-Wshorten-64-to-32`: warn on 64 bit truncation (`long` to `int` for example)
* `-Warray-bounds`: which does not take an argument, contrary to GCC (enabled by default)
* `-Warray-bounds-pointer-arithmetic`
* `-Wimplicit-fallthrough`: does not take an argument
* `-Wconditional-uninitialized`
* `-Wloop-analysis`
* `-Wshift-sign-overflow`
* `-Wswitch-enum`
* `-Wtautological-constant-in-range-compare`

### Compiler flags

-fstack-clash-protection
-fstack-protector-strong (or -fstack-protector-all)
-fPIE
-fcf-protection
Generate code for Intel CET
-ftrivial-auto-var-init=pattern
Auto initialize variables with a random pattern, can be costly ?

### Runtime sanitizers

LLVM support of sanitizers is first class, besides `AddressSanitizer`, `ThreadSanitizer`, `LeakSanitizer` and `UndefinedBehaviorSanitizer`, which are included in GCC, the following are available:

* `MemorySanitizer`: MemorySanitizer is a detector of uninitialized reads. 

* `-fsanitize=integer`
* `-fsanitize=cfi`
* `-fsanitize=safe-stack`

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
