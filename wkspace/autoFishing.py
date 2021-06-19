from ctypes import windll
from ctypes.wintypes import HWND
import time
from PIL import ImageGrab
import operator
from functools import reduce
import time
import math

import datetime


from pykeyboard import PyKeyboard
kb = PyKeyboard()

# 钓鱼设置

# 钓鱼总时间（s）
fishingTime = 3600
# 钓鱼计时器
fishingTime_s = fishingTime_e = time.time()

# 单次钓鱼时间（s）
dancifishingTime = 30
# 单次计时器
danci_s = danci_e = time.time()

# 状态值
isFishing = False

# 按键设定
# 抛竿
paogan = '2'
# 提勾
tigou = '3'

# 对比用图片
# xy(959,624)
x = 0
y = 0
rangle = 0
rawImg = 0
rawImgH = 0

# 数据文件名
date_file = "wkspace\\init.txt"


targetImgH = None
# 方差大于这个阈值就算上钩
imgChangeThd = 10
# 平均值
imgAverageVal = 0
# 平均计数
averageCnt = 0
# 每秒处理次数
frameVal = 3


def setRangle(x, y):
    return (x-50, y-80, x+50, y+20)


def difference(hist1, hist2):
    sum1 = 0
    for i in range(len(hist1)):
        if (hist1[i] == hist2[i]):
            sum1 += 1
        else:
            sum1 += 1 - float(abs(hist1[i] - hist2[i])
                              ) / max(hist1[i], hist2[i])
    return sum1/len(hist1)


def isOutTime():

    global danci_s
    global danci_e
    global dancifishingTime

    danci_e = time.time()
    if (danci_e-danci_s >= dancifishingTime):
        danci_s = danci_e = time.time()
        logs("超过单次钓鱼时间")
        return True
    return False


def isGetFash():
    global rangle, rawImgH, targetImgH, frameVal
    global imgChangeThd, imgAverageVal, imgChangeThd, averageCnt

    targetImgH = ImageGrab.grab(rangle).histogram()
    rms = math.sqrt(reduce(operator.add,  list(map(lambda a, b: (a-b)**2,
                                                   rawImgH, targetImgH)))/len(rawImgH))
    rawImgH = targetImgH

    '''
    sqrt:计算平方根，reduce函数：前一次调用的结果和sequence的下一个元素传递给operator.add
    operator.add(x,y)对应表达式：x+y
    这个函数是方差的数学公式：S^2= ∑(X-Y) ^2 / (n-1)

    # rms的值越大，说明两者的差别越大；如果result=0,则说明两张图一模一样
    '''

    # 平均方差
    imgAverageVal = (rms+imgAverageVal*averageCnt) / (averageCnt+1)
    averageCnt += 1

    getFash = False
    if(averageCnt > 3*frameVal):

        if(abs(rms - imgAverageVal) > imgChangeThd):
            getFash = True
            print("钓鱼结果：", getFash, ", 方差: ", rms, ", 平均方差: ", imgAverageVal)

    return getFash


def paoganPress():
    kb.tap_key(paogan, n=1, interval=0.1)


def tigouPress():
    kb.tap_key(tigou, n=1, interval=0.1)


def logs(str):
    global fishingTime_s
    global fishingTime_e
    # textCtrl.write("运行时间:", round(fishingTime_e-fishingTime_s), ", ", str)
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(dt + ": "+str)


def fishingOnce():
    global isFishing, rawImgH, danci_s, danci_e, averageCnt
    if (isFishing == False):
        logs("抛竿")
        # 抛竿
        paoganPress()

        # 获取抛竿后截图
        time.sleep(4)
        rawImgH = ImageGrab.grab(rangle).histogram()

        isFishing = True
        logs("开始钓鱼。。。")
        danci_s = danci_e = time.time()

    else:
        # 是否超过单次钓鱼时间
        outTime = isOutTime()
        # 是否上钩
        getFash = isGetFash()

        if (outTime or getFash == True):
            time.sleep(0.2)
            logs("上钩提竿")
            # 上钩提竿
            tigouPress()
            isFishing = False
            averageCnt = 0
            time.sleep(8)
            if (getFash == True):
                time.sleep(5)

    # 循环结束


