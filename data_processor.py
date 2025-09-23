#!/usr/bin/env python3
"""
数据处理和整合脚本 - 最新版本
整合所有抓取的数据，进行清洗、去重、优先级排序，生成最终的仪表盘数据
"""

import json
import datetime
import os
from pathlib import Path

class DashboardDataProcessor:
    def __init__(self):
        self.data_dir = Path("data")
        self.final_data = {
            'last_updated': datetime.datetime.now().isoformat(),
            'current_date': datetime.datetime.now().strftime('%Y年%m月%d日'),
            'environmental_news': [],
            'ai_tools': [],
            'opportunities': []
        }

    def load_json_file(self, filename):
        """安全加载JSON文件"""
        filepath = self.data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载 {filename} 时出错: {e}")
                return None
        else:
            print(f"📂 文件 {filename} 不存在")
            return None

    def process_environmental_news(self):
        """处理环境科学新闻数据"""
        news_data = self.load_json_file("environmental_news.json")
        if news_data and 'news' in news_data:
            news_items = news_data['news']

            # 按紧急程度和时效性排序
            def sort_key(item):
                urgency_priority = {'high': 0, 'medium': 1, 'low': 2}
                category_priority = {'climate': 0, 'academic': 1, 'policy': 2}
                return (
                    urgency_priority.get(item.get('urgency', 'medium'), 1),
                    category_priority.get(item.get('category', 'academic'), 1),
                    item.get('date', ''),
                    item.get('title', '')
                )

            news_items.sort(key=sort_key, reverse=True)

            # 限制数量并确保内容质量
            processed_news = []
            for item in news_items[:6]:  # 最多6条新闻
                if item.get('title') and len(item['title']) > 10:
                    processed_news.append(item)

            self.final_data['environmental_news'] = processed_news
            print(f"📰 处理了 {len(processed_news)} 条环境科学新闻")
        else:
            print("⚠️  未找到环境新闻数据，使用备用内容")
            self.add_fallback_news()

    def add_fallback_news(self):
        """添加备用新闻内容"""
        fallback_news = [
            {
                'title': '环境科学数据收集完成',
                'description': '系统已成功初始化，开始收集最新的环境科学动态。请等待下次自动更新以获取实时新闻内容。',
                'source': '系统通知',
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'category': 'system',
                'urgency': 'medium',
                'link': '#'
            }
        ]
        self.final_data['environmental_news'] = fallback_news

    def process_ai_tools(self):
        """处理AI工具推荐数据"""
        tools_data = self.load_json_file("ai_tools.json")
        if tools_data and 'tools' in tools_data:
            tools_items = tools_data['tools']

            # 按类别和实用性排序
            def sort_key(item):
                category_priority = {'GIS': 0, '编程': 1, 'programming': 1, '配置': 2}
                difficulty_priority = {'初级': 0, '中级': 1, '中高级': 2, '高级': 3}
                return (
                    category_priority.get(item.get('category', 'programming'), 1),
                    difficulty_priority.get(item.get('difficulty', '中级'), 1),
                    item.get('name', '')
                )

            tools_items.sort(key=sort_key)

            # 确保工具多样性
            processed_tools = []
            categories_seen = set()

            for item in tools_items:
                if len(processed_tools) >= 5:  # 最多5个工具
                    break

                category = item.get('category', 'other')
                if len(processed_tools) < 3 or category not in categories_seen:
                    processed_tools.append(item)
                    categories_seen.add(category)

            self.final_data['ai_tools'] = processed_tools
            print(f"🤖 处理了 {len(processed_tools)} 个AI工具推荐")
        else:
            print("⚠️  未找到工具数据，使用备用内容")
            self.add_fallback_tools()

    def add_fallback_tools(self):
        """添加备用工具内容"""
        fallback_tools = [
            {
                'name': '工具推荐系统初始化',
                'summary': '正在收集最新的AI和GIS工具推荐',
                'usefulness': '系统正在为您收集最适合环境科学学习和研究的工具推荐。',
                'technical': '下次更新将包含QGIS、Google Earth Engine、Python工具等推荐。',
                'category': '系统',
                'difficulty': '无',
                'link': '#'
            }
        ]
        self.final_data['ai_tools'] = fallback_tools

    def process_opportunities(self):
        """处理实践机会数据"""
        opp_data = self.load_json_file("opportunities.json")
        if opp_data and 'opportunities' in opp_data:
            opp_items = opp_data['opportunities']

            # 按类型和地理位置优先级排序
            def sort_key(item):
                type_priority = {'志愿者': 0, '兼职研究': 1, '全职就业': 2, '配置提示': 3}
                location_priority = 0 if 'ACT' in item.get('location', '') else 1
                return (
                    type_priority.get(item.get('type', '其他'), 2),
                    location_priority,
                    item.get('title', '')
                )

            opp_items.sort(key=sort_key)

            # 确保机会类型多样性
            processed_opportunities = []
            types_seen = set()

            for item in opp_items:
                if len(processed_opportunities) >= 6:  # 最多6个机会
                    break

                opp_type = item.get('type', 'other')
                if len(processed_opportunities) < 3 or opp_type not in types_seen:
                    processed_opportunities.append(item)
                    types_seen.add(opp_type)

            self.final_data['opportunities'] = processed_opportunities
            print(f"💼 处理了 {len(processed_opportunities)} 个实践机会")
        else:
            print("⚠️  未找到机会数据，使用备用内容")
            self.add_fallback_opportunities()

    def add_fallback_opportunities(self):
        """添加备用机会内容"""
        fallback_opportunities = [
            {
                'title': '实践机会收集中',
                'description': '系统正在收集堪培拉地区最新的环境相关志愿者和就业机会。',
                'organization': '系统通知',
                'location': '堪培拉ACT',
                'type': '系统消息',
                'commitment': '请等待更新',
                'skills': '无需特殊技能',
                'contact': '系统自动更新',
                'link': '#'
            }
        ]
        self.final_data['opportunities'] = fallback_opportunities

    def add_metadata(self):
        """添加元数据和统计信息"""
        total_items = (
            len(self.final_data['environmental_news']) + 
            len(self.final_data['ai_tools']) + 
            len(self.final_data['opportunities'])
        )

        current_time = datetime.datetime.now()
        next_update = current_time + datetime.timedelta(days=1)

        self.final_data['metadata'] = {
            'total_items': total_items,
            'last_processing_time': current_time.strftime('%Y-%m-%d %H:%M:%S AEST'),
            'next_update': next_update.strftime('%Y-%m-%d %H:%M:%S AEST'),
            'data_sources': [
                'ANU Fenner School',
                'Australian Climate Council', 
                'GitHub Trending',
                'ACT Government',
                'Conservation Organizations',
                'Environmental Consulting Firms'
            ],
            'categories': {
                'news': len(self.final_data['environmental_news']),
                'tools': len(self.final_data['ai_tools']),
                'opportunities': len(self.final_data['opportunities'])
            }
        }

    def process_all_data(self):
        """执行完整的数据处理流程"""
        print("📊 开始数据处理和整合...")

        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)

        # 处理各类数据
        self.process_environmental_news()
        self.process_ai_tools()
        self.process_opportunities()
        self.add_metadata()

        # 保存最终整合数据
        output_file = self.data_dir / "dashboard_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.final_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 数据处理完成！最终数据保存到 {output_file}")
        print(f"📈 总共处理了 {self.final_data['metadata']['total_items']} 条记录")
        print(f"   📰 新闻: {self.final_data['metadata']['categories']['news']} 条")
        print(f"   🤖 工具: {self.final_data['metadata']['categories']['tools']} 个")
        print(f"   💼 机会: {self.final_data['metadata']['categories']['opportunities']} 个")

        return self.final_data

    def generate_summary_report(self):
        """生成数据摘要报告"""
        report_file = self.data_dir / "daily_summary.md"

        current_date = datetime.datetime.now().strftime('%Y年%m月%d日')

        report_content = f"""# 环境科学每日摘要报告

**生成时间**: {current_date} {datetime.datetime.now().strftime('%H:%M AEST')}

## 📊 数据统计
- 环境科学新闻: {len(self.final_data['environmental_news'])} 条
- AI工具推荐: {len(self.final_data['ai_tools'])} 个  
- 实践机会: {len(self.final_data['opportunities'])} 个
- 总计: {self.final_data['metadata']['total_items']} 条记录

## 🌳 今日环境科学亮点
"""

        for i, news in enumerate(self.final_data['environmental_news'][:3], 1):
            report_content += f"""
### {i}. {news['title']}
- **来源**: {news['source']}
- **类别**: {news['category']} 
- **紧急程度**: {news['urgency']}
- **摘要**: {news['description'][:150]}...
- **链接**: {news['link']}
"""

        report_content += f"""

## 🚀 推荐工具亮点
"""

        for i, tool in enumerate(self.final_data['ai_tools'][:2], 1):
            report_content += f"""
### {i}. {tool['name']} ({tool['category']} - {tool['difficulty']})
- **功能**: {tool['summary']}
- **实用性**: {tool['usefulness'][:200]}...
- **链接**: {tool['link']}
"""

        report_content += f"""

## 💼 热门实践机会
"""

        for i, opp in enumerate(self.final_data['opportunities'][:2], 1):
            report_content += f"""
### {i}. {opp['title']} ({opp['type']})
- **机构**: {opp['organization']}
- **地点**: {opp['location']}
- **承诺**: {opp['commitment']}
- **联系**: {opp['contact']}
"""

        report_content += f"""

---
*本报告由自动化系统生成 | 下次更新: {self.final_data['metadata']['next_update']}*
*数据来源: {', '.join(self.final_data['metadata']['data_sources'])}*
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📋 每日摘要报告已生成: {report_file}")

if __name__ == "__main__":
    processor = DashboardDataProcessor()
    processor.process_all_data()
    processor.generate_summary_report()
