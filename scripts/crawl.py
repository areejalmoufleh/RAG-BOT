import os
import re
import requests
from bs4 import BeautifulSoup

URLS_FILE = "urls.txt"

if os.path.exists(URLS_FILE):
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
else:
    urls = [
        "https://mostaql.com/projects?category=ai-machine-learning&sort=latest",
        "https://mostaql.com/projects?category=development&sort=latest",
    ]

output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)

def fetch_and_clean(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

for url in urls:
    try:
        content = fetch_and_clean(url)
        # تنظيف الرابط ليكون اسماً آمناً للملف
        safe_name = re.sub(r'[\\/*?:"<>|&=]', '_', url)   # استبدال الرموز الممنوعة بـ _
        filename = safe_name.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_") + ".txt"
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {url} -> {filename}")
    except Exception as e:
        print(f"❌ فشل {url}: {e}")

print("تم جمع المحتوى.")