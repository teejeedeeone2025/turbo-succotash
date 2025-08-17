import os
import sys
import zipfile
import requests
import shutil
import time
import logging
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

# Configuration
CONFIG = {
    'profile': {
        'zip_url': "https://github.com/teejeedeeone2025/turbo-succotash/raw/master/ChromeProfile_ultra.zip",
        'extract_dir': os.path.expanduser("~/chrome_profile"),
        'profile_name': "Profile 1"
    },
    'chrome': {
        'headless': True,
        'window_size': "1920,1080"
    }
}

def setup_environment():
    """Set up the environment for Chrome to run"""
    try:
        # Install required system packages
        os.system('sudo apt-get update')
        os.system('sudo apt-get install -y wget unzip libxss1 libappindicator1 libindicator7')
        os.system('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
        os.system('sudo apt install -y ./google-chrome-stable_current_amd64.deb')
        os.system('sudo apt --fix-broken install -y')
        
        # Verify Chrome installation
        chrome_version = os.popen('google-chrome --version').read().strip()
        logging.info(f"Chrome version: {chrome_version}")
        
        return True
    except Exception as e:
        logging.error(f"Environment setup failed: {str(e)}")
        return False

def download_profile():
    """Download and extract the Chrome profile"""
    try:
        profile_dir = CONFIG['profile']['extract_dir']
        
        # Clean up existing profile if it exists
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
        
        # Verify extraction
        profile_path = os.path.join(profile_dir, CONFIG['profile']['profile_name'])
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile directory not found at {profile_path}")
        
        logging.info(f"Profile successfully extracted to {profile_path}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup profile: {str(e)}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        return False

def create_driver():
    """Create and configure Chrome WebDriver"""
    try:
        options = Options()
        
        # Profile configuration
        profile_path = os.path.join(
            CONFIG['profile']['extract_dir'],
            CONFIG['profile']['profile_name']
        )
        options.add_argument(f"--user-data-dir={CONFIG['profile']['extract_dir']}")
        options.add_argument(f"--profile-directory={CONFIG['profile']['profile_name']}")
        
        # Chrome options
        if CONFIG['chrome']['headless']:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={CONFIG['chrome']['window_size']}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        logging.info("Chrome WebDriver successfully created")
        return driver
        
    except Exception as e:
        logging.error(f"Failed to create WebDriver: {str(e)}")
        return None

def main():
    """Main execution function"""
    try:
        # Setup environment
        if not setup_environment():
            raise RuntimeError("Environment setup failed")
        
        # Download profile
        if not download_profile():
            raise RuntimeError("Profile setup failed")
        
        # Create driver
        driver = create_driver()
        if not driver:
            raise RuntimeError("WebDriver creation failed")
        
        try:
            # Test navigation
            logging.info("Navigating to YouTube...")
            driver.get("https://www.youtube.com")
            
            # Verify page
            logging.info(f"Page title: {driver.title}")
            if 'YouTube' not in driver.title:
                raise AssertionError("YouTube not found in page title")
            
            # Take screenshot
            screenshot_path = 'youtube_screenshot.png'
            driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved to {screenshot_path}")
            
            # Keep browser open for debugging (headless will still close)
            time.sleep(5)
            
        finally:
            driver.quit()
            
        logging.info("Script completed successfully")
        return 0
        
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
