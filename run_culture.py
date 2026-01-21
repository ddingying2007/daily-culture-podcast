#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日文化播客一键启动脚本
"""

import os
import sys
from datetime import datetime


def main():
    """主函数"""
    
    print("=" * 70)
    print("🎨 每日文化播客系统")
    print("=" * 70)
    
    print("1. 生成今日文化播客")
    print("2. 生成视频号内容")
    print("3. 查看最新播客")
    print("4. 清理旧文件")
    print("5. 退出")
    
    choice = input("\n请选择操作 (1-5): ").strip()
    
    if choice == "1":
        print("\n" + "=" * 60)
        print("开始生成今日文化播客...")
        print("=" * 60)
        
        os.system("python culture_core.py")
        
    elif choice == "2":
        print("\n" + "=" * 60)
        print("开始生成视频号内容...")
        print("=" * 60)
        
        os.system("python simple_video.py --auto")
        
    elif choice == "3":
        print("\n" + "=" * 60)
        print("最新播客文件:")
        print("=" * 60)
        
        # 列出音频文件
        audio_dir = "culture_podcast/audio"
        if os.path.exists(audio_dir):
            files = sorted(os.listdir(audio_dir), reverse=True)
            for file in files[:5]:  # 显示最新的5个
                if file.endswith('.mp3'):
                    path = os.path.join(audio_dir, file)
                    size = os.path.getsize(path) / 1024 / 1024
                    print(f"🎵 {file} ({size:.1f}MB)")
        else:
            print("❌ 音频目录不存在")
        
        # 列出元数据
        metadata_dir = "culture_podcast/metadata"
        if os.path.exists(metadata_dir):
            print("\n📋 最新元数据:")
            files = sorted(os.listdir(metadata_dir), reverse=True)
            for file in files[:3]:
                if file.endswith('.json'):
                    print(f"📄 {file}")
        
    elif choice == "4":
        print("\n" + "=" * 60)
        print("清理旧文件...")
        print("=" * 60)
        
        import shutil
        import time
        
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30天前
        
        for dir_name in ["culture_podcast/audio", "weixin_videos"]:
            if os.path.exists(dir_name):
                print(f"\n清理 {dir_name}:")
                for file in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            print(f"🗑️  删除: {file}")
                        except:
                            pass
        
        print("\n✅ 清理完成")
        
    elif choice == "5":
        print("\n👋 再见！")
        sys.exit(0)
        
    else:
        print("\n❌ 无效选择")
    
    input("\n按Enter键返回主菜单...")
    main()  # 递归调用返回菜单


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
        sys.exit(0)
