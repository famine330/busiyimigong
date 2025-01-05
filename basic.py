import win32con, win32api
import win32gui
import pyautogui
import paddlehub as hub
import copy

import sys, os
import time

import cv2

from PyQt5.QtWidgets import QApplication
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


# 调用mumu模拟器的录制文件
def load_mumu_video(handle:HANDLE, path):
    resolution_x, resolution_y = handle.right-handle.left, handle.bottom-handle.top

    # with open(path, "r", encoding='gb18030', errors='ignore') as f:
    with open(path, "r", encoding='utf-8') as f:
        data = f.read()
        actions = eval(data)['actions']

        # 遍历每一次动作
        for ele in actions[1:-1]:
            # print(ele)
            ele_data = ele['data']
            timing = int(ele['timing'])//1000+1
            # print(f"休息{timing}秒")
            time.sleep(timing)
            if ele_data[:9]=='press_rel':

                point_str = ele_data.split(":")[1][1:-1]
                dx, dy = list(map(float, point_str.split(",")))
                x, y = int(dx*resolution_x), int(dy*resolution_y)
                left_mouse_click(handle, (x, y))
                print(f"点击({x},{y})")




# 模拟鼠标左键点击
def left_mouse_click(handle:HANDLE, point:tuple, normalize=False, size=(0, 0))->None:
    if normalize:
        # resolution_x, resolution_y = handle.right-handle.left, handle.bottom-handle.top   # 没有截图之前
        # resolution_x, resolution_y = 519, 923                                             # 截图之后变为图像大小
        size = (handle.right-handle.left, handle.bottom-handle.top)
        new_point = (int(point[0]*size[0]), int(point[1]*size[1]))
    else:
        new_point = point

    print(new_point)
    position = win32api.MAKELONG(new_point[0], new_point[1])
    win32api.SendMessage(handle.handle_id, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, position)
    win32api.SendMessage(handle.handle_id, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, position)
    return 


# handle-句柄; 获取截图(实时画面截图，以屏幕像素点为准)，可选转灰
def get_screenshot(handle:HANDLE):
    # Qt5截图
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(handle.handle_id).toImage()
    # Qimage转ndarray
    img_z = qimage2ndarray.rgb_view(img)

    # 调整图像大小以匹配目标分辨率
    img_z = cv2.resize(img_z, (handle.right-handle.left, handle.bottom-handle.top))      # 图片转成100%分辨率大小


    img_z = cv2.cvtColor(img_z, cv2.COLOR_BGR2RGB)  # BGR转RGB
    img_g = cv2.cvtColor(img_z, cv2.COLOR_BGR2GRAY)  # BGR转灰度
    return img_g, img_z   # 返回灰度图，色彩图


# #  伪IOU计算，两点之间差10即可   true相距远保留
# def ComputeIOU(box1, box2)->bool:
#     return True if (box1[0]-box2[0])**2+(box1[1]-box2[1])**2>distance_threshold else False


# # 没想到这里也要用到nms...
# def nms(dets, h, w):
#     dets.sort(key=lambda x:x[2])   # 根据值进行排序
#     dets = np.array(dets)
#     pick_bboxes = []
#     while dets.shape[0]:
#         bbox = dets[-1]   # 取最大conf的dt
#         keep_index = np.array([ComputeIOU(bbox, box) for box in dets[:-1]]+[False])
#         dets = dets[keep_index]    

#         pick_bboxes.append((int(bbox[0]+w/2), int(bbox[1]+h/2)))
    
#     return pick_bboxes



# def match_template(handle:HANDLE, img_template_list, match_threshold=0.8):
#     img_bottom, _ = get_screenshot(handle) 

#     dts = []
#     for img_template in img_template_list:
#         # 彩色图转灰度图
#         if img_template.ndim ==3:
#             img_template = cv2.cvtColor(img_template, cv2.COLOR_BGR2GRAY)

