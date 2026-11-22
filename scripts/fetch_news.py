import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from deep_translator import GoogleTranslator

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

def send_to_telegram(category, it):
    token = ("9049387111:AAER4XOSUxJin8jaOG1B8h4zUzhIH-81xGg") 
    chat_id = ("8064044934") 
    
    if not token or not chat_id:
        print("Ошибка: не заданы TELEGRAM_TOKEN или TELEGRAM_CHAT_ID")
        return

    try:
    time.sleep(2) 
    translator = GoogleTranslator(source='zh-CN', target='ru')
    title_ru = translator.translate(it['title'])
    time.sleep(1)
    desc_ru = translator.translate(it['description'])
except Exception as e:
        print(f"Ошибка перевода: {e}. Отправляем оригинал.")
        title_ru = it['title']
        desc_ru = it['description']

    emoji_map = {"android": "🤖", "apple": "🍎", "windows": "🪟"}
    cat_emoji = emoji_map.get(category, "📱")

    text = (
        f"{cat_emoji} **{category.upper()}**\n\n"
        f"🔥 **{title_ru}**\n\n"
        f"📝 {desc_ru}...\n\n"
        f"🔗 [Читать полностью]({it['link']})"
    )
    
    if it['image'] and "http" in it['image']:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": it['image'],
            "caption": text,
            "parse_mode": "Markdown"
        }
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Пост успешно отправлен в Telegram!")
    else:
        print(f"Ошибка отправки: {response.text}")

def main():
    tasks = [
        ("android", 2),
        ("apple", 2),
        ("windows", 1)
    ]
    
    print("=== Начинаем сбор всех постов ===")
    items = fetch_rss()
    
    for category, count in tasks:
        print(f"--- Ищем {count} новости для: {category.upper()} ---")
        selected = filter_news(items, category, count)
        
        if not selected:
            print(f"Свежих новостей по теме {category} не найдено.")
            continue
            
        for it in selected:
            print(f"Отправляем: {it['title']}")
            send_to_telegram(category, it)
            time.sleep(2)

if __name__ == "__main__":
    main()
