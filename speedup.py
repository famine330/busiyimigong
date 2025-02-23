import pymem
import ctypes
from ctypes import wintypes
import re
import struct

# 定义 Windows API 函数
kernel32 = ctypes.windll.kernel32

MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


def find_and_modify_pattern(process_name, pattern, modify_offset, new_value):
    try:
        # 打开进程
        pm = pymem.Pymem(process_name)

        # 将特征码字符串中的 ?? 替换为 00（占位符）
        pattern_cleaned = pattern.replace("??", "00")
        pattern_bytes = bytes.fromhex(pattern_cleaned)

        # 创建正则表达式，将 ?? 对应的字节替换为通配符（.）
        regex_pattern = re.compile(
            re.escape(pattern_bytes).replace(re.escape(b"\x00"), b".")
        )

        # 获取进程句柄
        process_handle = pm.process_handle

        # 初始化内存区域遍历
        address = 0
        while address < 0x7FFFFFFFFFFF:  # 32 位进程的最大地址
            mbi = MEMORY_BASIC_INFORMATION()
            result = kernel32.VirtualQueryEx(
                process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)
            )
            if result == 0:
                break

            # 检查内存区域是否可读
            if mbi.State == MEM_COMMIT and mbi.Protect & PAGE_READWRITE:
                try:
                    # 读取内存块
                    memory_block = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)

                    # 在内存块中搜索特征码
                    match = regex_pattern.search(memory_block)
                    if match:
                        # 计算匹配地址
                        match_address = mbi.BaseAddress + match.start()

                        # 计算要修改的地址
                        modify_address = match_address + modify_offset

                        # 修改内存中的值
                        pm.write_bytes(
                            modify_address,
                            bytes.fromhex(new_value),
                            len(new_value) // 2,
                        )

                        print(f"找到特征码地址: 0x{match_address:X}")
                        # print(f"已将地址 0x{modify_address:X} 的值修改为 {new_value}")
                        return match_address  # 找到后退出

                except pymem.exception.MemoryReadError:
                    # 如果读取失败，跳过该内存区域
                    pass

            # 移动到下一个内存区域
            address += mbi.RegionSize

        print("未找到特征码")

    except pymem.exception.ProcessNotFound:
        print(f"未找到进程: {process_name}")
    except Exception as e:
        print(f"发生错误: {e}")


def float_to_hex_bytes(
    number: float, precision: str = "single", endian: str = "big"
) -> list:
    """
    将浮点数转换为十六进制格式的字节数组

    参数：
    - number: 输入的浮点数
    - precision: 精度类型，可选 'single'（32位）或 'double'（64位）
    - endian: 字节序，可选 'big'（大端）或 'little'（小端）

    返回：
    - 包含十六进制字节字符串的列表（如 ['3f', '80', '00', '00']）
    """
    # 确定格式字符和字节长度
    format_char = "f" if precision == "single" else "d"
    byte_order = ">" if endian == "big" else "<"

    # 打包为二进制字节流
    packed = struct.pack(f"{byte_order}{format_char}", number)

    # 转换为十六进制字符串列表
    hex_bytes = [f"{byte:02x}" for byte in packed]

    return hex_bytes


if __name__ == "__main__":
    # 示例使用
    process_name = "MuMuVMMHeadless.exe"  # 替换为目标进程名称
    pattern = "90 B3 16 04 00 00 00 00 ?? ?? ?? ?? 05 00 00 00 05 00 00 00 00 00"
    # "00 00 00 00 00 00 00 00 90 B3 16 04 00 00 00 00 DF 01 00 00 05 00 00 00 05 00 00 00 00 00 A0 40"
    modify_offset = 22  # 80 3F 在特征码中的偏移量
    new_value = "A0 40"  # 要修改的新值
    ### "80 3F" 是 初始速度
    ### "00 40" 是 二倍速
    ### "A0 40" 是 五倍速

    address = find_and_modify_pattern(process_name, pattern, modify_offset, new_value)
    print(address)
