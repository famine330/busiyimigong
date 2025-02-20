import win32con, win32api
import win32gui, win32ui
import pyautogui
import paddlehub as hub
import pywintypes
import re
import traceback
import ctypes
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
Eternal_suit = {
    "永恒腕轮": "./img/equipments/reserved/5-6.png",
    "永恒王冠": "./img/equipments/reserved/5-2.png",
    "永恒披风": "./img/equipments/reserved/5-96.png",
    "永恒之球": "./img/equipments/reserved/5-99.png",
}
# 命运套装
Fate_suit = {
    "正义铠甲": "./img/equipments/4level/4-4.png",
    "勇气腰带": "./img/equipments/4level/4-8.png",
    "坚韧战靴": "./img/equipments/4level/4-95.png",
}

# 元素套装
Ele_suit = {"时光沙漏": "./img/equipments/reserved/5-97.png"}


class HANDLE:
    def __init__(self, handle_id) -> None:
        self.handle_id = handle_id  # 句柄ID
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(
            self.handle_id
        )  # 窗口长宽高
        # self.ocr = PaddleOCR(lang="ch", use_angle_cls=False, use_gpu=False, det_model_dir="./ch_PP-OCRv4_det_server_infer", rec_model_dir="./ch_PP-OCRv4_rec_server_infer", enable_mkldnn=True)
        self.ocr = PaddleOCR(
            lang="ch",
            use_angle_cls=False,
            use_gpu=False,
            enable_mkldnn=True,
            det_model_dir="./ch_PP-OCRv4_det_infer",
            rec_model_dir="./ch_PP-OCRv4_rec_infer",
        )
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.default_width = 720
        self.default_height = 1280


# 获得游戏句柄
def get_handle(FrameTitle="不思议迷宫"):
    mumu_handle_id = win32gui.FindWindow(0, FrameTitle) | win32gui.FindWindow(
        FrameTitle, None
    )
    handle_id = win32gui.FindWindowEx(mumu_handle_id, 0, None, "MuMuPlayer")

    if handle_id is not None:
        return HANDLE(handle_id=handle_id)
    else:
        return None


# 获得模拟器句柄
def get_mumu_handle(FrameTitle="不思议迷宫"):
    mumu_handle_id = win32gui.FindWindow(0, FrameTitle) | win32gui.FindWindow(
        FrameTitle, None
    )

    if mumu_handle_id is not None:
        return HANDLE(handle_id=mumu_handle_id)
    else:
        return None


def resize_to_720(handle, x):
    x = int(x / handle.width * 720)
    return x


def back_to_before(handle, x):

    x = int(x / 720 * handle.width)
    return x


# 模拟鼠标左键点击
def left_mouse_click(handle: HANDLE, point: list) -> None:

    position = win32api.MAKELONG(point[0][0], point[0][1])
    win32gui.SendMessage(
        handle.handle_id, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, position
    )
    win32gui.SendMessage(handle.handle_id, win32con.WM_LBUTTONUP, 0, position)
    time.sleep(1)


def capture_window(hwnd):
    # 获取窗口尺寸
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    # 创建设备上下文
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 复制图像数据
    result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    if result is None:
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        return img
    return None


# handle-句柄; 获取截图(实时画面截图，以屏幕像素点为准)，可选转灰
def get_screenshot(handle: HANDLE, debug=False):
    # # 获取窗口的边界
    # left, top, right, bottom = handle.left, handle.top, handle.right, handle.bottom
    # # 使用PIL库捕获指定区域的截图
    # screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    screenshot = capture_window(handle.handle_id)

    # 将PIL图像转换为numpy数组
    raw_color_img = np.array(screenshot)

    color_img = cv2.cvtColor(raw_color_img, cv2.COLOR_BGR2RGB)  # BGR转RGB
    gray_img = cv2.cvtColor(raw_color_img, cv2.COLOR_BGR2GRAY)  # BGR转灰度
    color_img = cv2.resize(
        color_img,
        (
            resize_to_720(handle, handle.width),
            (resize_to_720(handle, handle.height)),
        ),
    )
    gray_img = cv2.resize(
        gray_img,
        (
            resize_to_720(handle, handle.width),
            (resize_to_720(handle, handle.height)),
        ),
    )
    if debug:
        # 显示截图（可选）
        cv2.imshow("Gray Image", gray_img)
        cv2.imshow("Color Image", color_img)
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
            other_det_area = (other_det[2] - other_det[0]) * (
                other_det[3] - other_det[1]
            )

            # 计算交并比（IoU）
            iou = inter / (det_area + other_det_area - inter)

            # 如果IoU大于阈值，则抑制该检测结果
            if iou > thresh:
                suppress.append(other_det)
        dets = [d for d in dets if d not in suppress]

    return keep


