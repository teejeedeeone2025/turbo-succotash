from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Email settings
SENDER_EMAIL = "dahmadu071@gmail.com"
RECIPIENT_EMAILS = ["teejeedeeone@gmail.com"]
EMAIL_PASSWORD = "oase wivf hvqn lyhr"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_with_screenshot(screenshot_path):
    """Send an email with the screenshot attachment"""
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        msg['Subject'] = "YouTube Screenshot Result"
        
        # Add body text
        body = "Here's the screenshot of YouTube as requested."
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach screenshot
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot_path))
            msg.attach(img)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    options = Options()
    
    # Profile configuration
    options.add_argument('--user-data-dir=' + os.path.expanduser('~/.config/google-chrome'))
    options.add_argument('--profile-directory=Profile 1')  # Note: Fixed typo from 'directoy' to 'directory'
    
    # Chrome configuration
    options.add_argument('--headless=new')  # Using the new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    
    try:
        # Test code
        driver.get("https://www.youtube.com")
        print("Page title:", driver.title)
        assert 'YouTube' in driver.title
        
        # Save screenshot
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
        driver.quit()

if __name__ == "__main__":
    main()
