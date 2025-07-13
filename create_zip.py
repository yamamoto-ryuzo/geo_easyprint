#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QGIS Plugin ZIP Package Creator
Creates a distribution ZIP file for the geo_easyprint plugin
"""

import os
import zipfile
import shutil
import configparser
from pathlib import Path

def get_plugin_info_from_metadata():
    """Read plugin name and version from metadata.txt"""
    try:
        config = configparser.ConfigParser()
        config.read('metadata.txt', encoding='utf-8')
        name = config.get('general', 'name')
        version = config.get('general', 'version')
        return name, version
    except Exception as e:
        print(f"Warning: Could not read plugin info from metadata.txt: {e}")
        return "geo_easyprint", "3.0.0"  # fallback values

def create_plugin_zip():
    """Create ZIP package for QGIS plugin distribution"""
    
    # Read plugin info from metadata.txt
    plugin_name, plugin_version = get_plugin_info_from_metadata()
    ZIP_NAME = f"{plugin_name}_v{plugin_version}.zip"
    
    # Files to include in the ZIP
    FILES_TO_INCLUDE = [
        "__init__.py",
        "easyprint.py",
        "easyprintgui.py",
        "layout.py", 
        "decoration.py",
        "settings.py",
        "ui_control.py",
        "ui_control4.py",
        "Ui_easyprint.py",
        "Ui_easyprint.ui",
        "print_con.py",
        "print_ui.py",
        "print_ui.ui",
        "resources.py",
        "resources.qrc",
        "myToolBar.py",
        "SendKeys.py",
        "_sendkeys.py",
        "ui_test.py",
        "ui_test.ui",
        "ui_test4.py",
        "ui_test4.ui",
        "metadata.txt",
        "LICENSE",
        "README.md",
        "easyprint.png",
        "easyprint.pro",
        "changelog.md"
    ]
    
    # Directories to include
    DIRS_TO_INCLUDE = [
        "images",
        "layouts",
        "pictures",
        "preferences",
        "styles",
        "tools",
        "data"
    ]
    
    print(f"Creating plugin ZIP package: {ZIP_NAME}")
    
    # Remove existing ZIP file if it exists
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)
        print("Removed existing ZIP file")
    
    # Create ZIP file
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        print("Adding files to ZIP archive...")
        
        # Add individual files
        for file_name in FILES_TO_INCLUDE:
            if os.path.exists(file_name):
                arcname = f"{plugin_name}/{file_name}"
                zipf.write(file_name, arcname)
                print(f"✓ Added: {file_name}")
            else:
                print(f"✗ Not found: {file_name}")
        
        # Add directories
        for dir_name in DIRS_TO_INCLUDE:
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                for root, dirs, files in os.walk(dir_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = f"{plugin_name}/{file_path.replace(os.sep, '/')}"
                        zipf.write(file_path, arcname)
                        print(f"✓ Added: {file_path}")
            else:
                print(f"✗ Directory not found: {dir_name}")
    
    # Get file size and show results
    if os.path.exists(ZIP_NAME):
        file_size = os.path.getsize(ZIP_NAME)
        file_size_kb = round(file_size / 1024, 2)
        
        print(f"\n✓ Successfully created: {ZIP_NAME}")
        print(f"   File size: {file_size_kb} KB")
        print(f"   Full path: {os.path.abspath(ZIP_NAME)}")
        print("\nPlugin ZIP package created successfully!")
        print("Ready for distribution or upload to QGIS Plugin Repository")
        return True
    else:
        print("✗ Error: ZIP file was not created")
        return False

def list_zip_contents(zip_name):
    """List contents of the created ZIP file for verification"""
    if not os.path.exists(zip_name):
        print(f"ZIP file {zip_name} not found")
        return
    
    print(f"\nContents of {zip_name}:")
    print("-" * 50)
    
    with zipfile.ZipFile(zip_name, 'r') as zipf:
        for info in zipf.infolist():
            size_kb = round(info.file_size / 1024, 2) if info.file_size > 0 else 0
            print(f"{info.filename:<40} {size_kb:>8} KB")
    
    print("-" * 50)

if __name__ == "__main__":
    success = create_plugin_zip()
    
    if success:
        # Show ZIP contents for verification
        plugin_name, plugin_version = get_plugin_info_from_metadata()
        zip_name = f"{plugin_name}_v{plugin_version}.zip"
        list_zip_contents(zip_name)
    else:
        exit(1)
