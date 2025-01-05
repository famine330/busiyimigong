import basic
import cv2
import time
import numpy as np
import paddlehub as hub
import difflib
import os


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


    # _, img = basic.get_screenshot(handle)
    # h, w, _ = img.shape
    # top, down, left, right = int(area[0][1]*h), int(area[1][1]*h), int(area[0][0]*w), int(area[1][0]*w)
    # area_img = img[top:down, left:right, :]

    # cv2.imshow("1a", area_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # return True

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
                if int(655*handle_height)/1280 < equip_pts[1] < int(1000*handle_height)/1280:
                    candiate_equip.append(equip_dts[0])
                    break
            if len(candiate_equip)>0:
                return candiate_equip
        # 没找到

        # 往右翻页找装备
        right_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/right_bottom.png")], match_threshold=0.85)
        if len(right_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=right_botton_dts[0])
            time.sleep(0.5)
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
                if int(655*handle_height)/1280 < equip_pts[1] < int(1000*handle_height)/1280:
                    candiate_equip.append(equip_dts[0])
                    break
            if len(candiate_equip)>0:
                return candiate_equip
        # 没找到

        # 往左翻页找装备
        left_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/left_bottom.png")], match_threshold=0.85)
        if len(left_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=left_botton_dts[0])
            time.sleep(0.5)
        else:
            print("所有装备搜索结束")
            break
    return candiate_equip


# 查找熔炉位置,并点击,进入查找装备的界面
def find_stove(handle:basic.HANDLE)->bool:
    _, img = basic.get_screenshot(handle)
    stove_dts = basic.match_template(handle, [basic.imread(handle, "./img/shenduan/stove.png")], match_threshold=0.85)
    if len(stove_dts)==0:
        print("没找到熔炉")
        return False
    else:
        basic.left_mouse_click(handle=handle, point=stove_dts[0])
        time.sleep(1)
        # 点击添加装备
        add_bottom_dts = basic.match_template(handle, [basic.imread(handle, "./img/shenduan/add_equipment.png")], match_threshold=0.85)
        if len(add_bottom_dts)==0:
            print("没找到添加装备的按钮")
            return False
        else:
            basic.left_mouse_click(handle=handle, point=add_bottom_dts[0])
            time.sleep(1)
            return True

# 熔炼装备
def stove_equipment(handle:basic.HANDLE, equip_pos:tuple): 
    basic.left_mouse_click(handle=handle, point=equip_pos)
    time.sleep(1)
    basic.find_and_click(handle, "./img/shenduan/_20241026_161156.png")   # 添加装备
    # basic.left_mouse_click(handle=handle, point=(266, 615))
    basic.find_and_click(handle, "./img/shenduan/stove_bottom.png")    # 装备熔炼
    
def sequence_101_low(handle:basic.HANDLE, seq_len:int=101, is_detect:bool=False):
    seq_101 = np.zeros((101), dtype=int)
    sunshine_record = []

    # 进入选择装备的界面
    find_stove(handle)

    for i in range(seq_len):
        print(f"当前第{i}次测序   "*4)
        
        pos = find_equipment_from_left(handle, equipments_path["1"])
        
        if len(pos)==0:
            pos = find_equipment_from_left(handle, equipments_path["2"])
        if len(pos)==0:
            pos = find_equipment_from_left(handle, equipments_path["3"])        

        # 装备熔炼
        stove_equipment(handle, pos[0])

        if is_detect:
            # 结果检测
            result = check_sunshine(handle)
            if result:
                seq_101[i] = "x"
                sunshine_record.append(i)
                print(f"           第{i}次有日光！    ")
        # 重新回到装备选择界面  
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 2)
    

    print("*"*20)
    print(f"一共出现了 {len(sunshine_record)} 次日光， 出现位置为：")
    print(sunshine_record)
    print("*"*20)
    return seq_101, sunshine_record

# 返回特定星级装备的101序列
def sequence_101(handle:basic.HANDLE, grade:int, seq_len:int=101, is_detect:bool=True):
    seq_101 = np.zeros((101), dtype=int)
    sunshine_record = []

    # 进入选择装备的界面
    find_stove(handle)

    for i in range(seq_len):
        print(f"当前第{i}次测序   "*4)
        pos = find_equipment_from_right(handle, equipments_path[str(grade)])
        
        if len(pos)==0:
            # 说明没有装备了，sl垫过来
            # 点击返回按钮,两次返回
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.SL_basic(handle, ocr=ocr)
            # 点击炉子
            _, _ = sequence_101_low(handle, i, is_detect=False)   # 递归，推i次序              
            print("重新用低星装备垫结束")
            # 低星装备垫了i次
            pos = find_equipment_from_right(handle, equipments_path[str(grade)])
            if len(pos)==0:
                pos = []
                print("遇到未知错误， 错误点", i)

        # 装备熔炼
        stove_equipment(handle, pos[0])

        if is_detect:
            # 结果检测
            result = check_sunshine(handle)
            if result:
                seq_101[i] = grade
                sunshine_record.append(i)
                print(f"           第{i}次有日光！    ")
        # 重新回到装备选择界面  
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 2)
    

    print("*"*20)
    print(f"一共出现了 {len(sunshine_record)} 次日光， 出现位置为：")
    print(sunshine_record)
    print("*"*20)
    return seq_101, sunshine_record


