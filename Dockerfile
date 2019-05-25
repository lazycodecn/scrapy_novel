FROM ubuntu

MAINTAINER wezhyn (wezhyn@163.com)
ENV TZ=Asia/Shanghai
ENV LANG=C.UTF-8

ADD . /novel

WORKDIR /novel

VOLUME /kindle


RUN    sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt-get update  \
    && apt-get install -y cron \
    && touch /novel/novel.log
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get install tzdata \
    && apt-get -y install calibre \
    && apt-get install -y python3-pip \
    && pip3 install pyyaml   -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

CMD service cron start && crontab /novel/root && tail -f /novel/novel.log
