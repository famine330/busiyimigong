import basic
import time
import paddlehub as hub
import copy
import win32con, win32api
import win32gui



# 永恒套装
Eternal_suit = {"永恒腕轮":"./img/equipments/reserved/5-6.png", "永恒王冠":"./img/equipments/reserved/5-2.png", "永恒披风":"./img/equipments/reserved/5-96.png", "永恒之球":"./img/equipments/reserved/5-99.png"}
# Eternal_suit = {"永恒腕轮":"./img/equipments/5level/5-6.png", "永恒王冠":"./img/equipments/5level/5-2.png", "永恒披风":"./img/equipments/5level/5-96.png", "永恒之球":"./img/equipments/5level/5-99.png"}
# 命运套装
Fate_suit = {"正义铠甲":"./img/equipments/4level/4-4.png", "勇气腰带":"./img/equipments/4level/4-8.png", "坚韧战靴":"./img/equipments/4level/4-95.png"}
# Fate_suit = {"正义铠甲":"./img/equipments/4level/4-4.png", "勇气腰带":"./img/equipments/4level/4-8.png", "坚韧战靴":"./img/equipments/4level/4-95.png", "忠诚勋章":"./img/equipments/4level/4-99.png"}

# 元素套装
Ele_suit = {"时光沙漏":"./img/equipments/reserved/5-97.png"}



# 使用地震术
def use_quake(handle):
    time.sleep(2)
    print("点击右下角", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(1)
    print("点击卷轴系列", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.25,0.782031), normalize=True)
    time.sleep(1)
    print("点击土系魔法", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.901389,0.429688), normalize=True)
    time.sleep(1)
    print("点击地震术", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    time.sleep(1)
    print("点击头像使用", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.498611,0.947656), normalize=True)
    time.sleep(2)


# 使用死亡波纹
def use_death_ripper(handle):
    time.sleep(2)
    print("点击右下角", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(1)
    print("点击卷轴系列", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.25,0.782031), normalize=True)
    time.sleep(1)
    print("点击暗系魔法", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.888889,0.673438), normalize=True)
    time.sleep(1)
    print("点击死亡波纹", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    time.sleep(1)
    print("点击头像使用", end=' ', flush=True)
    basic.left_mouse_click(handle=handle, point=(0.498611,0.947656), normalize=True)
    time.sleep(2)



    
      

# 检测目前已经有的装备，返回列表中缺少的装备  equip_list包含装备路径
def check_equipment(handle:basic.HANDLE, equip_list:list):
    # 永恒套穿上
    equip_list_copy = copy.deepcopy(equip_list)

    basic.find_and_click(handle, "./img/common/equip_pack.png", 2)   # 点击背包

    

    # 所有装备都存在
    if len(equip_list_copy)==0:
        basic.find_and_click(handle, "./img/shenduan/back.png", 2)
        return []
    
    # 查找当前页面装备
    _, img = basic.get_screenshot(handle)

    remove_list = []
    for equip in equip_list_copy:
        equip_dts = basic.match_template(handle, [basic.imread(handle, equip)], match_threshold=0.85)
        if len(equip_dts)>0:
            remove_list.append(equip)
    
    for ele in remove_list:
        equip_list_copy.remove(ele)

    
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    return equip_list_copy


# 获得装备名字
def obtain_equip_name(handle:basic.HANDLE)->list:
    area = ((0.0747222,0.851094), (0.2597,0.913281))  

    print("开始截图并检测")
    screenshot_list = []
    for _ in range(30):
        _, img = basic.get_screenshot(handle)
        h, w, _ = img.shape
        top, down, left, right = int(area[0][1]*h), int(area[1][1]*h), int(area[0][0]*w), int(area[1][0]*w)
        area_img = img[top:down, left:right, :]
        screenshot_list.append(area_img)
        time.sleep(0.05)

    result_list = ocr.recognize_text(images=screenshot_list)
    # print(result_list)
    result_set = set()

    for result in result_list:
        if len(result['data'])==0:
            continue
        det_texts = result['data'][0]['text']
        result_set.add(det_texts)

    return list(result_set)

def SL_basic(handle, ocr):
    # basic.load_mumu_video(self.handle, "./img/mumu_video/小xl.mmor")
    basic.find_and_click_image(handle, ["./img/common/setting.png"])
    basic.find_and_click_image(handle, ["./img/common/account.png"])
    basic.find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=5)
    basic.find_and_click_text(handle, ["我知道了"], ocr=ocr)
    basic.find_and_click_text(handle, ["开始游戏"], ocr=ocr, sleep_time=5)
    basic.find_and_click_text(handle, ["确定"], ocr=ocr)
    basic.find_and_click_text(handle, ["继续冒险"], ocr=ocr, sleep_time=5)
    
    while True:
        if basic.find_image_center(handle, ["./img/common/setting.png"]):
            break
