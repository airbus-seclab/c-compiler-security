- [Warnings](#warnings)
- [Compilation flags](#compilation-flags)
- [Code analysis](#code-analysis)
- [Sanitizers](#sanitizers)
- [References](#references)

## Microsoft Visual Studio (2019)

As I am not running Windows, this section is less precise. But recent versions
of Visual Studio support using Clang as a compiler, so all the Clang options
apply.

### Note about the GUI

The flags described here are those you can set on the command line. Some options can be changed directly in the GUI.
Check the following documentation pages for reference:

* C/C++ project [properties](https://docs.microsoft.com/en-us/cpp/build/reference/c-cpp-prop-page?view=msvc-160)
* Linker [properties](https://docs.microsoft.com/en-us/cpp/build/reference/linker-property-pages?view=msvc-160)
* Setting [project properties](https://docs.microsoft.com/en-us/cpp/build/working-with-project-properties?view=msvc-160)


### Warnings

*All* warnings can be enabled by using the `/Wall` option, as documented [](https://docs.microsoft.com/en-us/cpp/preprocessor/compiler-warnings-that-are-off-by-default?view=msvc-160).

*Note*: The `/W4` option does **not** enable all "level 4" warnings: `/W4 displays level 1, level 2, and level 3 warnings, and all level 4 (informational) warnings that aren't off by default.`. So, you have to use `/Wall` and disable the ones that are not relevant.

As with GCC and Clang, MSVC supports disabling warnings for "external" headers, by using the `/external` option, documented [here](https://docs.microsoft.com/en-us/cpp/build/reference/external-external-headers-diagnostics?view=msvc-160). For example: `/external:anglebrackets /external:W3` will lower warnings to `W3` for headers included through `<>`.

### Compilation flags

* `/GS`: Checks buffer security [doc](https://docs.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check?view=msvc-160) (on by default).
* `/sdl`: enables "Strict mode" for `/GS` and additional checks. [doc](https://docs.microsoft.com/en-us/cpp/build/reference/sdl-enable-additional-security-checks?view=msvc-160)
* `/DYNAMICBASE`: Generate PIE code for ASLR (default on for recent).
* `/HIGHENTROPYVA`: High entropy ASLR for 64 bits targets (default on).
* `/SAFESEH`: Safe Structured Exception Handlers (x86 only) [doc](https://docs.microsoft.com/en-us/cpp/build/reference/safeseh-image-has-safe-exception-handlers?view=msvc-160)
* `/guard:cf`
* `/guard:ehcont`
* `/CETCOMPAT`: Mark the binary as compatible with Intel CET. [doc](https://docs.microsoft.com/en-us/cpp/build/reference/cetcompat?view=msvc-160).
* `/QSpectre` and `/Qspectre-load` can be used to produce code which mitigates the Spectre vulnerabilities on Intel and AMD. Read the [doc](https://docs.microsoft.com/en-us/cpp/build/reference/qspectre?view=msvc-160) before enabling.

### Code analysis

Recent versions of Visual Studio support "Code Analysis", as documented here: <https://docs.microsoft.com/en-us/cpp/code-quality/code-analysis-for-c-cpp-overview?view=msvc-160>

`/analyze`


### Sanitizers

Visual Studio 2019 introduced support for ASan, documented here: <https://docs.microsoft.com/en-us/cpp/sanitizers/?view=msvc-160>

The `/fsanitize` command line option is documented here: <https://docs.microsoft.com/en-us/cpp/build/reference/fsanitize?view=msvc-160>

Runtime checks (for debug builds): <https://docs.microsoft.com/en-us/cpp/build/reference/rtc-run-time-error-checks?view=msvc-160>


### References
* <https://devblogs.microsoft.com/cppblog/security-features-in-microsoft-visual-c/>
* <https://docs.microsoft.com/en-us/cpp/build/reference/linker-options?view=msvc-160>
* <https://clang.llvm.org/docs/MSVCCompatibility.html>
