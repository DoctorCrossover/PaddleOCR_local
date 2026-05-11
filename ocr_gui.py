import os
import uuid
import json
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import numpy as np
import pyautogui
import keyboard

os.environ['ONEDNN_MAX_CPU_ISA'] = 'SSE4_1'
os.environ['FLAGS_use_onednn'] = '0'
os.environ['PADDLE_ENABLE_ONEDNN_OPTS'] = '0'

DEFAULT_HOTKEY = 'ctrl+shift+s'
HOTKEY_CONFIG_FILE = 'hotkey_config.json'

class HotkeySettings:
    def __init__(self):
        self.hotkey = DEFAULT_HOTKEY
        self.load_config()
    
    def load_config(self):
        if os.path.exists(HOTKEY_CONFIG_FILE):
            try:
                with open(HOTKEY_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'hotkey' in config:
                        self.hotkey = config['hotkey']
            except:
                self.hotkey = DEFAULT_HOTKEY
    
    def save_config(self):
        with open(HOTKEY_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'hotkey': self.hotkey}, f)
    
    def set_hotkey(self, hotkey):
        self.hotkey = hotkey
        self.save_config()

class ScreenshotSelector:
    def __init__(self, parent):
        self.parent = parent
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.rect = None
        self.screenshot = None
        
        self.setup_selector()
    
    def setup_selector(self):
        screen_width = pyautogui.size()[0]
        screen_height = pyautogui.size()[1]
        
        self.selector = Toplevel(self.parent.root)
        self.selector.attributes('-fullscreen', True)
        self.selector.attributes('-alpha', 0.3)
        self.selector.attributes('-topmost', True)
        self.selector.config(bg='black')
        
        self.canvas = Canvas(self.selector, width=screen_width, height=screen_height, bg='black', highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        self.selector.bind('<Escape>', self.on_escape)
        
        self.selector.focus_set()
    
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_x = event.x
        self.current_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.current_x, self.current_y,
            outline='red', width=2, fill='', stipple='gray50'
        )
    
    def on_mouse_drag(self, event):
        self.current_x = event.x
        self.current_y = event.y
        
        self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.current_x, self.current_y,
            outline='red', width=2, fill='blue', stipple='gray50',
            dash=(5, 5)
        )
    
    def on_mouse_up(self, event):
        self.selector.destroy()
        
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 10 and height > 10:
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            self.parent.process_screenshot(screenshot)
        else:
            self.parent.status_label.config(text="选择区域太小，请重新选择")
    
    def on_escape(self, event):
        self.selector.destroy()
        self.parent.status_label.config(text="已取消截图")

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PaddleOCR 文字识别")
        self.root.geometry("1000x700")
        
        self.ocr = None
        self.current_image_path = None
        self.display_image = None
        self.hotkey_settings = HotkeySettings()
        self.screenshot_hotkey = None
        
        self.create_widgets()
        self.init_ocr()
        self.register_hotkey()
    
    def init_ocr(self):
        self.status_label.config(text="正在初始化OCR模型...")
        self.root.update()
        
        try:
            self.ocr = PaddleOCR(lang='ch', use_angle_cls=False)
            self.status_label.config(text="OCR模型初始化完成")
        except Exception as e:
            self.status_label.config(text=f"OCR初始化失败: {str(e)}")
    
    def create_widgets(self):
        main_frame = Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        button_frame = Frame(main_frame)
        button_frame.pack(fill=X, pady=(0, 10))
        
        self.select_btn = Button(button_frame, text="选择图片", command=self.select_image, width=12)
        self.select_btn.pack(side=LEFT, padx=5)
        
        self.screenshot_btn = Button(button_frame, text="区域截图", command=self.take_screenshot, width=12)
        self.screenshot_btn.pack(side=LEFT, padx=5)
        
        self.ocr_btn = Button(button_frame, text="开始识别", command=self.process_ocr, width=12, state=DISABLED)
        self.ocr_btn.pack(side=LEFT, padx=5)
        
        self.settings_btn = Button(button_frame, text="快捷键设置", command=self.open_settings, width=12)
        self.settings_btn.pack(side=LEFT, padx=5)
        
        self.clear_btn = Button(button_frame, text="清空结果", command=self.clear_results, width=12)
        self.clear_btn.pack(side=LEFT, padx=5)
        
        self.save_btn = Button(button_frame, text="保存结果", command=self.save_results, width=12)
        self.save_btn.pack(side=LEFT, padx=5)
        
        hotkey_info = Label(button_frame, text=f"截图快捷键: {self.hotkey_settings.hotkey}", fg="#666666")
        hotkey_info.pack(side=RIGHT, padx=10)
        
        content_frame = Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True)
        
        image_frame = Frame(content_frame, bg="#cccccc")
        image_frame.pack(side=LEFT, padx=(0, 10), fill=BOTH, expand=True)
        
        self.image_label = Label(image_frame, text="未选择图片", bg="#f0f0f0")
        self.image_label.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        result_frame = Frame(content_frame)
        result_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        Label(result_frame, text="识别结果:").pack(anchor=W)
        
        scrollbar = Scrollbar(result_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.result_text = Text(result_frame, width=50, yscrollcommand=scrollbar.set, font=("宋体", 12))
        self.result_text.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        self.status_label = Label(main_frame, text="就绪", relief=SUNKEN, anchor=W)
        self.status_label.pack(fill=X, pady=(10, 0))
    
    def register_hotkey(self):
        if self.screenshot_hotkey:
            keyboard.unhook_all_hotkeys()
        
        try:
            keyboard.add_hotkey(self.hotkey_settings.hotkey, self.take_screenshot)
            print(f"快捷键已注册: {self.hotkey_settings.hotkey}")
        except Exception as e:
            print(f"注册快捷键失败: {e}")
    
    def unregister_hotkey(self):
        keyboard.unhook_all_hotkeys()
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.result_text.delete(1.0, END)
            self.display_selected_image(file_path)
            self.ocr_btn.config(state=NORMAL)
            self.status_label.config(text=f"已选择图片: {file_path}")
    
    def take_screenshot(self):
        self.root.iconify()
        self.status_label.config(text="请拖动选择截图区域...")
        
        ScreenshotSelector(self)
    
    def process_screenshot(self, screenshot):
        self.root.deiconify()
        
        try:
            temp_path = os.path.join('uploads', f'screenshot_{uuid.uuid4().hex}.png')
            os.makedirs('uploads', exist_ok=True)
            screenshot.save(temp_path)
            
            self.current_image_path = temp_path
            self.result_text.delete(1.0, END)
            self.display_selected_image(temp_path)
            self.ocr_btn.config(state=NORMAL)
            self.status_label.config(text="截图完成，请点击\"开始识别\"")
            
        except Exception as e:
            self.status_label.config(text=f"截图失败: {str(e)}")
            messagebox.showerror("错误", f"截图失败: {str(e)}")
    
    def display_selected_image(self, image_path):
        try:
            img = Image.open(image_path)
            
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()
            
            if label_width <= 1:
                label_width = 400
            if label_height <= 1:
                label_height = 400
            
            img_width, img_height = img.size
            scale = min(label_width / img_width, label_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.display_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.display_image, text="")
            
        except Exception as e:
            self.image_label.config(text=f"图片加载失败:\n{str(e)}")
            self.status_label.config(text=f"图片加载失败: {str(e)}")
    
    def open_settings(self):
        SettingsDialog(self)
    
    def add_border_to_image(self, image_path, border_size=50, border_color=(255, 255, 255)):
        img = Image.open(image_path)
        width, height = img.size
        
        new_width = width + border_size * 2
        new_height = height + border_size * 2
        
        new_img = Image.new(img.mode, (new_width, new_height), border_color)
        new_img.paste(img, (border_size, border_size))
        
        temp_path = os.path.join('uploads', f'temp_{uuid.uuid4().hex}.png')
        new_img.save(temp_path)
        
        return temp_path
    
    def process_ocr(self):
        if not self.current_image_path or not self.ocr:
            return
        
        self.ocr_btn.config(state=DISABLED)
        self.status_label.config(text="正在识别...")
        self.root.update()
        
        try:
            bordered_image_path = self.add_border_to_image(self.current_image_path, border_size=30)
            
            result1 = self.ocr.predict(self.current_image_path)
            result2 = self.ocr.predict(bordered_image_path)
            
            if os.path.exists(bordered_image_path):
                os.remove(bordered_image_path)
            
            all_texts = []
            
            for result in [result1, result2]:
                for page in result:
                    if isinstance(page, dict):
                        rec_texts = page.get('rec_texts', [])
                        rec_boxes = page.get('rec_boxes', [])
                        
                        for i in range(len(rec_texts)):
                            text = rec_texts[i]
                            if text and text.strip():
                                box = None
                                if i < len(rec_boxes) and rec_boxes[i] is not None:
                                    box_arr = rec_boxes[i]
                                    if isinstance(box_arr, np.ndarray):
                                        flat_box = box_arr.flatten()
                                        if len(flat_box) >= 4:
                                            box = [float(flat_box[0]), float(flat_box[1])]
                                    elif isinstance(box_arr, list) and len(box_arr) > 0:
                                        if isinstance(box_arr[0], (list, np.ndarray)):
                                            if len(box_arr[0]) >= 2:
                                                box = [float(box_arr[0][0]), float(box_arr[0][1])]
                                        elif isinstance(box_arr[0], (int, float)):
                                            if len(box_arr) >= 4:
                                                box = [float(box_arr[0]), float(box_arr[1])]
                                
                                all_texts.append({
                                    'text': text.strip(),
                                    'box': box
                                })
            
            if all_texts:
                texts_set = {}
                for item in all_texts:
                    text = item['text']
                    if text not in texts_set:
                        texts_set[text] = item
                
                all_texts = sorted(texts_set.values(), key=lambda x: (
                    x['box'][1] if x['box'] else 0,
                    x['box'][0] if x['box'] else 0
                ))
                
                self.result_text.delete(1.0, END)
                line_count = 0
                
                for item in all_texts:
                    text = item['text']
                    line_count += 1
                    self.result_text.insert(END, f"{text}\n")
            else:
                self.result_text.delete(1.0, END)
                self.result_text.insert(END, "未识别到文字")
                line_count = 0
            
            self.status_label.config(text=f"识别完成，共识别 {line_count} 行文字")
            
        except Exception as e:
            self.result_text.delete(1.0, END)
            self.result_text.insert(END, f"识别出错:\n{str(e)}")
            self.status_label.config(text=f"识别失败: {str(e)}")
        
        self.ocr_btn.config(state=NORMAL)
    
    def clear_results(self):
        self.result_text.delete(1.0, END)
        self.current_image_path = None
        self.display_image = None
        self.image_label.config(image="", text="未选择图片")
        self.ocr_btn.config(state=DISABLED)
        self.status_label.config(text="已清空")
    
    def save_results(self):
        content = self.result_text.get(1.0, END).strip()
        if not content:
            self.status_label.config(text="没有可保存的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"结果已保存到: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"保存失败: {str(e)}")
    
    def update_hotkey(self, new_hotkey):
        self.unregister_hotkey()
        self.hotkey_settings.set_hotkey(new_hotkey)
        self.register_hotkey()
        
        for child in self.select_btn.master.winfo_children():
            if isinstance(child, Label) and "截图快捷键" in child.cget("text"):
                child.config(text=f"截图快捷键: {new_hotkey}")
                break
        
        self.status_label.config(text=f"快捷键已更新为: {new_hotkey}")

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = Toplevel(parent.root)
        self.dialog.title("快捷键设置")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        frame = Frame(self.dialog, padx=20, pady=20)
        frame.pack(fill=BOTH, expand=True)
        
        Label(frame, text="当前截图快捷键:").grid(row=0, column=0, sticky=W, pady=(0, 5))
        Label(frame, text=self.parent.hotkey_settings.hotkey, fg="#0066cc", font=("Arial", 12)).grid(row=0, column=1, sticky=W, pady=(0, 5))
        
        Label(frame, text="输入新的快捷键组合:").grid(row=1, column=0, sticky=W, pady=(10, 5))
        
        self.hotkey_entry = Entry(frame, width=20, font=("Arial", 12))
        self.hotkey_entry.grid(row=1, column=1, sticky=W, pady=(10, 5))
        self.hotkey_entry.insert(0, self.parent.hotkey_settings.hotkey)
        
        Label(frame, text="示例: ctrl+shift+s, alt+a, win+d", fg="#666666", font=("Arial", 10)).grid(row=2, column=0, columnspan=2, sticky=W, pady=(5, 15))
        
        button_frame = Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ok_btn = Button(button_frame, text="确定", command=self.apply_settings, width=10)
        ok_btn.pack(side=LEFT, padx=5)
        
        cancel_btn = Button(button_frame, text="取消", command=self.dialog.destroy, width=10)
        cancel_btn.pack(side=LEFT, padx=5)
        
        test_btn = Button(button_frame, text="测试快捷键", command=self.test_hotkey, width=12)
        test_btn.pack(side=LEFT, padx=5)
    
    def apply_settings(self):
        new_hotkey = self.hotkey_entry.get().strip().lower()
        
        if not new_hotkey:
            messagebox.showwarning("警告", "请输入快捷键组合")
            return
        
        valid_modifiers = ['ctrl', 'shift', 'alt', 'win']
        keys = new_hotkey.split('+')
        
        for key in keys:
            if key not in valid_modifiers and len(key) > 1:
                messagebox.showwarning("警告", f"无效的按键: {key}")
                return
        
        try:
            keyboard.add_hotkey(new_hotkey, lambda: None)
            keyboard.remove_hotkey(new_hotkey)
            
            self.parent.update_hotkey(new_hotkey)
            self.dialog.destroy()
            messagebox.showinfo("成功", f"快捷键已更新为: {new_hotkey}")
            
        except Exception as e:
            messagebox.showerror("错误", f"无效的快捷键组合: {str(e)}")
    
    def test_hotkey(self):
        new_hotkey = self.hotkey_entry.get().strip().lower()
        
        if not new_hotkey:
            messagebox.showwarning("警告", "请输入快捷键组合")
            return
        
        try:
            keyboard.add_hotkey(new_hotkey, self.on_test_hotkey)
            messagebox.showinfo("测试", f"请按下 {new_hotkey}\n按下后会自动关闭")
            
        except Exception as e:
            messagebox.showerror("错误", f"无效的快捷键组合: {str(e)}")
    
    def on_test_hotkey(self):
        keyboard.unhook_all_hotkeys()
        self.parent.register_hotkey()
        messagebox.showinfo("成功", "快捷键测试成功!")
        self.dialog.destroy()

if __name__ == '__main__':
    root = Tk()
    app = OCRApp(root)
    root.mainloop()
    app.unregister_hotkey()