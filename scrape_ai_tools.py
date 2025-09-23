#!/usr/bin/env python3
"""
AI工具推荐抓取脚本 - 最新版本
专门为环境科学、GIS和数据分析背景的学生定制的工具推荐
"""

import requests
import json
import datetime
import time
import random
import os

class AIToolsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        })
        self.tools_data = []

    def scrape_github_environmental_projects(self):
        """抓取GitHub环境科学相关热门项目"""
        try:
            # 搜索环境科学相关的热门项目
            keywords = ['environmental-data', 'climate-analysis', 'gis-tools', 'earth-observation']

            for keyword in keywords[:2]:  # 限制API调用
                url = "https://api.github.com/search/repositories"
                params = {
                    'q': f'{keyword} language:python stars:>100',
                    'sort': 'updated',
                    'per_page': 2
                }

                try:
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()

                        for repo in data.get('items', [])[:1]:
                            if repo.get('description'):
                                self.tools_data.append({
                                    'name': repo['name'],
                                    'summary': self.truncate_text(repo['description'], 80),
                                    'usefulness': f"这个{keyword}相关的Python项目特别适用于环境数据分析和地理空间处理任务。对于环境科学学生来说，它提供了实际的工具和方法来处理复杂的环境数据集。",
                                    'technical': f"基于Python开发，在GitHub上有{repo['stargazers_count']}个星标。可通过pip安装，与pandas、numpy、matplotlib等科学计算库无缝集成。支持Jupyter Notebook环境。",
                                    'category': 'programming',
                                    'difficulty': '中级',
                                    'link': repo['html_url'],
                                    'stars': repo['stargazers_count']
                                })

                    time.sleep(1)  # API调用间隔

                except Exception as api_error:
                    print(f"GitHub API error for {keyword}: {api_error}")

            print(f"GitHub projects: 收集 {len([t for t in self.tools_data if 'github.com' in t.get('link', '')])} 个热门项目")

        except Exception as e:
            print(f"GitHub scraping error: {e}")

    def truncate_text(self, text, max_length):
        """截断文本到指定长度"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def add_essential_gis_tools(self):
        """添加核心GIS和环境科学工具"""
        essential_tools = [
            {
                'name': 'QGIS',
                'summary': '世界领先的开源地理信息系统，支持全方位空间数据分析',
                'usefulness': '对环境科学学生来说是必备技能。QGIS完全免费，功能媲美昂贵的ArcGIS。支持200+种数据格式，从简单地图制作到复杂空间分析都能胜任。学会QGIS后可轻松转换到任何GIS平台，是求职和学术研究的重要加分项。',
                'technical': '基于C++和Qt框架，跨平台支持Windows/Mac/Linux。内置Python控制台支持自动化脚本，拥有500+插件扩展功能。支持OGC标准，可与R、Python、PostGIS无缝集成进行高级分析。',
                'category': 'GIS',
                'difficulty': '初级',
                'link': 'https://qgis.org/',
                'stars': 'N/A'
            },
            {
                'name': 'Google Earth Engine',
                'summary': '谷歌云端行星级地理空间分析平台，集成PB级卫星数据',
                'usefulness': '革命性的云端GIS平台，无需下载TB级数据即可进行全球分析。特别适用于气候变化监测、森林砍伐追踪、城市扩张研究、农业监测等大尺度环境研究。对发表高影响因子环境科学论文极其有用。',
                'technical': '通过JavaScript和Python API访问，集成Landsat、Sentinel、MODIS、CHIRPS等几十个权威数据集。计算在Google云端进行，支持机器学习算法。提供交互式代码编辑器，可导出高分辨率结果。',
                'category': 'GIS',
                'difficulty': '中级',
                'link': 'https://earthengine.google.com/',
                'stars': 'N/A'
            },
            {
                'name': 'Python地理空间生态系统',
                'summary': 'GeoPandas + Rasterio + Folium + Cartopy完整工具链',
                'usefulness': 'Python在环境数据科学中地位无可替代。GeoPandas让空间数据处理如Excel般简单，Folium创建交互式Web地图，Rasterio处理卫星影像，Cartopy制作科学地图。覆盖从数据获取到可视化的完整流程。',
                'technical': '核心库包括GeoPandas(空间DataFrame)、Rasterio(栅格I/O)、Shapely(几何运算)、Folium(交互地图)、Cartopy(地图投影)、PyProj(坐标转换)。与Jupyter、Pandas、NumPy、Matplotlib完美集成。',
                'category': '编程',
                'difficulty': '中级',
                'link': 'https://geopandas.org/',
                'stars': 'N/A'
            },
            {
                'name': 'R Spatial生态系统',
                'summary': 'sf + terra + tmap + rgee等R语言空间分析包',
                'usefulness': 'R在统计生态学和环境建模中优势显著。sf包提供现代空间数据处理，terra处理大型栅格，tmap创建出版级地图，rgee连接Google Earth Engine。特别适合物种分布建模、生态统计、环境监测分析。',
                'technical': '基于sf标准的现代空间框架，与tidyverse生态无缝集成。支持复杂统计模型如GAM、混合效应模型。通过rgee直接访问Google Earth Engine，实现R与云端GIS结合。拥有3000+专业包。',
                'category': '编程',
                'difficulty': '中高级',
                'link': 'https://r-spatial.github.io/sf/',
                'stars': 'N/A'
            },
            {
                'name': 'GRASS GIS',
                'summary': '功能强大的开源GIS和遥感分析系统',
                'usefulness': '特别擅长栅格数据分析和地形建模，是科学研究的利器。内置500+分析工具，支持高级水文建模、景观生态学分析、遥感图像处理。在学术界享有很高声誉，很多算法的标准实现。',
                'technical': '用C语言开发，执行效率极高。可通过Python、R接口调用。支持并行处理大数据集。拥有30年持续开发历史，算法经过充分验证。可与QGIS集成使用。',
                'category': 'GIS',
                'difficulty': '高级',
                'link': 'https://grass.osgeo.org/',
                'stars': 'N/A'
            }
        ]

        # 随机选择3-4个工具以保持新鲜感
        selected_tools = random.sample(essential_tools, min(4, len(essential_tools)))
        self.tools_data.extend(selected_tools)
        print(f"Essential tools: 添加 {len(selected_tools)} 个核心工具")

    def scrape_all_sources(self):
        """执行所有收集任务"""
        print("🤖 开始收集AI工具推荐...")

        # 先添加核心工具
        self.add_essential_gis_tools()

        # 尝试获取GitHub热门项目
        self.scrape_github_environmental_projects()

        # 随机排序保持新鲜感
        random.shuffle(self.tools_data)

        print(f"✅ 成功收集 {len(self.tools_data)} 个工具推荐")
        return self.tools_data

    def save_to_json(self, filename="data/ai_tools.json"):
        """保存数据到JSON文件"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.datetime.now().isoformat(),
                'tools': self.tools_data
            }, f, ensure_ascii=False, indent=2)

        print(f"📁 数据已保存到 {filename}")

if __name__ == "__main__":
    scraper = AIToolsScraper()
    scraper.scrape_all_sources()
    scraper.save_to_json()
