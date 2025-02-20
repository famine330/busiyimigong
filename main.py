import tkinter as tk
from tkinter import messagebox
import threading
import sys, os


import basic
import speedup  # 添加对speedup模块的导入

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("不思议迷宫辅助工具")

        # 计算屏幕中心位置
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 300  # 假设窗口宽度为300
        window_height = 400  # 假设窗口高度为400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.start_button = tk.Button(root, text="开始黑水池", command=self.run_sl_pool)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        # 更新按钮的pack方法以适应复选框
        self.start_button_body = tk.Button(
            root, text="开始黑尸体", command=self.run_sl_body
        )
        self.start_button_body.grid(row=1, column=0, padx=10, pady=10)
        # 添加复选框
        self.checkbox_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(root, text="星光", variable=self.checkbox_var)
        self.checkbox.grid(row=1, column=1, padx=10, pady=10)

        self.start_button_equip = tk.Button(
            root, text="开始黑永恒", command=self.run_sl_equip
        )
        self.start_button_equip.grid(row=2, column=0, padx=10, pady=10)

        self.handle = basic.get_handle()

        # 添加速度控制按钮
        self.speed_original_button = tk.Button(
            root, text="原始速度", command=lambda: self.set_game_speed("80 3F")
        )
        self.speed_original_button.grid(row=3, column=0, padx=10, pady=10)

        self.speed_double_button = tk.Button(
            root, text="二倍速", command=lambda: self.set_game_speed("00 40")
        )
        self.speed_double_button.grid(row=3, column=1, padx=10, pady=10)

        self.speed_five_button = tk.Button(
            root, text="五倍速", command=lambda: self.set_game_speed("A0 40")
        )
        self.speed_five_button.grid(row=3, column=2, padx=10, pady=10)

    def run_sl_pool(self):
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.execute_sl_pool).start()

    def run_sl_body(self):
        self.start_button_body.config(state=tk.DISABLED)
        # 根据复选框的状态传递参数
        threading.Thread(
            target=self.execute_sl_body, args=(self.checkbox_var.get(),)
        ).start()

    def run_sl_equip(self):
        self.start_button_equip.config(state=tk.DISABLED)
        threading.Thread(target=self.execute_sl_equip).start()

    def execute_sl_pool(self):
        try:
            basic.SL_pool(handle=self.handle)
            messagebox.showinfo("完成", "黑水池执行完毕")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")
        finally:
            self.start_button.config(state=tk.NORMAL)

    def execute_sl_body(self, star):
        try:
            # 接收参数并传递给basic.SL_body函数
            basic.SL_body(handle=self.handle, star=star)
            messagebox.showinfo("完成", "黑尸体执行完毕")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")
        finally:
            self.start_button_body.config(state=tk.NORMAL)

    def execute_sl_equip(self):
        try:
            basic.SL_equip(handle=self.handle)
            messagebox.showinfo("完成", "黑永恒执行完毕")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")
        finally:
            self.start_button_equip.config(state=tk.NORMAL)

    def set_game_speed(self, speed_hex):
        process_name = "MuMuVMMHeadless.exe"  # 替换为目标进程名称
        pattern = "90 B3 16 04 00 00 00 00 ?? ?? ?? ?? 05 00 00 00 05 00 00 00 00 00"
        modify_offset = 22  # 80 3F 在特征码中的偏移量
        speedup.find_and_modify_pattern(process_name, pattern, modify_offset, speed_hex)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
