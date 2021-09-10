- [Warnings](#warnings)
- [Compiler flags](#compiler-flags)
- [Runtime sanitizers](#runtime-sanitizers)
- [Code analysis](#code-analysis)
- [Fuzzing](#fuzzing)
- [References](#references)

## Clang

*Note: this guide is valid for Clang 12*

Clang compiler flags are described by a domain specific language call
[TableGen](https://llvm.org/docs/TableGen/index.html), and LLVM includes a tool
called `llvm-tblgen` which parses the definition files, `DiagnosticsGroups.td` in particular.

### Warnings

While Clang thankfully provides a `-Weverything` option which enables *all*
warnings, it is [strongly](https://quuxplusone.github.io/blog/2018/12/06/dont-use-weverything/) recommended by Clang developpers *not* to use it in production...

However, they (and I) recommend using `-Weverything` to identify warnings which
are relevant for your code base and then selectively add them to your standard
warning list.

Clang supports the following warnings which are compatible with [GCC](./gcc_compilation.md#warnings):

* the obvious `-Wall`, `-Wextra`, `-Wpedantic` and `-Werror` ([Note](https://flameeyes.blog/2009/02/25/future-proof-your-code-dont-use-werror/)).
* `-Walloca`,`-Wcast-qual`,`-Wconversion`,`-Wformat=2`,`-Wformat-security`,`-Wnull-dereference`,`-Wstack-protector`,`-Wvla`.

Some other warnings are of interest for security:

* `-Wconversion`: which enables a lot of warnings related to implicit conversions, with some which are particularly interesting:
    * `-Wshorten-64-to-32`: warn on 64 bits truncation (`size_t` to `int` on 64bits Linux for example).
* `-Warray-bounds`: which does not take an argument, contrary to GCC (enabled by default).
* `-Warray-bounds-pointer-arithmetic`: a more advanced version which takes pointer arithmetic into account.
* `-Wimplicit-fallthrough`: does not take an argument. Note that Clang does not parse comments and only supports `[[clang::fallthrough]]` and `__attribute__((fallthrough))` annotations.
* `-Wconditional-uninitialized`: warn if a variable may be uninitialized depending on a conditional branch.
* `-Wloop-analysis`: warn about loop variable misuse (double increment, etc.).
* `-Wshift-sign-overflow`: warn when left shift overflows into sign bit.
* `-Wswitch-enum`: warn when a switch statement does not handle all enum values.
* `-Wtautological-constant-in-range-compare`: warn about comparisons which are always `true` or `false` due to the variables value ranges. Ex: `comparison of unsigned expression < 0 is always false`.
* `-Wcomma`: warn about possible comma misuse.
* `-Wassign-enum`: integer constant not in range of enumerated type A.
* `-Wbad-function-cast`: cast from function call of type A to non-matching type B.
* `-Wfloat-equal`: comparing floating point with == or != is unsafe.
* `-Wformat-type-confusion`: format specifies type A but the argument has type B.
* `-Wpointer-arith`: various warnings related to pointer arithmetic.
* `-Widiomatic-parentheses`: using the result of an assignment as a condition without parentheses.
* `-Wunreachable-code-aggressive`: warn about unreachable code.
* `-Wthread-safety` and `-Wthread-safety-beta`: warn about potential threading/race condition issues.

*Note*: You can disable warnings for system includes by using the `-isystem`
option to specify the paths which will be used for "system" includes (`#include <file.h>`).

### Compiler flags


Clang supports various options for stack based buffer overflow protection and mitigations against control flow attacks:
* `-fstack-protector-strong` (or `-fstack-protector-all)`: enable stack cookies.
* `-fsanitize=safe-stack`: use two stacks ("safe" and "unsafe"), should not impact performance and can be combined with `-fstack-protector` [Doc](https://releases.llvm.org/12.0.0/tools/clang/docs/SafeStack.html), [Research](https://dslab.epfl.ch/research/cpi/).
* `-fsanitize=shadow-call-stack`: stronger protection which specific arch support (currently only `Aarch64`). [Doc](https://clang.llvm.org/docs/ShadowCallStack.html).
* `-fcf-protection=full|return|branch`: Generate code for [Intel CET](https://i.blackhat.com/asia-19/Thu-March-28/bh-asia-Sun-How-to-Survive-the-Hardware-Assisted-Control-Flow-Integrity-Enforcement.pdf).
* `-fsanitize=cfi`: ControlFlowIntegrity. [Doc](https://releases.llvm.org/12.0.0/tools/clang/docs/ControlFlowIntegrity.html).

Other compilation flags:
* `-fPIE`: generate position-independent code (needed for ASLR).
* `-fstack-clash-protection`: Insert code to probe each page of stack space as it is allocated to protect from [stack-clash](https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt) style attacks.
* `-ftrivial-auto-var-init=pattern`: Auto initialize variables with a random pattern, which can be costly in some cases. `=zero` option is only supported with `-enable-trivial-auto-var-init-zero-knowing-it-will-be-removed-from-clang`.

* Glibc flags: see [GCC page](./gcc_compilation.md#glibc-flags)
* Linker flags: see [GCC page](./gcc_compilation.md#linker-flags)

### Runtime sanitizers

LLVM support of sanitizers is first class, besides [`AddressSanitizer`](https://releases.llvm.org/12.0.0/tools/clang/docs/AddressSanitizer.html), [`ThreadSanitizer`](https://releases.llvm.org/12.0.0/tools/clang/docs/ThreadSanitizer.html), [`LeakSanitizer`](https://releases.llvm.org/12.0.0/tools/clang/docs/LeakSanitizer.html) and [`UndefinedBehaviorSanitizer`](https://releases.llvm.org/12.0.0/tools/clang/docs/UndefinedBehaviorSanitizer.html), which are included in [GCC](./gcc_compilation.md#runtime-sanitizers), the following are available:

* `-fsanitize=memory`: [MemorySanitizer](https://releases.llvm.org/12.0.0/tools/clang/docs/MemorySanitizer.html) is a detector of uninitialized reads.
* `-fsanitize=integer`: advanced analysis of undefined or risky integer behavior using UBSan. Note that this [enables](https://releases.llvm.org/12.0.0/tools/clang/docs/UndefinedBehaviorSanitizer.html#available-checks) detection of *legit* (per the C langage spec) detection of *unsigned* integer overflows. Instrumentation can be disabled on functions where overflowing is expected by using `__attribute__((no_sanitize("unsigned-integer-overflow")))`. Ditto with `unsigned-shift-base`.

#### Use with fuzzing

Runtime sanitizers are particularly useful when:

* running test suites,
* fuzzing code,

as they may uncover runtime errors which would not necessarily trigger a crash.

#### In production

While most sanitizers are not intended to be used in production builds, UBSan integer's checker is very interesting, as it will detect integer overflows and abort the program.

The code should be compiled with `-fsanitize=integer -fsanitize-minimal-runtime -fno-sanitize-recover`. The performance impact should be reasonable on modern CPUs (~1%). Android [enables](https://android-developers.googleblog.com/2018/06/compiler-based-security-mitigations-in.html) it in production builds for some libraries.

### Code analysis


#### Clang static analyzer

Clang has a "modern" static analyzer which can be used to analyze whole projects
and produce HTML reports of the potential problems identified by the tool.

"It implements path-sensitive, inter-procedural analysis based on symbolic execution technique."

[`scan-build`](https://clang-analyzer.llvm.org/scan-build.html) is simple to use and can wrap compilation tools such as `make`. It
will replace the `CC` and `CXX` environment variables to analyze your build and produce
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

### Fuzzing


While fuzzing is out of scope, you should fuzz your code with [sanitizers](#runtime-sanitizers) enabled. Options include:

* [libFuzzer](https://llvm.org/docs/LibFuzzer.html) which is included in LLVM and can be easily integrated in a build/test process.
* [AFL++](https://aflplus.plus/).


### Test files

Test files are a great way to understand in detail what is and what is not
covered by a specific command line flag.

They are located in the [`clang/test`](https://github.com/llvm/llvm-project/tree/main/clang/test) directory. For example, the test for `-Wshift-count-negative` can be found in [`clang/test/Sema/warn-shift-negative.c`](https://github.com/llvm/llvm-project/blob/main/clang/test/Sema/warn-shift-negative.c):

```C
// RUN: %clang_cc1 -fsyntax-only -Wshift-count-negative -fblocks -verify %s

int f(int a) {
  const int i = -1;
  return a << i; // expected-warning{{shift count is negative}}
}
```

### References

* <https://releases.llvm.org/12.0.0/tools/clang/docs/DiagnosticsReference.html>: All Clang warnings listed and "documented".
* <https://releases.llvm.org/12.0.0/tools/clang/docs/index.html>: Clang documentation
* <https://copperhead.co/blog/memory-disclosure-mitigations/>: Uses of sanitizers and hardening options in Android CopperheadOs
* <https://source.android.com/devices/tech/debug/intsan>: Android use of UBSan in production builds to mitigate integer overflows.
* <https://security.googleblog.com/2019/05/queue-hardening-enhancements.html>: Information about other hardening options in Android
* <https://clang-analyzer.llvm.org/>: Doc for `scan-build`
* <https://lld.llvm.org/>: The LLVM linker documentation.
* <https://blog.quarkslab.com/clang-hardening-cheat-sheet.html>: Quarkslab recommnendations for Clang hardening flags.
