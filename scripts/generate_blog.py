import os
import json
import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# 加载环境变量（本地测试用，Actions中用Secrets）
load_dotenv()

# 飞书API配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
FEISHU_TABLE_ID = os.getenv("FEISHU_TABLE_ID")

# 模板环境初始化
env = Environment(loader=FileSystemLoader("templates"))
index_template = env.get_template("index.html")
article_template = env.get_template("article.html")

# 创建docs目录（确保存在）
os.makedirs("docs", exist_ok=True)

def get_feishu_token():
    """获取飞书tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["tenant_access_token"]
    except Exception as e:
        raise Exception(f"获取飞书Token失败：{e}")

def get_blog_articles(token):
    """拉取飞书多维表格中已发布的文章"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"filter": 'CurrentValue["is_published"]="是"'}  # 筛选已发布的文章

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json()["data"]["items"]
        
        # 格式化文章数据
        articles = []
        for record in records:
            fields = record["fields"]
            # 处理日期格式（飞书返回的是时间戳，转成YYYY-MM-DD）
            publish_date = datetime.fromtimestamp(fields["publish_date"] / 1000).strftime("%Y-%m-%d")
            articles.append({
                "article_title": fields.get("article_title", ""),
                "article_slug": fields.get("article_slug", ""),
                "article_content": fields.get("article_content", ""),
                "publish_date": publish_date,
                "tags": fields.get("tags", [])
            })
        # 按发布日期倒序排序
        return sorted(articles, key=lambda x: x["publish_date"], reverse=True)
    except Exception as e:
        raise Exception(f"拉取文章数据失败：{e}")

def generate_static_pages(articles):
    """生成静态HTML页面"""
    # 生成首页
    index_html = index_template.render(articles=articles)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # 生成每篇文章的详情页
    for article in articles:
        if not article["article_slug"]:
            continue  # 跳过无slug的文章
        article_html = article_template.render(article=article)
        with open(f"docs/{article['article_slug']}.html", "w", encoding="utf-8") as f:
            f.write(article_html)

if __name__ == "__main__":
    try:
        token = get_feishu_token()
        articles = get_blog_articles(token)
        generate_static_pages(articles)
        print("静态页面生成成功！")
    except Exception as e:
        print(f"执行失败：{e}")
        exit(1)