def find_image_center(
    handle: HANDLE,
    template_paths,
    match_threshold=0.80,
    timeout=10,
    interval=1,
    debug=False,
    ROI=None,
):
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
    result_list = []
    start_time = time.time()
    print("开始查找图像")

    templates = [
        cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        for template_path in template_paths
    ]
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
                roi_x, roi_y, roi_w, roi_h = ROI
                gray_img = gray_img[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]

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
                    detections.append(
                        (
                            top_left[0],
                            top_left[1],
                            bottom_right[0],
                            bottom_right[1],
                            max_val,
                        )
                    )

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
                    center_x += roi_x
                    center_y += roi_y

                center_x = back_to_before(handle, center_x)
                center_y = back_to_before(handle, center_y)

                # 调试代码：在截图上绘制矩形框
                if debug:
                    print(f"图像中心坐标为:({center_x}, {center_y})")
                    print(
                        f"匹配图像: {best_template_path}, 匹配度: {best_match_val:.3f}"
                    )
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    cv2.rectangle(gray_img, top_left, bottom_right, (0, 0, 0), 2)
                    # 可视化调试：在截图上绘制ROI区域的矩形框
                    cv2.imshow("Matched Region", gray_img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                result_list.append((center_x, center_y))
                return result_list
        except Exception as e:
            print(f"发生错误: {str(e)}")
            print("完整错误信息：")
            print(traceback.format_exc())

        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配图像")
    return result_list


def find_and_click_image(
    handle: HANDLE,
    template_paths,
    sleep_time=0.5,
    match_threshold=0.80,
    timeout=10,
    interval=1,
    debug=False,
    contintue_flag=False,
    ROI=None,
):
    try:
        if contintue_flag == False:
            det_pos = find_image_center(
                handle=handle,
                template_paths=template_paths,
                match_threshold=match_threshold,
                timeout=timeout,
                interval=interval,
                debug=debug,
                ROI=ROI,
            )
        else:
            while contintue_flag:
                det_pos = find_image_center(
                    handle=handle,
                    template_paths=template_paths,
                    match_threshold=match_threshold,
                    timeout=timeout,
                    interval=interval,
                    debug=debug,
                    ROI=ROI,
                )
                if len(det_pos) != 0:
                    contintue_flag = False
        if len(det_pos) != 0:
            left_mouse_click(handle, det_pos)
            time.sleep(sleep_time)
            return True
        else:
            print("未找到匹配图像")
            raise Exception("未找到匹配图像")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("完整错误信息：")
        print(traceback.format_exc())
        return False


def find_text_center(
    handle: HANDLE, tar_txts, timeout=10, interval=1, debug=False, ROI=None
):
    result_list = []
    start_time = time.time()
    print(f"开始查找{tar_txts}")

    while time.time() - start_time < timeout:
        try:
            _, img = get_screenshot(handle)

            # 根据region参数裁剪图像

            if ROI is not None:
                roi_x, roi_y, roi_w, roi_h = ROI
                img = img[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]
                # cv2.imshow("Matched Region", img)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

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
                            center_x += roi_x
                            center_y += roi_y
                        center_x = back_to_before(handle, center_x)
                        center_y = back_to_before(handle, center_y)
                        if debug:
                            print(f"文本中心坐标为:({center_x}, {center_y})")
                            result = result[0]
                            image = Image.fromarray(
                                cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            )
                            boxes = [line[0] for line in result]
                            txts = [line[1][0] for line in result]
                            scores = [line[1][1] for line in result]
                            im_show = draw_ocr(
                                image,
                                boxes,
                                txts,
                                scores,
                                font_path="/path/to/PaddleOCR/doc/fonts/simfang.ttf",
                            )
                            im_show = Image.fromarray(im_show)
                            im_show.save("result.jpg")
                        result_list.append((center_x, center_y))
                        return result_list
            else:
                continue
        except Exception as e:
            print(f"发生错误: {str(e)}")
            print("完整错误信息：")
            print(traceback.format_exc())

        time.sleep(interval)  # 等待0.1秒后再进行下一次尝试

    print("超时未找到匹配文本")
    return result_list


def find_and_click_text(
    handle: HANDLE,
    tar_txts,
    timeout=10,
    interval=1,
    debug=False,
    sleep_time=0.5,
    continue_flag=False,
    ROI=None,
):
    try:
        if continue_flag == False:
            det_pos = find_text_center(
                handle=handle,
                tar_txts=tar_txts,
                timeout=timeout,
                interval=interval,
                debug=debug,
                ROI=ROI,
            )
        else:
            while continue_flag:
                det_pos = find_text_center(
                    handle=handle,
                    tar_txts=tar_txts,
                    timeout=timeout,
                    interval=interval,
                    debug=debug,
                    ROI=ROI,
                )
                if len(det_pos) != 0:
                    continue_flag = False
        if len(det_pos) != 0:
            left_mouse_click(handle, det_pos)
            time.sleep(sleep_time)
            return True
        else:
            print("未找到匹配文本")
            raise Exception("未找到匹配文本")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("完整错误信息：")
        print(traceback.format_exc())
        return False


def get_word_from_handle(handle: HANDLE, ROI=None):
    _, img = get_screenshot(handle)
    if ROI is not None:
        roi_x, roi_y, roi_w, roi_h = ROI
        img = img[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]
        # img = cv2.imshow("Matched Region", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        result = handle.ocr.ocr(img)
    return result


def push_one_squence(handle: HANDLE):
    time.sleep(0.5)
    find_and_click_image(
        handle=handle,
        template_paths=["./img/common/skill_pack.png"],
        ROI=(500, 1085, 218, 194),
    )
    find_and_click_text(handle=handle, tar_txts=["阶位"])
    time.sleep(0.5)
    if find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"]):
        find_and_click_text(handle=handle, tar_txts=["治疗术", "石肤术", "祝福术"])
        print("""使用了["治疗术", "石肤术", "祝福术"]中的一个""")


def use_quake(handle):
    time.sleep(0.5)
    find_and_click_image(
        handle=handle,
        template_paths=["./img/common/skill_pack.png"],
        ROI=(500, 1085, 218, 194),
    )
    find_and_click_text(handle=handle, tar_txts=["阶位"])
    time.sleep(0.5)
    left_mouse_click(
        handle=handle,
        point=[(back_to_before(handle, 635), back_to_before(handle, 434))],
    )
    if find_and_click_text(handle=handle, tar_txts=["地震术"]):
        find_and_click_text(handle=handle, tar_txts=["地震术"])


# 使用死亡波纹
def use_death_ripper(handle):
    time.sleep(0.5)
    find_and_click_image(
        handle=handle,
        template_paths=["./img/common/skill_pack.png"],
        ROI=(500, 1085, 218, 194),
    )
    find_and_click_text(handle=handle, tar_txts=["阶位"])
    time.sleep(0.5)

    left_mouse_click(
        handle=handle,
        point=[(back_to_before(handle, 635), back_to_before(handle, 434))],
    )
    if find_and_click_text(handle=handle, tar_txts=["死亡波纹"]):
        find_and_click_text(handle=handle, tar_txts=["死亡波纹"])


# 小sl
def SL_basic(handle: HANDLE):
    # basic.load_mumu_video(self.handle, "./img/mumu_video/小xl.mmor")
    time.sleep(1)
    left_mouse_click(
        handle, [(back_to_before(handle, 644), back_to_before(handle, 42))]
    )
    find_and_click_image(handle, ["./img/common/account.png"])
    find_and_click_text(handle, ["登出"])
    find_and_click_text(handle, ["开始游戏"], timeout=60)
    find_and_click_text(handle, ["确定"])
    find_and_click_text(handle, ["继续冒险"])
    time.sleep(2)
    while True:
        if (
            len(
                find_image_center(
                    handle, ["./img/common/setting.png"], match_threshold=0.8
                )
            )
            > 0
        ):
            time.sleep(1)
            break


# 暂离
def save_staute(handle: HANDLE):
    time.sleep(1)
    left_mouse_click(handle, [(back_to_before(handle, 64), back_to_before(handle, 42))])
    find_and_click_text(handle, ["暂离"])
    find_and_click_text(handle, ["确定"])
    find_and_click_text(handle, ["暂离"], ROI=(375, 0, 350, 400))
    time.sleep(2)
    while True:
        if (
            len(
                find_image_center(
                    handle, ["./img/common/setting.png"], match_threshold=0.8
                )
            )
            > 0
        ):
            time.sleep(1)
            break


# 执行一次断网，再执行联网
def change_network_state(handle):
    go_back_to_home(handle)
    # 启动V2RayNG应用
    find_and_click_image(handle, ["./img/global/V2rayN.png"])
    print("成功打开V2RayNG应用")
    find_and_click_image(handle, ["./img/global/off_button.png"])
    go_back_to_home(handle)
    find_and_click_image(handle, ["./img/global/game.png"])


def go_back_to_home(handle: HANDLE):

    # 设置焦点到指定的窗口句柄
    win32gui.SetForegroundWindow(handle.handle_id)
    # # 尝试将窗口恢复到正常状态
    # win32gui.ShowWindow(handle.handle_id, win32con.SW_RESTORE)

    # # 添加一个小的延时，确保窗口已经恢复
    # time.sleep(0.5)

    # 发送返回键事件
    try:
        # win32api.keybd_event(36, 0, 0, 0)  # HOME键按下
        win32gui.SendMessage(handle.handle_id, win32con.WM_KEYDOWN, win32con.VK_HOME, 0)
        time.sleep(0.1)
        win32gui.SendMessage(handle.handle_id, win32con.WM_KEYUP, win32con.VK_HOME, 0)
        # win32api.keybd_event(36, 0, win32con.KEYEVENTF_KEYUP, 0)  # HOME键抬起
    except Exception as e:
        print(f"发送HOME键事件失败: {e}")


def SL_body(handle: HANDLE, star=False, debug=False) -> bool:
    before_sunshine_star_believer_list = get_sunshine_star_number(handle)

    save_staute(handle=handle)
    # 检查尸体位置
    dts_pos = find_image_center(
        handle,
        [
            "./img/shenduan/body.png",
            "./img/shenduan/body_9.png",
            "./img/shenduan/weapenpile.png",
        ],
        match_threshold=0.85,
    )
    need_sl = False
    while len(dts_pos) == 0:
        print("没有检测到尸体，尝试推序规避时停影响")
        push_one_squence(handle)
        dts_pos = find_image_center(
            handle,
            [
                "./img/shenduan/body.png",
                "./img/shenduan/body_9.png",
                "./img/shenduan/weapenpile.png",
            ],
            match_threshold=0.85,
        )
        need_sl = True

    ##火神判断

    print("尸体像素位置：", dts_pos)

    if need_sl:
        SL_basic(handle=handle)
    continue_flag = True
    order = 0
    while continue_flag:
        print(f"第{order}次   " * 5)

        # 直接推序1次
        if order != 0:

            firegod_pos = find_image_center(
                handle,
                [
                    "./img/shenduan/red_body.png",
                    "./img/shenduan/firegod.png",
                    "./img/shenduan/weapon.png",
                ],
                timeout=3,
                interval=1,
            )
            if len(firegod_pos) == 0:
                time.sleep(0.5)
                push_one_squence(handle)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle)

        # 点击尸体并翻找
        find_and_click_image(
            handle=handle,
            template_paths=[
                "./img/shenduan/body.png",
                "./img/shenduan/body_9.png",
                "./img/shenduan/weapenpile.png",
            ],
            match_threshold=0.85,
        )
        find_and_click_text(handle=handle, tar_txts=["翻", "找"])

        now_sunshine_star_believer_list = get_sunshine_star_number(handle)

        # 检测是否为日光
        if star == False:
            result = (
                now_sunshine_star_believer_list[0]
                != before_sunshine_star_believer_list[0]
            )
        else:
            result = (
                now_sunshine_star_believer_list[0]
                != before_sunshine_star_believer_list[0]
                or now_sunshine_star_believer_list[1]
                != before_sunshine_star_believer_list[1]
            )
        if result:
            time.sleep(0.5)
            save_staute(handle=handle)
            return True

        order += 1

        SL_basic(handle=handle)

    return True


