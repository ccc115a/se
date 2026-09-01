Hero3C@DESKTOP-O093POU MINGW64 /c/ccc/course/sa/js/ffi/callrust/deno-image-transform (main)
$ make run
docker build -t deno-image-transform .
[+] Building 18.0s (5/19)
 => [internal] load metadata for docker.io/library/rust:1.49.0-buster@  14.7s 
 => [internal] load build context                                        0.1s 
 => => transferring context: 460.31kB                                    0.1s 
[+] Building 18.1s (5/19)
 => [rust 1/7] FROM docker.io/library/rust:1.49.0-buster@sha256:cf80a77  3.2s 
 => => sha256:cf80a77b3c4b1717558c1757bfdfb8ac347cd6da2e9ec 988B / 988B  0.0s 
 => => sha256:8d0d570729498de885e6b4b6be16cf1019f767ae9 6.42kB / 6.42kB  0.0s 
[+] Building 111.0s (8/19)
 => [internal] load build definition from Dockerfile                     0.0s 
 => => transferring dockerfile: 959B                                     0.0s 
 => [internal] load .dockerignore                                        0.0s 
 => => transferring context: 62B                                         0.0s 
 => [internal] load metadata for docker.io/hayd/debian-deno:1.6.2@sha2  13.7s 
 => [internal] load metadata for docker.io/library/rust:1.49.0-buster@  14.7s 
 => [internal] load build context                                        0.1s 
 => => transferring context: 460.31kB                                    0.1s 
 => CANCELED [rust 1/7] FROM docker.io/library/rust:1.49.0-buster@sha2  96.1s 
 => => resolve docker.io/library/rust:1.49.0-buster@sha256:cf80a77b3c4b  0.0s 
 => => sha256:cf80a77b3c4b1717558c1757bfdfb8ac347cd6da2e9ec 988B / 988B  0.0s 
 => => sha256:8d0d570729498de885e6b4b6be16cf1019f767ae9 6.42kB / 6.42kB  0.0s 
 => => sha256:6fb337bee09ea655d20ddb226f48e5f2caa911193 1.59kB / 1.59kB  0.0s 
 => => sha256:6c33745f49b41daad28b7b192c447938452ea4 45.09MB / 50.40MB  96.0s 
 => => sha256:ef072fc32a84ef237dd4fcc7dff2c5e2a77565f2 7.81MB / 7.81MB  61.8s 
 => => sha256:c0afb8e68e0bcdc1b6e05acaa713a6fe0d81808 9.44MB / 10.00MB  96.0s
 => => sha256:d599c07d28e6c920ef615f4f9b5cd0d52eb106f 5.24MB / 51.83MB  96.0s 
 => [deno 1/7] FROM docker.io/hayd/debian-deno:1.6.2@sha256:7180ef661e  68.0s 
 => => resolve docker.io/hayd/debian-deno:1.6.2@sha256:7180ef661ea29d69  0.0s 
 => => sha256:7180ef661ea29d697f9ad667bb691dfbf36b34b2f 1.36kB / 1.36kB  0.0s 
 => => sha256:48bab3db377a6e87c2a81522c6c3b0db4c4f6e96f 4.09kB / 4.09kB  0.0s 
 => => sha256:53d9ee195005b42e4b6f4d20b445f1aedcc597 27.10MB / 27.10MB  61.9s 
 => => sha256:f366e7eeb66bef8f910f913e8e8d076d97cb32 21.26MB / 21.26MB  42.1s 
 => => sha256:ad98f069c3d0963b046e133d5f53a473ac6479928 2.08kB / 2.08kB  2.4s 
 => => sha256:e3d0a883c479337dc9f613793b7e79fad8a6d6ca92ae0 309B / 309B  4.3s 
 => => sha256:7e31b1941ff7b4dd47a0af027a6a8248dd1be756fc488 310B / 310B  6.1s 
 => => extracting sha256:53d9ee195005b42e4b6f4d20b445f1aedcc597f688f5b7  3.5s 
 => => extracting sha256:f366e7eeb66bef8f910f913e8e8d076d97cb32b28722a3  1.7s 
 => => extracting sha256:ad98f069c3d0963b046e133d5f53a473ac647992870661  0.1s 
 => => extracting sha256:e3d0a883c479337dc9f613793b7e79fad8a6d6ca92ae03  0.0s 
 => => extracting sha256:7e31b1941ff7b4dd47a0af027a6a8248dd1be756fc4886  0.0s 
 => ERROR [deno 2/7] RUN apt-get update &&   apt-get install make=4.2.  28.1s 
------
 > [deno 2/7] RUN apt-get update &&   apt-get install make=4.2.1-1.2 -y:      
#6 1.662 Ign:1 http://security.debian.org/debian-security stable/updates InRelease
#6 1.768 Get:2 http://deb.debian.org/debian stable InRelease [113 kB]
#6 2.063 Err:3 http://security.debian.org/debian-security stable/updates Release
#6 2.063   404  Not Found [IP: 151.101.2.132 80]
#6 3.342 Get:4 http://deb.debian.org/debian stable-updates InRelease [36.8 kB]#6 3.848 Get:5 http://deb.debian.org/debian stable/main amd64 Packages [8178 kB]
#6 25.79 Reading package lists...
#6 27.16 E: The repository 'http://security.debian.org/debian-security stable/updates Release' does not have a Release file.
------
executor failed running [/bin/sh -c apt-get update &&   apt-get install make=4.2.1-1.2 -y]: exit code: 100
make: *** [Makefile:26: docker-build] Error 1