def save_staute(handle, ocr):
    basic.left_mouse_click(handle=handle, point=(0.0847222,0.0351563), normalize=True)   # 点左上角
    time.sleep(1)
    basic.find_and_click_text(handle, ["暂离"], ocr=ocr, sleep_time=5)
    
    basic.find_and_click_text(handle, ["确定"], ocr=ocr)
    basic.find_and_click_text(handle, ["重新连接"], ocr=ocr)
    basic.find_and_click_image(handle, ["./img/common/back2.png"], sleep_time=5)
    while True:
        if basic.find_image_center(handle, ["./img/common/setting.png"]):
            break
        
def change_network_state(handle):
    go_back_to_home(handle)
    # 启动V2RayNG应用
    basic.find_and_click_image(handle, ["./img/global/V2rayN.png"], sleep_time=5)
    print("成功打开V2RayNG应用")
    basic.find_and_click_image(handle, ["./img/global/off_button.png"], sleep_time=5)
    time.sleep(2)
    go_back_to_home(handle)
    basic.find_and_click_image(handle, ["./img/global/game.png"], sleep_time=5)



def go_back_to_home(handle):
    # 设置焦点到指定的窗口句柄
    win32gui.SetForegroundWindow(handle.handle_id)
    # 发送返回键事件
    # 单个按键
    # 注意：HOME键按下要抬起
    win32api.keybd_event(36,0,0,0) 
    time.sleep(0.1)
    win32api.keybd_event(36,0,win32con.KEYEVENTF_KEYUP,0)  
def get_lack_equipment(handle, ocr, equip_dict):
    equip_dict_copy = copy.deepcopy(equip_dict)
    basic.find_and_click_image(handle, ["./img/common/equip_pack.png"])
    for k, v in equip_dict.items():

        det_pos = basic.find_image_center(handle, [v])
        if det_pos is not None:
            del equip_dict_copy[k]
    return list(equip_dict_copy.keys())

def SL_equip(handle:basic.HANDLE, ocr=None, equip_name_list=['时光沙漏']):
    ops = 0
    while ops < 101:
        print(f"这是第{ops}次黑装备     "*4)
        save_staute(handle, ocr)
        print("检查是否断网")
        change_network_state(handle=handle)
        time.sleep(5)
        basic.find_and_click_image(handle, ["./img/common/open_door.png"], sleep_time=3)
        
        # 使用卷轴杀怪
        use_quake(handle)
        time.sleep(2)

        while not basic.find_image_center(handle, ["./img/common/equip_box.png"]):
            use_death_ripper(handle)
            time.sleep(2)

        # 点击宝箱
        basic.find_and_click_image(handle, ["./img/common/equip_box.png"])
        result = basic.find_text_center(handle, equip_name_list, timeout=3, interval=0.01, ocr=ocr, region= ((0.05,0.85), (0.3,0.95)))
        if result:
            # 联网保存
            change_network_state(handle=handle)
            save_staute(handle, ocr=ocr)
            return True
        else:
            ops+=1
            # 小SL
            basic.find_and_click_image(handle, "./img/common/setting.png", 3)
            basic.find_and_click_image(handle, "./img/common/account.png", 3)
            basic.find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=8)
            while not basic.find_image_center(handle, "./img/common/startgame.png"):
                time.sleep(1)
            change_network_state(handle=handle)
            time.sleep(10)
            basic.find_and_click_text(handle, ["我知道了"], ocr=ocr)     
            basic.find_and_click_text(handle, ["开始游戏"], ocr=ocr)     
            basic.find_and_click_text(handle, ["确定"], ocr=ocr) 
            basic.find_and_click_text(handle, ["继续冒险"], 8, ocr=ocr) 
            
    else:
        print("超过了101次，需要大SL")
        basic.find_and_click_image(handle, "./img/common/setting.png", 3)
        basic.find_and_click_image(handle, "./img/common/account.png", 3)
        basic.find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=8)
        while not basic.find_image_center(handle, "./img/common/startgame.png"):
                time.sleep(1)
        change_network_state(handle=handle)

