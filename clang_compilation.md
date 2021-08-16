- [Clang](#clang)
  - [Warnings](#warnings)
  - [Compiler flags](#compiler-flags)
  - [Runtime sanitizers](#runtime-sanitizers)
  - [Code analysis](#code-analysis)
  - [References](#references)

## Clang

*Note: this guide is valid for Clang 12*

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
* `-fsanitize=safe-stack`: use two stacks ("safe" and "unsafe"), should not impact perfs and can be combined with `-fstack-protector` [Doc](https://releases.llvm.org/12.0.0/tools/clang/docs/SafeStack.html)
* `-fsanitize=shadow-call-stack`: stronger protection which specific arch support (currently only `Aarch64`). [Doc](https://clang.llvm.org/docs/ShadowCallStack.html)

Clang support several mitigations against control flow attacks:
* `-fcf-protection=full|return|branch`: Generate code for [Intel CET](https://i.blackhat.com/asia-19/Thu-March-28/bh-asia-Sun-How-to-Survive-the-Hardware-Assisted-Control-Flow-Integrity-Enforcement.pdf)
* `-fsanitize=cfi`: [Doc](https://releases.llvm.org/12.0.0/tools/clang/docs/ControlFlowIntegrity.html)

Other compilation flags:
* `-fPIE`: generate position-independant code (needed for ASLR)
* `-fstack-clash-protection`: Insert code to probe each page of stack space as it is allocated to protect from [stack-clash](https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt) style attacks.
* `-ftrivial-auto-var-init=pattern`: Auto initialize variables with a random pattern (can be costly ?). `=zero` option is not supported.

### Runtime sanitizers

LLVM support of sanitizers is first class, besides `AddressSanitizer`, `ThreadSanitizer`, `LeakSanitizer` and `UndefinedBehaviorSanitizer`, which are included in [GCC](./gcc_compilation.md#runtime-sanitizers), the following are available:

* `-fsanitize=memory`: [MemorySanitizer](https://releases.llvm.org/12.0.0/tools/clang/docs/MemorySanitizer.html) is a detector of uninitialized reads.
* `-fsanitize=integer`: advanced analysis of undefined or risky integer behaviour using UBSan

#### In production

While most sanitizers are not intended to be used in production builds, UBSan integer's checker is very interesting, as it will detect integer overflows and abort the program.

The code should be compiled with `-fsanitize=integer -fsanitize-minimal-runtime -fsanitize-no-recover`. The performance impact should be reasonable on modern CPUs (~1%).

### Code analysis


#### Clang static analyzer

LLVM has a "modern" static analyser which can be used to analyse whole projects
and produce HTML reports of the potential problems identified by the tool.

"It implements path-sensitive, inter-procedural analysis based on symbolic execution technique."

[`scan-build`](https://clang-analyzer.llvm.org/scan-build.html) is simple to use and can wrap compilation tools such as `make`. It
will replace the `CC` and `CXX` env variables to analyse your build and produce
the report.

```console
$ scan-build make
```

The [*default* checkers](https://releases.llvm.org/12.0.0/tools/clang/docs/analyzer/checkers.html)
are relatively few, and do not really target security, however, "alpha" (which may have many false positives) checkers related to security can be enabled by using the `-enable-checker alpha.security` CLI option.

Other interesting checkers:

* `alpha.core.CastSize`
* `alpha.core.CastToStruct`
* `alpha.core.Conversion` (it is relevant when `-Wconversion` is enabled ?)
* `alpha.core.IdenticalExpr`
* `alpha.core.PointerArithm`
* `alpha.core.PointerSub`
* `alpha.core.SizeofPtr`
* `alpha.core.TestAfterDivZero`
* `alpha.unix`, which has a bunch of useful checks

#### Others

* [`DataFlowSanitizer`](https://releases.llvm.org/12.0.0/tools/clang/docs/DataFlowSanitizerDesign.html) can be used to develop your own, application specific, code analyzer.

### References

* <https://releases.llvm.org/12.0.0/tools/clang/docs/DiagnosticsReference.html>
* <https://releases.llvm.org/12.0.0/tools/clang/docs/index.html>
* <https://copperhead.co/blog/memory-disclosure-mitigations/>
* <https://source.android.com/devices/tech/debug/intsan>
* <https://security.googleblog.com/2019/05/queue-hardening-enhancements.html>
* <https://clang-analyzer.llvm.org/>