def SL_pool(handle: HANDLE, debug=False) -> bool:
    # 检查水池位置
    before_health = get_health_max(handle)
    save_staute(handle=handle)

    dts_pos = find_image_center(
        handle, ["./img/shenduan/pool.png"], match_threshold=0.8
    )
    need_sl = False
    while len(dts_pos) == 0:
        print("没有检测到水池，尝试推序规避时停影响")
        push_one_squence(handle)
        dts_pos = find_image_center(
            handle, ["./img/shenduan/pool.png"], match_threshold=0.8
        )
        need_sl = True

    print("水池像素位置：", dts_pos)

    if need_sl:
        SL_basic(handle=handle)

    continue_flag = True
    order = 0
    while continue_flag:
        print(f"第{order}次   " * 5)

        # 直接推序1次
        if order != 0:

            firegod_pos = find_image_center(
                handle,
                [
                    "./img/shenduan/red_body.png",
                    "./img/shenduan/firegod.png",
                    "./img/shenduan/weapon.png",
                ],
                timeout=3,
                interval=1,
            )
            if len(firegod_pos) == 0:
                push_one_squence(handle)

        print("推序完成")
        # 暂离保存，不用重复推序
        save_staute(handle=handle)

        # 点击尸体并翻找
        find_and_click_image(handle=handle, template_paths=["./img/shenduan/pool.png"])
        find_and_click_text(handle=handle, tar_txts=["浸泡铠甲"])

        now_health = get_health_max(handle)
        # 检测是否为日光
        result = now_health > before_health
        if result:
            print("血量增加了!!!")
            time.sleep(0.5)
            save_staute(handle=handle)
            return True

        order += 1
        print("没找到,开始小sl")

        SL_basic(handle=handle)

    return True


