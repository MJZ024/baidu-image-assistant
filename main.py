"""
百度图片内容分析与解说助手 - 主程序
图形界面：tkinter（Python 内置，无需安装）
"""
import os
import sys
import threading
import webbrowser
from tkinter import (
    Tk, Label, Button, Text, Scrollbar, filedialog,
    messagebox, StringVar, PhotoImage, Canvas, Frame,
    END, LEFT, BOTH, RIGHT, Y, W, CENTER, DISABLED, NORMAL,
    ttk
)
from tkinter.messagebox import showinfo, showerror

import config
import baidu_api


# ---------------------------------------------------------------
# 全局变量
# ---------------------------------------------------------------
GLOBAL_IMAGE_PATH = None   # 当前图片路径
AUDIO_FILE = None          # 生成的音频文件路径


# ---------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------

def resource_path(relative_path: str) -> str:
    """兼容 PyInstaller 打包时的资源路径"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def open_file_dialog() -> str:
    """打开文件选择对话框，只支持图片"""
    file_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("所有文件", "*.*"),
        ],
    )
    return file_path


def format_analysis_text(analysis: dict) -> str:
    """把分析结果格式化为易读的文本"""
    lines = []
    lines.append("=" * 40)
    lines.append("【图像识别结果】")
    lines.append("=" * 40)

    # 动物
    animal = analysis.get("animal")
    if animal and animal.get("name"):
        lines.append(f"\n🐾 动物识别：{animal['name']}（置信度 {animal['score']}%）")

    # 花卉
    flower = analysis.get("flower")
    if flower and flower.get("name"):
        lines.append(f"\n🌸 花卉识别：{flower['name']}（置信度 {flower['score']}%）")

    # 通用物体
    objects = analysis.get("objects", [])
    if objects:
        lines.append("\n🔍 物体识别：")
        for i, obj in enumerate(objects, 1):
            name = obj.get("keyword", "未知")
            score = obj.get("score", 0)
            lines.append(f"   {i}. {name}（{score}%）")

    # 文字
    texts = analysis.get("texts", [])
    if texts:
        lines.append(f"\n📝 文字识别（共 {len(texts)} 条）：")
        for t in texts[:10]:
            if t.strip():
                lines.append(f"   • {t}")
    else:
        lines.append("\n📝 文字识别：未检测到文字")

    lines.append("\n" + "=" * 40)
    return "\n".join(lines)


# ---------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------

class ImageAnalysisApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("百度图片内容分析与解说助手")
        self.root.geometry("900x720")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        # 窗口居中
        self._center_window()

        # 顶部信息栏
        self._build_header()

        # 主体布局：左侧图片区 + 右侧结果区
        self._build_main_area()

        # 底部控制栏
        self._build_control_bar()

        # 状态栏
        self._build_status_bar()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ---- 顶部标题栏 ----
    def _build_header(self):
        header = Frame(self.root, bg="#16213e", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        # 标题
        title = Label(
            header, text="🖼️ 百度图片内容分析与解说助手",
            font=("微软雅黑", 18, "bold"),
            fg="#e94560", bg="#16213e"
        )
        title.pack(pady=(15, 5))

        # 副标题
        sub = Label(
            header,
            text=f"学生：{config.STUDENT_NAME}（{config.STUDENT_ID}）| "
                 f"API：图像识别 · OCR文字识别 · 语音合成",
            font=("微软雅黑", 9),
            fg="#a0a0a0", bg="#16213e"
        )
        sub.pack(pady=(0, 10))

    # ---- 主体区域 ----
    def _build_main_area(self):
        main_frame = Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        # --- 左侧：图片预览 ---
        left_frame = Frame(main_frame, bg="#1a1a2e", width=400)
        left_frame.pack(side=LEFT, fill="both", padx=(0, 10))

        # 图片显示区域（Canvas）
        img_label = Label(
            left_frame, text="📷 点击下方「上传图片」按钮\n选择要分析的图片",
            font=("微软雅黑", 11),
            fg="#666", bg="#0f0f23",
            relief="groove", bd=2, anchor="center", justify="center"
        )
        img_label.configure(width=46, height=18)
        img_label.pack(fill="both", expand=True, pady=(0, 8))

        self.img_label = img_label
        self.img_label.pack_propagate(False)

        # 上传按钮
        self.upload_btn = Button(
            left_frame, text="📂 上传图片",
            font=("微软雅黑", 12, "bold"),
            bg="#e94560", fg="white", relief="flat",
            cursor="hand2", command=self.upload_image
        )
        self.upload_btn.pack(fill="x", ipady=6)

        # 重新上传
        self.reupload_btn = Button(
            left_frame, text="🔄 更换图片",
            font=("微软雅黑", 10),
            bg="#2d3a4a", fg="#aaa", relief="flat",
            cursor="hand2", command=self.upload_image
        )
        self.reupload_btn.pack(fill="x", ipady=4, pady=(5, 0))

        # --- 右侧：分析结果 ---
        right_frame = Frame(main_frame, bg="#16213e", width=500)
        right_frame.pack(side=RIGHT, fill="both", expand=True)
        right_frame.pack_propagate(False)

        # 结果标题
        result_title = Label(
            right_frame, text="📊 分析结果",
            font=("微软雅黑", 12, "bold"),
            fg="#e94560", bg="#16213e"
        )
        result_title.pack(anchor="w", padx=15, pady=(12, 5))

        # 结果文本区
        text_frame = Frame(right_frame, bg="#16213e")
        text_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.result_text = Text(
            text_frame,
            font=("微软雅黑", 10),
            fg="#d0d0d0", bg="#0f0f23",
            relief="flat", bd=0,
            wrap="word",
            yscrollcommand=scrollbar.set,
            insertbackground="white"
        )
        self.result_text.pack(side=LEFT, fill="both", expand=True)
        scrollbar.config(command=self.result_text.yview)

        # 解说词标题
        narration_title = Label(
            right_frame, text="📝 自动解说词",
            font=("微软雅黑", 12, "bold"),
            fg="#0feca8", bg="#16213e"
        )
        narration_title.pack(anchor="w", padx=15, pady=(5, 5))

        # 解说词文本区
        narr_frame = Frame(right_frame, bg="#16213e")
        narr_frame.pack(fill="x", padx=12, pady=(0, 10))

        narr_scroll = Scrollbar(narr_frame)
        narr_scroll.pack(side=RIGHT, fill=Y)

        self.narration_text = Text(
            narr_frame,
            font=("微软雅黑", 10),
            fg="#0feca8", bg="#0a1a14",
            relief="flat", bd=0,
            wrap="word",
            height=4,
            yscrollcommand=narr_scroll.set
        )
        self.narration_text.pack(side=LEFT, fill="x")
        narr_scroll.config(command=self.narration_text.yview)

    # ---- 底部控制栏 ----
    def _build_control_bar(self):
        ctrl = Frame(self.root, bg="#16213e", height=70)
        ctrl.pack(fill="x", side="bottom", padx=15, pady=(0, 5))

        # 分析按钮
        self.analyze_btn = Button(
            ctrl, text="🔍 开始分析",
            font=("微软雅黑", 13, "bold"),
            bg="#e94560", fg="white", relief="flat",
            cursor="hand2", command=self.start_analysis
        )
        self.analyze_btn.pack(side="left", ipadx=20, ipady=8, padx=(0, 10))

        # 语音按钮
        self.tts_btn = Button(
            ctrl, text="🔊 朗读解说",
            font=("微软雅黑", 12),
            bg="#2d6a4f", fg="white", relief="flat",
            cursor="hand2", command=self.play_narration,
            state=DISABLED
        )
        self.tts_btn.pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        # 清空按钮
        self.clear_btn = Button(
            ctrl, text="🗑️ 清空",
            font=("微软雅黑", 11),
            bg="#3d3d3d", fg="#ccc", relief="flat",
            cursor="hand2", command=self.clear_all
        )
        self.clear_btn.pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        # 进度条
        self.progress = ttk.Progressbar(
            ctrl, mode="indeterminate",
            length=200
        )
        self.progress.pack(side="right", padx=(0, 5))
        self.progress.pack_forget()

        self.status_label = Label(
            ctrl, text="等待上传图片...",
            font=("微软雅黑", 9),
            fg="#888", bg="#16213e"
        )
        self.status_label.pack(side="right", padx=5)

    # ---- 状态栏 ----
    def _build_status_bar(self):
        self.info_bar = Label(
            self.root, text="",
            font=("微软雅黑", 9),
            fg="#555", bg="#0f0f23",
            anchor="w"
        )
        self.info_bar.pack(fill="x", padx=15, pady=(0, 3))

    # ---------------------------------------------------------------
    # 事件处理
    # ---------------------------------------------------------------

    def upload_image(self):
        """上传图片"""
        path = open_file_dialog()
        if not path:
            return

        global GLOBAL_IMAGE_PATH
        GLOBAL_IMAGE_PATH = path

        # 预览图片（缩放显示）
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((360, 340), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.img_label.configure(image=photo, text="")
            self.img_label.image = photo  # 保持引用
        except Exception:
            self.img_label.configure(
                text=f"✅ 图片已加载：\n{os.path.basename(path)}",
                fg="#0feca8"
            )

        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", "图片已加载，请点击「开始分析」进行图像识别...\n\n提示：系统将自动调用以下百度AI接口：\n① 通用物体和场景识别\n② 动物识别\n③ 花卉识别\n④ OCR文字识别\n⑤ 语音合成")
        self.narration_text.delete("1.0", END)
        self.tts_btn.config(state=DISABLED)
        self.status_label.config(text="图片已加载，待分析", fg="#0feca8")
        self.info_bar.config(text=f"当前图片：{path}")

    def start_analysis(self):
        """开始分析（后台线程运行）"""
        if not GLOBAL_IMAGE_PATH or not os.path.exists(GLOBAL_IMAGE_PATH):
            showerror("错误", "请先上传图片！")
            return

        self.analyze_btn.config(state=DISABLED, text="⏳ 分析中...")
        self.progress.pack(side="right", padx=(0, 5))
        self.progress.start(10)
        self.status_label.config(text="正在调用百度AI接口...", fg="#e94560")
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", "🔄 正在调用百度图像识别API，请稍候...\n（首次运行需获取Access Token，约3-5秒）\n\n")
        self.narration_text.delete("1.0", END)
        self.root.update()

        thread = threading.Thread(target=self._analysis_worker, daemon=True)
        thread.start()

    def _analysis_worker(self):
        """后台分析线程"""
        global AUDIO_FILE
        try:
            result = baidu_api.full_analysis(
                GLOBAL_IMAGE_PATH,
                audio_output="narration.mp3"
            )

            analysis = result["analysis"]
            narration = result["narration"]
            AUDIO_FILE = result["audio"]

            # 更新界面
            self.root.after(0, self._show_result, analysis, narration)

        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_result(self, analysis: dict, narration: str):
        """在主线程更新结果"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state=NORMAL, text="🔍 开始分析")
        self.status_label.config(text="✅ 分析完成", fg="#0feca8")

        # 格式化显示结果
        formatted = format_analysis_text(analysis)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", formatted)

        # 显示解说词
        self.narration_text.delete("1.0", END)
        self.narration_text.insert("1.0", narration)

        # 解说词高亮（变色）
        self.narration_text.tag_config("highlight", foreground="#0feca8")
        self.narration_text.tag_add("highlight", "1.0", END)

        # 启用朗读按钮
        if AUDIO_FILE:
            self.tts_btn.config(state=NORMAL)

        # 更新信息栏
        objects = analysis.get("objects", [])
        count = len(objects)
        self.info_bar.config(
            text=f"✅ 识别到 {count} 个物体 | "
                 f"文字 {len(analysis.get('texts', []))} 条 | "
                 f"学生：{config.STUDENT_NAME}（{config.STUDENT_ID}）"
        )

    def _show_error(self, error_msg: str):
        """显示错误"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state=NORMAL, text="🔍 开始分析")
        self.status_label.config(text="❌ 分析失败", fg="#e94560")
        self.result_text.delete("1.0", END)
        self.result_text.insert(
            "1.0",
            f"❌ 调用百度API出错：\n\n{error_msg}\n\n"
            f"请检查：\n"
            f"1. API Key 和 Secret Key 是否正确\n"
            f"2. 是否已领取「图像识别」免费额度\n"
            f"3. 网络连接是否正常"
        )
        messagebox.showerror("分析失败", f"百度API调用错误：\n{error_msg}")

    def play_narration(self):
        """播放语音解说"""
        if not AUDIO_FILE or not os.path.exists(AUDIO_FILE):
            showinfo("提示", "请先执行分析生成解说！")
            return

        try:
            if sys.platform == "win32":
                import winsound
                winsound.PlaySound(AUDIO_FILE, winsound.SND_FILENAME)
            else:
                os.system(f'start "" "{AUDIO_FILE}"' if sys.platform == "darwin" else f'xdg-open "{AUDIO_FILE}"')
            self.status_label.config(text="🔊 正在播放语音解说...", fg="#0feca8")
        except Exception as e:
            showinfo("提示", f"播放失败：{e}\n\n音频文件已保存至：{AUDIO_FILE}")

    def clear_all(self):
        """清空所有内容"""
        global GLOBAL_IMAGE_PATH, AUDIO_FILE
        GLOBAL_IMAGE_PATH = None
        AUDIO_FILE = None

        self.img_label.configure(image="", text="📷 点击下方「上传图片」按钮\n选择要分析的图片")
        self.img_label.image = None
        self.result_text.delete("1.0", END)
        self.narration_text.delete("1.0", END)
        self.tts_btn.config(state=DISABLED)
        self.status_label.config(text="等待上传图片...", fg="#888")
        self.info_bar.config(text="")
        self.analyze_btn.config(state=NORMAL, text="🔍 开始分析")


# ---------------------------------------------------------------
# 程序入口
# ---------------------------------------------------------------

def main():
    root = Tk()
    app = ImageAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
