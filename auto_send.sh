#!/bin/sh
#!/usr/bin/ebook-convert
#!/usr/bin/calibre-smtp

if [ ! "$1" ]
then
    echo "必须输入文件名"
    exit 1
fi

if [ ! "$2" ]
then
    echo "必须输入作者名"
    exit 1
fi
if [ ! "$3" ]
then
    echo "必须输入储存地址"
    exit 1
fi
base_dist="$3"
author="$2"
txt_url="$base_dist""$1"".txt"
out_put="$base_dist""$1"".mobi"
mobi_name="$base_dist""$1"".mobi"


echo $txt_url
if [ ! -e $txt_url ]
then
    echo "当前无该文件"
    exit 2
fi
ebook-convert "$txt_url" "$mobi_name"  --input-profile=kindle --output-profile=kindle_pw3  --change-justification=left  --smarten-punctuation --enable-heuristics --language=zh --authors="$author"


#calibre-smtp -a "$mobi_name" -p ebsjyzhocgrsjgjb -r smtp.qq.com --port=465 -e SSL -u wezhyn@qq.com wezhyn@qq.com wezhyn@kindle.cn ""

