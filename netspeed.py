#! /usr/bin/python3
#! encoding:utf-8
'''
很早之前写的python软件，代码不好看
操作方法：
    左键双击窗口换肤，右键双击退出程序；
    右键单击窗口左侧切换显示流量还是CPU和内存占用；
    右键单击窗口右侧切换显示全部或一部分内容。
    悬浮窗口移动到屏幕右边时会自动隐藏，当鼠标再次移动到悬浮窗口上时，悬浮窗口会弹出。
    09版更新：增加CPU和内存占用显示
'''

import time
import pickle
import datetime
import os
import os.path
import sys
import tkinter as tk
from subprocess import check_output

DEFAULT_VERSION = 0.9
DEFAULT_POSx = 50  # 窗口默认起始位置
DEFAULT_POSy = 50

DEMO_CPU = 'CPU:{:.0f}% MEM:{:.0f}%'
DEMO_NET = '↓ {:<5}/s  ↑ {:>5}/s'

SKIN_LIST = (('GreenYellow', 'black'), ('#F5BB00', 'white'),
             ('DeepSkyBlue', 'Ivory'), ('Violet', 'Ivory'))

# button binding
PROG_CATCH = '<Button-1>'
PROG_MOVE = '<B1-Motion>'
PROG_EXIT = '<Double-Button-3>'
PROG_SKIN_CG = '<Button-3>'
PROG_MODE_CG = '<Double-Button-1>'
PROG_SHOW = '<Enter>'

# config file path
CONFIG_FILE_PATH = sys.path[0] + '/config.bin'
LOCK_FILE_PATH = sys.path[0] + '/netspeed.loc'
LAUNCHER_ICON_PATH = sys.path[0] + '/Minimalist.png'
LAUNCHER_FILE_PATH = os.environ['HOME'] + \
    '/.local/share/applications/Minimalist.desktop'
DEMO_LAUNCHER = '''
[Desktop Entry]
Encoding=UTF-8
Name=Minimalist
Comment=极简系统监视器
Exec=python3 {}
Icon={}
Categories=Application;
Version={}
Type=Application
Terminal=false\n'''


class SoftConfig():
    ''' 配置信息 '''

    # 是否显示为单列模式（弃用）
    IsSingleMode = False
    # 显示网速或者cpu，内存数据
    IsShowNet = True
    # 程序位置
    CurPos = [DEFAULT_POSx, DEFAULT_POSy]
    # 程序版本
    Version = DEFAULT_VERSION
    # 皮肤样式
    CurSkin = 0


class SoftData():
    ''' 运行非保存数据 '''

    IsNetFirstRun = True
    IsCpuFirstRun = True
    Time = 0
    CpuData = []
    RecvList = []
    SendList = []


c = SoftConfig()
d = SoftData()
root = tk.Tk()
mainUI = tk.Label()


def func(x, y):
    return int(y) - int(x)


def humanize(netSpeed):
    '''人性化显示流量单位'''

    n = 0
    while netSpeed >= 1000:
        netSpeed /= 1024
        n += 1
    return '{:.1f}'.format(netSpeed) + ('B', 'KB', 'MB', 'GB', 'TB')[n]


def get_cpu_and_mem_date():
    ''' 获取cpu、内存占用数据 '''

    if d.IsNetFirstRun:
        d.IsNetFirstRun = False
        d.Time = time.time()
        d.CpuData = open('/proc/stat', 'r').readline().split()[1:]
        return DEMO_CPU.format(0, 0)

    curTime = time.time()
    curCpuData = open('/proc/stat', 'r').readline().split()[1:]
    cpuRate = 1 - (int(curCpuData[3]) - int(d.CpuData[3])) / \
        sum(map(func, d.CpuData, curCpuData))
    # 避免由于计算误差出现使用率超过100%的情况
    if cpuRate > 1.0:
        cpuRate = 1.0

    d.CpuData = curCpuData
    d.Time = curTime

    memData = open('/proc/meminfo', 'r').readlines()
    memRate = 1 - int(memData[2].split()[1]) / int(memData[0].split()[1])
    return DEMO_CPU.format(cpuRate * 100, memRate * 100)


def get_net_date():
    ''' 获取网络数据 '''

    curRecvList = []
    curSendList = []
    if d.IsCpuFirstRun:
        d.IsCpuFirstRun = False
        d.RecvList = []
        d.SendList = []
        dates = open('/proc/net/dev', 'r').readlines()[2:]
        d.Time = time.time()
        for date in dates:
            d.RecvList.append(int(date.split()[1]))
            d.SendList.append(int(date.split()[9]))
        time.sleep(0.5)

    dates = open('/proc/net/dev', 'r').readlines()[2:]
    curTime = time.time()
    for date in dates:
        curRecvList.append(int(date.split()[1]))
        curSendList.append(int(date.split()[9]))
    recv = max(map(func, d.RecvList, curRecvList)) / (curTime - d.Time)
    send = max(map(func, d.SendList, curSendList)) / (curTime - d.Time)
    d.RecvList = curRecvList.copy()
    d.SendList = curSendList.copy()
    d.Time = curTime
    return DEMO_NET.format(humanize(recv), humanize(send))


