import os
import sys
import json
import zipfile
import requests
import shutil
import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('script.log')
    ]
)

CONFIG = {
    'profile': {
        'zip_url': "https://github.com/teejeedeeone2025/turbo-succotash/raw/master/ChromeProfile_ultra.zip",
        'extract_dir': os.path.expanduser("~/chrome_profile"),
        'profile_name': "Profile 1"
    },
    'chrome': {
        'headless': True,
        'window_size': "1920,1080",
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    'email': {
        'sender': "tajuttech360@gmail.com",
        'recipients': ["teejeedeeone@gmail.com"],
        'password': "clda nqsc scnj kpfd",
        'smtp_server': "smtp.gmail.com",
        'smtp_port': 587
    }
}

def convert_windows_profile_to_linux(profile_path):
    """Convert Windows Chrome profile to work on Linux"""
    try:
        # 1. Fix Preferences file
        prefs_file = os.path.join(profile_path, "Preferences")
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r+', encoding='utf-8') as f:
                prefs = json.load(f)
                # Convert Windows paths to Linux
                for key in ['profile', 'extensions']:
                    if key in prefs:
                        if 'last_active_profiles' in prefs[key]:
                            prefs[key]['last_active_profiles'] = ["Profile 1"]
                        if 'content_settings' in prefs[key]:
                            for origin in list(prefs[key]['content_settings'].get('exceptions', {}).keys()):
                                if 'C:\\' in origin:
                                    del prefs[key]['content_settings']['exceptions'][origin]
                f.seek(0)
                json.dump(prefs, f, indent=2)
                f.truncate()

        # 2. Clean up Windows-specific files
        for file in ['SingletonCookie', 'SingletonLock', 'SingletonSocket']:
            file_path = os.path.join(profile_path, file)
            if os.path.exists(file_path):
                os.remove(file_path)

        # 3. Fix Cookies database (if exists)
        cookies_db = os.path.join(profile_path, "Cookies")
        if os.path.exists(cookies_db):
            os.remove(cookies_db)  # Chrome will recreate this

        logging.info("Successfully converted Windows profile to Linux")
        return True
    except Exception as e:
        logging.error(f"Profile conversion failed: {e}")
        return False

def download_and_prepare_profile():
    """Download and prepare Chrome profile"""
    try:
        profile_dir = CONFIG['profile']['extract_dir']
        
        # Clean existing profile
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        os.makedirs(profile_dir, exist_ok=True)

        # Download profile
        logging.info("Downloading Chrome profile...")
        zip_path = os.path.join(profile_dir, "profile.zip")
        
        response = requests.get(
            CONFIG['profile']['zip_url'],
            stream=True,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Extract profile
        logging.info("Extracting profile...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(profile_dir)

        # Convert Windows profile to Linux
        profile_path = os.path.join(profile_dir, CONFIG['profile']['profile_name'])
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile directory not found at {profile_path}")
        
        if not convert_windows_profile_to_linux(profile_path):
            raise RuntimeError("Profile conversion failed")

        logging.info(f"Profile ready at: {profile_path}")
        return True

    except Exception as e:
        logging.error(f"Profile preparation failed: {e}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        return False

def send_email_with_screenshot(screenshot_path):
    """Send email with screenshot attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = CONFIG['email']['sender']
        msg['To'] = ", ".join(CONFIG['email']['recipients'])
        msg['Subject'] = "YouTube Automation Result"
        
        body = f"""
        <html>
            <body>
                <h2>YouTube Automation Report</h2>
                <p>Screenshot attached from automated browser session.</p>
                <p>Page title: {driver.title if 'driver' in locals() else 'N/A'}</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename="youtube_screenshot.png")
            msg.attach(img)
        
        with smtplib.SMTP(CONFIG['email']['smtp_server'], CONFIG['email']['smtp_port']) as server:
            server.starttls()
            server.login(CONFIG['email']['sender'], CONFIG['email']['password'])
            server.send_message(msg)
        
        logging.info("Email sent successfully!")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def setup_chrome_driver():
    """Configure and return Chrome WebDriver"""
    options = Options()
    
    # Profile settings
    options.add_argument(f"--user-data-dir={CONFIG['profile']['extract_dir']}")
    options.add_argument(f"--profile-directory={CONFIG['profile']['profile_name']}")
    
    # Chrome options
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={CONFIG['chrome']['window_size']}")
    options.add_argument(f"--user-agent={CONFIG['chrome']['user_agent']}")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    
    return driver

def main():
    try:
        # Setup profile
        if not download_and_prepare_profile():
            raise RuntimeError("Failed to prepare Chrome profile")
        
        # Initialize browser
        driver = setup_chrome_driver()
        logging.info("Chrome WebDriver initialized")
        
        try:
            # Navigate to YouTube
            driver.get("https://www.youtube.com")
            logging.info(f"Page title: {driver.title}")
            
            # Take screenshot
            screenshot_path = "youtube_screenshot.png"
            driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved to {screenshot_path}")
            
            # Send email
            if not send_email_with_screenshot(screenshot_path):
                raise RuntimeError("Failed to send results email")
            
            return 0
            
        finally:
            driver.quit()
            
    except Exception as e:
        logging.error(f"Script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
