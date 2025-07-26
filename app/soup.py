# app/soup.py
import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging

# Setup basic logging
# Initial logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional: Use a session for connection pooling
# Using sessions to optimize connections
session = requests.Session()
# It's good practice to set a user-agent
# Setting the User-Agent is a good practice so that sites don't block the request.
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
})

def get_page_content(url: str) -> Optional[BeautifulSoup]:
    """دریافت و تجزیه محتوای یک صفحه وب.
    Fetch and parse the content of a web page.
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing HTML from {url}: {e}")
        return None

def scrape_main_page_info() -> str:
    """
    اسکرپ کردن اطلاعات کلی از صفحه اصلی علی‌بابا.
    Scrape general information from Alibaba.ir's main page.
    """
    url = "https://www.alibaba.ir/"
    soup = get_page_content(url)
    if not soup:
        return "❌ خطأ در دریافت یا پردازش صفحه اصلی علی‌بابا."

    info_lines = []
    info_lines.append("🏠 اطلاعات کلی از صفحه اصلی علی‌بابا:")

    # 1. Extract the main services (airline tickets, train tickets, hotels, tours, ...)
    # Extract main services
    try:
        main_services = soup.find_all('a', class_='wrapper-sub-product')
        if main_services:
            services = [service.find('span', class_='text-body-md').get_text(strip=True) for service in main_services if service.find('span', class_='text-body-md')]
            info_lines.append(f"خدمات اصلی: {', '.join(services)}")
        else:
            info_lines.append("خدمات اصلی: یافت نشد.")
    except Exception as e:
        logger.warning(f"خطا در استخراج خدمات اصلی: {e}")
        info_lines.append("خدمات اصلی: خطا در استخراج")

    # 2. Extract footer links (Help, Rules, Contact Us, ...)
    # Extracting footer links
    try:
        footer_links_section = soup.find('div', {'data-v-d38533f6': ''}) # This attribute seems unique.
        if footer_links_section:
            footer_links = footer_links_section.find_all('a', class_='footer-link')
            links_info = [f"{link.get_text(strip=True)} ({link.get('href')})" for link in footer_links]
            info_lines.append(f"لینک‌های پایین صفحه: {', '.join(links_info)}")
        else:
            info_lines.append("لینک‌های پایین صفحه: یافت نشد.")
    except Exception as e:
        logger.warning(f"خطا در استخراج لینک‌های پایین صفحه: {e}")
        info_lines.append("لینک‌های پایین صفحه: خطا در استخراج")

    # 3. Extract the 'Companion of every trip' and 'Companion of all moments of the trip' sections
    # Extract the 'Travel companion for every trip' and 'Travel companion for every moment of the trip' sections'
    try:
        service_benefits = soup.find('ul', {'style': 'grid-template-columns:1fr 1fr 1fr 3fr;gap:16px;'})
        if service_benefits:
            benefit_items = service_benefits.find_all('li', {'data-v-af62246a': ''})
            benefits = []
            for item in benefit_items:
                title_elem = item.find('h3', class_='mt-0 mb-2')
                desc_elem = item.find('span', class_='text-grays-400')
                title = title_elem.get_text(strip=True) if title_elem else "بدون عنوان"
                desc = desc_elem.get_text(strip=True) if desc_elem else "بدون توضیح"
                benefits.append(f"{title}: {desc}")
            info_lines.append("مزایای سفر با علی‌بابا:")
            info_lines.extend([f"  - {b}" for b in benefits])
        else:
             info_lines.append("مزایای سفر با علی‌بابا: یافت نشد.")
    except Exception as e:
        logger.warning(f"خطا در استخراج مزایای سفر: {e}")
        info_lines.append("مزایای سفر با علی‌بابا: خطا در استخراج")

    return "\n".join(info_lines)

# --- Additional tools for specific sections ---
# Additional tools for specific sections

def scrape_hotel_page_info() -> str:
    """اسکرپ کردن اطلاعات از صفحه هتل.
    Scrape information from the hotel booking page.
    """
    url = "https://www.alibaba.ir/hotel"
    soup = get_page_content(url)
    if not soup:
        return "❌ خطأ در دریافت یا پردازش صفحه هتل علی‌بابا."

    info_lines = []
    info_lines.append("🏨 اطلاعات از صفحه رزرو هتل علی‌بابا:")

    # Extract the original text of the page
    # Extract the original text of the page
    try:
        main_paragraph = soup.find('p')
        if main_paragraph:
            info_lines.append(f"توضیحات: {main_paragraph.get_text(strip=True)}")
        else:
            info_lines.append("توضیحات: یافت نشد.")
    except Exception as e:
        logger.warning(f"خطا در استخراج توضیحات صفحه هتل: {e}")
        info_lines.append("توضیحات: خطا در استخراج")

    return "\n".join(info_lines)
