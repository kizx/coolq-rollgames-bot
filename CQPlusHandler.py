# -*- coding:utf-8 -*-

import cqplus
import os
from random import sample
import sqlite3


class sqlHandle:
    def __init__(self, Env, QQ, Group):
        self.env = Env
        self.qq = QQ
        self.group = Group
        self.con = sqlite3.connect('app/me.cqp.kizx.rollgames/activities.db')
        self.cur = self.con.cursor()

    def __del__(self):
        self.cur.close()
        self.con.commit()
        self.con.close()

    def create(self, game):
        '''新建活动'''
        self.cur.execute(
            'create table '+game+'(id integer primary key autoincrement,qq int64,name text)')
        info = cqplus._api.get_group_member_info(
            self.env, self.group, self.qq, True)
        name = info['card'] if info['card'] != '' else info['nickname']
        self.cur.execute('insert into '+game +
                         '(qq,name) values(?,?)', (self.qq, name))
        mess = '\n'.join(['\n您已成功发起roll"' + game + '"活动！',
                          '===发送以下命令参加活动===', inst['3'], game,
                          '===发送以下命令查看名单===', inst['4'], game])
        return mess

    def join(self, game):
        '''参加活动'''
        self.cur.execute('select qq from '+game+' where id>1')
        memlist = []
        for row in self.cur.fetchall():
            memlist.append(row[0])
        if self.qq not in memlist:
            info = cqplus._api.get_group_member_info(
                self.env, self.group, self.qq, True)
            name = info['card'] or info['nickname']
            self.cur.execute('insert into '+game +
                             '(qq,name) values(?,?)', (self.qq, name))
            mess = '恭喜您已成功报名参加roll<' + game + '>'
        else:
            mess = '你已经参加过了哦，请勿重复报名'
        return mess

    def view_memb(self, game):
        '''查看已报名参加人员名单'''
        self.cur.execute('select qq from '+game)
        mastqq = self.cur.fetchone()
        mastqq = mastqq+(inst['10'],)
        if self.qq in mastqq:
            self.cur.execute('select qq,name from '+game+' where id>1')
            memlist = self.cur.fetchall()
            mess = '\n已报名参加'+game+'名单如下：'
            for row in memlist:
                miqq = str(row[0])
                anqq = miqq[:3] + '****' + miqq[7:]
                mess = mess+'\n'+anqq+' - '+row[1]
        else:
            mess = '你没有这个权限哦'
        return mess

    def roll(self, game):
        '''roll游戏'''
        self.cur.execute('select qq from '+game)
        mastqq = self.cur.fetchone()
        mastqq = mastqq+(inst['10'],)
        if self.qq in mastqq:
            self.cur.execute('select qq from '+game+' where id>1')
            memlist = self.cur.fetchall()
            qqlist = []
            for row in memlist:
                qqlist.append(row[0])
            lucky = sample(qqlist, 1)
            mess = '[CQ:at,qq='+str(lucky[0])+']'
            mess = '\n[CQ:face,id=99]恭喜欧皇' + mess + '获得了' + game + \
                '\n[CQ:face,id=30]没有获奖的小伙伴也不要沮丧哦~\nPS.确认无误后请用结束活动命令删除活动'
        else:
            mess = '你没有这个权限哦'
        return mess

    def endgame(self, game):
        '''结束活动'''
        self.cur.execute('select qq from '+game)
        mastqq = self.cur.fetchone()
        mastqq = mastqq+(inst['10'],)
        if self.qq in mastqq:
            self.cur.execute('drop table '+game)
            mess = '已成功删除' + game + '活动！'
        else:
            mess = '你没有这个权限哦'
        return mess

    def timer_swich(self, isoff):
        '''定时播报开关'''
        path = 'app/me.cqp.kizx.rollgames/setting.ini'
        if isoff == '开启' or isoff == '关闭':
            if self.qq == inst['10']:
                with open(path, 'w') as f:
                    f.write(str(self.group) + ' - ' + isoff)
                    mess = '定时播报已' + isoff
            else:
                mess = '你没有这个权限哦'
        else:
            mess = '输入的指令格式有误！'
        return mess


class Handle():

    def menu(self):
        '''查看所有命令'''
        mess = '\n'.join(['\n====本插件命令如下====',
                          inst['2']+'+游戏名',
                          inst['3']+'+游戏名',
                          inst['4']+'+游戏名',
                          inst['9']+'+游戏名',
                          inst['6']+'+游戏名',
                          inst['7'],
                          inst['11']+'+开启/关闭',
                          '='*20,
                          '[CQ:face,id=29]注意以上命令中+表示换行'])
        return mess

    def view_acti(self):
        '''查看当前活动'''
        con = sqlite3.connect('app/me.cqp.kizx.rollgames/activities.db')
        cur = con.cursor()
        cur.execute("select name from sqlite_sequence")
        acti = []
        for row in cur.fetchall():
            acti.append(row[0])
        if acti == []:
            mess = '当前没有活动哦~要不你来整一个[CQ:face,id=178]'
        else:
            mess = '当前有如下活动：\n' + '\n'.join(acti)
        cur.close()
        con.close()
        return mess


class MainHandler(cqplus.CQPlusHandler):
    def handle_event(self, event, params):
        # 处理群聊消息
        if event == "on_group_msg":
            msg = params['msg']
            mess = ''
            if msg in dic1:
                msgHandle = Handle()
                mess = dic1[msg](msgHandle)
            else:
                strlist = msg.splitlines()
                if strlist[0] in dic2:
                    sqlmsg = sqlHandle(
                        params['env'], params['from_qq'], params['from_group'])
                    try:
                        mess = dic2[strlist[0]](sqlmsg, strlist[1])
                    except sqlite3.OperationalError as e:
                        mess = '\n'+str(e)
                    except ValueError:
                        mess = '\n找不到对象'
                    finally:
                        del sqlmsg
            if mess != '':
                mess = '[CQ:at,qq=' + str(params['from_qq']) + ']' + mess
                self.api.send_group_msg(params['from_group'], mess)

        # 定时器消息(功能有待完善)
        if event == 'on_timer':
            if params['name'] == '1min':
                path = 'app/me.cqp.kizx.rollgames/setting.ini'
                with open(path, 'r') as f:
                    setting = f.readline().split(' - ')
                    if setting[1] == '开启':
                        msgHandle = Handle()
                        mess = msgHandle.view_acti()
                        if mess != '当前没有活动哦~要不你来整一个[CQ:face,id=178]':
                            self.api.send_group_msg(int(setting[0]), mess)

        # 菜单动作
        # if event == 'on_menu':
        #     if params['name'] == 'menu01':
        #         self.api.send_private_msg(inst['10'], '菜单01被点击')

        # 处理私聊消息
        # if event == "on_private_msg":
        #     msg = params['msg']
        #     qq = params['from_qq']
        #     self.api.send_private_msg(inst['10'], str(qq) + '发送了：' + msg)


inst = {'0': '查看命令', '2': '!!!我要roll游戏#', '3': '我要参加roll游戏', '4': '查看名单',
        '6': '结束活动', '7': '查看当前活动', '9': '!!!开始roll游戏', '10': 3317200497, '11': '定时器'}
dic1 = {'查看命令': Handle.menu, '查看当前活动': Handle.view_acti}
dic2 = {'!!!我要roll游戏': sqlHandle.create, '我要参加roll游戏': sqlHandle.join, '查看名单': sqlHandle.view_memb,
        '!!!开始roll游戏': sqlHandle.roll, '结束活动': sqlHandle.endgame, '定时器': sqlHandle.timer_swich}
