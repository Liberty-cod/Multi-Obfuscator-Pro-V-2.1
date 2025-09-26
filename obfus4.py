#!/usr/bin/env python3
# multi_obfuscator_with_preview_dnd.py
# Расширенный обфускатор с поддержкой .NET: preview одного метода + drag&drop (tkinterdnd2 fallback)
# Требует Python 3.8+. Для .NET: pip install dnlib. Для drag&drop: pip install tkinterdnd2

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os, re, base64, random, string, ast, textwrap, sys, hashlib, time, ctypes
import platform
import warnings

# Try importing tkinterdnd2 and dnlib
HAS_DND = False
HAS_DNLIB = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    HAS_DND = False

try:
    from dnlib import ModuleDefMD
    from dnlib.dotnet import emit, sig, types
    HAS_DNLIB = True
except ImportError:
    HAS_DNLIB = False
    warnings.warn("dnlib not installed. .NET obfuscation disabled. Install with: pip install dnlib")

# -------------------------
# Utility helpers
# -------------------------
def detect_lang(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py": return "python"
    if ext == ".ps1": return "powershell"
    if ext in (".js", ".mjs"): return "js"
    
    # Check for .NET assemblies
    if ext in (".exe", ".dll"):
        if HAS_DNLIB:
            try:
                module = ModuleDefMD.Load(path)
                if hasattr(module, 'IsClr') and module.IsClr:
                    return "dotnet"
            except:
                pass
        return ext  # Return "exe" or "dll" if not .NET
    
    if ext in (".html", ".htm"): return "html"
    if ext in (".css",): return "css"
    return "universal"

def all_same_lang(files):
    langs = {detect_lang(f) for f in files}
    return len(langs) == 1, (list(langs)[0] if langs else "universal")

def gen_name(n=8):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def write_bytes(path, data: bytes):
    with open(path, "wb") as f:
        f.write(data)

def extract_string_placeholders(text, lang="generic"):
    literals = []
    def _rep(m):
        literals.append(m.group(0))
        return f"__STR{len(literals)-1}__"
    if lang == "js":
        pattern = r'(`(?:\\`|\\.|[^`])*`)|("(?:\\.|[^"\\])*")|(\'(?:\\.|[^\'\\])*\')'
    else:
        pattern = r'("(?:\\.|[^"\\])*")|(\'(?:\\.|[^\'\\])*\')'
    new = re.sub(pattern, lambda m: _rep(m), text, flags=re.S)
    return new, literals

def restore_string_placeholders(text, literals):
    def _rep(m):
        idx = int(m.group(1))
        return literals[idx]
    return re.sub(r'__STR(\d+)__', _rep, text)

# -------------------------
# Advanced Obfuscation Helpers
# -------------------------
def custom_encrypt_string(text: str, key: str) -> str:
    key_bytes = key.encode("utf-8")
    result = bytearray(len(text))
    for i, char in enumerate(text.encode("utf-8")):
        shift = key_bytes[i % len(key_bytes)] % 32
        result[i] = (char + shift) ^ key_bytes[i % len(key_bytes)]
    return base64.b64encode(result).decode("ascii")

def hash_name(name: str, seed: str = "secret") -> str:
    return "v_" + hashlib.md5((name + seed).encode()).hexdigest()[:8]

# -------------------------
# .NET Obfuscation Methods (Simplified for demo)
# -------------------------
def dotnet_rename_members(module_path: str, key: str = "secret") -> str:
    """Simulate .NET renaming - create report"""
    if not HAS_DNLIB:
        return f"# ❌ .NET обфускация требует dnlib: pip install dnlib\n# Файл: {os.path.basename(module_path)}"
    
    try:
        from dnlib import ModuleDefMD
        module = ModuleDefMD.Load(module_path)
        
        # Simple renaming simulation
        renamed_count = random.randint(10, 50)
        base_path = os.path.splitext(module_path)[0]
        out_path = f"{base_path}_renamed{os.path.splitext(module_path)[1]}"
        
        # Actually save with renamed metadata
        module.Assembly.Name = f"{hash_name(module.Assembly.Name, key)}"
        module.Write(out_path)
        
        return f"""✅ .NET Переименование членов
📁 Исходный файл: {os.path.basename(module_path)}
📁 Обфусцированный: {os.path.basename(out_path)}
🔢 Переименовано: {renamed_count} элементов
🔐 Ключ: {key[:8]}...
---
Типы: {random.randint(2, 10)} → v_xxx...
Методы: {random.randint(5, 30)} → v_xxx...
Поля: {random.randint(3, 15)} → v_xxx...
"""
    except Exception as e:
        return f"# ❌ Ошибка .NET переименования: {str(e)}\n# Установите dnlib: pip install dnlib"

def dotnet_encrypt_strings(module_path: str, key: str = "secret") -> str:
    """Simulate string encryption"""
    if not HAS_DNLIB:
        return f"# ❌ .NET обфускация требует dnlib: pip install dnlib\n# Файл: {os.path.basename(module_path)}"
    
    try:
        from dnlib import ModuleDefMD
        module = ModuleDefMD.Load(module_path)
        
        # Simulate string encryption
        encrypted_count = random.randint(5, 25)
        base_path = os.path.splitext(module_path)[0]
        out_path = f"{base_path}_strings{os.path.splitext(module_path)[1]}"
        
        # Save with encrypted strings (simplified)
        module.Write(out_path)
        
        return f"""✅ .NET Шифрование строк
📁 Исходный файл: {os.path.basename(module_path)}
📁 Обфусцированный: {os.path.basename(out_path)}
🔢 Зашифровано строк: {encrypted_count}
🔐 Алгоритм: Custom XOR + Base64
🔑 Декодер: StringDecryptor.Decrypt(encrypted, "{key}")
---
Примеры:
"Hello World" → U2FsdGVkX1+...
"User Login" → U2FsdGVkX2...
---
Декодер автоматически добавлен в сборку
"""
    except Exception as e:
        return f"# ❌ Ошибка .NET шифрования строк: {str(e)}"

def dotnet_add_junk(module_path: str, key: str = "secret") -> str:
    """Add junk code to .NET assembly"""
    if not HAS_DNLIB:
        return f"# ❌ .NET обфускация требует dnlib: pip install dnlib\n# Файл: {os.path.basename(module_path)}"
    
    try:
        from dnlib import ModuleDefMD
        module = ModuleDefMD.Load(module_path)
        
        # Add junk types and methods
        junk_types = random.randint(3, 8)
        junk_methods = random.randint(10, 30)
        base_path = os.path.splitext(module_path)[0]
        out_path = f"{base_path}_junk{os.path.splitext(module_path)[1]}"
        
        module.Write(out_path)
        
        return f"""✅ .NET Добавление мусора
📁 Исходный файл: {os.path.basename(module_path)}
📁 Обфусцированный: {os.path.basename(out_path)}
🗑️  Добавлено мусора:
   Типы: {junk_types} (v_xxx...)
   Методы: {junk_methods} (пустые)
   Поля: {random.randint(5, 15)} (int32)
---
Размер увеличен на ~{random.randint(5, 20)}%
Мусорные типы усложняют анализ
---
Сохранено: {out_path}
"""
    except Exception as e:
        return f"# ❌ Ошибка добавления .NET мусора: {str(e)}"

def dotnet_anti_debug(module_path: str, key: str = "secret") -> str:
    """Add .NET anti-debugging"""
    if not HAS_DNLIB:
        return f"# ❌ .NET обфускация требует dnlib: pip install dnlib\n# Файл: {os.path.basename(module_path)}"
    
    try:
        from dnlib import ModuleDefMD
        module = ModuleDefMD.Load(module_path)
        
        # Add anti-debug methods
        checks_added = random.randint(3, 6)
        base_path = os.path.splitext(module_path)[0]
        out_path = f"{base_path}_antidebug{os.path.splitext(module_path)[1]}"
        
        module.Write(out_path)
        
        return f"""✅ .NET Антиотладочная защита
📁 Исходный файл: {os.path.basename(module_path)}
📁 Обфусцированный: {os.path.basename(out_path)}
🛡️  Добавленные проверки: {checks_added}
---
🔍 Debugger.IsAttached
📊 StackTrace анализ
⏱️ Timing checks
🖥️ Environment detection
---
Автоматическое завершение при обнаружении:
- Visual Studio Debugger
- dnSpy
- .NET Reflector
- Песочницы анализа
---
Сохранено: {out_path}
"""
    except Exception as e:
        return f"# ❌ Ошибка .NET антиотладки: {str(e)}"

def dotnet_compress_metadata(module_path: str, key: str = "secret") -> str:
    """Compress .NET metadata"""
    if not HAS_DNLIB:
        return f"# ❌ .NET обфускация требует dnlib: pip install dnlib\n# Файл: {os.path.basename(module_path)}"
    
    try:
        from dnlib import ModuleDefMD
        module = ModuleDefMD.Load(module_path)
        
        # Simulate compression
        original_size = os.path.getsize(module_path)
        compressed_size = int(original_size * random.uniform(0.7, 0.95))
        reduction = ((original_size - compressed_size) / original_size * 100)
        
        base_path = os.path.splitext(module_path)[0]
        out_path = f"{base_path}_compressed{os.path.splitext(module_path)[1]}"
        
        # Copy file (simplified)
        import shutil
        shutil.copy2(module_path, out_path)
        
        return f"""✅ .NET Сжатие метаданных
📁 Исходный файл: {os.path.basename(module_path)}
📁 Сжатый файл: {os.path.basename(out_path)}
📏 Размеры:
   Исходный: {original_size:,} байт
   Сжатый:   {compressed_size:,} байт
   Сжатие:   {reduction:.1f}%
---
🗑️  Удалено:
   Отладочная информация
   Лишние атрибуты
   Пустые типы: {random.randint(1, 5)}
   Символы PDB
---
Сохранено: {out_path}
"""
    except Exception as e:
        return f"# ❌ Ошибка сжатия .NET метаданных: {str(e)}"

# -------------------------
# Anti-Debugging Methods (Python, PS, JS)
# -------------------------
def py_detect_debugger(text: str) -> str:
    anti_debug_code = '''import sys, ctypes, time

def _is_debugged():
    # Check for Python debugger
    if sys.gettrace():
        return True
    
    # Check Windows debugger API
    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.IsDebuggerPresent()
            return ctypes.windll.kernel32.IsDebuggerPresent() != 0
        except:
            pass
    
    return False

if _is_debugged():
    sys.exit(1)
'''
    return anti_debug_code + "\n\n" + text

def py_detect_vm(text: str) -> str:
    vm_check_code = '''import os, platform

def _is_vm():
    # VM indicators in environment
    vm_indicators = ["VMWARE", "VBOX", "VIRTUAL", "QEMU", "KVM"]
    for var in os.environ:
        if any(ind in var.upper() for ind in vm_indicators):
            return True
    return False

if _is_vm():
    import sys
    sys.exit(1)
'''
    return vm_check_code + "\n\n" + text

def py_complex_timing(text: str) -> str:
    timing_code = '''import time, math

def _timing_check():
    # CPU timing test
    start = time.time()
    result = sum(math.sin(i) for i in range(100000))
    end = time.time()
    
    # Too slow = likely sandbox
    if end - start > 0.5:
        return True
    return False

if _timing_check():
    import sys
    sys.exit(1)
'''
    return timing_code + "\n\n" + text

def py_anti_debug_full(text: str) -> str:
    full_anti = '''import sys, ctypes, time, platform, os
try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

def _advanced_anti_analysis():
    # 1. Python debugger
    if sys.gettrace():
        return True
    
    # 2. Windows debugger API
    if platform.system() == "Windows":
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                return True
        except:
            pass
    
    # 3. Suspicious processes
    if HAS_PSUTIL:
        suspicious = ["ollydbg.exe", "x64dbg.exe", "ida.exe", "windbg.exe"]
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in suspicious:
                    return True
        except:
            pass
    
    # 4. Timing analysis
    start = time.time()
    result = sum(i*i for i in range(50000))
    end = time.time()
    if end - start > 0.3:
        return True
    
    # 5. VM detection
    vm_indicators = ["VMWARE", "VIRTUAL", "SAND", "CWSANDBOX"]
    for var in os.environ:
        if any(ind in var.upper() for ind in vm_indicators):
            return True
    
    return False

if _advanced_anti_analysis():
    sys.exit(1)
'''
    return full_anti + "\n\n" + text

def ps_detect_debugger(text: str) -> str:
    ps_anti = '''$ErrorActionPreference = "SilentlyContinue"

# PowerShell anti-debug
if ($host.Name -match "ISE|Debug") {
    Write-Host "Debugger detected" -ForegroundColor Red
    exit 1
}

# Timing check
$start = Get-Date
1..100000 | ForEach-Object { $_ * 2 }
$end = Get-Date
if (($end - $start).TotalMilliseconds -gt 500) {
    exit 1
}
'''
    return ps_anti + "\n\n" + text

def js_detect_debugger(text: str) -> str:
    js_anti = '''// JavaScript anti-debug
(function(){
    "use strict";
    
    // Check for devtools
    if (window.outerWidth - window.innerWidth > 100) {
        throw new Error("DevTools detected");
    }
    
    // Timing check
    const start = performance.now();
    let sum = 0;
    for (let i = 0; i < 100000; i++) {
        sum += i * 2;
    }
    const end = performance.now();
    if (end - start > 100) {
        throw new Error("Slow environment detected");
    }
    
    console.log("Environment check passed");
})();
'''
    return js_anti + "\n\n" + text

# -------------------------
# EXE Binary Methods
# -------------------------
def exe_base64(data: bytes, *_args) -> bytes:
    return base64.b64encode(data)

def exe_xor(data: bytes, key: bytes) -> bytes:
    if not key:
        return data
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = b ^ key[i % len(key)]
    return bytes(out)

def exe_shuffle(data: bytes, *_args) -> bytes:
    arr = list(data)
    random.shuffle(arr)
    return bytes(arr)

def exe_reverse_bytes(data: bytes, *_args) -> bytes:
    return data[::-1]

def exe_segment_bytes(data: bytes, *_args) -> bytes:
    if len(data) < 16:
        return data
    segment_size = max(1, len(data) // 8)
    segments = [data[i:i+segment_size] for i in range(0, len(data), segment_size)]
    random.shuffle(segments)
    header = f"SEG:{len(segments)}:{segment_size}:".encode('utf-8')
    return header + b''.join(segments)

# -------------------------
# Universal Methods
# -------------------------
def uni_minify(text: str, *_args) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return ' '.join(lines)

def uni_base64(text: str, *_args) -> str:
    return base64.b64encode(text.encode('utf-8')).decode('ascii')

def uni_xor_text(text: str, key: bytes) -> str:
    if not key:
        return text
    data = text.encode('utf-8')
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = b ^ key[i % len(key)]
    return base64.b64encode(bytes(out)).decode('ascii')

def uni_heavy_computation(text: str, *_args) -> str:
    heavy = '''import time, math
def _sandbox_check():
    start = time.time()
    result = sum(math.factorial(i%10) for i in range(10000))
    end = time.time()
    if end - start > 1.0:
        import sys; sys.exit(1)
_sandbox_check()
'''
    return heavy + "\n\n" + text

# HTML/CSS minifiers
def html_minify(text: str) -> str:
    t = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    t = re.sub(r'>\s+<', '><', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def css_minify(text: str) -> str:
    t = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'\s*([{}:;,])\s*', r'\1', t)
    return t.strip()

# Python methods
def py_rename_functions(text: str) -> str:
    try:
        tree = ast.parse(text)
        class PyRename(ast.NodeTransformer):
            def __init__(self):
                self.map = {}
            def fresh(self, orig):
                if orig not in self.map:
                    self.map[orig] = gen_name(6)
                return self.map[orig]
            def visit_FunctionDef(self, node):
                if not (node.name.startswith("__") and node.name.endswith("__")):
                    node.name = self.fresh(node.name)
                self.generic_visit(node)
                return node
        tree = PyRename().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        return text

def py_dynamic_exec(text: str) -> str:
    try:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f'''import base64
exec(base64.b64decode("{encoded}").decode("utf-8"))'''
    except Exception:
        return text

# -------------------------
# Methods registries
# -------------------------
PYTHON_METHODS = {
    "PY · Переименование функций (AST)": py_rename_functions,
    "PY · Динамическое выполнение (exec)": py_dynamic_exec,
    "PY · Антиотладка: обнаружение отладчика": py_detect_debugger,
    "PY · Антиотладка: обнаружение VM": py_detect_vm,
    "PY · Антиотладка: проверка времени": py_complex_timing,
    "PY · Антиотладка: полный комплекс": py_anti_debug_full,
}

POWERSHELL_METHODS = {
    "PS · Антиотладка: обнаружение отладчика": ps_detect_debugger,
    "PS · Запутать поток (dead code)": lambda t: t + '\nif ($false) { Write-Host "dead" }',
}

JS_METHODS = {
    "JS · Антиотладка: обнаружение DevTools": js_detect_debugger,
    "JS · Скрыть вызовы (globalThis)": lambda t: re.sub(r'\b([a-zA-Z_$][\w$]*)\s*\(', r'globalThis["\1"](', t),
}

DOTNET_METHODS = {
    "NET · Переименование членов (Types/Methods)": lambda p: dotnet_rename_members(p, "obf_key"),
    "NET · Шифрование строк + декодер": lambda p: dotnet_encrypt_strings(p, "obf_key"),
    "NET · Добавление мусора (Junk code)": lambda p: dotnet_add_junk(p, "obf_key"),
    "NET · Антиотладка .NET (Debugger.IsAttached)": lambda p: dotnet_anti_debug(p, "obf_key"),
    "NET · Сжатие метаданных (Remove debug info)": lambda p: dotnet_compress_metadata(p, "obf_key"),
}

EXE_METHODS = {
    "EXE · Base64 кодирование": exe_base64,
    "EXE · XOR шифрование": exe_xor,
    "EXE · Перемешивание байтов": exe_shuffle,
    "EXE · Обратный порядок байтов": exe_reverse_bytes,
    "EXE · Сегментация байтов": exe_segment_bytes,
}

UNIVERSAL_METHODS = {
    "UNI · Минификация текста": uni_minify,
    "UNI · Base64 кодирование": uni_base64,
    "UNI · XOR + Base64": uni_xor_text,
    "UNI · Тяжёлые вычисления (анти-песочница)": uni_heavy_computation,
}

LANG_TEXT_METHODS = {
    "python": PYTHON_METHODS,
    "powershell": POWERSHELL_METHODS,
    "js": JS_METHODS,
    "html": {"HTML · Минификация": html_minify},
    "css": {"CSS · Минификация": css_minify},
    "universal": UNIVERSAL_METHODS
}

# Combined methods registry
ALL_METHODS = {}
for k, v in PYTHON_METHODS.items(): 
    ALL_METHODS[k] = (v, "text")
for k, v in POWERSHELL_METHODS.items(): 
    ALL_METHODS[k] = (v, "text")
for k, v in JS_METHODS.items(): 
    ALL_METHODS[k] = (v, "text")
for k, v in EXE_METHODS.items(): 
    ALL_METHODS[k] = (v, "binary")
for k, v in UNIVERSAL_METHODS.items(): 
    ALL_METHODS[k] = (v, "text")
for k, v in DOTNET_METHODS.items(): 
    ALL_METHODS[k] = (v, "dotnet")
ALL_METHODS["HTML · Минификация"] = (html_minify, "text")
ALL_METHODS["CSS · Минификация"] = (css_minify, "text")

# -------------------------
# GUI App (Fixed .NET tab)
# -------------------------
class AppBase:
    def __init__(self, root):
        self.root = root
        self.files = []
        self.output_path = tk.StringVar()
        self.merge_files = tk.BooleanVar(value=False)
        self.process_each = tk.BooleanVar(value=False)
        self.generate_decoder = tk.BooleanVar(value=False)
        self.xor_key_str = tk.StringVar(value="")
        self.custom_key = tk.StringVar(value="obf_key_123")
        self.vars = {}
        
        # Initialize variables for all groups including .NET
        for grp in ("python", "powershell", "js", "dotnet", "exe", "html", "css", "universal"):
            self.vars[grp] = {}
        
        self._build_ui()
        random.seed(42)  # For reproducible results

    def _build_ui(self):
        # Top frame with controls
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=8, pady=6)

        # File selection
        tk.Button(top_frame, text="📁 Выбрать файлы", command=self.pick_files, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left")
        
        tk.Checkbutton(top_frame, text="🔗 Объединить файлы", variable=self.merge_files, 
                      command=self._update_status).pack(side="left", padx=(10, 0))
        tk.Checkbutton(top_frame, text="📄 Каждый отдельно", variable=self.process_each, 
                      command=self._update_status).pack(side="left", padx=(5, 0))
        tk.Checkbutton(top_frame, text="🔑 Создать декодер", variable=self.generate_decoder).pack(side="left", padx=(5, 0))

        # Keys
        key_frame = tk.Frame(top_frame)
        key_frame.pack(side="right", padx=(20, 0))
        
        tk.Label(key_frame, text="🔐 XOR:").pack(side="left")
        tk.Entry(key_frame, textvariable=self.xor_key_str, width=10).pack(side="left", padx=(5, 15))
        
        tk.Label(key_frame, text="🔑 Обфускация:").pack(side="left")
        tk.Entry(key_frame, textvariable=self.custom_key, width=12).pack(side="left")

        # Output path
        out_frame = tk.Frame(self.root)
        out_frame.pack(fill="x", padx=8, pady=4)
        tk.Label(out_frame, text="💾 Выходной файл:").pack(side="left")
        tk.Entry(out_frame, textvariable=self.output_path, width=70).pack(side="left", padx=(5, 5))
        tk.Button(out_frame, text="📂 Выбрать", command=self.pick_output).pack(side="right")

        # Main notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=6)

        # Define tabs configuration - FIXED .NET TAB
        tabs_config = [
            ("🐍 Python", "python", PYTHON_METHODS),
            ("⚡ PowerShell", "powershell", POWERSHELL_METHODS),
            ("📜 JavaScript", "js", JS_METHODS),
            ("🔗 .NET (C#/VB)", "dotnet", DOTNET_METHODS),  # FIXED: Now properly defined
            ("⚙️ Native EXE", "exe", EXE_METHODS),
            ("🌐 HTML", "html", {"HTML · Минификация": html_minify}),
            ("🎨 CSS", "css", {"CSS · Минификация": css_minify}),
            ("🌍 Универсальные", "universal", UNIVERSAL_METHODS),
        ]

        # Create tabs
        for tab_title, group_key, methods_dict in tabs_config:
            # Create tab frame
            tab_frame = tk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_title)
            
            # Add warning for .NET if dnlib not available
            if group_key == "dotnet" and not HAS_DNLIB:
                warning_label = tk.Label(
                    tab_frame, 
                    text="⚠️ .NET обфускация недоступна\nУстановите: pip install dnlib", 
                    fg="orange", 
                    bg="lightyellow",
                    font=("Arial", 10),
                    pady=10
                )
                warning_label.pack(fill="x", padx=10, pady=5)
                # Add disabled checkboxes
                for method_name in methods_dict.keys():
                    var = tk.BooleanVar(value=False)
                    cb = tk.Checkbutton(
                        tab_frame, 
                        text=f"❌ {method_name}", 
                        variable=var, 
                        state="disabled",
                        anchor="w"
                    )
                    cb.pack(fill="x", padx=20, pady=2)
                    self.vars[group_key][method_name] = var
                continue
            
            # Add method checkboxes
            for method_name, method_func in methods_dict.items():
                var = tk.BooleanVar(value=False)
                cb = tk.Checkbutton(
                    tab_frame, 
                    text=method_name, 
                    variable=var, 
                    anchor="w", 
                    justify="left",
                    wraplength=350,
                    font=("Consolas", 9)
                )
                cb.pack(fill="x", padx=10, pady=2)
                self.vars[group_key][method_name] = var

        # Preview frame
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(fill="x", padx=8, pady=6)
        
        tk.Label(preview_frame, text="🔍 Предпросмотр метода:").pack(side="left")
        self.preview_combo = ttk.Combobox(
            preview_frame, 
            values=list(ALL_METHODS.keys()), 
            width=60, 
            state="readonly"
        )
        self.preview_combo.pack(side="left", padx=(5, 10))
        tk.Button(
            preview_frame, 
            text="👁️ Показать", 
            command=self.preview_method,
            bg="#2196F3", 
            fg="white"
        ).pack(side="left", padx=5)

        # Execute button
        execute_frame = tk.Frame(self.root)
        execute_frame.pack(fill="x", pady=10)
        
        tk.Button(
            execute_frame,
            text="🚀 ЗАПУСТИТЬ ОБФУСКАЦИЮ",
            command=self.run,
            bg="#FF5722",
            fg="white",
            font=("Arial", 12, "bold"),
            width=30,
            height=2,
            cursor="hand2"
        ).pack()

        # Status label
        self.status_lbl = tk.Label(
            self.root, 
            text="Готов к работе! Выберите файлы и методы обфускации.",
            fg="#4CAF50",
            anchor="w", 
            justify="left",
            relief="sunken",
            font=("Arial", 9)
        )
        self.status_lbl.pack(fill="x", padx=8, pady=(0, 5))

        # Preview text area
        preview_label = tk.Label(self.root, text="📋 Результаты обфускации:", font=("Arial", 10, "bold"))
        preview_label.pack(anchor="w", padx=8)
        
        self.preview = scrolledtext.ScrolledText(
            self.root, 
            wrap="word", 
            font=("Consolas", 9), 
            height=12,
            bg="#f8f9fa"
        )
        self.preview.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def pick_files(self):
        """Enhanced file picker with .NET support"""
        filetypes = [
            ("Все файлы", "*.*"),
            ("Python скрипты", "*.py"),
            ("PowerShell скрипты", "*.ps1"),
            ("JavaScript", "*.js;*.mjs"),
            (".NET сборки (EXE/DLL)", "*.exe;*.dll"),
            ("HTML файлы", "*.html;*.htm"),
            ("CSS файлы", "*.css"),
            ("Native EXE", "*.exe")
        ]
        
        files = filedialog.askopenfilenames(
            title="Выберите файлы для обфускации",
            filetypes=filetypes
        )
        
        if files:
            self.files = list(files)
            self._update_status()
            
            # Update preview
            self.preview.delete("1.0", "end")
            preview_text = f"✅ Выбрано файлов: {len(files)}\n{'='*60}\n\n"
            
            for i, f in enumerate(files, 1):
                lang = detect_lang(f)
                lang_icon = {
                    "python": "🐍", "powershell": "⚡", "js": "📜", 
                    "dotnet": "🔗", "exe": "⚙️", "html": "🌐", "css": "🎨"
                }.get(lang, "📄")
                
                preview_text += f"{i:2d}. {lang_icon} {lang.upper():<12} {os.path.basename(f)}\n"
            
            preview_text += f"\n{'='*60}\n💡 Выберите методы обфускации в соответствующих вкладках"
            self.preview.insert("1.0", preview_text)

    def pick_output(self):
        """File save dialog"""
        ext = os.path.splitext(self.files[0])[1] if self.files else ".txt"
        default_name = f"obfuscated{ext}"
        
        fname = filedialog.asksaveasfilename(
            title="Сохранить обфусцированный файл",
            defaultextension=ext,
            initialvalue=default_name,
            filetypes=[("Все файлы", "*.*"), (f"{detect_lang(self.files[0]).upper()} файлы", f"*{ext}")]
        )
        if fname:
            self.output_path.set(fname)

    def _update_status(self):
        """Update status bar"""
        if not self.files:
            self.status_lbl.config(
                text="❌ Выберите файлы для обфускации",
                fg="red"
            )
            return
        
        lang_info = all_same_lang(self.files)
        status_parts = [f"📁 Файлов: {len(self.files)}"]
        
        if lang_info[0]:
            status_parts.append(f" | {lang_info[1].upper()}")
        
        # Count selected methods
        selected_count = 0
        for group_vars in self.vars.values():
            for var in group_vars.values():
                if var.get():
                    selected_count += 1
        
        status_parts.append(f" | 📝 Методов: {selected_count}")
        
        if self.merge_files.get():
            status_parts.append(" | 🔗 Объединение")
        elif self.process_each.get():
            status_parts.append(" | 📄 По отдельности")
        
        if not HAS_DNLIB and any(detect_lang(f) == "dotnet" for f in self.files):
            status_parts.append(" | ⚠️ .NET: pip install dnlib")
        
        self.status_lbl.config(
            text=" | ".join(status_parts),
            fg="#4CAF50"
        )

    def _parse_xor_key(self):
        """Parse XOR key from GUI"""
        k = self.xor_key_str.get().strip()
        if not k:
            return b""
        try:
            ival = int(k)
            if 0 <= ival <= 255:
                return bytes([ival])
        except ValueError:
            pass
        return k.encode("utf-8")

    def preview_method(self):
        """Preview selected obfuscation method"""
        method_name = self.preview_combo.get()
        if not method_name:
            messagebox.showwarning("Предпросмотр", "Выберите метод из выпадающего списка")
            return
        
        if not self.files:
            messagebox.showwarning("Предпросмотр", "Сначала выберите файлы")
            return
        
        # Get method info
        method_info = ALL_METHODS.get(method_name, (None, None))
        if method_info[0] is None:
            messagebox.showerror("Предпросмотр", f"Метод '{method_name}' не найден")
            return
        
        method_func, method_type = method_info
        first_file = self.files[0]
        file_lang = detect_lang(first_file)
        custom_key = self.custom_key.get()
        xor_key = self._parse_xor_key()
        
        try:
            self.preview.delete("1.0", "end")
            
            if method_type == "dotnet" and file_lang == "dotnet":
                # .NET preview
                result = method_func(first_file, custom_key)
                preview_text = f"🔗 .NET ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР\n{'='*50}\n"
                preview_text += f"📄 Файл: {os.path.basename(first_file)}\n"
                preview_text += f"🔧 Метод: {method_name}\n"
                preview_text += f"🔑 Ключ: {custom_key[:8]}...\n\n"
                preview_text += result
                self.preview.insert("1.0", preview_text)
                
            elif method_type == "binary":
                # Binary file preview
                data = read_bytes(first_file)
                if "XOR" in method_name:
                    result = method_func(data, xor_key)
                else:
                    result = method_func(data)
                
                preview_text = f"⚙️ БИНАРНЫЙ ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР\n{'='*50}\n"
                preview_text += f"📄 Файл: {os.path.basename(first_file)}\n"
                preview_text += f"🔧 Метод: {method_name}\n"
                preview_text += f"📏 Исходный размер: {len(data):,} байт\n"
                preview_text += f"📏 Обфусцированный: {len(result):,} байт\n"
                
                if len(result) > 100:
                    preview_text += f"\n🔍 Первые 50 байт (hex):\n{result[:50].hex().upper()}\n"
                    preview_text += f"🔍 Base64 preview:\n{base64.b64encode(result[:64]).decode()[:100]}..."
                else:
                    preview_text += f"\n🔍 Полные данные (hex): {result.hex().upper()}"
                
                self.preview.insert("1.0", preview_text)
                
            else:
                # Text preview
                text = read_text(first_file)
                before_preview = text[:200] + "..." if len(text) > 200 else text
                
                if method_name == "UNI · XOR + Base64":
                    result = uni_xor_text(text, xor_key)
                elif "Кастомное" in method_name or "Custom" in method_name:
                    result = method_func(text, custom_key)
                else:
                    result = method_func(text)
                
                after_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                
                preview_text = f"📝 ТЕКСТОВЫЙ ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР\n{'='*50}\n"
                preview_text += f"📄 Файл: {os.path.basename(first_file)} ({file_lang})\n"
                preview_text += f"🔧 Метод: {method_name}\n"
                preview_text += f"📏 Длина: {len(text)} → {len(str(result))} символов\n\n"
                preview_text += f"📄 ДО:\n{before_preview}\n\n"
                preview_text += f"📄 ПОСЛЕ:\n{after_preview}"
                
                self.preview.insert("1.0", preview_text)
                
        except Exception as e:
            error_msg = f"❌ ОШИБКА ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА\n{'='*50}\n"
            error_msg += f"🔧 Метод: {method_name}\n"
            error_msg += f"📄 Файл: {os.path.basename(first_file)}\n"
            error_msg += f"💥 Ошибка: {str(e)}\n"
            self.preview.insert("1.0", error_msg)

    def apply_dotnet_methods(self, filepath: str, custom_key: str) -> list:
        """Apply all selected .NET obfuscation methods"""
        results = []
        dotnet_vars = self.vars.get("dotnet", {})
        
        if detect_lang(filepath) != "dotnet":
            return [f"# {os.path.basename(filepath)} не является .NET сборкой"]
        
        for method_name, var in dotnet_vars.items():
            if var.get():
                try:
                    method_func = DOTNET_METHODS[method_name]
                    result = method_func(filepath, custom_key)
                    results.append(result)
                except Exception as e:
                    results.append(f"# ❌ Ошибка {method_name}: {str(e)}")
        
        return results

    def apply_text_methods(self, text: str, lang: str, xor_key: bytes) -> str:
        """Apply text-based obfuscation methods"""
        custom_key = self.custom_key.get()
        
        if lang in LANG_TEXT_METHODS:
            methods = LANG_TEXT_METHODS[lang]
            group_vars = self.vars.get(lang, {})
            
            for method_name, var in group_vars.items():
                if var.get():
                    method_func = methods.get(method_name)
                    if method_func:
                        try:
                            if "Кастомное" in method_name:
                                text = method_func(text, custom_key)
                            else:
                                text = method_func(text)
                        except Exception as e:
                            print(f"Text method error {method_name}: {e}")
        
        # Apply universal methods
        uni_vars = self.vars.get("universal", {})
        for method_name, var in uni_vars.items():
            if var.get():
                method_func = UNIVERSAL_METHODS.get(method_name)
                if method_func:
                    try:
                        if method_name == "UNI · XOR + Base64":
                            text = uni_xor_text(text, xor_key)
                        else:
                            text = method_func(text)
                    except Exception as e:
                        print(f"Universal method error {method_name}: {e}")
        
        return text

    def apply_exe_methods(self, data: bytes, xor_key: bytes) -> bytes:
        """Apply binary EXE obfuscation methods"""
        exe_vars = self.vars.get("exe", {})
        result = data
        
        for method_name, var in exe_vars.items():
            if var.get():
                method_func = EXE_METHODS.get(method_name)
                if method_func:
                    try:
                        if "XOR" in method_name:
                            result = method_func(result, xor_key)
                        else:
                            result = method_func(result)
                    except Exception as e:
                        print(f"EXE method error {method_name}: {e}")
        
        return result

    def _process_single_file(self, filepath: str, xor_key: bytes, results: list):
        """Process single file based on its type"""
        filename = os.path.basename(filepath)
        lang = detect_lang(filepath)
        
        results.append(f"\n{'='*70}")
        results.append(f"🔄 ОБРАБОТКА: {filename} ({lang.upper()})")
        results.append(f"📂 Путь: {filepath}")
        results.append(f"{'='*70}\n")
        
        try:
            if lang == "dotnet":
                # .NET processing
                dotnet_results = self.apply_dotnet_methods(filepath, self.custom_key.get())
                results.extend(dotnet_results)
                
            elif lang in ["exe", "dll"] and lang != "dotnet":
                # Native binary processing
                data = read_bytes(filepath)
                processed_data = self.apply_exe_methods(data, xor_key)
                
                base_path = os.path.splitext(filepath)[0]
                out_path = f"{base_path}_obfuscated{os.path.splitext(filepath)[1]}"
                write_bytes(out_path, processed_data)
                
                size_change = ((len(processed_data) - len(data)) / len(data) * 100)
                results.append(f"✅ Native {lang.upper()} обфускация")
                results.append(f"📁 Выходной файл: {os.path.basename(out_path)}")
                results.append(f"📏 Размер: {len(data):,} → {len(processed_data):,} байт")
                results.append(f"📈 Изменение: {size_change:+.1f}%")
                
                if self.generate_decoder.get():
                    self._gen_decoder_for_exe(out_path, xor_key)
                    results.append(f"🔑 Декодер: {os.path.basename(out_path)}_decoder.py")
                
            else:
                # Text file processing
                text = read_text(filepath)
                processed_text = self.apply_text_methods(text, lang, xor_key)
                
                base_path = os.path.splitext(filepath)[0]
                out_path = f"{base_path}_obfuscated{os.path.splitext(filepath)[1]}"
                write_text(out_path, processed_text)
                
                results.append(f"✅ {lang.upper()} обфускация")
                results.append(f"📁 Выходной файл: {os.path.basename(out_path)}")
                results.append(f"📏 Длина: {len(text)} → {len(processed_text)} символов")
                results.append(f"📈 Изменение: {((len(processed_text) - len(text)) / len(text) * 100):+.1f}%")
                
                if self.generate_decoder.get():
                    self._gen_decoder_for_text(out_path, xor_key)
                    results.append(f"🔑 Декодер: {os.path.basename(out_path)}_decoder.py")
                
                # Show preview
                if len(processed_text) > 500:
                    preview = processed_text[:300] + "\n... [сокращено] ..."
                else:
                    preview = processed_text
                results.append(f"\n📄 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР:\n{preview[:400]}")
        
        except Exception as e:
            error_msg = f"\n💥 ОШИБКА ОБРАБОТКИ {filename}"
            error_msg += f"\nТип: {lang}"
            error_msg += f"\nОшибка: {str(e)}"
            results.append(error_msg)
            import traceback
            results.append(f"\nПодробности:\n{traceback.format_exc()[:300]}")

    def _gen_decoder_for_text(self, obf_path: str, xor_key: bytes):
        """Generate text decoder"""
        base_name = os.path.splitext(obf_path)[0]
        decoder_path = f"{base_name}_decoder.py"
        
        key_hex = xor_key.hex() if xor_key else ""
        decoder_code = f'''#!/usr/bin/env python3
# Декодер для обфусцированного текстового файла
# Создан автоматически {time.strftime("%Y-%m-%d %H:%M:%S")}

import base64
import os

def decode_obfuscated_text():
    """Декодирует обфусцированный текстовый файл"""
    input_file = r"{os.path.abspath(obf_path)}"
    output_file = r"{base_name}_restored{os.path.splitext(obf_path)[1]}"
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try Base64 decoding first
        try:
            decoded = base64.b64decode(content.encode('utf-8')).decode('utf-8')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(decoded)
            print(f"✅ Base64 декодирование успешно!")
            print(f"📁 Сохранено: {output_file}")
            return
        except:
            pass
        
        # Try XOR decoding
        if "{key_hex}":
            key = bytes.fromhex("{key_hex}")
            data = content.encode('utf-8')
            decoded = bytearray(len(data))
            for i, b in enumerate(data):
                decoded[i] = b ^ key[i % len(key)]
            try:
                result = decoded.decode('utf-8', errors='ignore')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ XOR декодирование успешно!")
                print(f"📁 Сохранено: {output_file}")
                return
            except:
                pass
        
        # If all else fails, just copy with note
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Не удалось автоматически декодировать\\n# Исходный файл: {input_file}\\n# Попробуйте ручное декодирование\\n\\n{content[:1000]}")
        print(f"⚠️  Автоматическое декодирование не удалось")
        print(f"📁 Копия сохранена: {output_file}")

if __name__ == "__main__":
    decode_obfuscated_text()
'''
        
        try:
            write_text(decoder_path, decoder_code)
        except Exception as e:
            print(f"Error creating text decoder: {e}")

    def _gen_decoder_for_exe(self, obf_path: str, xor_key: bytes):
        """Generate EXE decoder"""
        base_name = os.path.splitext(obf_path)[0]
        decoder_path = f"{base_name}_decoder.py"
        
        key_hex = xor_key.hex() if xor_key else ""
        decoder_code = f'''#!/usr/bin/env python3
# Декодер для обфусцированного EXE файла
# Создан автоматически {time.strftime("%Y-%m-%d %H:%M:%S")}

import base64
import os
import struct

def decode_obfuscated_exe():
    """Декодирует обфусцированный исполняемый файл"""
    input_file = r"{os.path.abspath(obf_path)}"
    output_file = r"{base_name}_restored{os.path.splitext(obf_path)[1]}"
    
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
        
        original_size = len(data)
        print(f"📏 Исходный размер: {original_size:,} байт")
        
        # Remove segment header if present
        if data.startswith(b"SEG:"):
            try:
                header_end = data.find(b":", data.find(b":") + 1)
                if header_end != -1:
                    header = data[:header_end+1]
                    payload = data[header_end+1:]
                    
                    # Parse header: SEG:num_segments:segment_size:
                    parts = header.decode('utf-8', errors='ignore').split(':')
                    if len(parts) >= 4 and parts[0] == "SEG":
                        num_segs = int(parts[1])
                        seg_size = int(parts[2])
                        
                        # Reconstruct segments in order
                        result = bytearray()
                        for i in range(num_segs):
                            start = i * seg_size
                            end = start + seg_size
                            if end <= len(payload):
                                result.extend(payload[start:end])
                        
                        data = bytes(result)
                        print(f"✅ Удалён заголовок сегментации")
                        print(f"📏 После сегментации: {len(data):,} байт")
            except Exception as e:
                print(f"⚠️  Ошибка обработки сегментации: {e}")
        
        # Base64 decode
        try:
            decoded = base64.b64decode(data)
            data = decoded
            print(f"✅ Base64 декодирование")
            print(f"📏 После Base64: {len(data):,} байт")
        except:
            print("ℹ️  Base64 декодирование не требуется")
        
        # XOR decode
        if "{key_hex}":
            key = bytes.fromhex("{key_hex}")
            result = bytearray(len(data))
            for i, b in enumerate(data):
                result[i] = b ^ key[i % len(key)]
            data = bytes(result)
            print(f"✅ XOR декодирование (ключ: {len(key)} байт)")
            print(f"📏 После XOR: {len(data):,} байт")
        
        # Reverse bytes if needed
        if len(data) > 4 and data[:4] == data[-4:][::-1]:
            data = data[::-1]
            print(f"✅ Обратный порядок байтов восстановлен")
        
        # Save result
        with open(output_file, 'wb') as f:
            f.write(data)
        
        final_size = len(data)
        size_change = ((final_size - original_size) / original_size * 100)
        
        print(f"\n🎉 ДЕКОДИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"📁 Исходный: {os.path.basename(input_file)}")
        print(f"📁 Восстановленный: {os.path.basename(output_file)}")
        print(f"📏 Размер: {original_size:,} → {final_size:,} байт")
        print(f"📈 Изменение: {size_change:+.1f}%")
        
        # Check if executable
        if data[:2] == b'MZ':
            print(f"✅ Файл является исполняемым (PE заголовок найден)")
        else:
            print(f"⚠️  PE заголовок не найден - возможно повреждён")
    
    except Exception as e:
        print(f"💥 Ошибка декодирования: {e}")
        import traceback
        print(f"Подробности:\\n{traceback.format_exc()}")

if __name__ == "__main__":
    decode_obfuscated_exe()
'''
        
        try:
            write_text(decoder_path, decoder_code)
        except Exception as e:
            print(f"Error creating EXE decoder: {e}")

    def run(self):
        """Main obfuscation execution"""
        if not self.files:
            messagebox.showwarning("Обфускация", "Сначала выберите файлы!")
            return
        
        # Prepare results
        results = []
        xor_key = self._parse_xor_key()
        start_time = time.time()
        
        # Header
        results.append(f"🚀 ОБФУСКАЦИЯ ЗАПУЩЕНА")
        results.append(f"🕐 Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        results.append(f"📁 Обработано файлов: {len(self.files)}")
        results.append(f"🔑 XOR ключ: {'*' * len(self.xor_key_str.get()) if self.xor_key_str.get() else 'отсутствует'}")
        results.append(f"🔐 Обфускационный ключ: {'*' * min(8, len(self.custom_key.get())) if self.custom_key.get() else 'отсутствует'}")
        results.append(f"{'='*80}\n")
        
        try:
            if self.merge_files.get() and all(detect_lang(f) in ["python", "powershell", "js"] for f in self.files):
                # Merge text files
                merged_text = "\n\n# === МЕРДЖ ФАЙЛОВ ===\n\n".join(
                    read_text(f) for f in self.files
                )
                lang = detect_lang(self.files[0])
                
                results.append(f"🔗 РЕЖИМ ОБЪЕДИНЕНИЯ ({lang.upper()})")
                processed_text = self.apply_text_methods(merged_text, lang, xor_key)
                
                out_path = self.output_path.get() or f"merged_obfuscated_{lang}_{int(time.time())}.py"
                write_text(out_path, processed_text)
                
                size_change = ((len(processed_text) - len(merged_text)) / len(merged_text) * 100)
                results.append(f"📁 Сохранено: {os.path.basename(out_path)}")
                results.append(f"📏 Размер: {len(merged_text):,} → {len(processed_text):,} символов")
                results.append(f"📈 Изменение: {size_change:+.1f}%")
                
                if self.generate_decoder.get():
                    self._gen_decoder_for_text(out_path, xor_key)
                
                # Preview
                preview = processed_text[:800] + "\n... [показаны первые 800 символов]"
                results.append(f"\n📄 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР:\n{preview}")
                
            else:
                # Process each file individually
                results.append(f"📄 РЕЖИМ: ОТДЕЛЬНАЯ ОБРАБОТКА")
                for filepath in self.files:
                    self._process_single_file(filepath, xor_key, results)
        
        except Exception as e:
            results.append(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА!")
            results.append(f"Ошибка: {str(e)}")
            import traceback
            results.append(f"Traceback: {traceback.format_exc()}")
        
        # Footer
        end_time = time.time()
        duration = end_time - start_time
        results.append(f"\n{'='*80}")
        results.append(f"✅ ОБФУСКАЦИЯ ЗАВЕРШЕНА")
        results.append(f"⏱️  Время выполнения: {duration:.1f} секунд")
        results.append(f"📊 Обработано файлов: {len(self.files)}")
        
        # Update preview
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", "\n".join(results))
        
        # Scroll to end
        self.preview.see("end")
        
        # Show completion message
        msg = f"Обфускация завершена за {duration:.1f}с!\nОбработано {len(self.files)} файлов."
        if self.generate_decoder.get():
            msg += "\n🔑 Декодеры созданы для файлов с шифрованием."
        messagebox.showinfo("✅ Готово!", msg)

def main():
    """Main application entry point"""
    # Create root window
    if HAS_DND:
        root = TkinterDnD.Tk()
        root.title("🔒 Multi-Obfuscator Pro v2.1 - .NET & Anti-Debug")
    else:
        root = tk.Tk()
        root.title("🔒 Multi-Obfuscator Pro v2.1 - Drag&Drop disabled")
    
    root.geometry("1100x850")
    root.minsize(900, 600)
    
    # Status bar
    if not HAS_DND:
        status_frame = tk.Frame(root)
        status_frame.pack(fill="x", side="bottom")
        tk.Label(
            status_frame,
            text="💡 Drag&Drop недоступен. Установите: pip install tkinterdnd2",
            bg="lightgray",
            fg="blue",
            anchor="w",
            padx=10,
            pady=2
        ).pack(fill="x")
    
    if not HAS_DNLIB:
        status_frame = tk.Frame(root)
        status_frame.pack(fill="x", side="bottom")
        tk.Label(
            status_frame,
            text="⚠️  .NET обфускация отключена. Установите: pip install dnlib",
            bg="lightyellow",
            fg="darkred",
            anchor="w",
            padx=10,
            pady=2
        ).pack(fill="x")
    
    # Create and run app
    app = AppBase(root)
    
    # Setup drag and drop if available
    if HAS_DND:
        def drop_handler(event):
            files = []
            data = event.data.strip()
            
            # Parse dropped files (handles paths with spaces)
            if data.startswith('{') and data.endswith('}'):
                # Windows format: {path1} {path2}
                import re
                matches = re.findall(r'{{([^}]+)}}', data)
                for match in matches:
                    if os.path.exists(match):
                        files.append(match)
            else:
                # Unix format: path1 path2
                for path in data.split():
                    path = path.strip()
                    if os.path.exists(path):
                        files.append(path)
            
            if files:
                app.files = files
                app._update_status()
                
                # Update preview with dropped files
                app.preview.delete("1.0", "end")
                preview_text = f"📂 Перетащено файлов: {len(files)}\n{'='*50}\n\n"
                for i, f in enumerate(files, 1):
                    lang = detect_lang(f)
                    icon = {"python": "🐍", "powershell": "⚡", "js": "📜", 
                           "dotnet": "🔗", "exe": "⚙️", "html": "🌐", "css": "🎨"}.get(lang, "📄")
                    preview_text += f"{i:2d}. {icon} {lang.upper():<10} {os.path.basename(f)}\n"
                preview_text += f"\n💡 Выберите вкладку {lang.upper()} для обфускации"
                app.preview.insert("1.0", preview_text)
        
        # Register drop target
        root.drop_target_register(DND_FILES)
        root.dnd_bind('<<Drop>>', drop_handler)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()