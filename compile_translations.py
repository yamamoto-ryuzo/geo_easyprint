#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QGISプラグイン用の翻訳ファイル コンパイル スクリプト
"""

import subprocess
import sys
from pathlib import Path

def compile_translations():
    """翻訳ファイル(.ts)をコンパイル(.qm)する"""
    
    plugin_dir = Path(__file__).parent
    i18n_dir = plugin_dir / "i18n"
    
    if not i18n_dir.exists():
        print(f"i18n directory not found: {i18n_dir}")
        return False
    
    # .tsファイルを検索
    ts_files = list(i18n_dir.glob("*.ts"))
    
    if not ts_files:
        print("No .ts files found")
        return False
    
    success_count = 0
    
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"Compiling {ts_file.name} -> {qm_file.name}")
        
        try:
            # lreleaseコマンドを実行
            result = subprocess.run([
                'lrelease', str(ts_file), '-qm', str(qm_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Successfully compiled {ts_file.name}")
                success_count += 1
            else:
                print(f"✗ Error compiling {ts_file.name}: {result.stderr}")
                
        except FileNotFoundError:
            print("✗ lrelease command not found. Please install Qt development tools.")
            return False
    
    print(f"\nCompiled {success_count}/{len(ts_files)} files successfully")
    return success_count == len(ts_files)

if __name__ == "__main__":
    success = compile_translations()
    sys.exit(0 if success else 1)
