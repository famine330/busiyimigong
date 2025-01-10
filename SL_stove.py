import basic
import time
import numpy as np
import os
import utils


"""
用于神锻测序
"""
sunshine_seq = []
equipments_path = {"1":["./img/equipments/1level/" + path for path in os.listdir("./img/equipments/1level/")], 
                   "2":["./img/equipments/2level/" + path for path in os.listdir("./img/equipments/2level/")],
                   "3":["./img/equipments/3level/" + path for path in os.listdir("./img/equipments/3level/")],
                   "4":["./img/equipments/4level/" + path for path in os.listdir("./img/equipments/4level/")],
                   "5":["./img/equipments/5level/" + path for path in os.listdir("./img/equipments/5level/")],
                   "6":["./img/equipments/6level/" + path for path in os.listdir("./img/equipments/6level/")]}


# 从左侧第一页开始找装备,找到返回[（x,y）],没找到返回[]
def find_and_click_equipment_from_left(handle:basic.HANDLE, equip_path_list:list, debug: bool=False)->tuple:
    
    print("向左侧翻页，翻到第一页")
    while True:
        left_botton_dts = basic.find_image_center(handle, ['./img/common/left_bottom.png'], debug=True)
        if left_botton_dts:
            basic.left_mouse_click(handle=handle, point=left_botton_dts)
            time.sleep(0.5)
        else:
            break
        
    while True:
        # 在当前页找目标装备
        
        _, img = basic.get_screenshot(handle)
        equip_dts = basic.find_image_center(handle, [ele_path for ele_path in equip_path_list], debug=debug)
        print("equip_dts",equip_dts)

        if equip_dts:
            # 找到
            if equip_dts[1] > 0.5 * (handle.bottom - handle.top):
                basic.left_mouse_click(handle=handle, point=equip_dts)
                return equip_dts
        # 没找到

        # 往右翻页找装备
        right_botton_dts = basic.find_image_center(handle, ["./img/common/right_bottom.png"])
        if right_botton_dts:
            basic.left_mouse_click(handle=handle, point=right_botton_dts)
            time.sleep(2)
        else:
            print("所有装备搜索结束")
            break


# 从右侧第一页开始找装备,找到返回[（x,y）],没找到返回[]
def find_and_click_equipment_from_right(handle:basic.HANDLE, equip_path_list:list, debug: bool=False)->tuple:
    
    candiate_equip = []
    print("向右侧翻页，翻到、最后一页")
    while True:
        right_botton_dts = basic.find_image_center(handle, ["./img/common/right_bottom.png"])
        if right_botton_dts:
            basic.left_mouse_click(handle=handle, point=right_botton_dts)
            time.sleep(0.5)
        else:
            break
    while True:
        # 在当前页找目标装备
        _, img = basic.get_screenshot(handle)
        equip_dts = basic.find_image_center(handle, [ele_path for ele_path in equip_path_list],region = ((0, 0.5), (1, 1)), debug=debug)

        if len(equip_dts)>0:
            # 找到
                basic.left_mouse_click(handle=handle, point=equip_dts)
                break
            
        # 没找到

        # 往左翻页找装备
        left_botton_dts = basic.find_image_center(handle, [handle, "./img/common/left_bottom.png"], match_threshold=0.85)
        if left_botton_dts:
            basic.left_mouse_click(handle=handle, point=left_botton_dts)
            time.sleep(2)
        else:
            print("所有装备搜索结束")
            break


# 查找熔炉位置,并点击,进入查找装备的界面
def find_stove(handle:basic.HANDLE)->bool:
    _, img = basic.get_screenshot(handle)
    basic.find_and_click_image(handle, ["./img/shenduan/stove.png", "./img/shenduan/stove_2.png", "./img/shenduan/stove_3.png"])
    time.sleep(1)
    # 点击添加装备
    add_bottom_dts = basic.find_and_click_image(handle, ["./img/shenduan/add_equipment.png"])
    time.sleep(1)
    return True

# 熔炼装备
def stove_equipment(handle:basic.HANDLE): 
    time.sleep(1)
    basic.find_and_click_text(handle, tar_txts=["选择"])   # 添加装备
    time.sleep(1)
    basic.find_and_click_text(handle, tar_txts=["熔炼装备"])    # 装备熔炼
    

# def use_star_6_equipment(handle:basic.HANDLE, ocr:hub.Module, is_detect:bool=True, number=101):
#     sun_record = None
#     find_stove(handle)
    
#     for i in range(number):
        
#         print("这次是第"+str(i)+"次装备熔炼")
#         pos = find_equipment_from_right(handle, equipments_path["6"])
        
#         if len(pos)==0:
#             # 说明没有6星装备了,小SL恢复原状
#             basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#             basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#             basic.SL_basic(handle, ocr=ocr)
#             raise Exception("没有找到6星装备")
#         # 熔炼装备
#         stove_equipment(handle, pos[0],ocr=ocr)
        
#         if is_detect:
#             # 结果检测
#             result = check_sunshine(handle)
#             if result:
#                 sun_record = i
#                 print(f"           第{i}次有日光！    ")
#                 basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
#                 break
#             # 重新回到装备选择界面
                
#         print(sun_record)
#         basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
    
#     #小SL,回复现场
#     basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#     basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    
#     basic.SL_basic(handle, ocr=ocr)  
#     print("第"+str(sun_record)+"次装备熔炼出了日光") 
#     return sun_record


# def use_min_star_equipment_step_1(handle:basic.HANDLE, ocr:hub.Module, sun_record=None):
    
#     find_stove(handle)
    
