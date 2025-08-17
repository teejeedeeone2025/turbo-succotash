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
        'profile_name': None  # Will be detected automatically
    },
    'chrome': {
        'headless': True,
        'window_size': "1920,1080",
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
}

def setup_environment():
    """Set up the environment for Chrome to run"""
    try:
        logging.info("Setting up environment...")
        
        # Install required system packages
        os.system('sudo apt-get update -qq')
        os.system('sudo apt-get install -y wget unzip libxss1 libappindicator1 libindicator7 > /dev/null')
        
        # Install Chrome
        chrome_deb = 'google-chrome-stable_current_amd64.deb'
        if not os.path.exists(chrome_deb):
            os.system(f'wget -q https://dl.google.com/linux/direct/{chrome_deb}')
        os.system(f'sudo apt install -y ./{chrome_deb} > /dev/null')
        os.system('sudo apt --fix-broken install -y > /dev/null')
        
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
        
        # Clean up existing profile
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
        
        # Extract profile and detect structure
        logging.info("Extracting and analyzing profile...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            logging.debug(f"Files in archive: {file_list}")
            
            # Find profile directory (looking for common patterns)
            profile_candidates = [
                name for name in file_list 
                if any(x in name.lower() for x in ['profile', 'default', 'user data']) 
                and '/' in name
            ]
            
            if not profile_candidates:
                raise ValueError("No recognizable profile directory found in zip")
            
            # Get the root profile directory
            profile_root = profile_candidates[0].split('/')[0]
            CONFIG['profile']['profile_name'] = profile_root
            logging.info(f"Detected profile directory: {profile_root}")
            
            zip_ref.extractall(profile_dir)
        
        # Verify extraction
        profile_path = os.path.join(profile_dir, profile_root)
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile directory not found at {profile_path}")
        
        # Clean up Windows-specific files
        for root, _, files in os.walk(profile_path):
            for file in files:
                if file in ['SingletonCookie', 'SingletonLock', 'SingletonSocket']:
                    os.remove(os.path.join(root, file))
        
        logging.info(f"Profile successfully prepared at: {profile_path}")
        return True
        
    except Exception as e:
        logging.error(f"Profile setup failed: {str(e)}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        return False

def create_driver():
    """Create and configure Chrome WebDriver"""
    try:
        options = Options()
        
        # Profile configuration
        options.add_argument(f"--user-data-dir={CONFIG['profile']['extract_dir']}")
        options.add_argument(f"--profile-directory={CONFIG['profile']['profile_name']}")
        
        # Chrome options
        if CONFIG['chrome']['headless']:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={CONFIG['chrome']['window_size']}")
        options.add_argument(f"--user-agent={CONFIG['chrome']['user_agent']}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Initialize driver
        logging.info("Initializing Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        logging.info("WebDriver successfully created")
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
            
            # Keep browser open briefly for debugging
            time.sleep(3)
            
            return 0
            
        finally:
            driver.quit()
            
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
    #ll
