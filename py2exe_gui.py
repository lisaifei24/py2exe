import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading

class Py2ExeConverter:
    def __init__(self, root):
        self.root = root
        root.title("Py2Exe 打包工具")
        root.geometry("500x300")
        
        # 设置窗口图标（如果有的话）
        try:
            root.iconbitmap('icon.ico')  # 请确保有一个icon.ico文件或删除这行
        except:
            pass
        
        # 创建UI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="Py2Exe 打包工具", font=('Arial', 16))
        title_label.pack(pady=10)
        
        # 选择Python文件
        self.py_file_path = tk.StringVar()
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(file_frame, text="Python文件:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=self.py_file_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="浏览...", command=self.browse_py_file).pack(side=tk.LEFT)
        
        # 选择输出目录
        self.output_dir = tk.StringVar()
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="浏览...", command=self.browse_output_dir).pack(side=tk.LEFT)
        
        # 选项
        options_frame = tk.Frame(self.root)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.onefile_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="打包为单个文件", variable=self.onefile_var).pack(side=tk.LEFT)
        
        self.noconsole_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="无控制台窗口", variable=self.noconsole_var).pack(side=tk.LEFT, padx=10)
        
        # 打包按钮
        tk.Button(self.root, text="开始打包", command=self.start_conversion, bg="#4CAF50", fg="white").pack(pady=20)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_py_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python文件", "*.py")])
        if file_path:
            self.py_file_path.set(file_path)
            # 自动设置输出目录为.py文件所在目录
            dir_path = os.path.dirname(file_path)
            self.output_dir.set(dir_path)
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
    
    def start_conversion(self):
        py_file = self.py_file_path.get()
        output_dir = self.output_dir.get()
        
        if not py_file:
            messagebox.showerror("错误", "请选择Python文件")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        # 检查PyInstaller是否安装
        try:
            import PyInstaller
        except ImportError:
            if messagebox.askyesno("PyInstaller未安装", "需要安装PyInstaller才能继续。是否现在安装？"):
                self.install_pyinstaller()
            return
        
        # 在后台线程中运行打包过程
        threading.Thread(target=self.convert_to_exe, daemon=True).start()
    
    def install_pyinstaller(self):
        self.status_var.set("正在安装PyInstaller...")
        try:
            subprocess.check_call(["pip", "install", "pyinstaller"])
            messagebox.showinfo("成功", "PyInstaller安装成功")
            self.status_var.set("PyInstaller安装成功")
        except subprocess.CalledProcessError:
            messagebox.showerror("错误", "PyInstaller安装失败")
            self.status_var.set("PyInstaller安装失败")
    
    def convert_to_exe(self):
        py_file = self.py_file_path.get()
        output_dir = self.output_dir.get()
        
        # 构建PyInstaller命令
        cmd = ["pyinstaller", "--distpath", output_dir]
        
        if self.onefile_var.get():
            cmd.append("--onefile")
        
        if self.noconsole_var.get():
            cmd.append("--noconsole")
        
        cmd.append(py_file)
        
        self.status_var.set("正在打包...")
        
        try:
            # 运行PyInstaller
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            # 实时更新输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            return_code = process.poll()
            
            if return_code == 0:
                messagebox.showinfo("成功", "打包完成！")
                self.status_var.set("打包完成")
            else:
                error = process.stderr.read()
                messagebox.showerror("错误", f"打包失败:\n{error}")
                self.status_var.set("打包失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"发生异常:\n{str(e)}")
            self.status_var.set("打包出错")

if __name__ == "__main__":
    root = tk.Tk()
    app = Py2ExeConverter(root)
    root.mainloop()