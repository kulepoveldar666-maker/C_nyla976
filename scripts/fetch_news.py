import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

RSS_URL = "https://www.ithome.com/rss/"

KEYWORDS = {
    "android": ["安卓", "Android", "Pixel", "三星", "小米", "华为", "荣耀", "OPPO", "vivo", "一加"],
    "apple": ["苹果", "iPhone", "iPad", "Mac", "Apple", "iOS", "macOS", "AirPods"],
    "windows": ["Windows", "微软", "Microsoft", "Win11", "Win10", "Surface"],
}

def fetch_rss():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(RSS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        description = item.findtext("description") or ""
        pub_date = item.findtext("pubDate") or ""
        
        img_match = re.search(r'<img[^>]+src="([^"]+)"', description)
        image = img_match.group(1) if img_match else "Картинка не найдена в RSS"
        
        clean_desc = re.sub(r"<[^>]+>", "", description).strip()[:200]
        
        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "description": clean_desc,
            "image": image,
            "pub_date": pub_date,
        })
    return items

def filter_news(items, category, limit=1):
    kws = KEYWORDS.get(category, [])
    matched = []
    for it in items:
        text = (it["title"] + " " + it["description"]).lower()
        if any(k.lower() in text for k in kws):
            matched.append(it)
        if len(matched) >= limit:
            break
    return matched

def main():
    # Время по UTC (МСК минус 3 часа). 
    # 08:00 МСК = 05:00 UTC (Android)
    # 11:00 МСК = 08:00 UTC (Apple)
    # 14:00 МСК = 11:00 UTC (Windows)
    # 17:00 МСК = 14:00 UTC (Android)
    # 19:00 МСК = 16:00 UTC (Apple)
    
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    
    category, limit = "android", 1

    print(f"=== Пост для категории: {category.upper()} ===")
    items = fetch_rss()
    selected = filter_news(items, category, limit)
    
    if not selected:
        print(f"Свежих новостей по теме {category} в RSS не найдено.")
        return

    for it in selected:
        print("-" * 40)
        print(f"Заголовок: {it['title']}")
        print(f"Кратко: {it['description']}...")
        print(f"Ссылка на источник: {it['link']}")
        print(f"Ссылка на фото (отдельно): {it['image']}")
        print(f"Дата публикации: {it['pub_date']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
