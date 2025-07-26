# app/playwright.py
import asyncio
from playwright.async_api import async_playwright
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flight Search ---
# جستجوی پرواز داخلی

async def scrape_flight_schedules_async(
    origin: str,
    destination: str,
    date: str
) -> str:
    """
    جستجوی تعاملی بلیط هواپیمای داخلی در علی‌بابا.
    Interactive search for domestic flight tickets on Alibaba.ir.
    """
    logger.info(f"Starting flight schedule search: {origin} -> {destination} on {date}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/flight-ticket"
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle')

            # Fill origin
            logger.info("Filling origin field...")
            origin_input_selector = "input[placeholder*='مبدا']"
            await page.locator(origin_input_selector).first.fill(origin)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for origin.")
                pass

            # Fill destination
            logger.info("Filling destination field...")
            destination_input_selector = "input[placeholder*='مقصد']"
            await page.locator(destination_input_selector).first.fill(destination)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for destination.")
                pass

            # Fill date
            logger.info("Filling date field...")
            date_input_selector = "input[placeholder*='تاریخ رفت']"
            await page.locator(date_input_selector).first.fill(date)

            # Click search button
            logger.info("Clicking search button...")
            search_button_selector = "button:has-text('جستجو')"
            await page.locator(search_button_selector).click()

            # Wait for results
            logger.info("Waiting for results...")
            await page.wait_for_selector("text=پرواز", timeout=20000)

            # Extract results
            logger.info("Extracting results...")
            flight_items = await page.locator(".flight-item").all()
            
            results = []
            if not flight_items:
                try:
                    no_result_text = await page.locator("text=نتیجه‌ای یافت نشد").text_content(timeout=2000)
                    results.append("نتیجه‌ای یافت نشد.")
                except:
                    results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                for item in flight_items[:5]:
                    try:
                        airline = await item.locator(".airline-name, .flight-airline").text_content(timeout=1000)
                        departure_time = await item.locator(".departure-time, .flight-departure").text_content(timeout=1000)
                        arrival_time = await item.locator(".arrival-time, .flight-arrival").text_content(timeout=1000)
                        price = await item.locator(".price, .flight-price").text_content(timeout=1000)
                        
                        results.append(
                            f"شرکت هواپیمایی: {airline.strip()}, "
                            f"زمان پرواز: {departure_time.strip()} - {arrival_time.strip()}, "
                            f"قیمت: {price.strip()}"
                        )
                    except Exception as e:
                        logger.warning(f"Error extracting data from a flight item: {e}")

            await browser.close()
            logger.info("Browser closed.")

            if results:
                return f"✈️ نتایج جستجوی پرواز از {origin} به {destination} در تاریخ {date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره پرواز از {origin} به {destination} در تاریخ {date} پیدا نکردم."

    except asyncio.TimeoutError:
        logger.error("Timeout occurred during flight schedule scraping.")
        return "⏰ زمان زیادی برای دریافت اطلاعات طول کشید. لطفاً دوباره امتحان کنید."
    except Exception as e:
        logger.error(f"Error during flight schedule scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی بلیط هواپیما رخ داد: {str(e)}"

def scrape_flight_schedules(origin: str, destination: str, date: str) -> str:
    """Wrapper برای اجرای تابع async در یه event loop."""
    try:
        return asyncio.run(scrape_flight_schedules_async(origin, destination, date))
    except Exception as e:
        logger.error(f"Error in scrape_flight_schedules wrapper: {e}")
        return f"❌ خطایی در wrapper رخ داد: {str(e)}"

# --- Train Search ---
# جستجوی قطار

async def scrape_train_schedules_async(
    origin: str,
    destination: str,
    date: str
) -> str:
    """
    جستجوی تعاملی زمانبندی قطارها در علی‌بابا.
    Interactive search for train schedules on Alibaba.ir.
    """
    logger.info(f"Starting train schedule search: {origin} -> {destination} on {date}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/train-ticket"
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle')

            # Fill origin
            logger.info("Filling origin field...")
            origin_input_selector = "input[placeholder*='مبدا']"
            await page.locator(origin_input_selector).first.fill(origin)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for origin (train).")
                pass

            # Fill destination
            logger.info("Filling destination field...")
            destination_input_selector = "input[placeholder*='مقصد']"
            await page.locator(destination_input_selector).first.fill(destination)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for destination (train).")
                pass

            # Fill date
            logger.info("Filling date field...")
            date_input_selector = "input[placeholder*='تاریخ']" # Check the actual placeholder
            await page.locator(date_input_selector).first.fill(date)

            # Click search button
            logger.info("Clicking search button...")
            search_button_selector = "button:has-text('جستجو')"
            await page.locator(search_button_selector).click()

            # Wait for results
            logger.info("Waiting for results...")
            await page.wait_for_selector("text=قطار", timeout=15000)

            # Extract results
            logger.info("Extracting results...")
            train_items = await page.locator(".train-item").all()
            
            results = []
            if not train_items:
                try:
                    no_result_text = await page.locator("text=نتیجه‌ای یافت نشد").text_content(timeout=2000)
                    results.append("نتیجه‌ای یافت نشد.")
                except:
                    results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                for item in train_items[:5]:
                    try:
                        name = await item.locator(".train-name").text_content(timeout=1000)
                        departure = await item.locator(".departure-time").text_content(timeout=1000)
                        arrival = await item.locator(".arrival-time").text_content(timeout=1000)
                        price = await item.locator(".price").text_content(timeout=1000)
                        results.append(f"قطار: {name.strip()}, حرکت: {departure.strip()}, رسیدن: {arrival.strip()}, قیمت: {price.strip()}")
                    except Exception as e:
                        logger.warning(f"Error extracting data from a train item: {e}")

            await browser.close()
            logger.info("Browser closed.")

            if results:
                return f"🚆 نتایج جستجوی قطار از {origin} به {destination} در تاریخ {date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره قطار از {origin} به {destination} در تاریخ {date} پیدا نکردم."

    except asyncio.TimeoutError:
        logger.error("Timeout occurred during train schedule scraping.")
        return "⏰ زمان زیادی برای دریافت اطلاعات قطار طول کشید."
    except Exception as e:
        logger.error(f"Error during train schedule scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی زمانبندی قطار رخ داد: {str(e)}"

def scrape_train_schedules(origin: str, destination: str, date: str) -> str:
    """Wrapper برای اجرای تابع async در یه event loop."""
    try:
        return asyncio.run(scrape_train_schedules_async(origin, destination, date))
    except Exception as e:
        logger.error(f"Error in scrape_train_schedules wrapper: {e}")
        return f"❌ خطایی در wrapper رخ داد: {str(e)}"

# --- Hotel Search ---
# جستجوی هتل

async def scrape_hotel_info_async(
    city: str,
    checkin_date: str,
    checkout_date: str
) -> str:
    """
    جستجوی تعاملی اطلاعات هتل در علی‌بابا.
    Interactive search for hotel information on Alibaba.ir.
    """
    logger.info(f"Starting hotel search in {city} from {checkin_date} to {checkout_date}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/hotel"
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle')

            # Fill destination
            logger.info("Filling destination field...")
            destination_input_selector = "input[placeholder*='شهر یا نام هتل']"
            await page.locator(destination_input_selector).first.fill(city)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for hotel destination.")
                pass

            # Fill check-in date
            logger.info("Filling check-in date...")
            checkin_input_selector = "input[placeholder*='تاریخ ورود']"
            await page.locator(checkin_input_selector).first.fill(checkin_date)

            # Fill check-out date
            logger.info("Filling check-out date...")
            checkout_input_selector = "input[placeholder*='تاریخ خروج']"
            await page.locator(checkout_input_selector).first.fill(checkout_date)

            # Click search button
            logger.info("Clicking search button...")
            search_button_selector = "button:has-text('جستجو')"
            await page.locator(search_button_selector).click()

            # Wait for results
            logger.info("Waiting for results...")
            await page.wait_for_selector("text=هتل", timeout=20000)

            # Extract results
            logger.info("Extracting results...")
            hotel_items = await page.locator(".hotel-item, .HotelCard").all()
            
            results = []
            if not hotel_items:
                try:
                    no_result_text = await page.locator("text=نتیجه‌ای یافت نشد").text_content(timeout=2000)
                    results.append("نتیجه‌ای یافت نشد.")
                except:
                    results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                for item in hotel_items[:3]:
                    try:
                        name = await item.locator(".hotel-name, .HotelCard__name").text_content(timeout=1000)
                        try:
                            rating = await item.locator(".hotel-rating, .HotelCard__rating").text_content(timeout=1000)
                        except:
                            rating = "امتیاز ندارد"
                        try:
                            price = await item.locator(".price, .HotelCard__price").first.text_content(timeout=1000)
                        except:
                            price = "قیمت نامشخص"
                        try:
                            location = await item.locator(".location, .HotelCard__location").text_content(timeout=1000)
                        except:
                            location = ""
                        
                        results.append(
                            f"🏨 {name.strip()} "
                            f"({rating.strip()}) - "
                            f"{price.strip()} "
                            f"({location.strip()})"
                        )
                    except Exception as e:
                        logger.warning(f"Error extracting data from a hotel item: {e}")

            await browser.close()
            logger.info("Browser closed.")

            if results:
                return f"🏨 نتایج جستجوی هتل در {city} از {checkin_date} تا {checkout_date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره هتل در {city} از {checkin_date} تا {checkout_date} پیدا نکردم."

    except asyncio.TimeoutError:
        logger.error("Timeout occurred during hotel info scraping.")
        return "⏰ زمان زیادی برای دریافت اطلاعات هتل طول کشید."
    except Exception as e:
        logger.error(f"Error during hotel info scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی اطلاعات هتل رخ داد: {str(e)}"

def scrape_hotel_info(city: str, checkin_date: str, checkout_date: str) -> str:
    """Wrapper برای اجرای تابع async در یه event loop."""
    try:
        return asyncio.run(scrape_hotel_info_async(city, checkin_date, checkout_date))
    except Exception as e:
        logger.error(f"Error in scrape_hotel_info wrapper: {e}")
        return f"❌ خطایی در wrapper رخ داد: {str(e)}"

# --- Villa/Accommodation Search ---
# جستجوی ویلا/اقامتگاه

async def scrape_villa_info_async(
    city: str,
    checkin_date: str,
    checkout_date: str
) -> str:
    """
    جستجوی تعاملی اطلاعات ویلا/اقامتگاه در علی‌بابا.
    Interactive search for villa/accommodation information on Alibaba.ir.
    """
    logger.info(f"Starting villa search in {city} from {checkin_date} to {checkout_date}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/accommodation"
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle')

            # Fill destination
            logger.info("Filling destination field...")
            destination_input_selector = "input[placeholder*='شهر یا منطقه']"
            await page.locator(destination_input_selector).first.fill(city)
            await page.wait_for_timeout(500)
            try:
                await page.locator("div.suggestion-item").first.click()
            except:
                logger.warning("No suggestion item found for villa destination.")
                pass

            # Fill check-in date
            logger.info("Filling check-in date...")
            checkin_input_selector = "input[placeholder*='تاریخ ورود']"
            await page.locator(checkin_input_selector).first.fill(checkin_date)

            # Fill check-out date
            logger.info("Filling check-out date...")
            checkout_input_selector = "input[placeholder*='تاریخ خروج']"
            await page.locator(checkout_input_selector).first.fill(checkout_date)

            # Click search button
            logger.info("Clicking search button...")
            search_button_selector = "button:has-text('جستجو')"
            await page.locator(search_button_selector).click()

            # Wait for results
            logger.info("Waiting for results...")
            await page.wait_for_selector("text=اقامتگاه", timeout=20000)

            # Extract results
            logger.info("Extracting results...")
            villa_items = await page.locator(".villa-item, .AccommodationCard").all()
            
            results = []
            if not villa_items:
                try:
                    no_result_text = await page.locator("text=نتیجه‌ای یافت نشد").text_content(timeout=2000)
                    results.append("نتیجه‌ای یافت نشد.")
                except:
                    results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                for item in villa_items[:3]:
                    try:
                        name = await item.locator(".villa-name, .AccommodationCard__name").text_content(timeout=1000)
                        try:
                            rating = await item.locator(".villa-rating, .AccommodationCard__rating").text_content(timeout=1000)
                        except:
                            rating = "امتیاز ندارد"
                        try:
                            price = await item.locator(".price, .AccommodationCard__price").first.text_content(timeout=1000)
                        except:
                            price = "قیمت نامشخص"
                        try:
                            location = await item.locator(".location, .AccommodationCard__location").text_content(timeout=1000)
                        except:
                            location = ""
                        
                        results.append(
                            f"🏡 {name.strip()} "
                            f"({rating.strip()}) - "
                            f"{price.strip()} "
                            f"({location.strip()})"
                        )
                    except Exception as e:
                        logger.warning(f"Error extracting data from a villa item: {e}")

            await browser.close()
            logger.info("Browser closed.")

            if results:
                return f"🏡 نتایج جستجوی اقامتگاه در {city} از {checkin_date} تا {checkout_date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره اقامتگاه در {city} از {checkin_date} تا {checkout_date} پیدا نکردم."

    except asyncio.TimeoutError:
        logger.error("Timeout occurred during villa info scraping.")
        return "⏰ زمان زیادی برای دریافت اطلاعات اقامتگاه طول کشید."
    except Exception as e:
        logger.error(f"Error during villa info scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی اطلاعات اقامتگاه رخ داد: {str(e)}"

def scrape_villa_info(city: str, checkin_date: str, checkout_date: str) -> str:
    """Wrapper برای اجرای تابع async در یه event loop."""
    try:
        return asyncio.run(scrape_villa_info_async(city, checkin_date, checkout_date))
    except Exception as e:
        logger.error(f"Error in scrape_villa_info wrapper: {e}")
        return f"❌ خطایی در wrapper رخ داد: {str(e)}"
