---
layout: post
title: 增强ruby日志类
description: 增强ruby日志类， 支持多输出。

---
{% highlight ruby %}
class Logger
  # Creates or opens a secondary log file.
  def attach(name)
    @logdev.attach(name)
  end

  # Closes a secondary log file.
  def detach(name)
    @logdev.detach(name)
  end

  class LogDevice # :nodoc:
    attr_reader :devs

    def attach(log)
      @devs ||= {}
      @devs[log] = open_logfile(log)
    end

    def detach(log)
      @devs ||= {}
      @devs[log].close
      @devs.delete(log)
    end

    alias_method :old_write, :write

    def write(message)
      old_write(message)
      #$ch << message
      @devs ||= {}
      @devs.each do |_, dev|
        dev.write(message)
      end
    end
  end
end
#使用示例：
$logger = Logger.new(STDOUT)
$logger_file = File.join(Dir.pwd, 'result.log')
$logger.attach($logger_file)
$logger.error 'logge error'
$logger.warn 'logge warn'
$logger.info 'logge info'
{% endhighlight %}
