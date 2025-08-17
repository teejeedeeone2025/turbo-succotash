import os
import sys
import json
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
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
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
        'profile_name': None  # Will be auto-detected
    },
    'chrome': {
        'headless': True,
        'window_size': "1920,1080",
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
}

def analyze_zip_structure(zip_path):
    """Analyze the zip file structure and detect profile directory"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        logging.debug(f"Zip contents: {file_list}")
        
        # Look for common profile directory patterns
        possible_profiles = [
            name.split('/')[0] 
            for name in file_list 
            if any(x in name.lower() for x in ['profile', 'default', 'user data'])
        ]
        
        if not possible_profiles:
            raise ValueError("No recognizable profile directory found in zip")
        
        # Get the most likely profile directory
        profile_dir = max(set(possible_profiles), key=possible_profiles.count)
        logging.info(f"Detected profile directory: {profile_dir}")
        return profile_dir

def download_and_prepare_profile():
    """Download and prepare Chrome profile with better structure detection"""
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

        # Detect profile structure
        CONFIG['profile']['profile_name'] = analyze_zip_structure(zip_path)
        
        # Extract profile
        logging.info(f"Extracting profile to {profile_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(profile_dir)

        # Verify extraction
        profile_path = os.path.join(profile_dir, CONFIG['profile']['profile_name'])
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile directory not found at {profile_path}")
        
        logging.info(f"Profile successfully prepared at: {profile_path}")
        return True

    except Exception as e:
        logging.error(f"Profile preparation failed: {str(e)}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        return False

def create_driver():
    """Create Chrome WebDriver with the prepared profile"""
    try:
        options = Options()
        
        # Profile configuration
        options.add_argument(f"--user-data-dir={CONFIG['profile']['extract_dir']}")
        options.add_argument(f"--profile-directory={CONFIG['profile']['profile_name']}")
        
        # Chrome options
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={CONFIG['chrome']['window_size']}")
        options.add_argument(f"--user-agent={CONFIG['chrome']['user_agent']}")
        
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
        # Prepare profile
        if not download_and_prepare_profile():
            raise RuntimeError("Failed to prepare Chrome profile")
        
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
            
            return 0
            
        finally:
            driver.quit()
            
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
