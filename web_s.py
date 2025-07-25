import yt_dlp
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time, requests, os

# Load creds
load_dotenv(dotenv_path="C:/Users/princ/Desktop/complete python programing/web_scrapping/store.env")
EMAIL = os.getenv("YOUTUBE_EMAIL")
PASSWORD = os.getenv("YOUTUBE_PASSWORD")


def login_youtube(driver):
    print("🔐 Logging into YouTube...")
    driver.get("https://accounts.google.com/signin/v2/identifier?service=youtube")
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "identifierId"))).send_keys(EMAIL, Keys.ENTER)
    time.sleep(3)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "Passwd"))).send_keys(PASSWORD, Keys.ENTER)
    time.sleep(5)

    print("✅ Logged in.")

def enable_dark_mode(driver):
    print("🌚 Enabling Dark Mode...")
    driver.get("https://www.youtube.com")
    time.sleep(5)

    driver.get("https://www.youtube.com/account")
    time.sleep(2)

    driver.get("https://www.youtube.com/account_advanced")
    time.sleep(1)

    driver.execute_script("""
        document.cookie = "PREF=f6=400; domain=.youtube.com; path=/";
        location.reload();
    """)
    time.sleep(2)
    print("✅ Dark mode should be active now.")

def download_thumbnail(url, save_path):
    try:
        thumb_data = requests.get(url).content
        with open(save_path, "wb") as f:
            f.write(thumb_data)
        print(f"🖼️ Thumbnail saved to {save_path}")
    except Exception as e:
        print(f"❌ Error downloading thumbnail: {e}")

def scrape_all_comments(driver, max_scrolls=30):
    print("🌀 Scrolling to load all comments...")
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#content-text')))
    comment_elements = driver.find_elements(By.CSS_SELECTOR, '#content-text')
    return [elem.text for elem in comment_elements if elem.text.strip()]

def scrape_youtube_all(video_url):
    print("🎬 Extracting metadata with yt-dlp...")
    ydl_opts = {'quiet': True, 'skip_download': True, 'forcejson': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        # info = ydl.extract_info(login_youtube)
    video_data = {
        'title': info.get('title'),
        'uploader': info.get('uploader'),
        'upload_date': info.get('upload_date'),
        'duration': info.get('duration'),
        'views': info.get('view_count'),
        'likes': info.get('like_count'),
        'description': info.get('description'),
        'thumbnail': info.get('thumbnail'),
        'formats': info.get('formats'),
        'audio_formats': [f for f in info['formats'] if f['vcodec'] == 'none']
    }

    thumb_path = "youtube_thumbnail.jpg"
    download_thumbnail(video_data['thumbnail'], thumb_path)

    print("🧠 Launching browser with stealth mode...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options)
    login_youtube(driver)
    enable_dark_mode(driver)

    print("📺 Opening video page...")
    driver.get(video_url)
    time.sleep(5)

    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1.title').text
    except:
        title = video_data['title']

    try:
        views = driver.find_element(By.CSS_SELECTOR, 'span.view-count').text
    except:
        views = f"{video_data['views']} views"

    try:
        uploader = driver.find_element(By.CSS_SELECTOR, 'ytd-channel-name').text
    except:
        uploader = video_data['uploader']

    all_comments = scrape_all_comments(driver)
    driver.quit()

    return {
        **video_data,
        'live_title': title,
        'live_views': views,
        'live_uploader': uploader,
        'top_5_comments': all_comments[:5],
        'total_comments': len(all_comments),
        'thumbnail_path': thumb_path
    }

# 🚀 Let's run it
url = "https://youtu.be/-6OFqkemd4c?si=-nGPM2smk5DjOdy2"
data = scrape_youtube_all(url)

# 🖨️ Show off the results
print("\n🎥 YouTube Video Details (Fully Upgraded):")
print(f"📌 Title: {data['live_title']}")
print(f"👤 Uploader: {data['live_uploader']}")
print(f"📅 Upload Date: {data['upload_date']}")
print(f"🕒 Duration: {data['duration']} seconds")
print(f"👁️ Views: {data['live_views']}")
print(f"👍 Likes: {data['likes']}")
print(f"💬 Top 5 Comments:")
for i, comment in enumerate(data['top_5_comments'], 1):
    print(f"   {i}. {comment[:100]}{'...' if len(comment) > 100 else ''}")
print(f"📝 Total Comments Fetched: {data['total_comments']}")
print(f"🖼️ Thumbnail Path: {data['thumbnail_path']}")
print(f"🎶 Audio Format Count: {len(data['audio_formats'])}")