if __name__ == "__main__":  
    ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)       # mkldnn加速仅在CPU下有效
    handle = basic.get_handle()
    
    # get_lack_equipment(handle, ocr, Ele_suit)
    SL_equip(handle, ocr=ocr, equip_name_list=['时光沙漏'])

    # equipment_dict = {}

    # # 设置要黑的套装
    # # target_suit = Eternal_suit         
    # # target_suit = Fate_suit

    # # Eternal_suit.update(Fate_suit)
    # target_suit = Eternal_suit

    

    # # 查找当前装备，得到缺少的装备信息
    # target_suit_path_list = list(target_suit.values())
    # lack_equipment_path_list = check_equipment(handle, target_suit_path_list)
    # lack_equipment_name_list = []
    # for k, v in target_suit.items():
    #     if v in lack_equipment_path_list:
    #         lack_equipment_name_list.append(k)

    # print("缺少的装备有：", lack_equipment_name_list)
    # # print(ans)

    # ops = 0
    # while ops < 101:
    #     # break
    #     print(f"这是第{ops}次黑装备     "*4)

    #     # 暂离+断网+下楼
    #     basic.save_staute(handle, ocr=ocr)
    #     print("检查是否断网")
    #     basic.change_network_state(handle=handle)
    #     time.sleep(5)
    #     basic.find_and_click(handle, "./img/common/open_door.png", 3)
    #     time.sleep(3)

    #     # 使用卷轴杀怪
    #     use_quake(handle)
    #     time.sleep(2)

    #     for _ in range(1):
    #         use_death_ripper(handle)
    #         time.sleep(2)

    #     # 点击宝箱
    #     basic.find_and_click(handle, "./img/common/equip_box.png", match_threshold=0.7)

    #     # 获得装备检测
    #     det_str_list = obtain_equip_name(handle)
    #     for name in det_str_list:
    #         if len(name) > 3:
    #             if name in equipment_dict:
    #                 equipment_dict[name] += 1
    #             else:
    #                 equipment_dict[name] = 1
    #     print(det_str_list)
    #     print(equipment_dict)
    #     ### "神谕手套,永恒王冠,永恒之球,永恒披风,永恒手套, 魔导士斗篷,神谕之盔,时光沙漏"

    #     flag = False
    #     for ch in det_str_list:
    #         if ch in lack_equipment_name_list:
    #             print("找到装备：", ch)
    #             flag = True

    #             # 联网保存
    #             basic.change_network_state(handle=handle)
    #             time.sleep(10)
    #             basic.save_staute(handle, ocr=ocr)
    #             break
        
    #     if flag:
    #         break
    #     else:
    #         ops+=1
    #         # 小SL
    #         basic.find_and_click(handle, "./img/common/setting.png", 3)
    #         basic.find_and_click(handle, "./img/common/account.png", 3)
    #         basic.find_and_click_text(handle, ["登出"], 8, ocr=ocr)
           
    #         while not basic.find(handle, "./img/common/startgame.png"):
    #             time.sleep(1)
    #         basic.change_network_state(handle=handle)
    #         time.sleep(10)
    #         print("开始游戏")
    #         while not basic.find(handle, "./img/common/SLsure.png"):
    #             basic.find_and_click_text(handle, ["我知道了"], 1, ocr=ocr)     
    #             basic.find_and_click_text(handle, ["开始游戏"], 1, ocr=ocr)     
    #         basic.find_and_click(handle, "./img/common/SLsure.png", 3)
    #         basic.find_and_click_text(handle, ["继续冒险"], 8, ocr=ocr)
    #         while True:
    #             dts = basic.match_template(handle, [basic.imread(handle, "./img/common/setting.png")], match_threshold=0.9)
    #             if len(dts)>0:
    #                 break
    # else:
    #     print("超过了101次，需要大SL")
    #     basic.find_and_click(handle, "./img/common/setting.png", 3)
    #     basic.find_and_click(handle, "./img/common/account.png", 3)
    #     basic.find_and_click(handle, "./img/common/logout.png", 6)
    #     while not basic.find(handle, "./img/common/startgame.png"):
    #             time.sleep(1)
    #     basic.change_network_state(handle=handle)