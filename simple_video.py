#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易视频生成器 - 为视频号创建内容
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


class SimpleVideoGenerator:
    """简易视频生成器"""
    
    def __init__(self, output_dir: str = "weixin_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def check_ffmpeg(self):
        """检查ffmpeg是否可用"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ffmpeg未安装")
            print("💡 请安装: sudo apt install ffmpeg 或 brew install ffmpeg")
            return False
    
    def create_simple_video(self, audio_path: str, image_path: str = None):
        """创建简单视频"""
        
        if not self.check_ffmpeg():
            return None
        
        # 如果没提供图片，使用默认黑色背景
        if not image_path or not os.path.exists(image_path):
            # 创建简单背景图
            from PIL import Image
            bg_path = "background.jpg"
            img = Image.new('RGB', (1080, 1920), color=(30, 40, 60))
            img.save(bg_path, quality=90)
            image_path = bg_path
        
        # 输出视频路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"culture_video_{timestamp}.mp4"
        
        try:
            # 获取音频时长
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            
            # 限制最长60秒（视频号限制）
            if duration > 60:
                duration = 60
            
            # 创建视频（静态图片+音频）
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", image_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-t", str(duration),
                "-c:a", "aac",
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920",
                "-shortest",
                "-y",  # 覆盖输出
                str(output_path)
            ]
            
            print(f"🎬 正在生成视频...")
            subprocess.run(cmd, capture_output=True, check=True)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                size_mb = output_path.stat().st_size / 1024 / 1024
                print(f"✅ 视频生成成功: {output_path} ({size_mb:.1f}MB)")
                return output_path
            else:
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 视频生成失败: {e}")
            return None
    
    def create_from_latest_podcast(self):
        """从最新播客创建视频"""
        # 查找最新音频文件
        audio_dir = Path("culture_podcast/audio")
        if not audio_dir.exists():
            print("❌ 音频目录不存在")
            return None
        
        audio_files = list(audio_dir.glob("*.mp3"))
        if not audio_files:
            print("❌ 未找到音频文件")
            return None
        
        latest_audio = max(audio_files, key=lambda f: f.stat().st_mtime)
        
        print(f"🎵 使用最新音频: {latest_audio.name}")
        
        # 生成视频
        video_path = self.create_simple_video(str(latest_audio))
        
        return video_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成简易视频')
    parser.add_argument('--audio', help='音频文件路径')
    parser.add_argument('--image', help='背景图片路径')
    parser.add_argument('--auto', action='store_true', help='自动使用最新播客')
    
    args = parser.parse_args()
    
    generator = SimpleVideoGenerator()
    
    if args.auto:
        video_path = generator.create_from_latest_podcast()
    elif args.audio:
        video_path = generator.create_simple_video(args.audio, args.image)
    else:
        print("❌ 请提供音频文件或使用 --auto 参数")
        return
    
    if video_path:
        print(f"\n🎉 视频生成完成！")
        print(f"📱 可用于视频号发布: {video_path}")
    else:
        print("\n❌ 视频生成失败")


if __name__ == "__main__":
    main()
