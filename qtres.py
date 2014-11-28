# -*- coding: utf-8 -*-

class ReportStyle:
    """
    报告的样式内容，这里仅支持office2003的样式。
    """
    #标题行的格式
    TitleStyle = 'font:bold True, color black;' \
                 'borders: left thick, right thick, top thick, bottom thick;' \
                 'pattern: pattern solid, fore_colour bright_green;'
    #内容行的格式
    ContentStyle = 'borders: left thin, right thin, top thin, bottom thin;' \
                   'pattern: pattern solid, fore_colour white;'


class Data:
    """
    数据源的结构

    用于描述数据源的结构，也就是xml文件的关键字，由于dict类型会自动排序，为了保证顺序，后面加了一个数字表标识
    1、Excel 07-2003一个工作表最多可有65536行，行用数字1—65536表示;最多可有256列，列用英文字母A—Z，AA—AZ，BA—BZ，……，IA—IV表示；
    一个工作簿中最多含有255个工作表，默认情况下是三个工作表；
    2、Excel 2007及以后版本，一个工作表最多可有1048576行，16384列；
    """
    MaxSizeInOneZip = 1000
    MaxRowCountInExcel2003 = 65535
    MaxColumnCountInExcel2003 = 256
    MaxRowCountInExcel2007 = 1048576
    MaxColumnCountInExcel2007 = 16384

    DateTimeFormat = '%Y-%m-%d %H:%M:%S'

    #时间间隔选择，365天表示一年之内的统计。
    MaxDataDelta = 365

    #数据表
    UsersNumberTable = 'user'
    ChannelTable = 'channel'
    UserDetailTable = 'detail'
    HistoryTable = 'his'
    ScheduleTable = 'sch'
    OnlineTable = 'online'

    #属性关键字
    struct = 'struct'
    fileRule = 'filter'
    flag = 'flag'
    childFlag = 'childFlag'
    mapInfo = 'map'
    other = 'other'

    Info = {
        UsersNumberTable: {
            struct: {
                'DateField': ['datetime', 0],  #这个字段是自定义的
                'OrganizationID': ['str', 1],
                'OrganizationName': ['str', 2],
                'TotalUserNumber': ['int', 3]
            },
            fileRule: '[\w]*_orgUserStatistics.xls$',
            flag: None,
            childFlag: None,
            mapInfo: None,
            other: None
        },
        ChannelTable: {
            struct: {
                'ChannelName': ['str', 0],
                'TelNumber': ['str', 1]
            },
            fileRule: 'sxy_daily_log_[\d]{%d}.zip$' % len('20130724'),
            flag: None,
            childFlag: None,
            mapInfo: {
                #'﻿渠道名称': 'ChannelName',
                '渠道名称': 'ChannelName',
                '手机号码': 'TelNumber'
            },
            other: 'GMCCMMEET'  # 广东移动随心议业务组织ID
        },
        UserDetailTable: {
            struct: {
                'Creator': ['str', 0],
                'OrgID': ['str', 1],
                'ConfID': ['str', 2],
                'StartTime': ['datetime', 3],
                'EndTime': ['datetime', 4],
                'ConfLength': ['int', 5],
                'CallerCount': ['int', 6],
                'RealCallerCount': ['int', 7],
                'ChannelID': ['int', 8]
            },
            fileRule: None,
            flag: None,
            childFlag: None,
            mapInfo: None,
            other: None
        },
        HistoryTable: {
            struct: {
                'his:ConferenceID': ['str', 0],
                'his:SubConferenceID': ['str', 1],
                'his:WebAccount': ['str', 2],
                'his:OrganizationID': ['str', 3],
                'his:StartTime': ['datetime', 4],
                'his:FactEndTime': ['datetime', 5],
                'his:FactLength': ['int', 6]
            },
            fileRule: '[\w]*_historyconf.zip$',
            flag: 'his:HistoryConfReport',
            childFlag: None,
            mapInfo: None,
            other: None
        },
        ScheduleTable: {
            struct: {
                'sch:SchTime': ['datetime', 0],
                'sch:IsSuc': ['str', 1],
                'sch:MeetingID': ['str', 2],
                'sch:MeetingFrequency': ['str', 3],
                'sch:MeetingMode': ['str', 4],
                'sch:ServiceMode': ['str', 5],
                'sch:OrganizationID': ['str', 6],
                'sch:UserID': ['str', 7],
                'sch:StartTime': ['datetime', 8],
                'sch:EndTime': ['datetime', 9],
                'sch:OrderParty': ['int', 10],
                'sch:MediaType': ['str', 11],
                'sch:AudioPortResource': ['int', 12],
                'sch:VideoPortResource': ['int', 13],
                'sch:MultiPicResource': ['int', 14],
                'sch:AdapterResource': ['int', 15],
                'sch:BandwidthResource': ['int', 16],
                'sch:CurrentTelepresenceParty': ['int', 17],
                'sch:PayAccount': ['str', 18],
                'sch:GroupID': ['str', 19],
                'sch:EncryptMode': ['str', 20]
            },
            fileRule: '[\w]*_scheduleconf.zip$',
            flag: 'sch:SchConfReport',
            'childFlag': 'sch:Record',
            mapInfo: None,
            other: None
        },
        OnlineTable: {
            struct: {
                'con:SessionID': ['str', 0],
                'con:MeetingID': ['str', 1],
                'con:OrganizationID': ['str', 2],
                'con:UserID': ['int', 3],
                'con:IsDataConf': ['str', 4],
                'con:MeetingFrequency': ['str', 5],
                'con:MeetingMode': ['str', 6],
                'con:ServiceMode': ['str', 7],
                'con:UserMedia': ['str', 8],
                'con:SdpInfo': ['str', 9],
                'con:UserNumber': ['str', 10],
                'con:AccessNumber': ['str', 11],
                'con:StartTime': ['datetime', 12],
                'con:EndTime': ['datetime', 13],
                'con:MediaType': ['str', 14],
                'con:BillType': ['str', 15],
                'con:PayAccount': ['str', 16],
                'con:ExitCode': ['str', 17],
                'con:GroupID': ['str', 18],
                'con:MainConfID': ['str', 19],
                'con:EncryptMode': ['str', 20]
            },
            fileRule: '[\w]*_conf.zip',
            flag: 'con:ConfReport',
            childFlag: None,
            mapInfo: None,
            other: None
        }
    }


