# 智能終端機 (Intelligent Terminal)

這是一個基於 Python 的跨平台命令列介面（CLI）工具，它能理解並執行標準的 shell 指令以及日常的自然語言。透過整合 [DeepSeek AI](https://platform.deepseek.com/)，您可以像對話一樣操作您的終端機。

## ✨ 主要功能

* **跨平台支援**: 可在 Windows, Linux, 及 macOS 上一致地運作。
* **自然語言處理**: 輸入像「幫我列出所有檔案」或「建立一個叫 '報告' 的資料夾」這樣的指令，AI 將會為您轉換成對應的 shell 指令。
* **標準指令執行**: 完美兼容您熟悉的標準 shell 指令，例如 `dir`, `ls -l`, `cd` 等。
* **智慧型指令判斷**: 程式會先嘗試將您的輸入作為標準指令執行，若失敗則自動切換至 AI 模式進行解析。
* **動態路徑提示**: 提示符會永遠顯示您目前所在的完整工作目錄。
* **Tab 自動補全**: 支援檔名與目錄名的自動補全，提升您的工作效率。
* **安全確認機制**: 所有由 AI 生成的指令在執行前，都會請求您的確認，防止意外操作。
* **彩色化輸出**: 使用不同的顏色區分提示、成功訊息與錯誤訊息，讓終端機畫面更清晰易讀。

## 🚀 開始使用

請依照以下步驟來設定並執行本專案。

### 1. 環境需求

請先確認您的電腦已安裝：

* Python 3.8 或更高版本
* pip (Python 套件管理工具)

### 2. 安裝步驟

1.  **複製專案庫**
    ```bash
    git clone [https://github.com/your-username/intelligent-terminal.git](https://github.com/your-username/intelligent-terminal.git)
    cd intelligent-terminal
    ```

2.  **安裝必要函式庫**
    ```bash
    pip install -r requirements.txt
    ```
    *若您尚未建立 `requirements.txt`，請手動安裝：*
    ```bash
    pip install requests colorama
    # 如果您是 Windows 用戶，建議加裝以啟用 Tab 補全功能
    pip install pyreadline3
    ```

3.  **設定 API 金鑰**
    您需要一個 DeepSeek 的 API 金鑰。
    * 前往 [DeepSeek API Keys](https://platform.deepseek.com/api_keys) 頁面取得您的金鑰。
    * 將金鑰設定為環境變數 `DEEPSEEK_API_KEY`。

    **Windows (CMD)**:
    ```cmd
    set DEEPSEEK_API_KEY=您的金鑰
    ```
    *(此設定僅在當前視窗有效)*

    **Linux / macOS**:
    ```bash
    export DEEPSEEK_API_KEY='您的金鑰'
    ```
    *(可將此行加入 `~/.bashrc` 或 `~/.zshrc` 中使其永久生效)*

### 3. 如何執行

完成設定後，在專案根目錄下執行以下指令即可啟動程式：

```bash
python ai_shell.py
````

## 📝 使用範例

**標準指令**:

```
D:\Projects\intelligent-terminal >>> dir
D:\Projects\intelligent-terminal >>> cd ..
D:\Projects >>>
```

**自然語言指令**:

```
D:\Projects\intelligent-terminal >>> 建立一個測試用的資料夾
非標準指令，嘗試使用 AI 進行轉換...
AI 建議執行: mkdir test_folder
確認執行？(y/n): y
```

## 🧪 測試

本專案使用 `pytest` 進行單元測試。

1.  **安裝 pytest**:
    ```bash
    pip install pytest
    ```
2.  **執行測試**:
    ```bash
    pytest
    ```

## 📜 授權條款

本專案採用 [MIT License](https://www.google.com/search?q=LICENSE) 授權。