def get_lack_equipment(handle, equip_dict):
    equip_dict_copy = copy.deepcopy(equip_dict)
    find_and_click_image(handle, ["./img/common/equip_pack.png"])
    for k, v in equip_dict.items():

        det_pos = find_image_center(handle, [v])
        if len(det_pos) > 0:
            del equip_dict_copy[k]
    find_and_click_text(handle=handle, tar_txts=["返回"], sleep_time=1)
    return list(equip_dict_copy.keys())


def SL_equip(handle: HANDLE, target_suit=Eternal_suit):

    equip_name_list = get_lack_equipment(handle, target_suit)
    print(f"缺少装备：{equip_name_list}")
    before_len = len(equip_name_list)
    if len(equip_name_list) == 0:
        return True
    ops = 0
    while ops < 101:
        print(f"这是第{ops}次黑装备     " * 4)
        save_staute(handle)
        print("检查是否断网")
        change_network_state(handle=handle)
        time.sleep(5)
        find_and_click_image(handle, ["./img/common/open_door.png"])
        while not find_image_center(handle, ["./img/common/closed_door.png"]):
            time.sleep(1)

        # 使用卷轴杀怪
        use_quake(handle)
        while not find_image_center(handle, ["./img/common/equip_box.png"]):
            use_death_ripper(handle)
            time.sleep(1)

        # 点击宝箱
        find_and_click_image(handle, ["./img/common/equip_box.png"])
        after_len = len(get_lack_equipment(handle, target_suit))
        result = before_len > after_len
        if result:
            # 联网保存
            change_network_state(handle=handle)
            save_staute(handle)
            return True
        else:
            ops += 1
            # 小SL
            left_mouse_click(
                handle, [(back_to_before(handle, 644), back_to_before(handle, 44))]
            )
            find_and_click_image(handle, ["./img/common/account.png"])
            find_and_click_text(handle, ["登出"])
            while not find_image_center(handle, ["./img/common/startgame.png"]):
                time.sleep(1)

            change_network_state(handle=handle)
            time.sleep(1)
            find_and_click_text(handle, ["开始游戏"])
            while not find_text_center(handle, ["确定"]):
                time.sleep(1)
            find_and_click_text(handle, ["确定"])
            find_and_click_text(handle, ["继续冒险"])

    else:
        print("超过了101次，需要大SL")
        left_mouse_click(
            handle, [(back_to_before(handle, 644), back_to_before(handle, 44))]
        )
        find_and_click_image(handle, ["./img/common/account.png"], sleep_time=3)
        find_and_click_text(handle, ["登出"], sleep_time=8)
        while not find_image_center(handle, ["./img/common/startgame.png"]):
            time.sleep(1)
        change_network_state(handle=handle)