# 优化101序列
def optimize_sequence_101(handle:basic.HANDLE, grade:int, seq_101, is_detect:bool=True):
    sunshine_record = []

    # 进入选择装备的界面
    find_stove(handle)

    for i in range(len(seq_101)):
        print(f"当前第{i}次测序   "*4)
        
        if seq_101[i] != 0:
            is_detect = True
            if grade < 3:
                pos = find_equipment_from_left(handle, equipments_path[str(grade)])
            else:
                pos = find_equipment_from_right(handle, equipments_path[str(grade)])
            
        else:
            is_detect = False
            pos = find_equipment_from_left(handle, equipments_path["1"])
            
            
        
        if len(pos)==0:
            # 说明没有装备了，sl垫过来
            # 点击返回按钮,两次返回
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.find_and_click(handle, "./img/shenduan/back.png", 2)
            basic.SL_basic(handle, ocr=ocr)
            # 点击炉子
            _, _ = sequence_101_low(handle, i, is_detect=False)   # 递归，推i次序              
            print("重新用低星装备垫结束")
            # 低星装备垫了i次
            pos = find_equipment_from_left(handle, equipments_path[str(grade)])
            if len(pos)==0:
                pos = []
                print("遇到未知错误， 错误点", i)

        # 装备熔炼
        stove_equipment(handle, pos[0])

        if is_detect:
            # 结果检测
            result = check_sunshine(handle)
            if result:
                seq_101[i] = grade
                sunshine_record.append(i)
                print(f"           第{i}次有日光！    ")
        # 重新回到装备选择界面  
        basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 2)
    

    print("*"*20)
    print(f"一共出现了 {len(sunshine_record)} 次日光， 出现位置为：")
    print(sunshine_record)
    print("*"*20)
    return seq_101, sunshine_record

# 细化101序列,输入6星的101序列，向下推导至3星
# 废弃
def refine_seq_101(handle:basic.HANDLE,grade:int, seq_101:np, is_detect:bool=True):

    print("向左侧翻页，翻到第一页")
    while True:
        left_botton_dts = basic.match_template(handle, [basic.imread(handle, "./img/common/left_bottom.png")], match_threshold=0.85)
        if len(left_botton_dts)>0:
            basic.left_mouse_click(handle=handle, point=left_botton_dts[0])
            time.sleep(0.5)
        else:
            break
    
    for i in range(101):
        if seq_101[i]==0:
            pos = find_equipment_from_left(handle, equipments_path["1"])
            
            stove_equipment(handle, pos[0])
        else:
            pos = find_equipment_from_left(handle, equipments_path[str(grade)])
            
            stove_equipment(handle, pos[0])
                
def save_seq(seq101, position, flag_txt=""):
    with open("./seq101.txt", "a") as f:
        if len(flag_txt)>0:
            f.writelines(flag_txt + "\n")
        f.writelines(time.asctime()+ "\n")
        f.writelines("一共出现" + str(len(position)) + "次日光，出现位置为：\n")
        f.writelines(str(position) + "\n")
        temp_record = ""
        for ch in seq101:
            if str(ch) == "0":
                temp_record+="x"
            else:
                temp_record+=str(ch)
                f.writelines(str(len(temp_record)-1) + "   "+ temp_record + "\n")
                temp_record = ""
        if len(temp_record)>0:
            f.writelines(str(len(temp_record)) + "   "+ temp_record + "\n")

        for _ in range(3):
            f.writelines("\n")


def choose_function(x,y,z,z1):
    if x==0:
        return 0
    else:
        if y==0:
            return x
        else:
            if z==0:
                return y
            else:
                if z1==0:
                    return z
                else:
                    return z1


if __name__ == "__main__":
    ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)       # mkldnn加速仅在CPU下有效

    handle = basic.get_handle()

    print("记得穿铠甲！！！！")

    seq_101_6, position = sequence_101(handle, 6, 101, is_detect=True)
    print(seq_101_6)
    if len(position) < 15:
        print("日光少于15个, 退出程序")
        exit()
    seq_101_5, position = optimize_sequence_101(handle, 5, seq_101_6, is_detect=True)
    print(seq_101_5)
    seq_101_4, position = optimize_sequence_101(handle, 4, seq_101_5, is_detect=True)
    print(seq_101_4)
    seq_101_3, position = optimize_sequence_101(handle, 3, seq_101_4, is_detect=True)
    print(seq_101_3)
    save_seq(seq_101_6, position, "最终装备测试结果")
    print(time.asctime())

    print(seq_101_6)
    print(position)
    
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.find_and_click(handle, "./img/shenduan/back.png", 2)
    basic.SL_basic(handle, ocr=ocr)


    
    # result_sequence = [choose_function(x,y,z,z1) for x, y, z, z1 in zip(seq_record[0], seq_record[1], seq_record[2], seq_record[3])]
    # save_seq(result_sequence, "所有装备测试结果")
    # print(result_sequence)
    # print(time.asctime())

    
    # a = check_sunshine(handle)
    # print(a)