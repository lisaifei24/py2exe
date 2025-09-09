import os
import sys
import subprocess
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class PyToExePackager:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 打包成 EXE 工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建变量
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.onefile = tk.BooleanVar(value=True)
        self.console = tk.BooleanVar(value=True)
        self.icon_path = tk.StringVar()
        self.additional_data = []
        self.hidden_imports = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        header = ttk.Label(self.main_frame, text="Python 文件打包成 EXE 工具", style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件
        ttk.Label(self.main_frame, text="Python 文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.input_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.browse_input_file).grid(row=1, column=2, padx=5, pady=5)
        
        # 输出目录
        ttk.Label(self.main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.browse_output_dir).grid(row=2, column=2, padx=5, pady=5)
        
        # 打包选项
        ttk.Checkbutton(self.main_frame, text="打包为单个文件", variable=self.onefile).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(self.main_frame, text="显示控制台窗口", variable=self.console).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 图标文件
        ttk.Label(self.main_frame, text="图标文件:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.icon_path, width=50).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.browse_icon_file).grid(row=5, column=2, padx=5, pady=5)
        
        # 附加数据文件
        ttk.Label(self.main_frame, text="附加数据文件:").grid(row=6, column=0, sticky=tk.W, pady=5)
        data_frame = ttk.Frame(self.main_frame)
        data_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.data_listbox = tk.Listbox(data_frame, height=4)
        self.data_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        data_btn_frame = ttk.Frame(data_frame)
        data_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        ttk.Button(data_btn_frame, text="添加", command=self.add_data_file).pack(fill=tk.X, pady=2)
        ttk.Button(data_btn_frame, text="删除", command=self.remove_data_file).pack(fill=tk.X, pady=2)
        
        # 隐藏导入
        ttk.Label(self.main_frame, text="隐藏导入模块:").grid(row=7, column=0, sticky=tk.W, pady=5)
        import_frame = ttk.Frame(self.main_frame)
        import_frame.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.import_listbox = tk.Listbox(import_frame, height=4)
        self.import_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        import_btn_frame = ttk.Frame(import_frame)
        import_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        ttk.Button(import_btn_frame, text="添加", command=self.add_import).pack(fill=tk.X, pady=2)
        ttk.Button(import_btn_frame, text="删除", command=self.remove_import).pack(fill=tk.X, pady=2)
        
        # 打包按钮
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=20)
        ttk.Button(btn_frame, text="开始打包", command=self.start_packaging).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # 进度条和状态
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.status_label = ttk.Label(self.main_frame, text="就绪")
        self.status_label.grid(row=10, column=0, columnspan=3, sticky=tk.W)
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="选择Python文件",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            if not self.output_dir.get():
                default_dir = os.path.join(os.path.dirname(filename), 'dist')
                self.output_dir.set(default_dir)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def browse_icon_file(self):
        filename = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)
    
    def add_data_file(self):
        src = filedialog.askopenfilename(title="选择要添加的数据文件")
        if src:
            dest = filedialog.askdirectory(title="选择数据文件在EXE中的目标目录")
            if dest:
                # 简化显示路径
                display_src = os.path.basename(src)
                display_dest = os.path.basename(dest) if dest != '.' else dest
                self.data_listbox.insert(tk.END, f"{display_src} -> {display_dest}")
                self.additional_data.append((src, dest))
    
    def remove_data_file(self):
        selection = self.data_listbox.curselection()
        if selection:
            index = selection[0]
            self.data_listbox.delete(index)
            self.additional_data.pop(index)
    
    def add_import(self):
        import_name = tk.simpledialog.askstring("添加隐藏导入", "请输入模块名称:")
        if import_name:
            self.import_listbox.insert(tk.END, import_name)
            self.hidden_imports.append(import_name)
    
    def remove_import(self):
        selection = self.import_listbox.curselection()
        if selection:
            index = selection[0]
            self.import_listbox.delete(index)
            self.hidden_imports.pop(index)
    
    def start_packaging(self):
        # 验证输入
        if not self.input_file.get():
            messagebox.showerror("错误", "请选择要打包的Python文件")
            return
        
        if not os.path.isfile(self.input_file.get()):
            messagebox.showerror("错误", "输入的Python文件不存在")
            return
        
        # 在后台线程中运行打包过程
        self.progress.start()
        self.status_label.config(text="正在打包...")
        
        thread = threading.Thread(target=self.package_py_to_exe)
        thread.daemon = True
        thread.start()
    
    def package_py_to_exe(self):
        try:
            input_file = self.input_file.get()
            output_dir = self.output_dir.get() or os.path.join(os.path.dirname(input_file), 'dist')
            
            # 构建 PyInstaller 命令
            cmd = ['pyinstaller', '--noconfirm']
            
            if self.onefile.get():
                cmd.append('--onefile')
            else:
                cmd.append('--onedir')
                
            if not self.console.get():
                cmd.append('--windowed')
                
            icon_path = self.icon_path.get()
            if icon_path and os.path.isfile(icon_path):
                cmd.extend(['--icon', icon_path])
                
            if self.additional_data:
                for src, dest in self.additional_data:
                    cmd.extend(['--add-data', f"{src}{os.pathsep}{dest}"])
                    
            if self.hidden_imports:
                for imp in self.hidden_imports:
                    cmd.extend(['--hidden-import', imp])
                    
            # 添加输入文件和输出目录
            cmd.extend(['--distpath', output_dir])
            cmd.append(input_file)
            
            # 运行 PyInstaller
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 清理临时文件
                build_dir = os.path.join(os.path.dirname(input_file), 'build')
                spec_file = os.path.join(os.path.dirname(input_file), f"{Path(input_file).stem}.spec")
                
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)
                if os.path.exists(spec_file):
                    os.remove(spec_file)
                
                self.root.after(0, self.on_success, output_dir)
            else:
                self.root.after(0, self.on_error, result.stderr)
                
        except Exception as e:
            self.root.after(0, self.on_error, str(e))
    
    def on_success(self, output_dir):
        self.progress.stop()
        self.status_label.config(text="打包完成!")
        messagebox.showinfo("成功", f"打包完成！EXE 文件已保存到: {output_dir}")
    
    def on_error(self, error_msg):
        self.progress.stop()
        self.status_label.config(text="打包失败")
        messagebox.showerror("错误", f"打包过程中出错:\n{error_msg}")

def main():
    root = tk.Tk()
    app = PyToExePackager(root)
    root.mainloop()

if __name__ == "__main__":
    main()