#         h, w = img_template.shape[:2]
#         # 模板匹配
#         match = cv2.matchTemplate(img_bottom, img_template, cv2.TM_CCOEFF_NORMED)

#         rows, cols = np.where(match > match_threshold)  # (2, len)  第一行x，第二行y

#         for i in range(len(rows)):
#             dts.append((cols[i], rows[i], match[rows[i], cols[i]]))

#     # 做nms
#     nms_dts = nms(dts, h=h, w=w)

#     # 调试
#     # for ele in nms_dts:
#     #     cv2.circle(img_bottom, ele, 10, (0, 0, 255), 4)
#     # cv2.imshow("1a", img_bottom)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#     return nms_dts

def find_and_click_image_from_screen(template_path, confidence=0.7, region=None, debug=True):
    """
    在屏幕上找到指定图像并点击。

    :param template_path: 模板图像的路径
    :param confidence: 匹配的置信度阈值
    :param region: 指定屏幕范围 (left, top, width, height)
    :param debug: 是否启用调试模式
    """
    # 读取模板图像
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"无法读取模板图像: {template_path}")
        return

    # 获取屏幕截图
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()

    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 如果匹配度超过阈值，则点击图像中心
    if max_val >= confidence:
        h, w = template.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2

        # 如果指定了region，需要将坐标转换为屏幕上的绝对坐标
        if region:
            center_x += region[0]
            center_y += region[1]

        print(f"找到图像，中心位置: ({center_x}, {center_y}), 匹配度: {max_val:.4f}")
        pyautogui.click(center_x, center_y)
        
        # 调试代码：在截图上绘制矩形框
        if debug:
            bottom_right = (max_loc[0] + w, max_loc[1] + h)
            cv2.rectangle(screenshot, max_loc, bottom_right, (0, 255, 0), 2)
            cv2.imshow("Matched Region", screenshot)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return (center_x, center_y)
    else:
        print(f"未找到图像，最大匹配度: {max_val:.4f}")
        return None


def find_image_center(handle: HANDLE, template_paths, match_threshold=0.7, timeout=10, interval=0.1, debug=False):
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

    default_h = 1280
    default_w = 720

    handle_h = handle.bottom-handle.top
    handle_w = handle.right-handle.left
    
    start_time = time.time()
    print("开始查找图像")
    
    templates = [cv2.resize(cv2.imread(template_path, cv2.IMREAD_GRAYSCALE), 
                            (int(cv2.imread(template_path, cv2.IMREAD_GRAYSCALE).shape[1] * handle_w / default_w), 
                             int(cv2.imread(template_path, cv2.IMREAD_GRAYSCALE).shape[0] * handle_h / default_h))) 
                 for template_path in template_paths]
    if any(template is None for template in templates):
        print("错误: 无法读取所有模板图像")
        return None

    best_match = None
    best_match_val = -1
    best_template_path = None

    while time.time() - start_time < timeout:
        try:
            _, img = get_screenshot(handle)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 确保截图是灰度图


            for template_path, template in zip(template_paths, templates):
                result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val > best_match_val:
                    best_match_val = max_val
                    best_match = max_loc
                    best_template = template
                    best_template_path = template_path

            if best_match_val >= match_threshold:
                print("找到！！！")
                if debug:
                    print(f"匹配图像: {best_template_path}, 匹配度: {best_match_val:.4f}")
                # 获取匹配区域的左上角坐标
                if best_match is not None:  # 检查 best_match 是否为 None
                    top_left = best_match
                    # 获取模板图像的宽度和高度
                    h, w = best_template.shape[:2]
                    # 计算中心位置
                    center_x = top_left[0] + w // 2
                    center_y = top_left[1] + h // 2

                    # 调试代码：在截图上绘制矩形框
                    if debug:
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
                        cv2.imshow("Matched Region", img)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()

                    return (center_x, center_y)
        except Exception as e:
            print(f"发生错误: {e}")
        
        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配图像")
    return None


