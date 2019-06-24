# -*- coding:utf-8 -*-

import cqplus
import os
import random




class MainHandler(cqplus.CQPlusHandler):
    def handle_event(self, event, params):
        # 处理群聊消息
        if event == "on_group_msg":
            msg = params['msg']
            qq = params['from_qq']
            group = params['from_group']
            mess = ''
            if msg == inst['8']:
                path = 'app/me.cqp.kizx.rollgames/activities'
                if not os.path.exists(path):
                    os.mkdir(path)
                mess = '初始化路径成功'
            elif msg == inst['0']:
                mess = '\n'.join(['\n====本插件命令如下====',                                  
                                  inst['1'],
                                  inst['7'],
                                  inst['3']+'+游戏名',
                                  inst['4']+'+游戏名',
                                  inst['5']+'+游戏名+中奖人数',
                                  inst['6']+'+游戏名',
                                  '='*20,
                                  '[CQ:face,id=29]注意以上命令中+表示换行'])
            elif msg == inst['1']:
                mess = '\n'.join(['欢迎老板Roll游戏！',
                                  '↓请按以下格式发送指令↓',
                                  '='*22,
                                  inst['2'],
                                  '游戏名称（注意相同名称会覆盖）',
                                  '描述（如15号开奖）'])
            elif msg == inst['7']:
                path = 'app/me.cqp.kizx.rollgames/activities'
                acti = []
                for filename in os.listdir(path):
                    acti.append(os.path.splitext(filename)[0])
                mess = '当前有如下活动：\n' + '\n'.join(acti)
            else:
                strlist = msg.splitlines()
                try:
                    # 发起活动
                    if strlist[0] == inst['2']:
                        path = 'app/me.cqp.kizx.rollgames/activities/' + \
                            strlist[1] + '.txt'
                        with open(path, 'w') as f:
                            info = self.api.get_group_member_info(
                                group, qq, True)
                            name = info['card'] if info['card'] != '' else info['nickname']
                            f.write('金主：' + str(qq) + ' - ' + name + '\n游戏：'
                                    + strlist[1] + '\n描述：' + strlist[2])
                        mess = '\n'.join(['您已成功发起Roll<' + strlist[1] + '>活动！',
                                          '↓发送以下命令参加活动↓', inst['3'], strlist[1],
                                          '↓发送以下命令查看名单↓', inst['4'], strlist[1]])
                    # 报名参加活动
                    elif strlist[0] == inst['3']:
                        path = 'app/me.cqp.kizx.rollgames/activities/' + \
                            strlist[1] + '.txt'
                        memb = []
                        with open(path, 'r') as f:
                            for line in f:
                                memb.append(line.split(' - ')[0])
                        if str(qq) not in memb:
                            with open(path, 'a') as f:
                                info = self.api.get_group_member_info(
                                    group, qq, True)
                                name = info['card'] if info['card'] != '' else info['nickname']
                                f.write('\n' + str(qq) + ' - ' + name)
                            mess = '恭喜您已成功报名参加roll<' + strlist[1] + '>'
                        else:
                            mess = '您已经参加过了哦，请勿重复报名'
                    # 查看参加成员
                    elif strlist[0] == inst['4']:
                        path = 'app/me.cqp.kizx.rollgames/activities/' + \
                            strlist[1] + '.txt'
                        with open(path, 'r') as f:
                            mastqq = f.readline().split('：')[1].split(' - ')[0]
                            mastqqan = mastqq[:3] + '****' + mastqq[7:]
                            f.seek(0, 0)
                            messlist = []
                            for index, line in enumerate(f):
                                if index == 0:
                                    line = line.replace(mastqq, mastqqan)
                                    messlist.append(line)
                                elif index >= 3:
                                    messlist.append(
                                        line[:3] + '****' + line[7:])
                                else:
                                    messlist.append(line)
                        mess = '\n' + ''.join(messlist)
                    # 开奖
                    elif strlist[0] == inst['5']:
                        path = 'app/me.cqp.kizx.rollgames/activities/' + \
                            strlist[1] + '.txt'
                        with open(path, 'r') as f:
                            mastqq = f.readline().split('：')[1].split(' - ')[0]
                        if str(qq) == mastqq or str(qq) == inst['9']:
                            with open(path, 'r') as f:
                                memb = f.readlines()
                            memb.pop(0)
                            memb.pop(0)
                            memb.pop(0)
                            lucky = random.sample(memb, int(strlist[2]))
                            mess = ''
                            for each in lucky:
                                lucky_qq = each.split(' - ')[0]
                                mess = mess+'[CQ:at,qq='+lucky_qq+']'
                            mess = '[CQ:face,id=99]恭喜欧皇' + mess + '获得了' + \
                                strlist[1] + \
                                '\n[CQ:face,id=30]没有获奖的小伙伴也不要沮丧哦~\nPS.确认无误后请用结束活动命令结束活动'
                        else:
                            mess = '你没有这个权限哦'
                    # 结束活动
                    elif strlist[0] == inst['6']:
                        path = 'app/me.cqp.kizx.rollgames/activities/' + \
                            strlist[1] + '.txt'
                        with open(path, 'r') as f:
                            mastqq = f.readline().split('：')[1].split(' - ')[0]
                        if str(qq) == mastqq or str(qq) == inst['9']:
                            os.remove(path)
                            mess = '已成功删除' + strlist[1] + '活动！'
                        else:
                            mess = '你没有这个权限哦'
                except IndexError:
                    mess = '输入的指令不完整！'
                except ValueError:
                    mess = '输入的指令格式有误！'
                except FileNotFoundError:
                    mess = '输入的活动不存在！'
            if mess != '':
                mess = '[CQ:at,qq=' + str(qq) + ']' + mess
                self.api.send_group_msg(group, mess)

        # 处理私聊消息
        if event == "on_private_msg":
            msg = params['msg']
            qq = params['from_qq']
            self.api.send_private_msg(int(inst['9']), str(qq) + msg)


inst = {'0': '查看命令', '1': '我要roll游戏', '2': '#我要roll游戏#', '3': '我要参加roll游戏',
        '4': '查看名单', '5': '开始roll游戏', '6': '结束活动', '7': '查看当前活动', '8': '初始化',
        '9': '3317200497'}
