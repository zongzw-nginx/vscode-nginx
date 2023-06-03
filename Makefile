
codesdir = $(shell pwd)/codes
tgtdir = $(shell pwd)/targets
confdir = $(shell pwd)/conf.d

nginx_version = 1.24.0

all: config build install

# ./configure --prefix=$(tgtdir)
# check and fix local dependencies like PCRE OpenSSL zlib
config:
	cd $(codesdir)/nginx-$(nginx_version); \
	./configure --with-debug --with-cc=/usr/bin/cc --with-cc-opt='-O0 -g' \
                    --prefix=$(tgtdir)
                    # --with-stream
                    # --add-module=$(codesdir)/ngx_dynamic_upstream
                    # --add-dynamic-module=$njs_src_dir/nginx

# bear make # Generates empty compile_commands.json on darwin
# install intercept-build from https://github.com/rizsotto/scan-build
build:
	cd $(codesdir)/nginx-$(nginx_version); \
	intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++

install:
	mkdir -p $(tgtdir)
	cd $(codesdir)/nginx-$(nginx_version); \
	make install; \
	rm -rf $(tgtdir)/conf/nginx.conf; \
	ln -s $(confdir)/nginx.conf $(tgtdir)/conf/nginx.conf

