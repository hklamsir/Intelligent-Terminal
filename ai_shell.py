import os
import sys
import subprocess
import requests
import json
import locale # 導入 locale 模組
import colorama # 導入 colorama

# --- 顏色代碼 ---
class Colors:
    """定義終端機輸出的 ANSI 顏色代碼"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text, color):
    """
    使用指定的 ANSI 顏色代碼打印文本。

    Args:
        text (str): 要打印的文字內容。
        color (str): 來自 Colors 類別的 ANSI 顏色代碼。
    """
    # 在 Windows 的舊版 cmd 中可能不支援 ANSI 顏色碼，但新版 Windows Terminal 支援
    print(f"{color}{text}{Colors.ENDC}")

# --- 1. 環境設置 & 2.5 作業系統偵測 ---
def get_os_type():
    """
    偵測當前的作業系統類型。

    Returns:
        str: 'windows', 'linux', 'macos', 或 'unknown'。
    """
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    else:
        return 'unknown'

# --- 3. AI 整合模組 ---
def get_ai_command(user_input, os_type):
    """
    呼叫 DeepSeek API 將自然語言轉換為 shell 指令。

    Args:
        user_input (str): 用戶輸入的自然語言。
        os_type (str): 當前的作業系統類型 ('windows', 'linux', 'macos')。

    Returns:
        str | None: 成功時返回轉換後的 shell 指令，失敗時返回 None。
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print_color("錯誤：未找到環境變數 DEEPSEEK_API_KEY。", Colors.FAIL)
        print_color("請先設定您的 DeepSeek API 金鑰。", Colors.WARNING)
        return None

    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    os_name_map = {
        'windows': 'Windows CMD',
        'linux': 'Linux Bash',
        'macos': 'macOS Bash'
    }
    os_prompt_name = os_name_map.get(os_type, 'shell')

    # --- 更新後的提示詞模板 (已移除範例) ---
    current_directory = os.getcwd()

    prompt = f"""
# 任務守則
1. **嚴格遵守目標系統**: 絕對只能生成適用於「{os_prompt_name}」的指令。禁止提供任何其他作業系統的指令。
2. **單行指令**: 回應必須是單一、可直接複製並執行的 Shell 指令。
3. **無任何多餘內容**: 絕對不要包含任何解釋、註解、程式碼區塊標記 (```)、或任何非指令的文字。

# 當前情境
- **作業系統**: {os_prompt_name}
- **目前工作目錄**: `{current_directory}`
- **使用者請求**: `{user_input}`

請根據以上情境，生成對應的指令："""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位頂尖的 Shell 指令專家，專門將自然語言精準地轉換為特定作業系統的單行 Shell 指令。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.3
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=20)
        response.raise_for_status()
        
        result = response.json()
        generated_command = result['choices'][0]['message']['content'].strip()
        
        if generated_command.startswith("```") and generated_command.endswith("```"):
            generated_command = generated_command.strip("```").split('\n')[-1].strip()
        
        return generated_command

    except requests.exceptions.RequestException as e:
        print_color(f"API 請求失敗: {e}", Colors.FAIL)
        return None
    except (KeyError, IndexError):
        print_color("無法從 API 回應中解析指令。", Colors.FAIL)
        return None

# --- 4. 指令執行模組 ---
def execute_command(command, os_type):
    """
    執行一個 shell 指令，並處理其輸出。

    Args:
        command (str): 要執行的指令。
        os_type (str): 當前的作業系統類型。

    Returns:
        bool: 指令是否成功執行 (returncode 為 0)。
    """
    parts = command.strip().split()
    if not parts:
        return True

    cmd_base = parts[0].lower()
    
    if cmd_base == 'cd':
        try:
            path = " ".join(parts[1:]) if len(parts) > 1 else os.path.expanduser("~")
            if not path:
                 path = os.path.expanduser("~")
            os.chdir(path)
            return True
        except FileNotFoundError:
            print_color(f"錯誤：找不到目錄 '{path}'", Colors.FAIL)
            return False
        except Exception as e:
            print_color(f"執行 'cd' 時發生錯誤: {e}", Colors.FAIL)
            return False

    try:
        if os_type == 'windows':
            console_encoding = locale.getpreferredencoding()
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding=console_encoding, errors='replace')
        else:
            result = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True, text=True)

        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print_color(result.stderr.strip(), Colors.FAIL)
        
        return result.returncode == 0

    except Exception as e:
        print_color(f"執行指令時發生未預期的錯誤: {e}", Colors.FAIL)
        return False

