#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日文化播客核心生成器
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import edge_tts

# 导入内容数据库
from culture_database import get_daily_content


class CulturePodcastCore:
    """文化播客核心生成器"""
    
    def __init__(self, config_path: str = "config_culture.yaml"):
        self.config = self.load_config(config_path)
        self.setup_directories()
        
    def load_config(self, config_path: str) -> Dict:
        """加载配置"""
        import yaml
        
        default_config = {
            "directories": {
                "podcast_output": "culture_podcast/audio",
                "metadata_output": "culture_podcast/metadata",
                "scripts_output": "culture_podcast/scripts",
                "videos_output": "weixin_videos",
                "assets_dir": "video_assets"
            },
            "audio": {
                "default_voice": "zh-CN-XiaoxiaoNeural",
                "speech_rate": "+5%",
                "output_format": "mp3"
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # 深度合并配置
                        import copy
                        config = copy.deepcopy(default_config)
                        
                        def deep_update(target, source):
                            for key, value in source.items():
                                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                                    deep_update(target[key], value)
                                else:
                                    target[key] = value
                        
                        deep_update(config, user_config)
                        return config
            except Exception as e:
                print(f"⚠️  配置文件读取失败，使用默认配置: {e}")
        
        return default_config
    
    def setup_directories(self):
        """设置目录"""
        dirs = self.config["directories"]
        for dir_path in dirs.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def create_script(self, content_data: Dict) -> str:
        """创建播客脚本"""
        
        today = datetime.now()
        date_str = today.strftime("%Y年%m月%d日")
        
        # 星期转换
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday_str = weekdays[today.weekday()]
        
        theme_cn = content_data["theme_cn"]
        content = content_data["content"]
        
        # 构建完整脚本
        script = f"""
【开场音乐，渐弱】
        
各位听众，大家好。
欢迎收听《每日文化》，我是您的文化向导。
今天是{date_str}，{weekday_str}。

今天，我们将一起探索{theme_cn}的世界。
准备好了吗？让我们开始今天的精神之旅。

【主题音乐，3秒】

今天要和大家分享的是：{content['title']}

{content['content']}

【过渡音乐，3秒】

以上就是今天的文化分享。
内容关键词包括：{'、'.join(content['keywords'][:3])}。

文化如光，照亮心灵；
艺术似水，滋养生命。

每天一点文化知识，让生活更有深度。
感谢您的收听，我们明天同一时间，继续文化之旅。
再见。

【结束音乐，渐强，10秒后结束】
"""
        
        # 清理多余空白
        import re
        script = re.sub(r'\n\s+', '\n', script)
        script = re.sub(r'\n{3,}', '\n\n', script)
        
        return script.strip()
    
    async def generate_audio(self, script: str, output_path: str) -> bool:
        """生成音频文件"""
        try:
            voice = self.config["audio"]["default_voice"]
            rate = self.config["audio"]["speech_rate"]
            
            communicate = edge_tts.Communicate(
                text=script,
                voice=voice,
                rate=rate,
                volume="+2dB"
            )
            
            await communicate.save(output_path)
            return True
            
        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return False
    
    def save_metadata(self, metadata: Dict, content_data: Dict, script: str, audio_path: str):
        """保存元数据"""
        
        output_dir = self.config["directories"]["metadata_output"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        theme = content_data["theme"]
        
        metadata_file = f"culture_{theme}_{timestamp}.json"
        metadata_path = os.path.join(output_dir, metadata_file)
        
        full_metadata = {
            **metadata,
            "theme": content_data["theme"],
            "theme_cn": content_data["theme_cn"],
            "title": content_data["content"]["title"],
            "content_preview": content_data["content"]["content"][:200] + "...",
            "keywords": content_data["content"]["keywords"],
            "script_preview": script[:500] + "..." if len(script) > 500 else script,
            "audio_file": os.path.basename(audio_path),
            "audio_path": audio_path,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, ensure_ascii=False, indent=2)
        
        return metadata_path
    
    def save_script(self, script: str, theme: str):
        """保存完整脚本"""
        scripts_dir = self.config["directories"]["scripts_output"]
        timestamp = datetime.now().strftime("%Y%m%d")
        
        script_file = f"script_{theme}_{timestamp}.txt"
        script_path = os.path.join(scripts_dir, script_file)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return script_path
    
    def generate(self, theme: Optional[str] = None) -> Optional[Dict]:
        """生成每日文化播客"""
        
        print("=" * 60)
        print("🎨 每日文化播客生成系统")
        print("=" * 60)
        
        # 1. 获取今日内容
        print("📚 获取今日文化内容...")
        content_data = get_daily_content(theme)
        
        print(f"✅ 主题: {content_data['theme_cn']}")
        print(f"📖 标题: {content_data['content']['title']}")
        
        # 2. 创建脚本
        print("📝 创建播客脚本...")
        script = self.create_script(content_data)
        print(f"📄 脚本长度: {len(script)} 字符")
        
        # 3. 保存脚本
        script_path = self.save_script(script, content_data["theme"])
        print(f"💾 脚本已保存: {script_path}")
        
        # 4. 生成音频
        print("🔊 生成音频文件...")
        
        audio_dir = self.config["directories"]["podcast_output"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = f"culture_{content_data['theme']}_{timestamp}.mp3"
        audio_path = os.path.join(audio_dir, audio_file)
        
        # 异步生成音频
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.generate_audio(script, audio_path))
            loop.close()
            
            if not success:
                print("❌ 音频生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 音频生成异常: {e}")
            return None
        
        # 5. 检查音频文件
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            print("❌ 音频文件未生成")
            return None
        
        file_size_mb = os.path.getsize(audio_path) / 1024 / 1024
        print(f"✅ 音频生成成功: {audio_file} ({file_size_mb:.1f}MB)")
        
        # 6. 保存元数据
        print("📋 保存元数据...")
        metadata = {
            "audio_size_mb": file_size_mb,
            "script_length": len(script),
            "estimated_duration_minutes": content_data["content"]["duration"],
            "difficulty": content_data["content"]["difficulty"]
        }
        
        metadata_path = self.save_metadata(metadata, content_data, script, audio_path)
        print(f"💾 元数据已保存: {metadata_path}")
        
        # 7. 输出结果
        print("\n" + "=" * 60)
        print("✅ 文化播客生成成功！")
        print("=" * 60)
        print(f"🎭 主题: {content_data['theme_cn']}")
        print(f"📖 标题: {content_data['content']['title']}")
        print(f"🎵 音频: {audio_file}")
        print(f"📦 大小: {file_size_mb:.1f} MB")
        print(f"⏱️  时长: 约 {content_data['content']['duration']} 分钟")
        print(f"🏷️  关键词: {', '.join(content_data['content']['keywords'][:3])}")
        print(f"📁 位置: {audio_path}")
        print("=" * 60)
        
        return {
            "success": True,
            "theme": content_data["theme"],
            "theme_cn": content_data["theme_cn"],
            "title": content_data["content"]["title"],
            "audio_path": audio_path,
            "metadata_path": metadata_path,
            "script_path": script_path,
            "file_size_mb": file_size_mb
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成每日文化播客')
    parser.add_argument('--theme', help='指定主题: art, history, literature, music, film, museum')
    parser.add_argument('--test', action='store_true', help='测试模式，不生成音频')
    
    args = parser.parse_args()
    
    # 验证主题参数
    valid_themes = ["art", "history", "literature", "music", "film", "museum"]
    if args.theme and args.theme not in valid_themes:
        print(f"❌ 无效主题，可选: {', '.join(valid_themes)}")
        sys.exit(1)
    
    if args.test:
        print("🧪 测试模式...")
        content = get_daily_content(args.theme)
        print(f"主题: {content['theme_cn']}")
        print(f"标题: {content['content']['title']}")
        print(f"内容预览:\n{content['content']['content'][:300]}...")
        return
    
    # 正常生成
    generator = CulturePodcastCore()
    result = generator.generate(args.theme)
    
    if result:
        print("\n🎉 播客生成完成！")
        print(f"🎧 收听地址: {result['audio_path']}")
        sys.exit(0)
    else:
        print("\n❌ 播客生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
