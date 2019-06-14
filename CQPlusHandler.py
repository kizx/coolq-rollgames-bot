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
            if msg == inst['0']:
                path = 'app/me.cqp.kizx.rollgames/notes'
                if not os.path.exists(path):
                    os.mkdir(path)
                mess = '初始化路径成功'
            elif msg == inst['1']:
                mess = '\n'.join(['欢迎老板Roll游戏！', '↓请严格按以下格式发送指令↓',
                                  inst['2'], '游戏名称（注意相同名称会覆盖）', '描述（如15号开奖）'])
            elif msg == inst['6']:
                mess = '\n'.join(['本插件命令如下：', '我要roll游戏', '我要参加roll游戏/n游戏名', '查看名单/n游戏名',
                                  '开始roll游戏/n游戏名/n中奖人数', '[CQ:face, id=30]注意以上命令中/n代表换行，游戏名由roll游戏者指定，请确保每次活动的游戏名各不相同以避免冲突'])
            else:
                strlist = msg.splitlines()
                try:
                    # 发起活动
                    if strlist[0] == inst['2']:
                        path = 'app/me.cqp.kizx.rollgames/notes/' + \
                            strlist[1] + '.txt'
                        with open(path, 'w') as f:
                            info = self.api.get_group_member_info(
                                group, qq, True)
                            name = info['card'] if info['card'] != '' else info['nickname']
                            f.write('发起人：' + str(qq) + ' - ' + name + '\n游戏：' + strlist[1] + '\n描述：' +
                                    strlist[2] + '\n')
                        mess = '\n'.join(['您已成功发起Roll<' +
                                          strlist[1] +
                                          '>活动！', '↓发送以下命令参加活动↓', inst['3'], strlist[1],
                                          '↓发送以下命令查看名单↓', inst['4'], strlist[1]])
                    # 报名参加活动
                    elif strlist[0] == inst['3']:
                        path = 'app/me.cqp.kizx.rollgames/notes/' + \
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
                                f.write(str(qq) + ' - ' + name + '\n')
                            mess = '恭喜您已成功报名参加roll<' + strlist[1] + '>'
                        else:
                            mess = '您已经参加过了哦，请勿重复报名'
                    # 查看参加成员
                    elif strlist[0] == inst['4']:
                        path = 'app/me.cqp.kizx.rollgames/notes/' + \
                            strlist[1] + '.txt'
                        with open(path, 'r') as f:
                            mess = ''.join(f.readlines())
                    # 开奖
                    elif strlist[0] == inst['5']:
                        path = 'app/me.cqp.kizx.rollgames/notes/' + \
                            strlist[1] + '.txt'
                        with open(path, 'r') as f:
                            masqq = f.readline().split('：')[1].split(' - ')[0]
                        if str(qq) == masqq:
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
                            mess = '恭喜欧皇' + mess + '获得了' + \
                                strlist[1] + '\n没有获奖的小伙伴也不要沮丧哦~'
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
            self.api.send_private_msg(3317200497, str(qq) + msg)


inst = {'0': '初始化', '1': '我要roll游戏', '2': '#我要roll游戏#',
        '3': '我要参加roll游戏', '4': '查看名单', '5': '开始roll游戏', '6': '查看命令'}
