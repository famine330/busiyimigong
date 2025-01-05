import basic
import cv2
import time
import numpy as np
import paddlehub as hub
import difflib
import os
import utils


"""
用于神锻测序
"""
N=101
equipments_path = {"1":["./img/equipments/1level/" + path for path in os.listdir("./img/equipments/1level/")], 
                   "2":["./img/equipments/2level/" + path for path in os.listdir("./img/equipments/2level/")],
                   "3":["./img/equipments/3level/" + path for path in os.listdir("./img/equipments/3level/")],
                   "4":["./img/equipments/4level/" + path for path in os.listdir("./img/equipments/4level/")],
                   "5":["./img/equipments/5level/" + path for path in os.listdir("./img/equipments/5level/")],
                   "6":["./img/equipments/6level/" + path for path in os.listdir("./img/equipments/6level/")]}


# 检查是否出现天下布武
def check_sunshine(handle:basic.HANDLE)->bool:
    # start_time = time.time()
    area = ((0.28,0.318), (0.7166666,0.362))      # 天下布武截图区域

    print("开始截图并检测")
    screenshot_list = []
    for _ in range(20):
        _, img = basic.get_screenshot(handle)
        h, w, _ = img.shape
        top, down, left, right = int(area[0][1]*h), int(area[1][1]*h), int(area[0][0]*w), int(area[1][0]*w)
        area_img = img[top:down, left:right, :]
        screenshot_list.append(area_img)
        time.sleep(0.05)

    result_list = ocr.recognize_text(images=screenshot_list)
    for result in result_list:
        if len(result['data'])==0:
            continue
        det_texts = result['data'][0]['text']
        conf = difflib.SequenceMatcher(None, det_texts, "发动！天下布武").quick_ratio()  # 文本相似度匹配
        if conf>0.4:
            print("出现！天下布武")
            return True
    
    print("没有出现")
    return False


# 从左侧第一页开始找装备,找到返回[（x,y）],没找到返回[]
def find_equipment_from_left(handle:basic.HANDLE, equip_path_list:list)->tuple:
    
    candiate_equip = []
    print("向左侧翻页，翻到第一页")
    while True:
        left_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/left_bottom.png")], match_threshold=0.85)
        if len(left_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=left_botton_dts[0])
            time.sleep(0.5)
        else:
            break
    while True:
        # 在当前页找目标装备
        
        _, img = basic.get_screenshot(handle)
        equip_dts = basic.match_template(handle, [basic.imread(handle, ele_path) for ele_path in equip_path_list], match_threshold=0.85)

        if len(equip_dts)>0:
            # 找到
            handle_height = handle.bottom - handle.top
            for equip_pts in equip_dts:
                if int(670*handle_height)/1280 < equip_pts[1] < int(1000*handle_height)/1280:
                    candiate_equip.append(equip_dts[0])
                    break
            if len(candiate_equip)>0:
                return candiate_equip
        # 没找到

        # 往右翻页找装备
        right_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/right_bottom.png")], match_threshold=0.85)
        if len(right_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=right_botton_dts[0])
            time.sleep(2)
        else:
            print("所有装备搜索结束")
            break
    return candiate_equip


# 从右侧第一页开始找装备,找到返回[（x,y）],没找到返回[]
def find_equipment_from_right(handle:basic.HANDLE, equip_path_list:list)->tuple:
    
    candiate_equip = []
    print("向右侧翻页，翻到、最后一页")
    while True:
        right_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/right_bottom.png")], match_threshold=0.85)
        if len(right_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=right_botton_dts[0])
            time.sleep(0.5)
        else:
            break
    while True:
        # 在当前页找目标装备
        _, img = basic.get_screenshot(handle)
        equip_dts = basic.match_template(handle, [basic.imread(handle, ele_path) for ele_path in equip_path_list], match_threshold=0.85)

        if len(equip_dts)>0:
            # 找到
            handle_height = handle.bottom - handle.top
            for equip_pts in equip_dts:
                
                if 500 < equip_pts[1]:
                    candiate_equip.append(equip_dts[0])
                    break
            if len(candiate_equip)>0:
                return candiate_equip
        # 没找到

        # 往左翻页找装备
        left_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/left_bottom.png")], match_threshold=0.85)
        if len(left_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=left_botton_dts[0])
            time.sleep(2)
        else:
            print("所有装备搜索结束")
            break
    return candiate_equip