def fMain():
    global fishingTime, frameVal
    global fishingTime_s
    global fishingTime_e

    logs("钓鱼脚本10s后开始")
    logs("点击游戏任意空白位置，之后请不要操作鼠标键盘！")
    time.sleep(10)

    # 钓鱼计时器
    fishingTime_s = fishingTime_e = time.time()

    # 逻辑帧
    frame_s = frame_e = time.time()

    while (fishingTime_e-fishingTime_s <= fishingTime):
        if (frame_e-frame_s >= 1/frameVal):
            frame_e = frame_s = time.time()
            fishingOnce()
        else:
            frame_e = time.time()

        fishingTime_e = time.time()

    logs("钓鱼脚本结束")


def setMode(m_state, m_states):
    print("-"*50)
    print("输入f查看当前设定位置截图")
    print("输入a设定钓鱼检测位置")
    print("输入t设置钓鱼时间（秒）")
    print("输入s开始脚本")
    print("输入q退出")
    str = input("请输入：")

    if(str == "s"):
        m_state = m_states[1]
    if(str == "f"):
        m_state = m_states[2]
    if(str == "a"):
        m_state = m_states[3]
    if(str == "t"):
        m_state = m_states[4]
    if(str == "q"):
        m_state = m_states[5]

    print(m_state)

    return m_state


def resource_path(relative_path):

    import os

    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = os.getcwd()
    return os.path.join(base_path, relative_path)


def readInit():
    global x, y, rawImg, rawImgH, rangle, fishingTime

    print("-"*50)
    init_file = open(resource_path(date_file), "r+")
    print("初始设置文件名为: ", init_file.name)

    # 钓鱼感叹号区域初始化
    line = init_file.readline()
    (x1, y1) = line.split(",")
    x = int(x1)
    y = int(y1)
    rangle = setRangle(x, y)
    rawImg = ImageGrab.grab(rangle)
    rawImgH = ImageGrab.grab(rangle).histogram()

    # 钓鱼时间初始化
    line = init_file.readline()
    fishingTime = int(line)

    print("初始化屏幕角色头部坐标(x,y)：", x, y)
    print("初始化钓鱼时常：", fishingTime)

    print("-"*50)

    # 关闭文件
    init_file.close()


def writeFile():
    init_file = open(resource_path(date_file), "r+")

    init_file.truncate(0)
    seq = [str(x)+","+str(y)+"\n",
           str(fishingTime)]
    init_file.writelines(seq)

    print("数据保存成功（x，y），钓鱼时间：", x, y, fishingTime)

    # 关闭文件
    init_file.close()


if __name__ == '__main__':
    readInit()
    print("")
    print("提示：用winspy工具找到你人物头部的位置坐标")

    m_states = ("主菜单", "钓鱼模式", "查询显示模式", "坐标设置模式", "设置钓鱼时间（秒）", "退出")
    m_state = m_states[0]
    while True:
        if(m_state == m_states[0]):
            m_state = setMode(m_state, m_states)
        if(m_state == m_states[1]):
            fMain()
        if(m_state == m_states[2]):
            rawImg = ImageGrab.grab(rangle)
            print(rawImg)
            rawImg.show()
            m_state = m_states[0]
        if(m_state == m_states[3]):
            print("1080p最远距离，角色头部坐标为：959,624")
            print("两个纯整数，例如：111,222")
            input_str = input("请输入：")
            try:
                [x1, y1] = input_str.split(",")
                print(x1, ",", y1)

                x = int(x1)
                y = int(y1)
                rangle = setRangle(x, y)
                rawImg = ImageGrab.grab(rangle)
                writeFile()
                rawImg.show()
                m_state = m_states[0]
            except Exception as err:
                print("格式错了!!!", err)
        if(m_state == m_states[4]):
            print("当前钓鱼总时长：", fishingTime)
            print("整数（秒），例如：3600")
            input_str = input("请输入：")
            try:
                fishingTime = int(input_str)
                writeFile()
                print("设置成功。钓鱼时间：", fishingTime, "秒")
                m_state = m_states[0]
            except Exception as err:
                print("格式错了!!!")

        if(m_state == m_states[5]):
            break
