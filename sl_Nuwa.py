import basic
import utils
import time
import paddlehub as hub

def use_nuwa_skill(handle):
    time.sleep(3)
    print("点击右下角", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(1)
    print("点击特殊技能", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.5959, 0.7894), normalize=True)
    time.sleep(1)
    print("点击第一个技能---补天", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.2420,0.3785), normalize=True)
    time.sleep(1)
    # print("点击死亡波纹", end=' ', flush=True)
    # basic.left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    # time.sleep(1)
    print("点击头像使用", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.498611,0.498611), normalize=True)
    time.sleep(2)

def use_quake(handle):
    time.sleep(2)
    print("点击右下角", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(0.5)
    print("点击卷轴系列", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.25,0.782031), normalize=True)
    time.sleep(0.5)
    print("点击土系魔法", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.901389,0.429688), normalize=True)
    time.sleep(0.5)
    print("点击地震术", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    time.sleep(0.5)
    print("点击头像使用", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.498611,0.947656), normalize=True)
    time.sleep(2)

if __name__ == "__main__":  
    # ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)
    handle = basic.get_handle()
    # 暂离
    for i in range(101):
        print(f"第{i}次尝试")
        basic.save_staute(handle)
        # 释放女娲技能
        
        use_nuwa_skill(handle)
        # 释放地震术
        use_quake(handle)
        # 检查装备是否出现
        
        input("确认是否出现合适装备")
        #如果没有出现那就离开，再次尝试
        basic.find_and_click(handle, "./img/common/setting.png", 3)
        basic.find_and_click(handle, "./img/common/account.png", 3)
        basic.find_and_click(handle, "./img/common/logout.png", 10)
        basic.find_and_click(handle, "./img/common/startgame.png", 10)
        basic.find_and_click(handle, "./img/common/SLsure.png", 3)
        basic.find_and_click(handle, "./img/common/adventure.png", 10)
    