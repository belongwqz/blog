---
layout: post
title: kafka topic迁移
description: kafka reblance或指定topic到自定义broker列表步骤。

---


1、生成move.json，用户生成迁移信息，示例：
{% highlight json %}
{
    "topics": [
        {
            "topic": "TOPIC名称"
        }
    ],
    "version": 1
}
{% endhighlight %}

2、生成迁移建议，将“Proposed partition reassignment configuration”后的内容写入reassign.json，根据需要进行修改
{% highlight shell %}
kafka-reassign-partitions.sh --broker-list "broker id list，逗号分隔" --topics-to-move-json-file move.json --zookeeper ZK地址 --generate
{% endhighlight %}
reassign.json样例：
{% highlight json %}
{
    "version": 1,
    "partitions": [
        {
            "topic": "TOPIC_NAME",
            "partition": 0,
            "replicas": [
                1,
                2
            ]
        },
        {
            "topic": "TOPIC_NAME",
            "partition": 3,
            "replicas": [
                1,
                2
            ]
        },
        {
            "topic": "TOPIC_NAME",
            "partition": 2,
            "replicas": [
                1,
                2
            ]
        },
        {
            "topic": "TOPIC_NAME",
            "partition": 1,
            "replicas": [
                1,
                2
            ]
        }
    ]
}
{% endhighlight %}

3、开始迁移，会提示当前状态的json，用于回滚，自行拷贝备份
{% highlight shell %}
kafka-reassign-partitions.sh --broker-list "broker id list，逗号分隔" --reassignment-json-file reassign.json --zookeeper  ZK地址  --execute
{% endhighlight %}

4、查看迁移进度
{% highlight shell %}
kafka-reassign-partitions.sh --verify --zookeeper  ZK地址--reassignment-json-file reassign.json
{% endhighlight %}

5、查看迁移后的分布情况
{% highlight shell %}
kafka-topics.sh --zookeeper  ZK地址 --topic TOPIC名称 --describe
{% endhighlight %}
