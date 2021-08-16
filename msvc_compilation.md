## Microsoft Visual Studio (2019)

As I am not running Windows, this section is less precise. But recent versions
of Visual Studio support using Clang as a compiler, so all the Clang options
apply.

### Warnings

*All* warnings can be enabled by by using the `/Wall` option, as documented [here](https://docs.microsoft.com/en-us/cpp/preprocessor/compiler-warnings-that-are-off-by-default?view=msvc-160)

### Compilation flags

* `/GS`: Checks buffer security [doc](https://docs.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check?view=msvc-160). (on by default)
* `/sdl`: enables "Strict mode" for `/GS` and additional checks. [doc](https://docs.microsoft.com/en-us/cpp/build/reference/sdl-enable-additional-security-checks?view=msvc-160)
* `/DYNAMICBASE`: Generate PIE code for ASLR (default on for recent)
* `/HIGHENTROPYVA`: High entropy ASLR for 64 bits targets. (default on)
* `/SAFESEH`: Safe Structured Exception Handlers (x86 only) [doc](https://docs.microsoft.com/en-us/cpp/build/reference/safeseh-image-has-safe-exception-handlers?view=msvc-160)
* `/guard:cf`
* `/guard:ehcont`

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
