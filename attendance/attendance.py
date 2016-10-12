# -*- coding: utf-8 -*-
import sys
import os

FILE = 'GLG_001_10.TXT'
SUFFIX = 'TO_'

TIME_DELTA = 3600

CHECK_IN_UNDEFINED = 0
CHECK_IN_NORMAL = 1
CHECK_IN_LATE   = 2

CHECK_OUT_UNDEFINED = 0
CHECK_OUT_NORMAL = 1
CHECK_OUT_EARLY  = 2

TIME_CHECK_IN_MIN = '4:0:0'
TIME_CHECK_IN = '9:0:0'
TIME_CHECK_OUT = '18:0:0'

USERS = {
    1   : u'周长生',
    10  : u'谢启荣',
    11  : u'魏文伟',
    13  : u'张贵生',
    17  : u'江镜鸿',
    18  : u'杨少婉',
    26  : u'许伟浩',
    28  : u'陈小靖',
    29  : u'林城右',
    44  : u'张嵘',
    62  : u'詹子慰',
    116 : u'陈璇'
}

def parse_daytime(value):
    return value.split(' ')

def parse_day(value):
    return parse_daytime(value)[0]

def parse_time(value):
    return parse_daytime(value)[1]

def to_second(time):
    time_list = time.split(':')
    if len(time_list) == 3:
        [hour, minute, second] = time_list
        return int(hour) * 3600 + int(minute) * 60 + int(second)
    else:
        [hour, minute] = time_list
        second = 0
        return int(hour) * 3600 + int(minute) * 60 + int(second)

def time_delta(time_a, time_b):
    return to_second(time_a) - to_second(time_b)

def abs_time_delta(time_a, time_b):
    return abs(time_delta(time_a, time_b))

def check_same_day(value_a, value_b):
    [DayA, TimeA] = parse_daytime(value_a)
    [DayB, TimeB] = parse_daytime(value_b)
    return DayA == DayB

def check_same_time(value_a, value_b):
    [DayA, TimeA] = parse_daytime(value_a)
    [DayB, TimeB] = parse_daytime(value_b)
    if (DayA == DayB):
        if time_delta(TimeA, TimeB) < TIME_DELTA:
            return True
        else:
            return False
    else:
        return False

def check_in_state(value):
    if time_delta(TIME_CHECK_IN, value) >= 0:
        if time_delta(value, TIME_CHECK_IN_MIN) >= 0:
            # 指定时间之后的签到才算
            return CHECK_IN_NORMAL
        else:
            # 不算，可能是跨天遗留的
            return CHECK_IN_UNDEFINED
    else:
        return CHECK_IN_LATE, time_delta(value, TIME_CHECK_IN)

def check_leave_early(value):
    if time_delta(value, TIME_CHECK_OUT) >= 0:
        return CHECK_OUT_NORMAL
    else:
        return CHECK_OUT_EARLY, time_delta(TIME_CHECK_OUT, value)

# 注册信息
class RegInfo:
    def __init__(self, EnNo, DateTime):
        self.en_no = EnNo
        self.datetime = 0
        self.day = 0
        self.check_in_state = CHECK_IN_UNDEFINED
        self.check_out_state = CHECK_OUT_UNDEFINED
        self.update_state(EnNo, DateTime)

    def update_state(self, EnNo, DateTime):
        if self.en_no != EnNo:
            # 完全不匹配
            return False
        if self.datetime != 0 and not check_same_day(self.datetime, DateTime):
            # 不是同一天的，也不匹配
            return False
        if self.datetime != 0 and check_same_time(self.datetime, DateTime):
            # 重复的签到，不需要处理，处理完毕
            return True
        else:
            self.datetime = DateTime
            [day, time] = parse_daytime(DateTime)
            self.day = day
            if self.check_in_state == CHECK_IN_UNDEFINED:
                self.check_in_state = check_in_state(time)
            elif self.check_out_state == CHECK_OUT_UNDEFINED:
                self.check_out_state = check_out_state(time)
            else:
                print "something wrong of: " + self.en_no + ", " + DateTime
            return True

# 注册信息列表
class RegInfoList:
    def __init__(self):
        self.days = []
        self.info_list = []

    def add(self, EnNo, DateTime):
        self.add_day(DateTime)
        self.add_register(EnNo, DateTime)

    # add to day list
    def add_day(self, DateTime):
        Day = parse_day(DateTime)
        for day in self.days:
            if day == Day:
                return
        self.days.append(Day)
            
    # 添加注册信息
    def add_register(self, EnNo, DateTime):
        for info in self.info_list:
            if info.update_state(EnNo, DateTime):
                # 处理完毕，不再继续查找
                return
        # 整个列表当中都没有，那么生成一个新的信息
        self.info_list.append(RegInfo(EnNo, DateTime))

    # 根据字符串添加注册信息
    def parse_register_info(self, Value):
        if not Value.startswith('No'):
            [No, TMNo, EnNo, Name, GmNo, Mode, DateTime] = Value.split('\t')
            self.add(int(EnNo), DateTime.strip('\r\n'))

    # 统计
    def calc(self, EnNo):
        total_days = 0
        not_days = 0
        total_late_times = 0
        total_late = 0
        for day in self.days:
            info = self.find_info(EnNo, day)
            if info:
                total_days += 1
                if info.check_in_state == CHECK_IN_NORMAL:
                    continue
                elif info.check_in_state == CHECK_IN_UNDEFINED:
                    print "no ", EnNo, USERS.get(EnNo), day
                    not_days += 1
                else:
                    CHECK_IN_LATE, late_time = info.check_in_state
                    print info.en_no, USERS.get(info.en_no), info.datetime
                    total_late_times += 1
                    total_late += late_time
            else:
                print "no ", EnNo, USERS.get(EnNo), day
                not_days += 1
        return EnNo, USERS.get(EnNo), total_days, not_days, total_late_times, total_late

    # 根据 id 和日期信息查找注册信息
    def find_info(self, EnNo, Day):
        for info in self.info_list:
            if info.en_no == EnNo and info.day == Day:
                return info
            
def generate():
    fr = open(FILE, 'r')
    AllInfo = fr.readlines()
    fr.close()
    info_list = RegInfoList()
    for value in AllInfo:
        info_list.parse_register_info(value)
    fw = open(SUFFIX + FILE, 'w')
    fw.write(u"考勤号\t名字\t出勤天数\t缺勤天数\t迟到次数\t累计迟到时间（分钟）\t是否全勤" + os.linesep)
    for key in USERS.keys():
        Id, Name, Days, NotDays, LateTimes, Late = info_list.calc(key)
        fw.write(str(Id) + "\t" + Name + "\t" + str(Days) + "\t" + str(NotDays) + "\t" + str(LateTimes) + "\t" + str(Late / 60) + '\t0' + os.linesep)
    fw.close()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    generate()