def refresh():
    '''实时刷新流量显示'''

    if c.IsShowNet:
        mainUI.config(text=get_net_date(), width=20)
    else:
        mainUI.config(text=get_cpu_and_mem_date(), width=20)

    root.after(1000, refresh)


def mouse_move(e):
    '''移动窗口'''

    if e.x_root < root.winfo_screenwidth() - 10:
        relPos = [e.x - c.CurPos[0] + root.winfo_x(),
                  e.y - c.CurPos[1] + root.winfo_y()]
        if relPos[0] < 10:
            relPos[0] = 0
        if relPos[0] > root.winfo_screenwidth() - root.winfo_width() - 10:
            relPos[0] = root.winfo_screenwidth() - 4
        if relPos[1] < 10:
            relPos[1] = 0
        if relPos[1] > root.winfo_screenheight() - root.winfo_height() - 10:
            relPos[1] = root.winfo_screenheight() - root.winfo_height()
        root.geometry('+{}+{}'.format(relPos[0], relPos[1]))


def mouse_click(e):
    '''左键单击窗口时获得鼠标位置，辅助移动窗口'''

    c.CurPos = [e.x, e.y]


def change_skin(e):
    ''' 修改皮肤 '''

    if c.CurSkin == len(SKIN_LIST)-1:
        c.CurSkin = 0
    else:
        c.CurSkin += 1
    mainUI.config(bg=SKIN_LIST[c.CurSkin][0], fg=SKIN_LIST[c.CurSkin][1])


def change_mode(e):
    '''切换显示内容'''

    global c
    c.IsShowNet = not c.IsShowNet


def exit_program(e):
    '''退出程序，并保存退出之前状态'''
    writeConfig()
    deinit()
    root.destroy()


def show(e):
    '''取消隐藏'''

    if root.winfo_x() == root.winfo_screenwidth() - 4:
        root.geometry('+{}+{}'.format(root.winfo_screenwidth() -
                                      root.winfo_width() - 10, root.winfo_y()))


def writeConfig():
    c.CurPos = [root.winfo_x(), root.winfo_y()]
    dic = {
        'isSingleMode': c.IsSingleMode,
        'isShowNet': c.IsShowNet,
        'curPos': c.CurPos,
        'version': c.Version,
        'curSkin': c.CurSkin
    }
    with open(sys.path[0] + '/config.bin', 'wb') as fp:
        pickle.dump(dic, fp)


def readConfig():
    # 判断是否安装过该软件，如果没有，就开始安装
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'rb') as fp:
            dic = pickle.load(fp)
        c.IsSingleMode = dic.get('isSingleMode')
        c.IsShowNet = dic.get('isShowNet')
        c.CurPos = dic.get('curPos')
        c.Version = dic.get('version')
        c.CurSkin = dic.get('curSkin')
    else:
        # 启动器图标所需内容
        # content = DESKTOP_ENTRY_DEMO.format(
        #     os.path.realpath(__file__), LAUNCHER_ICON, version)
        # with open(LAUNCHER_FILE_PATH) as fp:
        #     fp.write(content)
        pass


def init():
    ''' 初始化 '''

    # 判断是否已经运行了一个实例
    if os.path.exists(LOCK_FILE_PATH) == False:
        open(LOCK_FILE_PATH, 'w').write(str(os.getpid()))
        return True

    old_pid = open(LOCK_FILE_PATH, 'r').readline()
    proc = os.popen('ps -x').readlines()
    for v in proc:
        if 'netspeed.py' in v and old_pid in v:
            return False

    open(LOCK_FILE_PATH, 'w').write(str(os.getpid()))
    return True


def deinit():
    ''' 清理现场 '''

    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)


def main():
    if init() == False:
        return

    readConfig()

    global mainUI
    global root
    global c
    global d

    root.geometry('+{}+{}'.format(c.CurPos[0], c.CurPos[1]))  # 窗口初始位置
    root.overrideredirect(True)  # 去掉标题栏
    root.wm_attributes('-topmost', 1)  # 置顶窗口
    mainUI = tk.Label(root, text='   starting...   ',
                      bg=SKIN_LIST[c.CurSkin][0], fg=SKIN_LIST[c.CurSkin][1])
    mainUI.pack()
    mainUI.bind(PROG_CATCH, mouse_click)
    mainUI.bind(PROG_MOVE, mouse_move)
    mainUI.bind(PROG_EXIT, exit_program)
    # mainUI.bind(PROG_SKIN_CG, change_skin)
    mainUI.bind(PROG_MODE_CG, change_mode)
    mainUI.bind(PROG_SHOW, show)

    root.after(1000, refresh)
    root.mainloop()


if __name__ == '__main__':
    main()
