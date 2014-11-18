---
layout: post
title: rubymine安装ruby-debug-base19x失败的解决办法
description: rubymine安装ruby-debug-base19x失败导致不能使用ruby-debug-ide的解决办法。

---
1. 将存在的ruby-debug-base19x、ruby-debug-ide、ruby_core_source、debugger-linecache、debugger-ruby_core_source等相关的gem卸载；
1. gem update --system 2.3.0；
1. 下载http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p545.tar.gz(解压到F盘生成F:/ruby-1.9.3-p545路径)；
1. 下载http://rubyforge.org/frs/download.php/75414/linecache19-0.5.13.gem；
1. gem install linecache19-0.5.13.gem ---with-ruby-include=F:/ruby-1.9.3-p545；
1. gem install --pre ruby-debug-base19x；
1. gem install ruby-debug-ide；
1. 搞定。