def check_acttack(handle) -> bool:
    result = find_text_center(
        handle,
        tar_txts=["攻击", "生命值"],
        timeout=3,
        interval=0.01,
        debug=False,
        ROI=(116, 987, 454, 213),
    )
    return len(result) != 0


def check_sun(handle) -> bool:
    result = find_text_center(
        handle,
        tar_txts=["日光"],
        timeout=3,
        interval=0.01,
        debug=False,
        ROI=(0, 1067, 223, 85),
    )
    return len(result) != 0


def check_sun_and_star(handle) -> bool:
    result = find_text_center(
        handle,
        tar_txts=["日光", "星光"],
        timeout=3,
        interval=0.01,
        debug=False,
        ROI=(0, 1067, 223, 85),
    )
    return len(result) != 0


def get_health_max(handle):
    left_mouse_click(
        handle, [(back_to_before(handle, 360), back_to_before(handle, 1200))]
    )
    time.sleep(0.5)
    results = get_word_from_handle(handle, ROI=(339, 613, 377, 73))
    for result in results[0]:
        if "/" in result[1][0]:
            health_max = result[1][0].split("/")[1]
    find_and_click_text(handle, ["返回"], sleep_time=1)
    return int(health_max)


def get_sunshine_star_number(handle):
    sunshine_star_number_list = [0, 0]
    while True:
        if len(find_image_center(handle, ["./img/shenduan/armor.png"])) > 0:
            break
    find_and_click_image(handle, ["./img/shenduan/armor.png"])
    find_and_click_text(handle, ["神力刻印"], sleep_time=1)
    find_and_click_image(handle, ["./img/shenduan/sunshine.png"])
    time.sleep(0.5)
    results = get_word_from_handle(handle, ROI=(54, 650, 606, 188))
    for result in results[0]:
        if "%" in result[1][0]:
            numbers = re.findall(r"\d+", result[1][0])
            sunshine_number = numbers[0]
            sunshine_number = int(sunshine_number) / 10
            sunshine_star_number_list[0] = sunshine_number
    find_and_click_image(handle, ["./img/shenduan/star.png"])
    time.sleep(0.5)
    results = get_word_from_handle(handle, ROI=(54, 650, 606, 188))
    for result in results[0]:
        if "%" in result[1][0]:
            numbers = re.findall(r"\d+", result[1][0])
            star_number = numbers[0]
            star_number = int(star_number) / 10
            sunshine_star_number_list[1] = star_number

    # find_and_click_image(handle, ["./img/shenduan/believer.png"])
    # time.sleep(0.5)
    # results = get_word_from_handle(handle, ROI=(54, 650, 606, 188))
    # for result in results[0]:
    #     if "点" in result[1][0]:
    #         numbers = re.findall(r"\d+", result[1][0])
    #         believer_number = numbers[0]
    #         print(believer_number)
    #         believer_number = int(believer_number) / 6
    #         sunshine_star_believer_number_list[2] = believer_number

    left_mouse_click(
        handle, [(back_to_before(handle, 600), back_to_before(handle, 1200))]
    )
    time.sleep(1)
    left_mouse_click(
        handle, [(back_to_before(handle, 600), back_to_before(handle, 1200))]
    )
    while True:
        if len(find_image_center(handle, ["./img/shenduan/armor.png"])) > 0:
            break
    return sunshine_star_number_list


if __name__ == "__main__":
    # (951, 535, 3)
    # ROI for 血量增加check(100, 700, 300, 200)
    # ROI for 装备和刻印check(0, 760, 150, 150)
    # ROI for 背包check(0, 450, 535, 500)
    handle = get_handle()
    # raw_color_img = np.array(capture_window(handle.handle_id))
    # color_img = cv2.cvtColor(raw_color_img, cv2.COLOR_BGR2RGB)
    # cv2.imshow("Color Image", color_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # change_network_state(handle)
    # SL_basic(handle)
    # save_staute(handle)
    # push_one_squence(handle)
    # print(get_sunshine_star_number(handle))
    # print(get_health_max(handle))

    # SL_pool(handle)
    # print(get_lack_equipment(handle, equip_dict=Eternal_suit))
    # SL_equip(handle)
    use_quake(handle)