class LanRes:
    """
    资源类

    用于存放语言信息
    """

    #支持的语言类型
    LanSupport = {
        'zh-cn': u'简体中文',
        'en-us': 'English'
    }

    #默认语言类型，可以从外面修改
    Type = 'en-us'

    mapData = {
        Data.HistoryTable: 'sheetHistoryList',
        Data.ScheduleTable: 'sheetSchedule',
        Data.OnlineTable: 'sheetOnline',
        Data.UsersNumberTable: 'sheetUsersNumber',
        Data.UserDetailTable: 'sheetUserDetail',
        Data.ChannelTable: 'sheetChannel'
    }

    @staticmethod
    def getTable(dataType):
        if dataType == Data.HistoryTable:
            return LanRes.I()[LanRes.mapData[dataType]][2]['sheetName']
        else:
            return LanRes.I()[LanRes.mapData[dataType]]['sheetName']

    @staticmethod
    def I():
        return LanRes.Info[LanRes.Type]

    #资源体
    Info = {
        'zh-cn': {
            'setting': '参数设置',
            'language': '选择语言',
            'winTitle': '融合会议业务数据分析工具',
            'execStat': '执行统计',
            'openResultPath': '打开结果目录',
            'dataSource': '数据源目录',
            'startDate': '开始日期',
            'endDate': '结束日期',
            'initState': '未启动……',
            'dateFormat': 'yyyy年M月d日',
            'ifPubOrgData': '是否导出原始数据',
            'warnCaption': u'警告',
            'askCaption': u'请确认',
            'dataSourceCation': u'数据源选择',
            'process': '当前操作进度',
            'loading': u'正在加载[%s]',
            'outOfMemory': u'数据过大，停止处理。',
            'single': u'已经有一个实例在运行！',
            'finding': u'正在发现文件！',
            'noData': u'数据源没有数据！',
            'waiting': u'请稍后……',
            'other': u'其他',
            'processTable': u'正在处理[%s]，请稍后……',
            'askMsg':{
                'taskNotFinish':u'任务未结束，是否确认退出?'
            },
            'errorMsg': {
                'canNotOpenFile': u'请确保没有打开报表文件。',
                'singleInstance': u'已经有实例在运行！'
            },
            'warnMsg': {
                'noDataSource': u'数据源路径无效！',
                'dataIsWrong': u'结束日期需大于开始日期且不得大于12个月！',
                'fileNotExist': u'文件不存在',
                'comTip': u'建议在软件运行期间保证excel为关闭状态！',
                'closeExcel': u'请先关闭excel！'
            },
            'info': {
                'beginStat': u'开始统计[%s]到[%s]的数据……',
                'statFinish': u'[%s]到[%s]的统计完成',
                'beginMakeReport': u'开始生成报告……',
                'makeReportFinish': u'结果路径：[%s]。\n耗时：[%d]（秒）。',
                'beginReadSource': u'开始读取数据源……',
                'ReadSourceFinish': u'读取数据源完成',
                'waitForLastAction': u'请先等待上一次操作完成……'
            },
            'sheetUsersNumber': {
                'sheetName': u'累计用户数',
                'title': {
                    0: u'日期',
                    1: u'组织ID',
                    2: u'组织名',
                    3: u'用户数'
                },
                'isOrg': False
            },
            'sheetUserDetail': {
                'sheetName': u'用户会议明细',
                'title': {
                    0: u'会议发起者',
                    1: u'组织ID',
                    2: u'会议ID',
                    3: u'开始时间',
                    4: u'实际结束时间',
                    5: u'实际会议时长(分钟)',
                    6: u'发起通话人数',
                    7: u'实际通话人次',
                    8: u'渠道ID'
                },
                'isOrg': False
            },
            'sheetChannel': {
                'sheetName': u'随心意用户渠道统计',
                'title': {
                    0: u'渠道类型',
                    1: u'活跃用户数',
                    2: u'通话总次数',
                    3: u'通话总时长',
                    4: u'户均通话次数',
                    5: u'户均通话时长(分钟)'
                },
                'isOrg': False
            },
            'sheetHistoryList': {
                0: {
                    'sheetName': u'用户会议统计',
                    'title': {
                        0: u'会议发起者',
                        1: u'组织ID',
                        2: u'%s会议数',
                        3: u'%s会议时长(分钟)'
                    },
                    'isOrg': False
                },
                1: {
                    'sheetName': u'组织会议统计',
                    'title': {
                        0: u'组织ID',
                        1: u'%s会议数',
                        2: u'%s会议时长(分钟)'
                    },
                    'isOrg': False
                },
                2: {
                    'sheetName': u'【原始数据】历史会议记录',
                    'title': {
                        0: u'会议ID',
                        1: u'子会议ID',
                        2: u'会议发起者',
                        3: u'组织ID',
                        4: u'开始时间',
                        5: u'实际结束时间',
                        6: u'实际会议时长(分钟)'
                    },
                    'isOrg': True
                }
            },
            'sheetSchedule': {
                'sheetName': u'【原始数据】预定会议记录',
                'title': {
                    0: u'预定时间',
                    1: u'是否预定成功',
                    2: u'会议ID',
                    3: u'会议控制模式',
                    4: u'会议模式',
                    5: u'会议业务模式',
                    6: u'组织ID',
                    7: u'用户ID',
                    8: u'会议开始时间',
                    9: u'会议结束时间',
                    10: u'会议方数',
                    11: u'会议媒体类型',
                    12: u'预留音频资源数',
                    13: u'预留视频资源数',
                    14: u'预留多画面资源数',
                    15: u'预留适配资源数',
                    16: u'预留带宽资源数',
                    17: u'智真终端数',
                    18: u'付费帐号',
                    19: u'群组号',
                    20: u'加密模式'
                },
                'isOrg': True
            },
            'sheetOnline': {
                'sheetName': u'【原始数据】与会者记录',
                'title': {
                    0: u'用户腿标记',
                    1: u'会议ID',
                    2: u'组织ID',
                    3: u'用户ID',
                    4: u'是否数据会议',
                    5: u'会议控制模式',
                    6: u'会议模式',
                    7: u'会议业务模式',
                    8: u'用户媒体类型',
                    9: u'音视频编解码',
                    10: u'与会者号码',
                    11: u'会议接入码',
                    12: u'接入会议时间',
                    13: u'退出会议时间',
                    14: u'会议媒体类型',
                    15: u'话单类型',
                    16: u'付费帐号',
                    17: u'退出方式',
                    18: u'群组号',
                    19: u'主会议ID',
                    20: u'是否加密'
                },
                'isOrg': True
            },
            'yearMonthFormat': u'[%d年%d月]'
        },
        'en-us': {
            'setting': 'Settings',
            'language': 'Language',
            'winTitle': 'CCS Service Data Analyzer',
            'execStat': 'Start Analysis',
            'openResultPath': 'Open Result Path',
            'dataSource': 'Source path',
            'startDate': 'Start date',
            'endDate': 'End date',
            'initState': 'Not started.',
            'dateFormat': 'yyyy-M-d',
            'ifPubOrgData': 'Export original data',
            'warnCaption': u'Warning',
            'askCaption': u'Confirm',
            'dataSourceCation': u'Select Data Source',
            'process': 'Progress',
            'loading': u'Loading [%s]',
            'outOfMemory': u'Processing failed because the data is too large.',
            'single': u'An instance is already running.',
            'finding': u'Detecting files…',
            'noData': u'No data found in the data source.',
            'waiting': u'Please wait…',
            'other': u'other',
            'processTable': u'processing[%s],please wait…',
            'askMsg':{
                'taskNotFinish':u'The task is in progress. Are you sure you want to exit?'
            },
            'errorMsg': {
                'canNotOpenFile': u'Please ensure that no statistics file has been opened.',
                'singleInstance': u'An instance is already running.'
            },
            'warnMsg': {
                'noDataSource': u'Invalid data source path.',
                'dataIsWrong': u'The end date must be later than the start date and the duration must not exceed 12 months.',
                'fileNotExist': u'The file does not exist.',
                'comTip': u'Please ensure that Excel is closed during the running of this analyzer.',
                'closeExcel': u'Please close Excel.'
            },
            'info': {
                'beginStat': u'Analyzing the data from [%s] to [%s]...',
                'statFinish': u'The analyzer has finished analyzing the data from [%s] to [%s].',
                'beginMakeReport': u'Generating report…',
                'makeReportFinish': u'Result path:[%s].\nTime spent:[%d] seconds.',
                'beginReadSource': u'Reading data source…',
                'ReadSourceFinish': u'Data source reading completed.',
                'waitForLastAction': u'Please wait for the previous task to complete.'
            },
            'sheetUsersNumber': {
                'sheetName': u'Total number of users',
                'title': {
                    0: u'date',
                    1: u'Organization ID',
                    2: u'Organization Name',
                    3: u'Users number'
                },
                'isOrg': False
            },
            'sheetUserDetail': {
                'sheetName': u'User Conference Details',
                'title': {
                    0: u'Web ID',
                    1: u'Organization ID',
                    2: u'Conference ID',
                    3: u'The fact start Time',
                    4: u'The fact end time',
                    5: u'The fact conference length(min)',
                    6: u'Number of parties',
                    7: u'Actual call times',
                    8: u'Channel ID'
                },
                'isOrg': False
            },
            'sheetChannel': {
                'sheetName': u'Channel statistics(GMCCMMEET)',
                'title': {
                    0: u'Channel Type',
                    1: u'Number of active users',
                    2: u'The total number of calls',
                    3: u'Total call duration',
                    4: u'The average number of calls',
                    5: u'The average call duration(min)'
                },
                'isOrg': False
            },
            'sheetHistoryList': {
                0: {
                    'sheetName': u'User conference',
                    'title': {
                        0: u'Web ID',
                        1: u'Organization ID',
                        2: u'Conference count during the %s',
                        3: u'Conference length during the %s(min)'
                    },
                    'isOrg': False
                },
                1: {
                    'sheetName': u'Organization conference',
                    'title': {
                        0: u'Organization ID',
                        1: u'Conference count during the %s',
                        2: u'Conference length during the %s'
                    },
                    'isOrg': False
                },
                2: {
                    'sheetName': u'History conference records',
                    'title': {
                        0: u'Conference ID',
                        1: u'Sub conference ID',
                        2: u'Web ID',
                        3: u'Organization ID',
                        4: u'The fact start Time',
                        5: u'The fact end time',
                        6: u'The fact conference length(min)'
                    },
                    'isOrg': True
                }
            },
            'sheetSchedule': {
            'sheetName': u'Conference Scheduling Records',
                'title': {
                    0: u'Scheduling time',
                    1: u'Is the scheduling successful',
                    2: u'Conference ID',
                    3: u'Conference control mode',
                    4: u'Conference mode',
                    5: u'Conference service mode',
                    6: u'Organization ID',
                    7: u'User ID',
                    8: u'Start time',
                    9: u'End time',
                    10: u'Number of parties',
                    11: u'Conference media type',
                    12: u'Reserved audio resources',
                    13: u'Reserved video resources',
                    14: u'Reserved multi-picture resources',
                    15: u'Reserved adaptation resources',
                    16: u'Reserved bandwidth resources',
                    17: u'Number of Telepresence terminals',
                    18: u'Payment account',
                    19: u'Group number',
                    20: u'Encrypt mode'
                },
                'isOrg': True
            },
            'sheetOnline': {
            'sheetName': u'Attend Conference records',
                'title': {
                    0: u'User leg flag',
                    1: u'Conference ID',
                    2: u'Organization ID',
                    3: u'User ID',
                    4: u'Data conference or not',
                    5: u'Conference control mode',
                    6: u'Conference mode',
                    7: u'Conference service mode',
                    8: u'User media type',
                    9: u'Audio/video codec',
                    10: u'Participant number',
                    11: u'Conference access number',
                    12: u'Join time',
                    13: u'Exit time',
                    14: u'Conference media type',
                    15: u'CDR type',
                    16: u'Payment account',
                    17: u'Exit mode',
                    18: u'Group number',
                    19: u'Main Conference ID',
                    20: u'Encrypted',
                },
                'isOrg': True
            },
            'yearMonthFormat': u'[%d-%d]'
        }
    }