#     start_level = 1
    
#     print("有日光，第一步：填入低星装备")
#     for i in range(sun_record):
#         print("这次是第"+str(i)+"次装备熔炼")
#         pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
#         if len(pos)==0:
#             print("1星装备不足，使用2星装备推序")
#             if start_level == 1:
#                 start_level = 2
#             pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
#             if len(pos)==0:
#                 print("2星装备不足，使用3星装备推序")
#                 if start_level == 2:
#                     start_level = 3
#                 pos = find_equipment_from_left(handle, equipments_path[str(start_level)])
#                 if len(pos)==0:
#                     print("3星装备不足，下楼打装备吧")
#                     return 10000000
    
#         # 熔炼装备
#         stove_equipment(handle, pos[0], ocr=ocr)
#         basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
            
            
#     #暂离保存
#     print("后面就是放最低星的高星装备")
#     basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#     basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#     basic.save_staute(handle, ocr=ocr)
        
            

# def use_min_star_equipment_step_2(handle:basic.HANDLE, ocr:hub.Module, equipment_list=["3", "4", "5", "6"]):

#     print("有日光，第二步：填入高星装备")
#     for i in equipment_list:
#         find_stove(handle)
        
#         pos = find_equipment_from_right(handle, equipments_path[i])
#         if len(pos)==0:
#             print(f"没有找到{i}星装备，寻找更高星装备")
#             continue
#         else:
#             print(f"找到{i}星装备，开始使用")
#             stove_equipment(handle, pos[0],ocr=ocr)

#             # 结果检测
#             result = check_sunshine(handle)
#             if result:
#                 #暂离
#                 basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#                 print("这里是暂离保存")
#                 basic.save_staute(handle, ocr=ocr)
#                 return i
#             else:
#                 print(f"没有日光,下次用{int(i) + 1}星装备继续尝试")
#                 basic.find_and_click(handle, "./img/shenduan/back.png", 2)
#                 basic.SL_basic(handle, ocr=ocr) 
    
def use_x_level_equipment_without_SL(handle:basic.HANDLE, is_detect:bool=True,level="6",sun_record = [], number=101, debug=False):

    find_stove(handle)
    
    for i in range(number):
        
        print("这次是第"+str(i)+"次装备熔炼")
        if int(level) >= 4:
            find_and_click_equipment_from_right(handle, equipments_path[level])
        else:
            find_and_click_equipment_from_left(handle, equipments_path[level])
        # 熔炼装备
        stove_equipment(handle)
        
        if level != "6" and sun_record[i] == "0":
            is_detect = False
        else:
            is_detect = True
        
        if is_detect:
            # 结果检测
            result = basic.find_text_center(handle, ["攻击","魔力"], timeout=3, interval=0.01, region= ((0,0.75), (1,1)), debug=debug)
            if result:
                sun_record[i] = level
                print(f"           第{i}次有日光！    ")
            else:
                pass
            # 重新回到装备选择界面
                
        print(sun_record)
        basic.find_and_click_image(handle, ["./img/shenduan/add_equipment.png"])
    
    #回复现场
    basic.find_and_click_text(handle, ["返回"])
    basic.find_and_click_text(handle, ["返回"])
    
    return sun_record 
   
    
def test_sequence(handle:basic.HANDLE):
    
    record_list = ["0" for _ in range(101)]
    record_list = use_x_level_equipment_without_SL(handle, is_detect=True, level="6", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle, is_detect=True, level="5", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle, is_detect=True, level="4", sun_record=record_list)
    record_list = use_x_level_equipment_without_SL(handle, is_detect=True, level="3", sun_record=record_list)
    return record_list


def get_sun_from_sequence(handle:basic.HANDLE, sun_record: list):
    continue_flag = True
    i = 0
    sun_number = 0
    while continue_flag:
        if sun_record[i] != "0":
            #熔炼装备
            find_stove(handle)
            
            pos = find_and_click_equipment_from_right(handle, equipments_path[sun_record[i%101]])
            stove_equipment(handle)
            i = i + 1
            sun_number = sun_number + 1
            basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
            basic.find_and_click_text(handle, ["返回"])
            basic.find_and_click_text(handle, ["返回"])
        else:
            # 填入低星装备
            find_stove(handle)
    
            start_level = 1
    
            print("填入低星装备")

            print("这次是第"+str(i)+"次装备熔炼")
            pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
            if len(pos)==0:
                print("1星装备不足，使用2星装备推序")
                if start_level == 1:
                    start_level = 2
                pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
                if len(pos)==0:
                    print("2星装备不足，使用3星装备推序")
                    if start_level == 2:
                        start_level = 3
                    pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
                    if len(pos)==0:
                        print("3星装备不足，下楼打装备吧")
                        return
            # 熔炼装备
            stove_equipment(handle)
            i = i + 1
            basic.find_and_click_image(handle, "./img/shenduan/add_equipment.png", 3) 
            basic.find_and_click_text(handle, ["返回"])
            basic.find_and_click_text(handle, ["返回"])
                    
            
            

if __name__ == "__main__":

    handle = basic.get_handle()
    print("记得穿铠甲！！！！")
    # test_sequence(handle)
    # get_sun_from_sequence(handle, sun_record=["0", "0", "3"])

    # print(find_and_click_equipment_from_left(handle, equipments_path["1"]))
    print(find_and_click_equipment_from_right(handle, equipments_path["5"],debug=True))
    # find_stove(handle)
    # stove_equipment(handle)
    
    # get_sun_from_sequence(handle, ocr, sun_record=["0","0","0","3"])
    
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