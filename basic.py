import win32con, win32api
import win32gui
import pyautogui
import paddlehub as hub

import copy

import sys, os
import time

import cv2

from PyQt5.QtWidgets import QApplication
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image, ImageGrab
import qimage2ndarray

import numpy as np

# 永恒套装
Eternal_suit = {"永恒腕轮":"./img/equipments/reserved/5-6.png", "永恒王冠":"./img/equipments/reserved/5-2.png", "永恒披风":"./img/equipments/reserved/5-96.png", "永恒之球":"./img/equipments/reserved/5-99.png"}
# 命运套装
Fate_suit = {"正义铠甲":"./img/equipments/4level/4-4.png", "勇气腰带":"./img/equipments/4level/4-8.png", "坚韧战靴":"./img/equipments/4level/4-95.png"}

# 元素套装
Ele_suit = {"时光沙漏":"./img/equipments/reserved/5-97.png"}

class HANDLE():
    def __init__(self, handle_id) -> None:
        self.handle_id = handle_id       # 句柄ID
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.handle_id)    # 窗口长宽高
        # self.ocr = PaddleOCR(lang="ch", use_angle_cls=False, use_gpu=False, det_model_dir="./ch_PP-OCRv4_det_server_infer", rec_model_dir="./ch_PP-OCRv4_rec_server_infer", enable_mkldnn=True)
        self.ocr = PaddleOCR(lang="ch", use_angle_cls=False, use_gpu=False, enable_mkldnn=True)



# 获得游戏句柄
def get_handle(FrameTitle = "不思议迷宫"):
    mumu_handle_id = win32gui.FindWindow(0, FrameTitle) | win32gui.FindWindow(FrameTitle, None)
    handle_id = win32gui.FindWindowEx(mumu_handle_id, 0, None, "MuMuPlayer")

    if handle_id is not None:
        return HANDLE(handle_id=handle_id)
    else:
        return None
    
# 获得模拟器句柄
def get_mumu_handle(FrameTitle = "不思议迷宫"):
    mumu_handle_id = win32gui.FindWindow(0, FrameTitle) | win32gui.FindWindow(FrameTitle, None)

    if mumu_handle_id is not None:
        return HANDLE(handle_id=mumu_handle_id)
    else:
        return None


# 模拟鼠标左键点击
def left_mouse_click(handle:HANDLE, point:tuple)->None:

    print(point)
    position = win32api.MAKELONG(point[0], point[1])
    win32api.SendMessage(handle.handle_id, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, position)
    win32api.SendMessage(handle.handle_id, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, position)
    return 