def setup_readline_completion():
    """
    為 Linux 和 macOS 設定 readline 以支援 Tab 自動補全。
    在 Windows 上，如果安裝了 'pyreadline3'，此功能也將啟用。
    """
    try:
        import readline
        import glob

        def completer(text, state):
            expanded_text = os.path.expanduser(text)
            options = glob.glob(expanded_text + '*')
            
            for i, option in enumerate(options):
                if os.path.isdir(option):
                    options[i] += os.sep
            
            if state < len(options):
                return options[state]
            else:
                return None

        readline.set_completer(completer)
        delims = ' \t\n`!@#$^&*()=+[{]}|;\'",<>?'
        readline.set_completer_delims(delims)
        readline.parse_and_bind("tab: complete")
        
    except ImportError:
        if get_os_type() == 'windows':
            print_color("\n提示：為了在 Windows 上啟用 Tab 自動補全功能，請安裝 'pyreadline3' 函式庫。", Colors.WARNING)
            print_color("指令: pip install pyreadline3\n", Colors.OKCYAN)

def get_single_char_input(prompt):
    """
    跨平台讀取單一字符輸入，不需按 Enter，且不加入歷史紀錄。

    Args:
        prompt (str): 顯示給用戶的提示文字。

    Returns:
        str: 用戶輸入的單一字符。
    """
    print(prompt, end='', flush=True)
    
    os_type = get_os_type()
    
    char = ''
    if os_type == 'windows':
        import msvcrt
        char_byte = msvcrt.getch()
        try:
            char = char_byte.decode('utf-8')
        except UnicodeDecodeError:
            char = char_byte.decode(locale.getpreferredencoding(), errors='ignore')
    else: # linux or macos
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    print(char)
    return char

def main():
    """
    程式主函式，負責初始化並進入主迴圈。
    """
    colorama.init(autoreset=True)
    
    os_type = get_os_type()
    setup_readline_completion()

    print_color("歡迎使用智能終端機（支援 Windows/Linux/macOS）。", Colors.OKGREEN)
    print_color("輸入 shell 指令或自然語言，輸入 'exit' 或 'quit' 退出。", Colors.OKCYAN)

    while True:
        try:
            print("")
            prompt = f"{os.getcwd()} >>> "
            user_input = input(prompt)

            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input.strip():
                continue
            
            command_succeeded = execute_command(user_input, os_type)

            if not command_succeeded:
                print_color("非標準指令，嘗試使用 AI 進行轉換...", Colors.OKCYAN)
                ai_command = get_ai_command(user_input, os_type)

                if ai_command:
                    print_color(f"AI 建議執行: {Colors.BOLD}{ai_command}{Colors.ENDC}", Colors.WARNING)
                    confirm = get_single_char_input("確認執行？(y/n): ").lower()
                    
                    if confirm == 'y':
                        execute_command(ai_command, os_type)
                    else:
                        if os_type != 'windows' and not confirm:
                             print()
                        print_color("操作已取消。", Colors.OKBLUE)
        
        except KeyboardInterrupt:
            print("\n偵測到 Ctrl+C，正在退出程式。")
            break
        except Exception as e:
            print_color(f"發生未知錯誤: {e}", Colors.FAIL)

if __name__ == "__main__":
    main()