def find_and_click_image(handle: HANDLE, template_paths, sleep_time=0, match_threshold=0.85, timeout=10, interval=0.1, debug=False):
    try:
        det_pos = find_image_center(handle, template_paths, match_threshold, timeout, interval, debug)
        left_mouse_click(handle, det_pos)
        time.sleep(sleep_time)
    except Exception as e:
        print(f"发生错误: {e}")


def find_text_center(handle: HANDLE, tar_txts, timeout=10, interval=0.1, ocr=None, debug=False, region=None):
    start_time = time.time()
    print("开始查找文本")

    while time.time() - start_time < timeout:
        try:
            _, img = get_screenshot(handle)
            h, w, _ = img.shape
            
            # 根据region参数裁剪图像
            if region:
                # 将相对坐标转换为像素坐标
                x1, y1 = int(region[0][0] * w), int(region[0][1] * h)
                x2, y2 = int(region[1][0] * w), int(region[1][1] * h)
                img = img[y1:y2, x1:x2]
                if debug:
                    print(f"裁剪区域: ({x1}, {y1}, {x2}, {y2})")
            
            result = ocr.recognize_text(images=[img])
            if debug:
                print(f"检测到文本：{result}")
            
            if len(result[0]['data']) > 0:
                for item in result[0]['data']:
                    # print(item)
                    det_texts = item['text']
                    
                    if debug:
                        print(f"检测到：{det_texts}")

                    if any(tar_txt in det_texts for tar_txt in tar_txts):
                        print("找到！！！")
                        # 获取文本框的坐标
                        if 'text_box_position' in item:
                            # 获取文本框的四个顶点坐标
                            points = item['text_box_position']
                            # 计算边界框的左上角和右下角坐标
                            x1 = min(point[0] for point in points)
                            y1 = min(point[1] for point in points)
                            x2 = max(point[0] for point in points)
                            y2 = max(point[1] for point in points)
                            # 计算中心位置
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            
                            # 如果指定了region，需要将坐标转换为原始图像上的绝对坐标
                            if region:
                                center_x += x1
                                center_y += y1
                            
                            if debug:
                                print(f"坐标: ({center_x}, {center_y})")
                                
                            
                            # 可视化调试
                            if debug:
                                # 绘制文本框
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                # 绘制中心点
                                cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)
                                # 显示图像
                                cv2.imshow("Detected Text", img)
                                cv2.waitKey(0)
                                cv2.destroyAllWindows()
                            
                            return (center_x, center_y)
                        else:
                            print("错误: 'text_box_position' 键不存在于 item 中")
        except Exception as e:
            print(f"发生错误: {e}")
        
        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配文本")
    return False   

def find_and_click_text(handle: HANDLE, tar_txts, timeout=10, interval=0.1, ocr=None, debug=False, sleep_time=0, region=None):
    try:
        det_pos = find_text_center(handle, tar_txts, timeout, interval, ocr, debug, region)
        left_mouse_click(handle, det_pos)
        time.sleep(sleep_time)
        return True
    except Exception as e:
        print(f"发生错误: {e}")
        
def push_one_squence(handle: HANDLE, ocr=None):
    time.sleep(0.5)
    # print("点击右下角", end=' ')
    left_mouse_click(handle=handle, point=(0.854167,0.939063), normalize=True, size=(519, 923))        
    find_and_click_text(handle=handle, tar_txts=["阶位"], ocr=ocr)
    time.sleep(0.5)
    if find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"], ocr=ocr, sleep_time=1):
        find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"], ocr=ocr)
        print("""使用了[治疗术", "石肤术", "祝福术"]中的一个""")

