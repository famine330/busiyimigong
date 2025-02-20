import basic
import time
import numpy as np
import os
import utils


"""
用于神锻测序
"""
sunshine_seq = []
equipments_path = {
    "1": [
        "./img/equipments/1level/" + path
        for path in os.listdir("./img/equipments/1level/")
    ],
    "2": [
        "./img/equipments/2level/" + path
        for path in os.listdir("./img/equipments/2level/")
    ],
    "3": [
        "./img/equipments/3level/" + path
        for path in os.listdir("./img/equipments/3level/")
    ],
    "4": [
        "./img/equipments/4level/" + path
        for path in os.listdir("./img/equipments/4level/")
    ],
    "5": [
        "./img/equipments/5level/" + path
        for path in os.listdir("./img/equipments/5level/")
    ],
    "6": [
        "./img/equipments/6level/" + path
        for path in os.listdir("./img/equipments/6level/")
    ],
}


# 从左侧第一页开始找装备,找到返回[（x,y）],没找到返回[]
def find_and_click_equipment_from_left(
    handle: basic.HANDLE, equip_path_list: list, debug: bool = False
) -> tuple:

    print("向左侧翻页，翻到第一页")
    for _ in range(15):
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 47), basic.back_to_before(handle, 814))],
        )
    time.sleep(2)

    for _ in range(15):
        # 在当前页找目标装备

        _, img = basic.get_screenshot(handle)
        find_result = basic.find_and_click_image(
            handle,
            [ele_path for ele_path in equip_path_list],
            timeout=2,
            ROI=(0, 620, 720, 424),
        )
        time.sleep(0.5)
        #
        if find_result:
            return True
        # 没找到,往右翻页找装备
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 674), basic.back_to_before(handle, 814))],
        )
        time.sleep(1)
    return False


# 从右侧第一页开始找装备
def find_and_click_equipment_from_right(
    handle: basic.HANDLE, equip_path_list: list, debug: bool = False
) -> tuple:

    print("向右侧翻页，翻到最后一页")
    for _ in range(15):
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 674), basic.back_to_before(handle, 814))],
        )
    time.sleep(2)

    for _ in range(15):
        # 在当前页找目标装备

        _, img = basic.get_screenshot(handle)
        find_result = basic.find_and_click_image(
            handle,
            [ele_path for ele_path in equip_path_list],
            timeout=3,
            ROI=(0, 620, 720, 424),
        )
        time.sleep(0.5)
        #
        if find_result:
            return True
        # 没找到,往左翻页找装备
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 47), basic.back_to_before(handle, 814))],
        )
        time.sleep(1)
    return False


# 查找熔炉位置,并点击,进入查找装备的界面
def find_stove(handle: basic.HANDLE) -> bool:
    _, img = basic.get_screenshot(handle)
    basic.find_and_click_image(
        handle,
        [
            "./img/shenduan/stove.png",
            "./img/shenduan/stove_2.png",
            "./img/shenduan/stove_3.png",
        ],
    )
    time.sleep(1)
    # 点击添加装备
    basic.find_and_click_image(handle, ["./img/shenduan/add_equipment.png"])
    time.sleep(1)
    return True


# 熔炼装备
def stove_equipment(handle: basic.HANDLE):
    basic.find_and_click_text(
        handle, tar_txts=["选择"], ROI=(0, 625, 720, 440)
    )  # 添加装备
    basic.find_and_click_text(handle, tar_txts=["熔炼装备"], sleep_time=1)  # 装备熔炼
    basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)


def stove_equipment_without_back(handle: basic.HANDLE):
    basic.find_and_click_text(
        handle, tar_txts=["选择"], ROI=(0, 625, 720, 440)
    )  # 添加装备
    basic.find_and_click_text(handle, tar_txts=["熔炼装备"], sleep_time=1)  # 装备熔炼


def use_star_6_equipment(handle: basic.HANDLE, is_detect: bool = True):
    before_sunshine_star_believer_list = basic.get_sunshine_star_number(handle)

    for i in range(101):
        find_stove(handle)
        print("这次是第" + str(i) + "次装备熔炼")
        find_result = find_and_click_equipment_from_right(
            handle, equipments_path["6"], debug=False
        )

        if not find_result:
            # 说明没有6星装备了,小SL恢复原状
            basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
            basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
            basic.SL_basic(handle)
            raise Exception("没有找到6星装备")
        # 熔炼装备
        stove_equipment(handle)

        if is_detect:
            # 结果检测
            now_sunshine_star_believer_list = basic.get_sunshine_star_number(handle)
            result = (
                now_sunshine_star_believer_list[0]
                != before_sunshine_star_believer_list[0]
            )
            if result:
                sun_record = i
                print(f"    第{i}次有日光！    " * 4)
                break

    basic.SL_basic(handle)
    print("第" + str(sun_record) + "次装备熔炼出了日光")
    return sun_record


