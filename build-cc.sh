#!/bin/bash

workdir=`cd $(dirname $0); pwd`
tgtdir=$workdir/execs/nginx
# tgtdir=/root/nginx
# njs_src_dir=/Users/zong/GitRepos/local/nginx/njs-3f094214cd64
codesdir=$workdir/codes
(
    cd $codesdir/nginx-1.16.1

    set -e
    for option; do
        case $option in 
            conf*)
                # ./configure --prefix=$tgtdir
                ./configure --with-debug --with-cc=/usr/bin/cc --with-cc-opt='-O0 -g' \
                    --prefix=$tgtdir \
                    --with-stream \
                    --add-module=$codesdir/ngx_dynamic_upstream
                    # --add-dynamic-module=$njs_src_dir/nginx
                ;;
            make)
                # bear make # Generates empty compile_commands.json on darwin
                intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++
                ;;
            install)
                mkdir -p $tgtdir
                make install
                cp $workdir/conf.d/nginx.conf $tgtdir/conf/nginx.conf
                ;;
            *)
                echo "$0 [conf[igure]|make|install]"
                ;;
        esac
    done
    set +e
)
