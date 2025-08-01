import os
import sys
import subprocess
import shutil
from pathlib import Path
import questionary  # Added for better interactive prompts

def package_py_to_exe(input_file, output_dir=None, onefile=True, console=True, icon_path=None, additional_data=None, hidden_imports=None):
    """
    将 Python 文件打包成 EXE 可执行文件
    
    参数:
        input_file (str): 要打包的 Python 文件路径
        output_dir (str, optional): 输出目录，默认为当前目录下的 'dist' 文件夹
        onefile (bool, optional): 是否打包为单个文件，默认为 True
        console (bool, optional): 是否显示控制台窗口，默认为 True
        icon_path (str, optional): 可执行文件的图标文件路径 (.ico)
        additional_data (list, optional): 额外需要包含的文件列表，格式为 [(源路径, 目标路径), ...]
        hidden_imports (list, optional): 需要手动指定的隐藏导入模块列表
    """
    try:
        # 检查输入文件是否存在
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
            
        # 检查文件扩展名
        if not input_file.lower().endswith('.py'):
            raise ValueError("输入文件必须是 .py 文件")
            
        # 检查 PyInstaller 是否安装
        try:
            import PyInstaller
        except ImportError:
            raise ImportError("PyInstaller 未安装，请先运行: pip install pyinstaller")
            
        # 准备输出目录
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(input_file), 'dist')
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建 PyInstaller 命令
        cmd = ['pyinstaller', '--noconfirm']
        
        if onefile:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')
            
        if not console:
            cmd.append('--windowed')
            
        if icon_path:
            if not os.path.isfile(icon_path):
                raise FileNotFoundError(f"图标文件不存在: {icon_path}")
            cmd.extend(['--icon', icon_path])
            
        if additional_data:
            for src, dest in additional_data:
                if not os.path.exists(src):
                    raise FileNotFoundError(f"附加数据文件不存在: {src}")
                cmd.extend(['--add-data', f"{src}{os.pathsep}{dest}"])
                
        if hidden_imports:
            for imp in hidden_imports:
                cmd.extend(['--hidden-import', imp])
                
        # 添加输入文件和输出目录
        cmd.extend(['--distpath', output_dir])
        cmd.append(input_file)
        
        # 运行 PyInstaller
        print(f"正在打包 {input_file} 为 EXE 文件...")
        subprocess.run(cmd, check=True)
        
        # 清理临时文件
        build_dir = os.path.join(os.path.dirname(input_file), 'build')
        spec_file = os.path.join(os.path.dirname(input_file), f"{Path(input_file).stem}.spec")
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(spec_file):
            os.remove(spec_file)
            
        print(f"打包完成！EXE 文件已保存到: {output_dir}")
        
    except Exception as e:
        print(f"打包过程中出错: {str(e)}")
        sys.exit(1)

def get_file_path(prompt, file_type=None):
    """Helper function to get file path with validation"""
    while True:
        path = questionary.path(prompt).ask()
        if not path:
            return None
        if not os.path.exists(path):
            print(f"错误: 文件或目录不存在: {path}")
            continue
        if file_type == 'file' and not os.path.isfile(path):
            print(f"错误: 必须是一个文件: {path}")
            continue
        if file_type == 'dir' and not os.path.isdir(path):
            print(f"错误: 必须是一个目录: {path}")
            continue
        return path

def get_additional_data():
    """Collect additional data files interactively"""
    additional_data = []
    while questionary.confirm("是否要添加额外的数据文件?").ask():
        src = get_file_path("请输入源文件路径:", file_type='file')
        if not src:
            continue
        dest = questionary.text("请输入目标路径 (在EXE中的相对路径):").ask()
        if not dest:
            continue
        additional_data.append((src, dest))
    return additional_data if additional_data else None

def get_hidden_imports():
    """Collect hidden imports interactively"""
    hidden_imports = []
    while questionary.confirm("是否要添加隐藏导入模块?").ask():
        imp = questionary.text("请输入模块名称:").ask()
        if imp:
            hidden_imports.append(imp)
    return hidden_imports if hidden_imports else None

def main():
    try:
        # Check if questionary is installed
        try:
            import questionary
        except ImportError:
            raise ImportError("questionary 未安装，请先运行: pip install questionary")

        print("\n" + "=" * 40)
        print(" Python 文件打包成 EXE 工具".center(40))
        print("=" * 40 + "\n")

        # Get input file
        input_file = get_file_path("请输入要打包的 Python 文件路径:", file_type='file')
        if not input_file:
            print("必须指定一个Python文件!")
            return

        # Get other options
        output_dir = get_file_path("请输入输出目录 (留空使用默认目录):", file_type='dir')
        
        onefile = questionary.confirm(
            "打包为单个文件?",
            default=True
        ).ask()
        
        console = questionary.confirm(
            "显示控制台窗口?",
            default=True
        ).ask()
        
        icon_path = get_file_path("请输入图标文件路径 (.ico) (留空跳过):", file_type='file')
        
        additional_data = get_additional_data()
        hidden_imports = get_hidden_imports()

        # Show summary
        print("\n" + "=" * 40)
        print(" 打包配置摘要 ".center(40))
        print("=" * 40)
        print(f"输入文件: {input_file}")
        print(f"输出目录: {output_dir or '默认 (dist)'}")
        print(f"打包为单个文件: {'是' if onefile else '否'}")
        print(f"显示控制台: {'是' if console else '否'}")
        print(f"图标文件: {icon_path or '无'}")
        print(f"附加数据文件: {additional_data or '无'}")
        print(f"隐藏导入模块: {hidden_imports or '无'}")
        print("=" * 40 + "\n")

        # Confirm before proceeding
        if not questionary.confirm("确认开始打包?", default=True).ask():
            print("打包已取消。")
            return

        # 调用打包函数
        package_py_to_exe(
            input_file=input_file,
            output_dir=output_dir,
            onefile=onefile,
            console=console,
            icon_path=icon_path,
            additional_data=additional_data,
            hidden_imports=hidden_imports
        )

    except Exception as e:
        print(f"发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()