# 截图默认在（1280， 720下截图，读取图片时候做大小变换）, 不然模板匹配的时候会出错
def imread(handle:HANDLE, img_path):
    img = cv2.imread(img_path)
    default_h = 1280
    default_w = 720

    handle_h = handle.bottom-handle.top
    handle_w = handle.right-handle.left

    img = cv2.resize(img, (int(img.shape[1]*handle_w/default_w), int(img.shape[0]*handle_h/default_h)))

    return img


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
def SL_basic(handle:HANDLE, ocr):
    # basic.load_mumu_video(self.handle, "./img/mumu_video/小xl.mmor")
    find_and_click_image(handle, ["./img/common/setting.png"])
    find_and_click_image(handle, ["./img/common/account.png"])
    find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=5)
    find_and_click_text(handle, ["开始游戏"], ocr=ocr, sleep_time=5)
    find_and_click_text(handle, ["确定"], ocr=ocr)
    find_and_click_text(handle, ["继续冒险"], ocr=ocr, sleep_time=5)
    
    while True:
        if find_image_center(handle, ["./img/common/setting.png"]):
            break

# 暂离
def save_staute(handle:HANDLE, ocr):
    left_mouse_click(handle=handle, point=(0.0847222,0.0351563), normalize=True)   # 点左上角
    time.sleep(1)
    find_and_click_text(handle, ["暂离"], ocr=ocr, sleep_time=5)
    
    find_and_click_text(handle, ["确定"], ocr=ocr)
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

    # 神锻黑尸体
def SL_body(handle: HANDLE, ocr=None, star=False, debug=False)->bool:
    save_staute(handle=handle, ocr=ocr)
    # 检查尸体位置
    dts_pos = find_image_center(handle, ["./img/shenduan/body.png", "./img/shenduan/body_9.png", "./img/shenduan/weapenpile.png"], match_threshold=0.7)
    need_sl = False
    while len(dts_pos)==0:
        print("没有检测到尸体，尝试推序规避时停影响")
        push_one_squence(handle, ocr=ocr)
        dts_pos = find_image_center(handle, ["./img/shenduan/body.png", "./img/shenduan/body_9.png", "./img/shenduan/weapenpile.png"], match_threshold=0)
        need_sl = True
        
    
    ##火神判断
    
    print("尸体像素位置：", dts_pos)
    
    if need_sl:
        SL_basic(handle=handle, ocr=ocr)

    continue_flag = True
    order = 0
    while continue_flag:     
        print(f"第{order}次   "*5)
        


        # 直接推序1次
        if order != 0:
            
            firegod_pos = find_image_center(handle, ["./img/shenduan/red_body.png", "./img/shenduan/firegod.png", "./img/shenduan/weapon.png"], timeout=3, interval=1)
            if firegod_pos is None:
                push_one_squence(handle, ocr=ocr)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle, ocr=ocr)

        # 点击尸体并翻找
        left_mouse_click(handle=handle, point=dts_pos)
        find_and_click_text(handle=handle, tar_txts=["翻找"], ocr=ocr)

        # 检测是否为日光
        if star == False:
            result = find_text_center(handle, ["日", "日光"], timeout=3, interval=0.01, ocr=ocr, region= ((0.05,0.85), (0.3,0.95)), debug=debug)
        else:
            result = find_text_center(handle, ["日", "日光", "星", "星光"], timeout=3, interval=0.01, ocr=ocr, region= ((0.05,0.85), (0.3,0.95)), debug=debug)
        if result:
            save_staute(handle=handle, ocr=ocr)
            return True 

        order+=1

        SL_basic(handle=handle, ocr=ocr)
        
    return True    


