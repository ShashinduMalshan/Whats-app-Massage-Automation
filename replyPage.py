from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

CHROME_DRIVER_PATH = "/usr/bin/chromedriver"
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
BIRTHDAY_KEYWORDS = ["happy birthday", "bday", "birthday", "hbd"]

def detect_birthday_wishes(messages):
    return [msg for msg in messages if any(keyword in msg.lower() for keyword in BIRTHDAY_KEYWORDS)]

def send_reply(driver, message):
    try:
        # Wait for the message input box to be present
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.click()
        time.sleep(1)
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"Error sending reply: {str(e)}")

def scroll_chat_list(driver):
    try:
        scrollable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
        )
        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 500", scrollable)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error scrolling chat list: {str(e)}")

def main():
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.get(WHATSAPP_WEB_URL)

    print("Please scan the QR code to log in to WhatsApp Web.")
    time.sleep(20)  # Wait for user to scan QR code

    try:
        # Wait until chats are loaded
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="listitem"]'))
        )

        scroll_chat_list(driver)

        # Get all chat elements
        chat_elements = driver.find_elements(By.XPATH, '//div[@role="listitem"]')
        print(f"Found {len(chat_elements)} chats. Checking for unread ones...")

        unread_chats = []
        for chat in chat_elements:
            try:
                # Check for unread message indicator
                unread_indicator = chat.find_elements(By.XPATH, './/span[@aria-label and contains(@class, "x1sbl2l")]')
                if unread_indicator:
                    unread_chats.append(chat)
            except:
                continue

        print(f"Found {len(unread_chats)} unread chats.")

        for chat in unread_chats:
            try:
                chat.click()
                time.sleep(2)

                # Get contact/group name
                contact_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//header//span[@dir="auto"]'))
                ).text

                # Get messages (both incoming and outgoing)
                messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]//span[contains(@class, "selectable-text")]')
                message_texts = [msg.text for msg in messages if msg.text.strip() != ""]

                birthday_wishes = detect_birthday_wishes(message_texts)
                if birthday_wishes:
                    print(f"🎉 Birthday wish detected from {contact_name}")
                    reply = f"Thank you for the birthday wish, {contact_name}!"
                    send_reply(driver, reply)
                    print(f"✅ Replied to {contact_name}")
                else:
                    print(f"No birthday wish found in {contact_name}'s messages.")

                # Go back to chat list
                time.sleep(1)

            except Exception as e:
                print(f"Error processing chat: {str(e)}")
                continue

    except Exception as e:
        print(f"Main error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()