def use_min_star_equipment_step_1(handle: basic.HANDLE, sun_record=None):
    find_stove(handle)

    start_level = 1

    print("有日光，第一步：填入低星装备")
    for i in range(sun_record):

        print("这次是第" + str(i) + "次装备熔炼")
        find_result = find_and_click_equipment_from_left(
            handle, equipments_path[str(start_level)], debug=False
        )
        if not find_result:
            print("1星装备不足，使用2星装备推序")
            if start_level == 1:
                start_level = 2
                find_result = find_and_click_equipment_from_left(
                    handle, equipments_path[str(start_level)], debug=False
                )
            if not find_result:
                print("2星装备不足，使用3星装备推序")
                if start_level == 2:
                    start_level = 3
                    find_result = find_and_click_equipment_from_left(
                        handle, equipments_path[str(start_level)], debug=False
                    )
                if not find_result:
                    print("3星装备不足，下楼打装备吧")
                    basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
                    basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
                    basic.SL_basic(handle)
                    return 10000000

        # 熔炼装备
        stove_equipment_without_back(handle)
        # 点击添加装备
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 446), basic.back_to_before(handle, 559))],
        )
        time.sleep(1)

    # 暂离保存
    print("后面就是放最低星的高星装备")
    basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
    basic.find_and_click_text(handle, tar_txts=["返回"], sleep_time=1)
    basic.save_staute(handle)
    return 0


def use_min_star_equipment_step_2(
    handle: basic.HANDLE, equipment_list=["3", "4", "5", "6"]
):
    before_sunshine_star_believer_list = basic.get_sunshine_star_number(handle)
    print("有日光，第二步：填入高星装备")
    for i in equipment_list:
        find_stove(handle)
        find_result = find_and_click_equipment_from_right(
            handle, equipments_path[i], debug=False
        )
        if not find_result:
            print(f"没有找到{i}星装备，寻找更高星装备")
            continue
        else:
            print(f"找到{i}星装备，开始使用")
            stove_equipment(handle)

            # 结果检测
            now_sunshine_star_believer_list = basic.get_sunshine_star_number(handle)
            result = (
                now_sunshine_star_believer_list[0]
                != before_sunshine_star_believer_list[0]
            )
            if result:
                # 暂离
                basic.save_staute(handle)
                return i
            else:
                print(f"没有日光,下次用{int(i) + 1}星装备继续尝试")
                basic.SL_basic(handle)


def get_sunshine_sequence(handle: basic.HANDLE):
    sunshine_seq = []

    while len(sunshine_seq) <= 101:
        print(sunshine_seq)
        sun_record = use_star_6_equipment(handle)
        for _ in range(sun_record):
            sunshine_seq.append("0")
        if sun_record != 0:
            temp = use_min_star_equipment_step_1(handle, sun_record=sun_record)
        else:
            temp = 0
        if temp != 10000000:
            equipment_level = use_min_star_equipment_step_2(handle)
            sunshine_seq.append(equipment_level)
    print(sunshine_seq)
    sunshine_seq = sunshine_seq[-101:]
    return sunshine_seq


def save_sequence(handle):
    while True:
        basic.left_mouse_click(
            handle,
            [(basic.back_to_before(handle, 614), basic.back_to_before(handle, 1194))],
        )
        time.sleep(10)


# def get_sun_from_sequence(handle:basic.HANDLE, sun_record: list):
#     continue_flag = True
#     i = 0
#     sun_number = 0
#     while continue_flag:
#         if sun_record[i] != "0":
#             #熔炼装备
#             find_stove(handle)

#             pos = find_and_click_equipment_from_right(handle, equipments_path[sun_record[i%101]])
#             stove_equipment(handle)
#             i = i + 1
#             sun_number = sun_number + 1
#             basic.find_and_click(handle, "./img/shenduan/add_equipment.png", 3)
#             basic.find_and_click_text(handle, ["返回"])
#             basic.find_and_click_text(handle, ["返回"])
#         else:
#             # 填入低星装备
#             find_stove(handle)

#             start_level = 1

#             print("填入低星装备")

#             print("这次是第"+str(i)+"次装备熔炼")
#             pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
#             if len(pos)==0:
#                 print("1星装备不足，使用2星装备推序")
#                 if start_level == 1:
#                     start_level = 2
#                 pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
#                 if len(pos)==0:
#                     print("2星装备不足，使用3星装备推序")
#                     if start_level == 2:
#                         start_level = 3
#                     pos = find_and_click_equipment_from_left(handle, equipments_path[str(start_level)])
#                     if len(pos)==0:
#                         print("3星装备不足，下楼打装备吧")
#                         return
#             # 熔炼装备
#             stove_equipment(handle)
#             i = i + 1
#             basic.find_and_click_image(handle, "./img/shenduan/add_equipment.png", 3)
#             basic.find_and_click_text(handle, ["返回"])
#             basic.find_and_click_text(handle, ["返回"])


if __name__ == "__main__":

    handle = basic.get_handle()
    # find_and_click_equipment_from_left(handle, equipments_path["1"])
    # find_stove(handle)
    # stove_equipment(handle)
    # use_star_6_equipment(handle)
    # use_min_star_equipment_step_1(handle, 3)
    # use_min_star_equipment_step_2(handle)
    result = get_sunshine_sequence(handle)
    print(result)
    save_sequence(handle)
