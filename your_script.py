from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def main():
    options = Options()
    
    # Profile configuration
    options.add_argument('--user-data-dir=' + os.path.expanduser('~/.config/google-chrome'))
    options.add_argument('--profile-directory=Profile 1')
    
    # Your existing config
   # Configure Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    return webdriver.Chrome(options=options)
    try:
        # Your test code here
        driver.get("https://www.youtube.com")
        print("Page title:", driver.title)
        assert 'YouTube' in driver.title
        driver.save_screenshot('result.png')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
