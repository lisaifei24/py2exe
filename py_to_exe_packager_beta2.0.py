import os
import sys
import subprocess
import shutil
from pathlib import Path
import PySimpleGUI as sg

# 设置主题
sg.theme('LightBlue2')

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
            sg.popup_error(f"输入文件不存在: {input_file}")
            return False
            
        # 检查文件扩展名
        if not input_file.lower().endswith('.py'):
            sg.popup_error("输入文件必须是 .py 文件")
            return False
            
        # 检查 PyInstaller 是否安装
        try:
            import PyInstaller
        except ImportError:
            sg.popup_error("PyInstaller 未安装", "请先运行: pip install pyinstaller")
            return False
            
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
                sg.popup_error(f"图标文件不存在: {icon_path}")
                return False
            cmd.extend(['--icon', icon_path])
            
        if additional_data:
            for src, dest in additional_data:
                if not os.path.exists(src):
                    sg.popup_error(f"附加数据文件不存在: {src}")
                    return False
                cmd.extend(['--add-data', f"{src}{os.pathsep}{dest}"])
                
        if hidden_imports:
            for imp in hidden_imports:
                cmd.extend(['--hidden-import', imp])
                
        # 添加输入文件和输出目录
        cmd.extend(['--distpath', output_dir])
        cmd.append(input_file)
        
        # 运行 PyInstaller
        sg.popup_auto_close("正在打包...", auto_close_duration=1)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            sg.popup_error("打包失败", f"错误信息:\n{result.stderr}")
            return False
        
        # 清理临时文件
        build_dir = os.path.join(os.path.dirname(input_file), 'build')
        spec_file = os.path.join(os.path.dirname(input_file), f"{Path(input_file).stem}.spec")
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(spec_file):
            os.remove(spec_file)
            
        sg.popup("打包完成", f"EXE 文件已保存到:\n{output_dir}")
        return True
        
    except Exception as e:
        sg.popup_error("打包过程中出错", str(e))
        return False

def browse_file(title, file_types=(("All files", "*.*"),)):
    """浏览文件对话框"""
    filename = sg.popup_get_file(title, file_types=file_types)
    return filename if filename else None

def browse_folder(title):
    """浏览文件夹对话框"""
    folder = sg.popup_get_folder(title)
    return folder if folder else None

def create_main_window():
    """创建主窗口"""
    layout = [
        [sg.Text('Python 文件打包成 EXE 工具', font=('Helvetica', 16), justification='center')],
        [sg.HorizontalSeparator()],
        [
            sg.Text('Python 文件:', size=(10, 1)), 
            sg.Input(key='-INPUT_FILE-'), 
            sg.FileBrowse(button_text="浏览", file_types=(("Python Files", "*.py"),))
        ],
        [
            sg.Text('输出目录:', size=(10, 1)), 
            sg.Input(key='-OUTPUT_DIR-'), 
            sg.FolderBrowse(button_text="浏览")
        ],
        [
            sg.Checkbox('打包为单个文件', default=True, key='-ONEFILE-'),
            sg.Checkbox('显示控制台窗口', default=True, key='-CONSOLE-')
        ],
        [
            sg.Text('图标文件:', size=(10, 1)), 
            sg.Input(key='-ICON_PATH-'), 
            sg.FileBrowse(button_text="浏览", file_types=(("Icon Files", "*.ico"),))
        ],
        [
            sg.Frame('附加数据文件', [
                [sg.Multiline(size=(50, 3), key='-ADDITIONAL_DATA-', disabled=True)],
                [sg.Button('添加文件', key='-ADD_DATA-'), sg.Button('清除', key='-CLEAR_DATA-')]
            ])
        ],
        [
            sg.Frame('隐藏导入模块', [
                [sg.Multiline(size=(50, 3), key='-HIDDEN_IMPORTS-', disabled=True)],
                [sg.Button('添加模块', key='-ADD_IMPORT-'), sg.Button('清除', key='-CLEAR_IMPORTS-')]
            ])
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button('开始打包', size=(10, 1), button_color=('white', 'green')), 
            sg.Button('退出', size=(10, 1), button_color=('white', 'red'))
        ],
        [sg.StatusBar('', key='-STATUS-', size=(60, 1))]
    ]
    
    return sg.Window('Python 打包工具', layout, finalize=True)

def create_add_data_window():
    """创建添加数据文件窗口"""
    layout = [
        [sg.Text('源文件路径:'), sg.Input(key='-SRC-'), sg.FileBrowse(button_text="浏览")],
        [sg.Text('目标路径:'), sg.Input(key='-DEST-', tooltip='在EXE中的相对路径')],
        [sg.Button('添加'), sg.Button('取消')]
    ]
    return sg.Window('添加数据文件', layout, modal=True)

def create_add_import_window():
    """创建添加隐藏模块窗口"""
    layout = [
        [sg.Text('模块名称:'), sg.Input(key='-IMPORT-')],
        [sg.Button('添加'), sg.Button('取消')]
    ]
    return sg.Window('添加隐藏模块', layout, modal=True)

def main():
    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller
    except ImportError:
        sg.popup_error("PyInstaller 未安装", "请先运行: pip install pyinstaller")
        return

    window = create_main_window()
    additional_data = []
    hidden_imports = []

    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '退出'):
            break
            
        elif event == '-ADD_DATA-':
            add_data_window = create_add_data_window()
            while True:
                add_event, add_values = add_data_window.read()
                if add_event in (sg.WIN_CLOSED, '取消'):
                    break
                elif add_event == '添加':
                    src = add_values['-SRC-']
                    dest = add_values['-DEST-']
                    if src and dest:
                        additional_data.append((src, dest))
                        window['-ADDITIONAL_DATA-'].update('\n'.join([f"{s} -> {d}" for s, d in additional_data]))
                        add_data_window.close()
                        break
                    else:
                        sg.popup_error("必须提供源文件和目标路径")
            add_data_window.close()
            
        elif event == '-CLEAR_DATA-':
            additional_data = []
            window['-ADDITIONAL_DATA-'].update('')
            
        elif event == '-ADD_IMPORT-':
            add_import_window = create_add_import_window()
            while True:
                add_event, add_values = add_import_window.read()
                if add_event in (sg.WIN_CLOSED, '取消'):
                    break
                elif add_event == '添加':
                    imp = add_values['-IMPORT-']
                    if imp:
                        hidden_imports.append(imp)
                        window['-HIDDEN_IMPORTS-'].update('\n'.join(hidden_imports))
                        add_import_window.close()
                        break
                    else:
                        sg.popup_error("必须提供模块名称")
            add_import_window.close()
            
        elif event == '-CLEAR_IMPORTS-':
            hidden_imports = []
            window['-HIDDEN_IMPORTS-'].update('')
            
        elif event == '开始打包':
            input_file = values['-INPUT_FILE-']
            if not input_file:
                sg.popup_error("必须选择Python文件")
                continue
                
            output_dir = values['-OUTPUT_DIR-']
            onefile = values['-ONEFILE-']
            console = values['-CONSOLE-']
            icon_path = values['-ICON_PATH-']
            
            # 更新状态栏
            window['-STATUS-'].update('正在打包...')
            window.refresh()
            
            # 调用打包函数
            success = package_py_to_exe(
                input_file=input_file,
                output_dir=output_dir if output_dir else None,
                onefile=onefile,
                console=console,
                icon_path=icon_path if icon_path else None,
                additional_data=additional_data if additional_data else None,
                hidden_imports=hidden_imports if hidden_imports else None
            )
            
            window['-STATUS-'].update('打包完成' if success else '打包失败')

    window.close()

if __name__ == "__main__":
    main()