# 查找熔炉位置,并点击,进入查找装备的界面
def find_stove(handle:basic.HANDLE)->bool:
    _, img = basic.get_screenshot(handle)
    stove_dts = basic.match_template(handle, [basic.imread(handle, "./img/shenduan/stove.png"), basic.imread(handle, "./img/shenduan/stove_2.png"), basic.imread(handle, "./img/shenduan/stove_3.png")], match_threshold=0.8)
    if len(stove_dts)==0:
        print("没有检测到熔炉")

        return False
    else:
        basic.left_mouse_click(handle=handle, point=stove_dts[0])
        time.sleep(1)
        # 点击添加装备
        add_bottom_dts = basic.match_template(handle, [basic.imread(handle, "./img/shenduan/add_equipment.png")], match_threshold=0.8)
        if len(add_bottom_dts)==0:
            print("没找到添加装备的按钮")
            return False
        else:
            basic.left_mouse_click(handle=handle, point=add_bottom_dts[0])
            time.sleep(1)
            return True

# 熔炼装备
def stove_equipment(handle:basic.HANDLE, equip_pos:tuple, ocr:hub.Module): 
    basic.left_mouse_click(handle=handle, point=equip_pos)
    time.sleep(1)
    basic.find_and_click(handle, "./img/shenduan/_20241026_161156.png")   # 添加装备
    time.sleep(1)
    # basic.left_mouse_click(handle=handle, point=(266, 615))
    basic.find_and_click_text(handle, tar_txts=["熔炼装备"],ocr=ocr)    # 装备熔炼
    
    
def stove_equipments(handle:basic.HANDLE, equip_pos:tuple, ocr:hub.Module, need:1): 
    # basic.left_mouse_click(handle=handle, point=equip_pos)
    # time.sleep(1)
    # basic.find_and_click(handle, "./img/shenduan/_20241026_161156.png")   # 添加装备
    # time.sleep(1)
    _, img = basic.get_screenshot(handle)
    result = ocr.recognize_text(images=[img])
    print(result)
    need -= 1
    while need > 0:
        basic.find_and_click_text(handle, tar_txts=["+"], ocr=ocr)
        need -= 1
    
    # basic.find_and_click_text(handle, tar_txts=["熔炼装备"], ocr=ocr)    # 装备熔炼
    

def use_star_6_equipment(handle:basic.HANDLE, ocr:hub.Module, is_detect:bool=True, number=101):
    sun_record = None
    find_stove(handle)
    
    for i in range(number):
        
        print("这次是第"+str(i)+"次装备熔炼")
        pos = find_equipment_from_right(handle, equipments_path["6"])
        
        if len(pos)==0:
            # 说明没有6星装备了,小SL恢复原状
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.SL_basic(handle, ocr=ocr)
            raise Exception("没有找到6星装备")
        # 熔炼装备
        stove_equipment(handle, pos[0],ocr=ocr)
        
        if is_detect:
            # 结果检测
            result = check_sunshine(handle)
            if result:
                sun_record = i
                print(f"           第{i}次有日光！    ")
                basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
                break
            # 重新回到装备选择界面
                
        print(sun_record)
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
    
    #小SL,回复现场
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    
    basic.SL_basic(handle, ocr=ocr)  
    print("第"+str(sun_record)+"次装备熔炼出了日光") 
    return sun_record


def use_min_star_equipment_step_1(handle:basic.HANDLE, ocr:hub.Module, sun_record=None):
    
    find_stove(handle)
    
    start_level = 1
    
    print("有日光，第一步：填入低星装备")
    for i in range(sun_record):
        print("这次是第"+str(i)+"次装备熔炼")
        pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
        if len(pos)==0:
            print("1星装备不足，使用2星装备推序")
            if start_level == 1:
                start_level = 2
            pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
            if len(pos)==0:
                print("2星装备不足，使用3星装备推序")
                if start_level == 2:
                    start_level = 3
                pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
                if len(pos)==0:
                    print("3星装备不足，下楼打装备吧")
                    return 10000000
    
        # 熔炼装备
        stove_equipment(handle, pos[0], ocr=ocr)
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
            
            
    #暂离保存
    print("后面就是放最低星的高星装备")
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.save_staute(handle, ocr=ocr)
        
            