def imread(handle: HANDLE, img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # 读取灰度图像
    default_h = 1280
    default_w = 720

    handle_h = handle.bottom - handle.top
    handle_w = handle.right - handle.left

    # 使用合适的插值方法进行缩放
    img = cv2.resize(img, (int(img.shape[1] * handle_w / default_w), int(img.shape[0] * handle_h / default_h)), interpolation=cv2.INTER_AREA)

    # 检查图像类型
    if img.dtype != np.uint8:
        print(f"模板图像类型错误: {img.dtype}")
        return None

    return img

# handle-句柄; 获取截图(实时画面截图，以屏幕像素点为准)，可选转灰
def get_screenshot(handle: HANDLE, debug=False):
    # 获取窗口的边界
    left, top, right, bottom = handle.left, handle.top, handle.right, handle.bottom
    
    # 使用PIL库捕获指定区域的截图
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    
    # 将PIL图像转换为numpy数组
    raw_color_img = np.array(screenshot)
    
    color_img = cv2.cvtColor(raw_color_img, cv2.COLOR_BGR2RGB)  # BGR转RGB
    gray_img = cv2.cvtColor(raw_color_img, cv2.COLOR_BGR2GRAY)  # BGR转灰度
    if debug:
        # 显示截图（可选）
        cv2.imshow('Gray Image', gray_img)
        cv2.imshow('Color Image', color_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(f"截图分辨率: {gray_img.shape}")
    
    return gray_img, color_img  # 返回灰度图，色彩图


def nms(dets, thresh=0.7):
    """
    非极大值抑制

    :param dets: 检测结果列表，每个元素为 (x1, y1, x2, y2, score)
    :param thresh: 阈值
    :return: 去除重叠的检测结果
    """
    if len(dets) == 0:
        return []

    # 按置信度排序
    dets = sorted(dets, key=lambda x: x[4], reverse=True)
    keep = []
    while dets:
        det = dets.pop(0)
        keep.append(det)
        suppress = []
        for other_det in dets:
            # 计算两个矩形的交集面积
            x1 = max(det[0], other_det[0])
            y1 = max(det[1], other_det[1])
            x2 = min(det[2], other_det[2])
            y2 = min(det[3], other_det[3])
            w = max(0, x2 - x1)
            h = max(0, y2 - y1)
            inter = w * h

            # 计算两个矩形的面积
            det_area = (det[2] - det[0]) * (det[3] - det[1])
            other_det_area = (other_det[2] - other_det[0]) * (other_det[3] - other_det[1])

            # 计算交并比（IoU）
            iou = inter / (det_area + other_det_area - inter)

            # 如果IoU大于阈值，则抑制该检测结果
            if iou > thresh:
                suppress.append(other_det)
        dets = [d for d in dets if d not in suppress]

    return keep



def find_image_center(handle: HANDLE, template_paths, match_threshold=0.85, timeout=10, interval=0.1, debug=True, ROI=None):
    """
    在指定句柄的窗口中找到指定图像并返回中心坐标。

    :param handle: 句柄对象
    :param template_paths: 模板图像的路径列表
    :param match_threshold: 匹配的置信度阈值
    :param timeout: 超时时间（秒）
    :param interval: 每次尝试之间的间隔时间（秒）
    :param debug: 是否启用调试模式
    :return: 图像中心坐标 (x, y) 或 None 如果未找到图像
    """
    
    start_time = time.time()
    print("开始查找图像")
    
    templates = [imread(handle, template_path) for template_path in template_paths]
    if any(template is None for template in templates):
        print("错误: 无法读取所有模板图像")
        return None

    best_match = None
    best_match_val = -1
    best_template_path = None

    while time.time() - start_time < timeout:
        try:
            gray_img, _ = get_screenshot(handle)
            
            # 检查图像类型
            if gray_img.dtype != np.uint8:
                print(f"截图图像类型错误: {gray_img.dtype}")
                return None
            
            # 如果提供了ROI参数，则裁剪图像
            if ROI is not None:
                x, y, w, h = ROI
                gray_img = gray_img[x:x+w, y:y+h]

            detections = []
            for template_path, template in zip(template_paths, templates):
                if template is None:
                    print(f"模板图像 {template_path} 为空")
                    continue

                result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val > match_threshold:
                    h, w = template.shape[:2]
                    top_left = max_loc
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    detections.append((top_left[0], top_left[1], bottom_right[0], bottom_right[1], max_val))

            # 应用非极大值抑制
            if detections:
                detections = nms(detections, thresh=0.7)

            if detections:
                best_match = detections[0][:2]  # 取第一个最佳匹配的左上角坐标
                best_match_val = detections[0][4]
                best_template_path = template_paths[0]

                print("找到！！！")
                # 获取匹配区域的左上角坐标
                top_left = best_match
                # 获取模板图像的宽度和高度
                h, w = templates[0].shape[:2]
                # 计算中心位置
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2
                
                if ROI is not None:
                    center_x += ROI[0]
                    center_y += ROI[1]
                

                # 调试代码：在截图上绘制矩形框
                if debug:
                    print(f"图像中心坐标为:({center_x}, {center_y})")          
                    print(f"匹配图像: {best_template_path}, 匹配度: {best_match_val:.3f}")
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    cv2.rectangle(gray_img, top_left, bottom_right, (0, 0, 0), 2)
                    # 可视化调试：在截图上绘制ROI区域的矩形框
                    cv2.imshow("Matched Region", gray_img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    
                return (center_x, center_y)
        except Exception as e:
            print(f"发生错误: {e}")
        
        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配图像")
    return ()


def find_and_click_image(handle: HANDLE, template_paths, sleep_time=0, match_threshold=0.85, timeout=10, interval=0.1, debug=True, ROI=None):
    try:
        det_pos = find_image_center(handle, template_paths, match_threshold, timeout, interval, debug, ROI)
        left_mouse_click(handle, det_pos)
        time.sleep(sleep_time)
    except Exception as e:
        print(f"发生错误: {e}")


def find_text_center(handle: HANDLE, tar_txts, timeout=5, interval=1, debug=False, ROI=None):
    start_time = time.time()
    print(f"开始查找{tar_txts}")

    while time.time() - start_time < timeout:
        try:
            _, img = get_screenshot(handle)
            h, w, _ = img.shape
            
            # 根据region参数裁剪图像
            if ROI is not None:
                x, y, w, h = ROI
                img = img[x:x+w, y:y+h]

            result = handle.ocr.ocr(img)

            
            if len(result[0]) > 0:
                for item in result[0]:
                    
                    det_texts = item[-1][0]
                    det_confidence = item[-1][1]
                    
                    if debug:
                        print(f"检测到：{det_texts}, 置信度：{det_confidence}")

                    if any(tar_txt in det_texts for tar_txt in tar_txts):
                        print(f"找到！！！{det_texts}")
                        # 获取文本框的四个顶点坐标
                        points = item[0]
                        # 计算边界框的左上角和右下角坐标
                        x1 = min(point[0] for point in points)
                        y1 = min(point[1] for point in points)
                        x2 = max(point[0] for point in points)
                        y2 = max(point[1] for point in points)
                        # 计算中心位置
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        
                        # 如果指定了region，需要将坐标转换为原始图像上的绝对坐标
                        if ROI is not None:
                            center_x += x
                            center_y += y
                        
                        if debug:
                            print(f"文本中心坐标为:({center_x}, {center_y})")
                            result = result[0]
                            image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                            boxes = [line[0] for line in result]
                            txts = [line[1][0] for line in result]
                            scores = [line[1][1] for line in result]
                            im_show = draw_ocr(image, boxes, txts, scores, font_path='/path/to/PaddleOCR/doc/fonts/simfang.ttf')
                            im_show = Image.fromarray(im_show)
                            im_show.save('result.jpg')
                        
                        return (int(center_x), int(center_y))
            else:
                continue
        except Exception as e:
            print(f"发生错误: {e}")
        
        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配文本")
    return False   

def find_and_click_text(handle: HANDLE, tar_txts, timeout=5, interval=1, debug=False, sleep_time=0, region=None):
    try:
        det_pos = find_text_center(handle, tar_txts, timeout, interval, debug, region)
        left_mouse_click(handle, det_pos)
        time.sleep(sleep_time)
        return True
    except Exception as e:
        print(f"发生错误: {e}")
        
def push_one_squence(handle: HANDLE):
    time.sleep(0.5)
    # print("点击右下角", end=' ')
    left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True, size=(519, 923))        
    find_and_click_text(handle=handle, tar_txts=["阶位"])
    time.sleep(0.5)
    if find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"], sleep_time=1):
        find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"])
        print("""使用了[治疗术", "石肤术", "祝福术"]中的一个""")

# # 截图默认在（1280， 720下截图，读取图片时候做大小变换）, 不然模板匹配的时候会出错
# def imread(handle:HANDLE, img_path):
#     img = cv2.imread(img_path)
#     default_h = 1280
#     default_w = 720

#     handle_h = handle.bottom-handle.top
#     handle_w = handle.right-handle.left

#     img = cv2.resize(img, (int(img.shape[1]*handle_w/default_w), int(img.shape[0]*handle_h/default_h)))

#     return img


# # 坐标转换，将几行几列(从1开始)变成点击坐标(坐标xy颠倒)
# def position_trans(handle:HANDLE, pos:tuple)->tuple:
#     rows = (0, 305, 430, 555, 680, 805, 930)           # x轴 6行每行中心点坐标   190+i*87
#     cols = (0, 85, 225, 365, 505, 645)

#     weight = 720
#     height = 1280

#     handle_h = handle.bottom-handle.top
#     handle_w = handle.right-handle.left

#     return (int(cols[pos[1]]*handle_w/weight), int(rows[pos[0]]*handle_h/height))


# 小sl
def SL_basic(handle:HANDLE):
    # basic.load_mumu_video(self.handle, "./img/mumu_video/小xl.mmor")
    find_and_click_image(handle, ["./img/common/setting.png"], ROI=(0.0, 0.0, 1.0, 0.1))
    find_and_click_image(handle, ["./img/common/account.png"])
    time.sleep(1)
    find_and_click_text(handle, ["登出"], sleep_time=5)
    find_and_click_text(handle, ["开始游戏"], timeout=10, sleep_time=8)
    find_and_click_text(handle, ["确定"], sleep_time=1)
    find_and_click_text(handle, ["继续冒险"], sleep_time=5)
    
    while True:
        if find_image_center(handle, ["./img/common/setting.png"]):
            break

# 暂离
def save_staute(handle:HANDLE):
    left_mouse_click(handle=handle, point=(0.0847222,0.0351563), normalize=True)   # 点左上角
    time.sleep(1)
    find_and_click_text(handle, ["暂离"], sleep_time=5)
    
    find_and_click_text(handle, ["确定"], sleep_time=1)
    # find_and_click_text(handle, ["重新连接"], 1, ocr=ocr)
    find_and_click_image(handle, ["./img/common/back2.png"], sleep_time=5)
    while True:
        if find_image_center(handle, ["./img/common/setting.png"]):
            break

# 执行一次断网，再执行联网
def change_network_state(handle):
    go_back_to_home(handle)
    # 启动V2RayNG应用
    find_and_click_image(handle, ["./img/global/V2rayN.png"], sleep_time=5)
    print("成功打开V2RayNG应用")
    find_and_click_image(handle, ["./img/global/off_button.png"], sleep_time=5)
    time.sleep(2)
    go_back_to_home(handle)
    find_and_click_image(handle, ["./img/global/game.png"], sleep_time=5)



def go_back_to_home(handle: HANDLE):
    # 设置焦点到指定的窗口句柄
    win32gui.SetForegroundWindow(handle.handle_id)
    # 发送返回键事件
    # 单个按键
    # 注意：HOME键按下要抬起
    win32api.keybd_event(36,0,0,0) 
    time.sleep(0.1)
    win32api.keybd_event(36,0,win32con.KEYEVENTF_KEYUP,0)  

def check_sunshine_number(handle):
    find_and_click_image(handle, "./img/shenduan/armor.png",sleep_time=1)
    find_and_click_text(handle, "神力刻印")
    
    pass

    # 神锻黑尸体
def SL_body(handle: HANDLE, star=False, debug=False)->bool:
    save_staute(handle=handle)
    # 检查尸体位置
    dts_pos = find_image_center(handle, ["./img/shenduan/body.png", "./img/shenduan/body_9.png", "./img/shenduan/weapenpile.png"], match_threshold=0.7)
    need_sl = False
    while dts_pos is None:
        print("没有检测到尸体，尝试推序规避时停影响")
        push_one_squence(handle)
        dts_pos = find_image_center(handle, ["./img/shenduan/body.png", "./img/shenduan/body_9.png", "./img/shenduan/weapenpile.png"], match_threshold=0.7)
        need_sl = True
        
    ##火神判断
    
    print("尸体像素位置：", dts_pos)
    
    if need_sl:
        SL_basic(handle=handle)
    continue_flag = True
    order = 0
    while continue_flag:     
        print(f"第{order}次   "*5)

        # 直接推序1次
        if order != 0:
            
            firegod_pos = find_image_center(handle, ["./img/shenduan/red_body.png", "./img/shenduan/firegod.png", "./img/shenduan/weapon.png"], timeout=3, interval=1)
            if firegod_pos is None:
                time.sleep(0.5)
                push_one_squence(handle)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle)

        # 点击尸体并翻找
        left_mouse_click(handle=handle, point=dts_pos)
        time.sleep(1)
        find_and_click_text(handle=handle, tar_txts=["翻找"])

        # 检测是否为日光
        if star == False:
            result = find_text_center(handle, ["日", "日光"], timeout=3, interval=0.01, region= ((0.075,0.85), (0.17,0.91)), debug=debug)
        else:
            result = find_text_center(handle, ["日", "日光", "星", "星光"], timeout=3, interval=0.01, region= ((0.075,0.85), (0.17,0.91)), debug=debug)
        if result:
            save_staute(handle=handle)
            return True 

        order+=1

        SL_basic(handle=handle)
        
    return True    


def SL_pool(handle: HANDLE, debug=False)->bool:
    # 检查水池位置
    save_staute(handle=handle)
    
    dts_pos = find_image_center(handle, ["./img/shenduan/pool.png"], match_threshold=0.8)
    need_sl =  False
    while dts_pos is None:
        print("没有检测到水池，尝试推序规避时停影响")
        push_one_squence(handle)
        dts_pos = find_image_center(handle, ["./img/shenduan/pool.png"], match_threshold=0.8)
        need_sl = True


    print("水池像素位置：", dts_pos)
    
    if need_sl:
        SL_basic(handle=handle)

    continue_flag = True
    order = 0
    while continue_flag:     
        print(f"第{order}次   "*5)
        


        # 直接推序1次
        if order != 0:
            
            firegod_pos = find_image_center(handle, ["./img/shenduan/red_body.png", "./img/shenduan/firegod.png", "./img/shenduan/weapon.png"], timeout=3, interval=1)
            if firegod_pos is None:
                push_one_squence(handle)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle)

        # 点击尸体并翻找
        left_mouse_click(handle=handle, point=dts_pos)
        time.sleep(1)
        
        find_and_click_text(handle=handle, tar_txts=["浸泡铠甲"])

        # 检测是否为日光
        result = find_text_center(handle, ["布武"], timeout=3, interval=0.01, region= ((0.25,0.32), (0.72,0.36)), debug=debug)
        if result:
            print("找到了布武!!!")
            save_staute(handle=handle)
            return True

        order+=1
        print("没找到,开始小sl")

        SL_basic(handle=handle)

    
    return True

