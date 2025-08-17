from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import zipfile
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
import shutil

# Email settings
SENDER_EMAIL = "tajuttech360@gmail.com"
RECIPIENT_EMAILS = ["teejeedeeone@gmail.com"]
EMAIL_PASSWORD = "clda nqsc scnj kpfd"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# GitHub profile settings
PROFILE_ZIP_URL = "https://github.com/teejeedeeone2025/turbo-succotash/raw/master/ChromeProfile_ultra.zip"
PROFILE_DIR = os.path.expanduser("~/chrome_profile")
PROFILE_EXTRACTED_DIR = os.path.join(PROFILE_DIR, "ChromeProfile")

def convert_windows_to_linux_profile(profile_path):
    """Convert Windows Chrome profile to work on Linux"""
    try:
        # Fix preferences file
        prefs_file = os.path.join(profile_path, "Preferences")
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r+', encoding='utf-8') as f:
                content = f.read()
                # Replace Windows paths with Linux paths
                content = content.replace(r'C:\\Users\\', '/home/runner/')
                content = content.replace('\\\\', '/')
                f.seek(0)
                f.write(content)
                f.truncate()
        
        # Remove problematic files
        for file in ["SingletonCookie", "SingletonLock", "SingletonSocket"]:
            file_path = os.path.join(profile_path, file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return True
    except Exception as e:
        print(f"Profile conversion failed: {e}")
        return False

def download_and_extract_profile():
    """Download and extract Chrome profile from GitHub"""
    try:
        if os.path.exists(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        
        print("Downloading Chrome profile...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(PROFILE_ZIP_URL, headers=headers, stream=True)
        response.raise_for_status()
        
        zip_path = os.path.join(PROFILE_DIR, "profile.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Downloaded file is not a valid zip file")
        
        print("Extracting Chrome profile...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PROFILE_DIR)
        
        # Convert Windows profile to Linux-compatible
        profile_path = os.path.join(PROFILE_EXTRACTED_DIR, "Profile 1")
        if not convert_windows_to_linux_profile(profile_path):
            raise RuntimeError("Failed to convert Windows profile to Linux format")
        
        print("Profile successfully prepared for Linux")
        return True
        
    except Exception as e:
        print(f"Profile setup failed: {str(e)}")
        if os.path.exists(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR)
        return False

# [Rest of your functions remain the same...]

def setup_chrome_options():
    """Configure Chrome options with profile"""
    options = Options()
    
    # Profile configuration
    options.add_argument(f"--user-data-dir={PROFILE_EXTRACTED_DIR}")
    options.add_argument("--profile-directory=Profile 1")
    
    # Critical options for GitHub Actions
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    
    # Additional stability options
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    return options

# [Rest of your script remains the same...]