def SL_pool(handle: HANDLE, ocr=None, debug=False)->bool:
    # 检查水池位置
    save_staute(handle=handle, ocr=ocr)
    
    dts_pos = find_image_center(handle, ["./img/shenduan/pool.png"], match_threshold=0.8)
    need_sl =  False
    while len(dts_pos)==0:
        print("没有检测到水池，尝试推序规避时停影响")
        push_one_squence(handle,ocr=ocr)
        dts_pos = find_image_center(handle, ["./img/shenduan/pool.png"], match_threshold=0.8)
        need_sl = True


    print("水池像素位置：", dts_pos)
    
    if need_sl:
        SL_basic(handle=handle, ocr=ocr)

    continue_flag = True
    order = 0
    while continue_flag:     
        print(f"第{order}次   "*5)
        


        # 直接推序1次
        if order != 0:
            
            firegod_pos = find_image_center(handle, ["./img/shenduan/red_body.png", "./img/shenduan/firegod.png", "./img/shenduan/weapon.png"], timeout=3, interval=1)
            if firegod_pos is None:
                push_one_squence(handle,ocr=ocr)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle, ocr=ocr)

        # 点击尸体并翻找
        left_mouse_click(handle=handle, point=dts_pos)
        time.sleep(1)
        
        find_and_click_text(handle=handle, tar_txts=["浸泡铠甲"], ocr=ocr)

        # 检测是否为日光
        result = find_text_center(handle, ["布武"], timeout=3, interval=0.01, ocr=ocr, region= ((0.20,0.30), (0.72,0.36)), debug=debug)
        if result:
            print("找到了布武!!!")
            save_staute(handle=handle, ocr=ocr)
            return True

        order+=1
        print("没找到,开始小sl")

        SL_basic(handle=handle, ocr=ocr)

    
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

def get_lack_equipment(handle, ocr, equip_dict):
    equip_dict_copy = copy.deepcopy(equip_dict)
    find_and_click_image(handle, ["./img/common/equip_pack.png"])
    for k, v in equip_dict.items():

        det_pos = find_image_center(handle, [v])
        if det_pos is not None:
            del equip_dict_copy[k]
    return list(equip_dict_copy.keys())
def SL_equip(handle:HANDLE, ocr=None, target_suit=Eternal_suit):
    
    equip_name_list = get_lack_equipment(handle, ocr, target_suit)
    print(f"缺少装备：{equip_name_list}")
    if len(equip_name_list) == 0:
        return True
    ops = 0
    while ops < 101:
        print(f"这是第{ops}次黑装备     "*4)
        save_staute(handle, ocr)
        print("检查是否断网")
        change_network_state(handle=handle)
        time.sleep(5)
        find_and_click_image(handle, ["./img/common/open_door.png"], sleep_time=3)
        
        # 使用卷轴杀怪
        use_quake(handle)
        time.sleep(2)

        while not find_image_center(handle, ["./img/common/equip_box.png"]):
            use_death_ripper(handle)
            time.sleep(2)

        # 点击宝箱
        find_and_click_image(handle, ["./img/common/equip_box.png"])
        result = find_text_center(handle, equip_name_list, timeout=3, interval=0.01, ocr=ocr, region= ((0.05,0.85), (0.3,0.95)))
        if result:
            # 联网保存
            change_network_state(handle=handle)
            save_staute(handle, ocr=ocr)
            return True
        else:
            ops+=1
            # 小SL
            find_and_click_image(handle, ["./img/common/setting.png"], sleep_time=3)
            find_and_click_image(handle, ["./img/common/account.png"], sleep_time=3)
            find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=8)
            while not find_image_center(handle, ["./img/common/startgame.png"]):
                time.sleep(1)
            change_network_state(handle=handle)
            time.sleep(10)
            find_and_click_text(handle, ["我知道了"], sleep_time=3, ocr=ocr)     
            find_and_click_text(handle, ["开始游戏"], sleep_time=5, ocr=ocr)     
            find_and_click_text(handle, ["确定"], ocr=ocr) 
            find_and_click_text(handle, ["继续冒险"], sleep_time=5, ocr=ocr) 
            
    else:
        print("超过了101次，需要大SL")
        find_and_click_image(handle, ["./img/common/setting.png"], sleep_time=3)
        find_and_click_image(handle, ["./img/common/account.png"], sleep_time=3)
        find_and_click_text(handle, ["登出"], ocr=ocr, sleep_time=8)
        while not find_image_center(handle, ["./img/common/startgame.png"]):
                time.sleep(1)
        change_network_state(handle=handle)



if __name__ == '__main__':
    handle = get_handle()
    ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)