def use_quake(handle):
    time.sleep(2)
    print("点击右下角", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(1)
    print("点击卷轴系列", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.25,0.782031), normalize=True)
    time.sleep(1)
    print("点击土系魔法", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.901389,0.429688), normalize=True)
    time.sleep(1)
    print("点击地震术", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    time.sleep(1)
    print("点击头像使用", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.498611,0.947656), normalize=True)
    time.sleep(2)


# 使用死亡波纹
def use_death_ripper(handle):
    time.sleep(2)
    print("点击右下角", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True)
    time.sleep(1)
    print("点击卷轴系列", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.25,0.782031), normalize=True)
    time.sleep(1)
    print("点击暗系魔法", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.888889,0.673438), normalize=True)
    time.sleep(1)
    print("点击死亡波纹", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.609722,0.36875), normalize=True)
    time.sleep(1)
    print("点击头像使用", end=' ', flush=True)
    left_mouse_click(handle=handle, point=(0.498611,0.947656), normalize=True)
    time.sleep(2)

def get_lack_equipment(handle, equip_dict):
    equip_dict_copy = copy.deepcopy(equip_dict)
    find_and_click_image(handle, ["./img/common/equip_pack.png"])
    for k, v in equip_dict.items():

        det_pos = find_image_center(handle, [v])
        if det_pos is not None:
            del equip_dict_copy[k]
    find_and_click_text(handle=handle, tar_txts=["返回"], sleep_time=1)
    return list(equip_dict_copy.keys())
