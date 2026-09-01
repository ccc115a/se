# build deno

* https://deno.land/manual/contributing/building_from_source
    * https://deno.land/manual@v1.13.1/contributing/building_from_source

確認安裝好 rust, python, 與 VS Community 2019 (選擇套件如下) 

1. Visual C++ tools for CMake
2. Windows 10 SDK (10.0.17763.0)
3. Testing tools core features - Build Tools
4. Visual C++ ATL for x86 and x64
5. Visual C++ MFC for x86 and x64
6. C++/CLI support
7. VC++ 2015.3 v14.00 (v140) toolset for desktop 

然後用 cargo build -vv

## 過程

```
$ git clone --recurse-submodules https://github.com/denoland/deno.git
$ cd deno
$ cargo build -vv
$ ./target/debug/deno run cli/tests/testdata/002_hello.ts
```
