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

# Email settings
SENDER_EMAIL = "tajuttech360@gmail.com"
RECIPIENT_EMAILS = ["teejeedeeone@gmail.com"]
EMAIL_PASSWORD = "clda nqsc scnj kpfd"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# GitHub profile settings - USING RAW CONTENT URL
PROFILE_ZIP_URL = "https://github.com/teejeedeeone2025/turbo-succotash/raw/master/ChromeProfile_ultra.zip"
PROFILE_DIR = os.path.expanduser("~/chrome_profile")
PROFILE_EXTRACTED_DIR = os.path.join(PROFILE_DIR, "ChromeProfile")

def download_and_extract_profile():
    """Download and extract Chrome profile from GitHub"""
    try:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        
        # Download the profile zip
        print("Downloading Chrome profile...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(PROFILE_ZIP_URL, headers=headers, stream=True)
        response.raise_for_status()  # Raise error for bad status codes
        
        zip_path = os.path.join(PROFILE_DIR, "profile.zip")
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
        
        # Verify it's a valid zip file
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Downloaded file is not a valid zip file")
        
        # Extract the profile
        print("Extracting Chrome profile...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PROFILE_DIR)
        
        # Verify extraction
        if not os.path.exists(os.path.join(PROFILE_EXTRACTED_DIR, "Profile 1")):
            raise FileNotFoundError("Profile 1 directory not found in extracted files")
        
        print(f"Profile successfully extracted to: {PROFILE_EXTRACTED_DIR}")
        return True
        
    except Exception as e:
        print(f"Failed to download/extract profile: {str(e)}")
        # Clean up if something went wrong
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
        return False

def send_email_with_screenshot(screenshot_path):
    """Send an email with the screenshot attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        msg['Subject'] = "YouTube Screenshot Result"
        
        body = "Here's the screenshot of YouTube as requested."
        msg.attach(MIMEText(body, 'plain'))
        
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot_path))
            msg.attach(img)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def setup_chrome_options():
    """Configure Chrome options with profile"""
    options = Options()
    
    # Profile configuration (Linux paths)
    options.add_argument(f"--user-data-dir={PROFILE_EXTRACTED_DIR}")
    options.add_argument("--profile-directory=Profile 1")
    
    # Headless and stability options
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    return options

def main():
    # Download and extract the Chrome profile first
    if not download_and_extract_profile():
        print("Failed to setup Chrome profile, exiting...")
        return
    
    # Setup Chrome options
    options = setup_chrome_options()
    
    try:
        # Initialize Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        # Test code
        print("Navigating to YouTube...")
        driver.get("https://www.youtube.com")
        print("Page title:", driver.title)
        assert 'YouTube' in driver.title
        
        # Take screenshot
        time.sleep(2)
        screenshot_path = 'result.png'
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Send email with screenshot
        send_email_with_screenshot(screenshot_path)
        
    except AssertionError:
        print("YouTube not found in page title!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