def SL_equip(handle:HANDLE, target_suit=Eternal_suit):
    
    equip_name_list = get_lack_equipment(handle, target_suit)
    print(f"缺少装备：{equip_name_list}")
    if len(equip_name_list) == 0:
        return True
    ops = 0
    while ops < 101:
        print(f"这是第{ops}次黑装备     "*4)
        save_staute(handle)
        print("检查是否断网")
        change_network_state(handle=handle)
        time.sleep(5)
        find_and_click_image(handle, ["./img/common/open_door.png"], sleep_time=5)
        
        # 使用卷轴杀怪
        use_quake(handle)
        time.sleep(2)

        while not find_image_center(handle, ["./img/common/equip_box.png"]):
            use_death_ripper(handle)
            time.sleep(2)

        # 点击宝箱
        find_and_click_image(handle, ["./img/common/equip_box.png"])
        result = find_text_center(handle, equip_name_list, timeout=3, interval=0.01, region= ((0.075,0.85), (0.17,0.91)))
        if result:
            # 联网保存
            change_network_state(handle=handle)
            save_staute(handle)
            return True
        else:
            ops+=1
            # 小SL
            find_and_click_image(handle, ["./img/common/setting.png"], sleep_time=3)
            find_and_click_image(handle, ["./img/common/account.png"], sleep_time=3)
            find_and_click_text(handle, ["登出"], sleep_time=8)
            while not find_image_center(handle, ["./img/common/startgame.png"]):
                time.sleep(1)
            change_network_state(handle=handle)
            time.sleep(10)
            find_and_click_text(handle, ["我知道了"], sleep_time=3)     
            find_and_click_text(handle, ["开始游戏"], sleep_time=5)     
            find_and_click_text(handle, ["确定"], sleep_time=1) 
            find_and_click_text(handle, ["继续冒险"], sleep_time=5) 
            
    else:
        print("超过了101次，需要大SL")
        find_and_click_image(handle, ["./img/common/setting.png"], sleep_time=3)
        find_and_click_image(handle, ["./img/common/account.png"], sleep_time=3)
        find_and_click_text(handle, ["登出"], sleep_time=8)
        while not find_image_center(handle, ["./img/common/startgame.png"]):
                time.sleep(1)
        change_network_state(handle=handle)



if __name__ == '__main__':
    handle = get_handle()
    # find_image_center(handle, ["./img/common/test.png"], ROI=(50, 50, 500, 500))
    find_text_center(handle, ["星期五"], debug=True, ROI=(10, 10, 500, 500))
    # gray_img, color_img = get_screenshot(handle, True)
    # find_and_click_text(handle, ["开始游戏"], region=((0, 0.3), (1, 0.9)),debug=True)
    # find_text_center(handle, ["37"], region=((0, 0), (1, 0.35)),debug=True)
    # SL_body(handle,star=0)
    # save_staute(handle)
    # SL_basic(handle)
    # find_text_center(handle, ["阶位"],debug=True)
    # SL_equip(handle)