def use_min_star_equipment_step_2(handle:basic.HANDLE, ocr:hub.Module, equipment_list=["3", "4", "5", "6"]):

    print("有日光，第二步：填入高星装备")
    for i in equipment_list:
        find_stove(handle)
        
        pos = find_equipment_from_right(handle, equipments_path[i])
        if len(pos)==0:
            print(f"没有找到{i}星装备，寻找更高星装备")
            continue
        else:
            print(f"找到{i}星装备，开始使用")
            stove_equipment(handle, pos[0],ocr=ocr)

            # 结果检测
            result = check_sunshine(handle)
            if result:
                #暂离
                basic.find_and_click(handle, "./img/shenduan/back.png", 2)
                print("这里是暂离保存")
                basic.save_staute(handle, ocr=ocr)
                return i
            else:
                print(f"没有日光,下次用{int(i) + 1}星装备继续尝试")
                basic.find_and_click(handle, "./img/shenduan/back.png", 2)
                basic.SL_basic(handle, ocr=ocr) 
    
def use_x_level_equipment_without_SL(handle:basic.HANDLE, ocr:hub.Module, is_detect:bool=True,level="6",sun_record = [], number=101):

    find_stove(handle)
    
    for i in range(number):
        
        print("这次是第"+str(i)+"次装备熔炼")
        pos = find_equipment_from_right(handle, equipments_path[level])
        
        if len(pos)==0:
            raise Exception(f"没有找到{i}星装备")
        # 熔炼装备
        stove_equipment(handle, pos[0],ocr=ocr)
        
        if level != "6" and sun_record[i] == "0":
            is_detect = False
        else:
            is_detect = True
        
        if is_detect:
            # 结果检测
            result = check_sunshine(handle)
            if result:
                sun_record[i] = level
                print(f"           第{i}次有日光！    ")
            else:
                pass
            # 重新回到装备选择界面
                
        print(sun_record)
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
    
    #回复现场
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    
    return sun_record 
   
    
def test_sequence(handle:basic.HANDLE, ocr:hub.Module):
    
    record_list = ["0" for _ in range(101)]
    record_list = use_x_level_equipment_without_SL(handle, ocr=ocr, is_detect=True, level="6", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle,ocr=ocr, is_detect=True, level="5", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle,ocr=ocr, is_detect=True, level="4", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle,ocr=ocr, is_detect=True, level="3", sun_record=record_list)
    return record_list


def get_sun_from_sequence(handle:basic.HANDLE, ocr:hub.Module, sun_record: list):
    continue_flag = True
    i = 0
    sun_number = 0
    while continue_flag:
        if sun_record[i] != "0":
            #熔炼装备
            find_stove(handle)
            
            pos = find_equipment_from_right(handle, equipments_path[sun_record[i%101]])
            stove_equipment(handle, pos[0], ocr=ocr)
            i = i + 1
            sun_number = sun_number + 1
            basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
        else:
            # 填入低星装备
            find_stove(handle)
    
            start_level = 1
    
            print("填入低星装备")

            print("这次是第"+str(i)+"次装备熔炼")
            pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
            if len(pos)==0:
                print("1星装备不足，使用2星装备推序")
                if start_level == 1:
                    start_level = 2
                pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
                if len(pos)==0:
                    print("2星装备不足，使用3星装备推序")
                    if start_level == 2:
                        start_level = 3
                    pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
                    if len(pos)==0:
                        print("3星装备不足，下楼打装备吧")
                        return
            # 熔炼装备
            stove_equipment(handle, pos[0], ocr=ocr)
            i = i + 1
            basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3) 
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            
            
            

if __name__ == "__main__":
    ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)       # mkldnn加速仅在CPU下有效

    handle = basic.get_handle()
    now_floor = utils.floor(handle)
    print("记得穿铠甲！！！！")
    
    
    get_sun_from_sequence(handle, ocr, sun_record=["0","0","0","3"])
    
    # print(test_sequence(handle, ocr))
    
    
    # continue_flag = True
    # while continue_flag:
    #     sun_record = use_star_6_equipment(handle,ocr=ocr, number=101)
    #     for i in range(sun_record):
    #         record_list.append(0)
        
    #     if sun_record is None:
    #         continue_flag = False
    #     if sun_record == 10000000:
    #         continue_flag = False
        
    #     if sun_record != 0:
    #         use_min_star_equipment_step_1(handle,ocr=ocr, sun_record=sun_record)
    #     if sun_record is not None:
    #         level = use_min_star_equipment_step_2(handle,ocr=ocr)
    #         record_list.append(level)
    #         print(record_list)
            
    #         if len(record_list) >= 101:
    #             # 21
    #             record_list = record_list[-101:]
    #             print(record_list)
    #             print(len(record_list))
    #             continue_flag = False