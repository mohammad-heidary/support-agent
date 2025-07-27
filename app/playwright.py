# app/playwright.py
import asyncio
from playwright.sync_api import sync_playwright
import logging
import regex

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_faq_simple(question: str, category: str = "پرواز داخلی") -> str:
    """
    نسخه ساده (sync) از جستجوی تعاملی FAQ.
    Simple (sync) version of interactive FAQ search.
    """
    if not category:
        category = "پرواز داخلی" # دسته‌ی پیش‌فرض
    logger.info(f"Starting FAQ search for question: '{question}' in category: '{category}'")

    try:
        with sync_playwright() as p:
            # برای دیباگ می‌تونی headless=False بذاری
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/help-center/categories/faq"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === انتخاب دسته ===
            logger.info(f"Selecting category: {category}")
            # استفاده از selector از recorder
            # توجه: بعضی اوقات لینک‌ها ممکنه دقیقاً مطابقت نداشته باشن، یا نیاز به کلیک خاصی داشته باشن.
            # از کد codegen: await page.getByRole('link', { name: 'اتوبوس', exact: true }).click();
            category_link = page.get_by_role("link", name=category, exact=True)
            if category_link.count() > 0:
                category_link.click()
                page.wait_for_timeout(1000) # صبر کمی برای بارگذاری سوالات
            else:
                logger.warning(f"Category '{category}' not found with exact match. Trying partial match...")
                # اگه مطابقت دقیق نبود، مطابقت جزئی رو امتحان کن
                category_link_partial = page.get_by_role("link").filter(has_text=category)
                if category_link_partial.count() > 0:
                     category_link_partial.first.click()
                     page.wait_for_timeout(1000)
                else:
                     logger.warning(f"Category '{category}' not found with partial match either. Proceeding without category selection.")
                     # اگه دسته پیدا نشد، سعی می‌کنیم تو همه سوالات جستجو کنیم
                     # یا می‌تونیم یه پیام خطا برگردونیم

            # === جستجوی سوال ===
            # روش 1: جستجوی متنی در بین سوالات موجود
            # فرض کنیم سوالات تو المنت‌های <summary> هستن (همونطور که تو کد codegen دیدیم)
            logger.info("Searching for question in the list...")
            # از کد codegen: await page.getByText('میزان بار مجاز هر مسافر در سفر با اتوبوس داخلی چقدر است؟').click();
            # یعنی سوالات تو یه المنت متنی ساده هستن، نه لزوماً summary.
            # پس بهتره از has_text استفاده کنیم.
            
            # روش پیشنهادی: جستجو برای المنتی که متن سوال کاربر رو داره.
            # این روش انعطاف بیشتری می‌ده.
            matching_question_element = page.get_by_text(question)
            if matching_question_element.count() > 0:
                logger.info(f"Found matching question element. Clicking...")
                matching_question_element.first.click()
                page.wait_for_timeout(1000) # صبر کمی برای باز شدن پاسخ

                # === استخراج پاسخ ===
                # بعد از کلیک روی سوال، پاسخ ظاهر می‌شه.
                # باید المنتی که پاسخ توشه رو پیدا کنیم.
                # از کد codegen: await page.getByText('طبق قوانین سازمان حمل‌ونقل، میزان بار مجاز 20').click();
                # یعنی پاسخ هم یه متن ساده هست.
                # یه راه خوب اینه که المنت بعدی از سوال رو پیدا کنیم یا المنتی که بعد از سوال ظاهر می‌شه.
                # ولی این کمی tricky هست.
                # راه ساده‌تر: گرفتن تمام متن صفحه بعد از کلیک و استخراج متن اطراف سوال.
                # یا اینکه سعی کنیم المنتی که حاوی پاسخ هست رو پیدا کنیم.
                
                # فرض: پاسخ تو یه المنت بعدی یا یه المنت با کلاس خاص هست.
                # اما چون ساختار دقیق رو نمی‌دونیم، می‌تونیم یه روش عمومی‌تر استفاده کنیم.
                # مثلاً گرفتن متن کل صفحه و استخراج متن بعد از سوال.
                # ولی بهتره سعی کنیم یه المنت منطقی پیدا کنیم.
                
                # روش ساده: گرفتن متن المنتی که کلیک کردیم + متن المنت‌های بعدی
                # ولی بهتره یه کم هوشمندانه‌تر عمل کنیم.
                # فرض کنیم پاسخ تو یه div یا p بعد از سوال هست.
                # می‌تونیم از xpath استفاده کنیم تا المنت بعدی رو پیدا کنیم.
                # ولی برای سادگی، یه روش دیگه:
                # گرفتن محتوای کل صفحه و جستجوی متن سوال، بعد استخراج متن بعد از اون.
                
                # راه بهتر: استفاده از والد سوال و پیدا کردن پاسخ نسبت به اون.
                # ولی چون سوال یه text element هست، والدش رو می‌گیریم.
                parent_of_question = matching_question_element.first.locator('xpath=..')
                # حالا سعی می‌کنیم پاسخ رو تو والد یا فرزندان والد پیدا کنیم.
                # این کمی سخته بدون دیدن ساختار دقیق DOM.
                
                # راه عملی: گرفتن متن کل صفحه و جستجو
                full_page_text = page.text_content("body")
                if full_page_text:
                    question_index = full_page_text.find(question)
                    if question_index != -1:
                        # شروع جستجو از بعد از سوال
                        start_extract_index = question_index + len(question)
                        # گرفتن چند کاراکتر بعدی (مثلاً 500 تا)
                        answer_snippet = full_page_text[start_extract_index:start_extract_index + 500].strip()
                        # حذف خطوط خالی اولیه
                        answer_lines = answer_snippet.split('\n')
                        answer_lines = [line.strip() for line in answer_lines if line.strip()]
                        answer_clean = "\n".join(answer_lines[:5]) # مثلاً 5 خط اول غیر خالی
                        if answer_clean:
                            browser.close()
                            logger.info("Browser closed (FAQ SIMPLE).")
                            return f"سؤال: {question}\nپاسخ: {answer_clean}"
                        else:
                            logger.warning("Could not extract clean answer text.")
                    else:
                        logger.warning("Question text not found in full page text (unexpected).")
                else:
                    logger.warning("Could not get full page text content.")

                # اگه روش بالا جواب نداد، یه fallback ساده:
                # گرفتن متن چند تا از المنت‌های بعدی
                try:
                    # فرض: پاسخ تو یه p یا div بعد از سوال هست
                    # این روش ممکنه نیاز به تنظیم بیشتری داشته باشه
                    next_elements = parent_of_question.locator('xpath=following::*[self::p or self::div]') # یا سلکتورهای دیگه
                    if next_elements.count() > 0:
                         answer_text = next_elements.first.text_content()
                         if answer_text:
                              browser.close()
                              logger.info("Browser closed (FAQ SIMPLE).")
                              return f"سؤال: {question}\nپاسخ (Fallback): {answer_text.strip()[:200]}..." # فقط 200 کاراکتر اول
                except Exception as e_fallback:
                     logger.error(f"Fallback method for answer extraction also failed: {e_fallback}")

                browser.close()
                logger.info("Browser closed (FAQ SIMPLE).")
                return f"سؤال: {question}\nپاسخ: (نتونستم متن پاسخ رو استخراج کنم، ولی سوال پیدا شد.)"
            else:
                browser.close()
                logger.info("Browser closed (FAQ SIMPLE).")
                return f"برای سوال '{question}' در دسته '{category}' سوال مرتبطی پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE FAQ search: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی سوالات متداول رخ داد: {str(e)}"

# Wrapper برای استفاده تو محیط async
def search_alibaba_faqs_interactive(question: str, category: str = "پرواز داخلی") -> str:
    """
    Wrapper برای جستجوی تعاملی FAQ.
    Wrapper for interactive FAQ search.
    """
    # برای تست ساده‌تر، می‌تونیم مستقیم تابع sync رو صدا کنیم:
    return search_faq_simple(question, category)
    # اگه می‌خوای تو محیط async اصلی اجرا بشه:
    # loop = asyncio.get_event_loop()
    # from functools import partial
    # return loop.run_in_executor(None, partial(search_faq_simple, question=question, category=category))

# --- Flight Search ---


def search_flight_schedules_simple(origin: str, destination: str, date: str) -> str:
    """نسخه ساده (sync) از جستجوی پرواز داخلی برای تست.
    Simple (sync) version of domestic flight search for testing."""
    logger.info(f"Starting search with parameters: origin={origin}, destination={destination}, date={date}")
    
    # تبدیل تاریخ به فرمت مورد نیاز سایت 
    # مثلاً اگه date = "1403/07/15" باشه، باید "15" رو استخراج کنیم
    try:
        year, month, day = date.split('/')
        logger.info(f"Extracted date parts: year={year}, month={month}, day={day}")
    except Exception as e:
        logger.error(f"Could not extract date parts from date: {date}. Error: {e}")
        # اگه نتونه، خود تاریخ رو می‌فرسته یا یه مقدار پیش‌فرض
        year, month, day = "1403", "05", "15" 

    try:
        with sync_playwright() as p:
            # برای دیباگ می‌تونی headless=False بذاری
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/flight-ticket"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. اطمینان از انتخاب "یک طرفه" (اگر لازم باشه)
            # کد codegen نشون میده که اول یک طرفه کلیک میشه. اینجا چک می‌کنیم.
            logger.info("Ensuring 'یک طرفه' is selected...")
            oneway_button = page.get_by_role('button', name='یک طرفه')
            # اگر کلیک خاصی لازم بود میشه اضافه کرد، ولی اول چک می‌کنیم وجود داره یا نه.
            if oneway_button.count() > 0:
                 # oneway_button.click(modifiers=['ControlOrMeta']) # این خط از کد codegen بود
                 # بهتره یه کلیک ساده بزنیم و ببینیم چی میشه
                 oneway_button.click()
                 page.wait_for_timeout(500) # کمی صبر کن تا تغییرات اعمال بشه (اگه لازم باشه)
            else:
                 logger.info("'یک طرفه' button not found or already selected.")

            # 2. پر کردن مبدا
            logger.info("Filling origin field...")
            origin_field = page.get_by_role("textbox", name="مبدا (شهر)")
            origin_field.click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000) 
            # انتخاب شهر مبدا از suggestion - استفاده از regex برای مطابقت دقیق
            logger.info(f"Selecting origin: {origin}")
            # page.locator('a').filter({ hasText: /^تهران$/ }).click(); // از کد codegen
            page.locator('a').filter(has_text=regex.compile(f"^{origin}$")).first.click()

            # 3. پر کردن مقصد
            logger.info("Filling destination field...")
            destination_field = page.get_by_role("textbox", name="مقصد (شهر)")
            destination_field.click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر مقصد از suggestion - استفاده از regex برای مطابقت دقیق
            logger.info(f"Selecting destination: {destination}")
            # page.locator('a').filter({ hasText: 'اهواز' }).click(); // از کد codegen
            page.locator('a').filter(has_text=regex.compile(f"^{destination}$")).first.click()

            # 4. انتخاب تاریخ
            logger.info("Selecting date...")
            # کلیک روی input تاریخ برای باز کردن datepicker
            # اسم فیلد تاریخ در کد codegen: 'تاریخ رفت'
            date_field = page.get_by_role("textbox", name="تاریخ رفت")
            date_field.click()
            # صبر کمی برای باز شدن تقویم
            page.wait_for_timeout(1000)
            
            # !!! مهم: سایت ممکنه تقویم خودش رو باز کنه یا یه تقویم جدا. 
            # کد codegen نشون میده که یه جا به '4200' کلیک کرده که احتمالاً یه روز هست.
            # ولی بهتره از تاریخ واقعی استفاده کنیم.
            # فرض کنیم سال و ماه درست هستن و ما باید روز رو پیدا کنیم.
            # یه راه راحت‌تر اینه که المنت روز رو پیدا کنیم.
            # ولی سایت ممکنه تقویم پیچیده‌ای داشته باشه. 
            # برای سادگی، فعلاً فرض می‌کنیم روز رو می‌شه مستقیم پیدا کرد.
            # این روش ممکنه نیاز به تطبیق بیشتری داشته باشه بسته به ساختار تقویم.
            logger.info(f"Clicking on day: {day}")
            # page.getByText('4200').first().click(); // این یه عدد رندوم بود. باید عوض بشه.
            # سعی می‌کنیم المنتی که فقط عدد روز رو داره پیدا کنیم.
            # این ممکنه نیاز به تنظیم بیشتری داشته باشه.
            page.get_by_text(day, exact=True).first.click()

            # 5. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            # page.getByRole('button', { name: 'جستجو' }).click(); // از کد codegen
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که تو کد recorder ظاهر می‌شد به عنوان نشانه
            # این یه رشته منحصر به فرد از نتایج هست.
            # page.wait_for_selector("div:has-text('تومان نرخ رسمی ایرلاین')", timeout=30000)
            # از کد codegen: await page.goto('https://www.alibaba.ir/flights/THR-AWZ?adult=1&child=0&infant=0&departing=1404-05-14');
            # یعنی بعد از جستجو، یه URL جدید بار میشه. می‌تونیم از اون استفاده کنیم.
            # ولی بهتره صبر کنیم تا یه المنت خاص از صفحه نتایج ظاهر بشه.
            # فرض کنیم یه المنت با متن خاص (مثلاً اسم یه هواپیمایی یا "قیمت") ظاهر میشه.
            # برای تست اولیه، صبر می‌کنیم تا URL تغییر کنه یا یه المنت خاص بیاد.
            # page.wait_for_url("**/flights/**", timeout=30000) # صبر کن تا URL شامل /flights/ بشه
            # یا صبر کن تا یه المنت از نتایج بیاد
            page.wait_for_selector("button:has-text('انتخاب')", timeout=30000) # فرض: دکمه انتخاب وجود داره


            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []

            # روش 1: پیدا کردن همه المنت‌هایی که اطلاعات بلیط توشه
            # استفاده از یه selector کلی‌تر برای شروع
            # ticket_containers = page.locator("div:has-text('تومان نرخ رسمی ایرلاین')")
            # فرض کنیم هر کارت پرواز یه دکمه "انتخاب" داره
            ticket_containers = page.locator("button:has-text('انتخاب')").locator("..") # والد دکمه انتخاب
            # یا میشه از div های خاصی که کارت هستن استفاده کرد. باید inspect کرد.
            # فرض کنیم کارت‌ها یه کلاس خاص دارن یا یه ساختار مشخص.
            # برای تست، از والد دکمه انتخاب استفاده می‌کنیم.
            count = ticket_containers.count()
            logger.info(f"Found {count} ticket containers.")

            if count == 0:
                results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                # پردازش تا 3 تا از اولین نتایج
                for i in range(min(count, 3)):
                    try:
                        container = ticket_containers.nth(i)
                        # استخراج اطلاعات از هر container
                        # این قسمت کمی tricky هست چون باید داخل container جستجو کنیم.
                        # فرض کنیم قیمت و شماره صندلی و ... تو یه ساختار مشابه هستن.
                        # یه راه ساده‌تر: گرفتن تمام متن container و پردازش متنی
                        full_text = container.text_content()
                        if full_text:
                             # می‌تونیم یه پردازش ساده روی متن انجام بدیم تا اطلاعات مهم رو استخراج کنیم
                             # مثلاً فقط چند خط اول یا خطوطی که حاوی کلمات خاصی هستن
                             lines = full_text.strip().split('\n')
                             # فیلتر کردن خطوط خالی
                             lines = [line.strip() for line in lines if line.strip()]
                             # مثلاً 5 خط اول رو می‌گیریم
                             snippet = "\n".join(lines[:8]) 
                             results.append(f"نتیجه {i+1}:\n{snippet}\n---")
                        else:
                             results.append(f"نتیجه {i+1}: (متن خالی)")
                    except Exception as e:
                        logger.error(f"Error extracting data from ticket container {i}: {e}", exc_info=True)
                        results.append(f"❌ خطایی در استخراج اطلاعات بلیط {i+1}.")

            browser.close()
            logger.info("Browser closed (SIMPLE).")
            if not results:
                return "هیچ نتیجه‌ای از جستجوی پرواز بدست نیومد."
            return "\n".join(results)

    except Exception as e:
        logger.error(f"Error during SIMPLE flight schedule scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده زمانبندی پرواز رخ داد: {str(e)}"

# به‌روزرسانی wrapper برای استفاده از نسخه sync جدید
def search_alibaba_flight_schedules(origin: str, destination: str, date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, search_flight_schedules_simple, origin, destination, date)

# --- Hotel Search ---
# جستجوی هتل

def search_hotel_info_simple(city: str, checkin_date: str, checkout_date: str) -> str:
    """
    نسخه ساده (sync) از جستجوی هتل برای تست.
    Simple (sync) version of hotel search for testing.
    """
    logger.info(f"Starting search with parameters: city={city}, checkin={checkin_date}, checkout={checkout_date}")
    
    # *** تبدیل تاریخ ***
    try:
        checkin_day = checkin_date.split('/')[-1].split('-')[-1]
        checkout_day = checkout_date.split('/')[-1].split('-')[-1]
        logger.info(f"Extracted days: checkin={checkin_day}, checkout={checkout_day}")
    except Exception as e:
        logger.error(f"Error extracting days from dates: {e}")
        checkin_day = checkin_date 
        checkout_day = checkout_date

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/hotel"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. پر کردن مقصد
            logger.info("Filling destination field...")
            page.get_by_role("textbox", name="مقصد یا هتل (داخلی و خارجی)").click()
            page.wait_for_timeout(1000)
            
            # انتخاب شهر/هتل از suggestion
            # فرض: suggestion شامل نام شهر هست (مثلاً "کیشهرمزگان")
            suggestion_text = city # یا متن دقیق‌تری که تو suggestion هست
            logger.info(f"Looking for suggestion containing: {suggestion_text}")
            try:
                page.locator('a').filter(has_text=suggestion_text).click()
            except:
                logger.warning(f"Exact suggestion '{suggestion_text}' not found. Trying partial match...")
                page.locator('a').filter(has_text=city).first.click()
            
            # 2. انتخاب تاریخ ورود
            logger.info("Selecting check-in date...")
            # فرض: روی تقویم کلیک می‌کنه و بعد روز رو انتخاب می‌کنه
            # ممکنه نیاز به کلیک روی input تاریخ ورود باشه:
            # page.get_by_role("textbox", name="تاریخ ورود").click()
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on check-in day: {checkin_day}")
            # استفاده از locator مشابه recorder
            page.locator('span').filter(has_text=checkin_day).first.click()

            # 3. انتخاب تاریخ خروج
            logger.info("Selecting check-out date...")
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on check-out day: {checkout_day}")
            # nth(1) برای انتخاب دومین روز (اگه چند تا باشن)
            page.get_by_text(checkout_day).nth(1).click() 

            # 4. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که نشانه ظاهر شدن نتایج هست.
            # این ممکنه نیاز به تغییر داشته باشه. "هتل" یه انتخاب عمومی هست.
            # اگه المنت خاص‌تری تو recorder بود، اون رو استفاده کن.
            page.wait_for_selector("text=هتل", timeout=30000) 
            # یا اگه المنت خاص‌تری هست (مثلاً یه div با کلاس خاص)، اون رو استفاده کن.
            # page.wait_for_selector(".hotel-search-results-container", timeout=30000)

            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []
            
            # روش 1: پیدا کردن المنت‌هایی که اطلاعات هتل توشه.
            # این یه فرض اولیه هست. باید با inspect صفحه نتایج واقعی بررسی بشه.
            # مثلاً فرض کنیم هتل‌ها تو div هایی با کلاس 'HotelCard' یا 'hotel-item' هستن.
            # اما چون recorder چیز خاصی نشون نداد، از یه selector عمومی‌تر استفاده می‌کنیم.
            
            # یه راه دیگه: پیدا کردن المنت‌هایی که قیمت دارن، چون احتمالاً هتل‌ها قیمت دارن.
            # یا پیدا کردن المنت‌هایی که اسم "هتل" یا "اتاق" توشه.
            
            # فرض کنیم نتایج تو یه ساختار مشخص هستن. مثلاً هر هتل تو یه div.hotel-card هست.
            # hotel_cards = page.locator("div.hotel-card") # این selector باید تغییر کنه
            
            # برای شروع، از یه روش کلی‌تر استفاده می‌کنیم:
            # پیدا کردن همه المنت‌هایی که "تومان" یا "ریال" یا "شب" تو متنشون هست
            # چون اینا معمولاً تو قیمت هتل‌ها می‌یاد.
            potential_hotel_elements = page.locator("div:has-text('تومان'), div:has-text('ریال'), div:has-text('شب')")
            count = potential_hotel_elements.count()
            logger.info(f"Found {count} potential hotel elements.")
            
            if count == 0:
                 # اگه روش بالا جواب نداد، روش قبلی (جستجو برای "هتل") رو امتحان کن
                 logger.info("Trying alternative selector for hotel results...")
                 # فرض کنیم نتایج تو یه div با کلاس خاص هستن
                 # این selector ها باید با inspect کردن صفحه نتایج واقعی پیدا بشن.
                 hotel_cards = page.locator(".hotel-item, .HotelCard, [class*='hotel'], [class*='Hotel']")
                 count = hotel_cards.count()
                 logger.info(f"Found {count} hotel cards with alternative selector.")
                 if count == 0:
                      results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
                 else:
                      # پردازش hotel_cards
                      for i in range(min(count, 3)):
                          try:
                              card = hotel_cards.nth(i)
                              # استخراج اطلاعات از card
                              # این selector ها باید با inspect کردن صفحه واقعی پیدا بشن.
                              name_elem = card.locator(".hotel-name, .HotelCard__name, h3, [class*='name']")
                              rating_elem = card.locator(".hotel-rating, .HotelCard__rating, [class*='rating']")
                              price_elem = card.locator(".price, .HotelCard__price, [class*='price']")
                              location_elem = card.locator(".location, .HotelCard__location, [class*='location']")
                              
                              def safe_text_content(locator_obj):
                                  try:
                                      if locator_obj.count() > 0:
                                          return locator_obj.first.text_content(timeout=2000).strip()
                                      else:
                                          return ""
                                  except:
                                      return ""
                              
                              name = safe_text_content(name_elem) or "هتل نامشخص"
                              rating = safe_text_content(rating_elem) or "امتیاز ندارد"
                              price = safe_text_content(price_elem) or "قیمت نامشخص"
                              location = safe_text_content(location_elem) or ""
                              
                              results.append(f"🏨 {name} ({rating}) - {price} ({location})")
                          except Exception as e:
                              logger.warning(f"Error extracting data from hotel card {i+1}: {e}")
                              results.append(f"خطا در استخراج اطلاعات هتل {i+1}.")
            else:
                # پردازش potential_hotel_elements
                 # این روش ممکنه نتایج اضافی هم بگیره، پس باید فیلتر بشه.
                 # برای سادگی، فعلاً همون روش قبلی رو ادامه می‌دیم.
                 # ولی می‌تونی این قسمت رو بهبود بدی.
                 
                 # برگرد به روش قبلی برای استخراج نتایج، چون روش جدید ممکنه پیچیده باشه.
                 # استفاده از selector هایی که قبلاً تعریف کردیم (با اینکه ممکنه درست نباشن)
                 hotel_items = page.locator(".hotel-item, .HotelCard").all() # all() برای sync
                 if not hotel_items:
                      results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده (روش جایگزین).")
                 else:
                      logger.info(f"Found {len(hotel_items)} hotel items with previous selector.")
                      for i, item in enumerate(hotel_items[:3]):
                          try:
                              # استخراج اطلاعات از هر item
                              # selector ها باید با inspect کردن صفحه واقعی پیدا بشن.
                              # اینا selector های حدس زده شده هستن.
                              name_elem = item.locator(".hotel-name, .HotelCard__name, h3")
                              rating_elem = item.locator(".hotel-rating, .HotelCard__rating")
                              price_elem = item.locator(".price, .HotelCard__price").first
                              location_elem = item.locator(".location, .HotelCard__location")
                              
                              def safe_text_content_sync(locator_obj):
                                  try:
                                      # برای sync API، count() و text_content() نیازی به await ندارن
                                      if locator_obj.count() > 0:
                                          return locator_obj.text_content(timeout=2000).strip()
                                      else:
                                          return ""
                                  except:
                                      return ""
                              
                              name = safe_text_content_sync(name_elem) or "هتل نامشخص"
                              try:
                                  rating = safe_text_content_sync(rating_elem) or "امتیاز ندارد"
                              except:
                                  rating = "امتیاز ندارد"
                              try:
                                  price = safe_text_content_sync(price_elem) or "قیمت نامشخص"
                              except:
                                  price = "قیمت نامشخص"
                              try:
                                  location = safe_text_content_sync(location_elem) or ""
                              except:
                                  location = ""
                              
                              results.append(
                                  f"🏨 {name} "
                                  f"({rating}) - "
                                  f"{price} "
                                  f"({location})"
                              )
                          except Exception as e:
                              logger.warning(f"Error extracting data from a hotel item (method 2): {e}")
                              results.append(f"خطا در استخراج اطلاعات هتل {i+1} (روش جایگزین).")


            browser.close()
            logger.info("Browser closed (SIMPLE).")

            if results:
                return f"🏨 نتایج جستجوی هتل در {city} از {checkin_date} تا {checkout_date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره هتل در {city} از {checkin_date} تا {checkout_date} پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE hotel scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده هتل رخ داد: {str(e)}"

# به‌روزرسانی wrapper برای استفاده از نسخه sync جدید
def search_alibaba_hotel_info(city: str, checkin_date: str, checkout_date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, search_hotel_info_simple, city, checkin_date, checkout_date)


# --- Villa/Accommodation Search ---
# جستجوی ویلا/اقامتگاه

def search_villa_info_simple(city: str, checkin_date: str, checkout_date: str) -> str:
    """
    نسخه ساده (sync) از جستجوی اقامتگاه برای تست.
    Simple (sync) version of accommodation search for testing.
    """
    logger.info(f"Starting search with parameters: city={city}, checkin={checkin_date}, checkout={checkout_date}")
    
    # *** تبدیل تاریخ ***
    # این بخش خیلی مهم هست. recorder تاریخ '24' و '27' رو گرفت.
    # ما باید روزهای checkin و checkout رو از رشته‌های تاریخ استخراج کنیم.
    # فرض می‌کنیم تاریخ به فرمت 'YYYY/MM/DD' یا 'YYYY-MM-DD' داده می‌شه.
    try:
        checkin_day = checkin_date.split('/')[-1].split('-')[-1] # گرفتن آخرین بخش (روز)
        checkout_day = checkout_date.split('/')[-1].split('-')[-1]
        logger.info(f"Extracted days: checkin={checkin_day}, checkout={checkout_day}")
    except Exception as e:
        logger.error(f"Error extracting days from dates: {e}")
        # اگه نتونه، خود روز رو می‌فرسته یا یه مقدار پیش‌فرض
        checkin_day = checkin_date 
        checkout_day = checkout_date

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/accommodation"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. پر کردن مقصد
            logger.info("Filling destination field...")
            page.get_by_role("textbox", name="مقصد یا نوع اقامتگاه").click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر/اقامتگاه از suggestion
            # *** مهم: متن دقیق suggestion ممکنه متفاوت باشه. ***
            # مثلاً اگه city='رامسر' باشه، suggestion ممکنه 'اقامتگاه های شهر رامسر' باشه.
            # برای سادگی، فعلاً سعی می‌کنیم متنی پیدا کنیم که شامل city هست.
            # این ممکنه نیاز به تنظیم بیشتری داشته باشه.
            suggestion_text = f"اقامتگاه های شهر {city}"
            logger.info(f"Looking for suggestion containing: {suggestion_text}")
            try:
                page.locator('a').filter(has_text=suggestion_text).click()
            except:
                logger.warning(f"Exact suggestion '{suggestion_text}' not found. Trying partial match...")
                # اگه متن دقیق پیدا نشد، سعی می‌کنیم المنتی پیدا کنیم که city توشه.
                page.locator('a').filter(has_text=city).first.click()
            
            # 2. انتخاب تاریخ ورود
            logger.info("Selecting check-in date...")
            page.get_by_role("textbox", name="تاریخ ورود").click()
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on check-in day: {checkin_day}")
            page.get_by_text(checkin_day).first.click()

            # 3. انتخاب تاریخ خروج
            logger.info("Selecting check-out date...")
            # فرض می‌کنیم تقویم هنوز باز هست یا دوباره باز می‌شه.
            # اگه نیاز به کلیک روی فیلد تاریخ خروج هست، اون خط رو هم اضافه کن.
            # page.get_by_role("textbox", name="تاریخ خروج").click() 
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on check-out day: {checkout_day}")
            # nth(1) یعنی دومین المنتی که متن checkout_day رو داره (اگه چند تا باشن)
            page.get_by_text(checkout_day).nth(1).click() 

            # 4. کلیک روی دکمه "افزودن" (اگه هست)
            logger.info("Clicking 'افزودن' button...")
            try:
                page.get_by_role("button", name="افزودن").click()
                page.wait_for_timeout(500) # کمی صبر کن
            except:
                logger.info("'افزودن' button not found or not needed.")

            # 5. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که تو کد recorder ظاهر می‌شد به عنوان نشانه
            # این یه رشته منحصر به فرد از نتایج هست. ممکنه نیاز به تغییر داشته باشه.
            page.wait_for_selector("section:has-text('رزرو آنی')", timeout=30000)

            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []
            # روش 1: پیدا کردن همه المنت‌هایی که اطلاعات اقامتگاه توشه
            # دوباره از المنتی که قبلاً استفاده کردیم به عنوان پایه استفاده می‌کنیم
            accommodation_containers = page.locator("section:has-text('رزرو آنی')")
            count = accommodation_containers.count()
            logger.info(f"Found {count} accommodation containers.")
            
            if count == 0:
                results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                # پردازش تا 3 تا از اولین نتایج
                for i in range(min(count, 3)):
                    try:
                        container = accommodation_containers.nth(i)
                        # استخراج اطلاعات از هر container
                        # این قسمت کمی tricky هست. باید با inspect کردن صفحه نتایج دقیق‌تر شه.
                        # یه راه ساده‌تر: گرفتن تمام متن container و پردازش متنی
                        full_text = container.text_content()
                        if full_text:
                            lines = full_text.strip().split('\n')
                            lines = [line.strip() for line in lines if line.strip()]
                            
                            # *** اینجا نیاز به بررسی دقیق‌تر داریم ***
                            # فرض‌ها ممکنه درست نباشن. باید با inspect نتایج واقعی سایت بررسی شه.
                            name = lines[0] if lines else "اقامتگاه نامشخص"
                            # فرض کنیم خطی با امتیاز هست (5/4.9)
                            rating_line = next((line for line in lines if '/' in line and '.' in line), "")
                            # فرض کنیم خطی با قیمت هست (عدد + تومان)
                            price_line = next((line for line in lines if "تومان" in line), "قیمت نامشخص")
                            # فرض کنیم خطی با ظرفیت یا امکانات هست
                            details_line = next((line for line in lines if ("تخت" in line or "ظرفیت" in line)), "")
                            
                            results.append(f"🏡 {name} {rating_line} - {price_line} - {details_line}")
                        else:
                            results.append(f"خطا در استخراج اطلاعات اقامتگاه {i+1}.")
                    except Exception as e:
                        logger.warning(f"Error extracting data from accommodation container {i+1}: {e}")
                        results.append(f"خطا در استخراج اطلاعات اقامتگاه {i+1}.")

            browser.close()
            logger.info("Browser closed (SIMPLE).")

            if results:
                return f"🏡 نتایج جستجوی اقامتگاه در {city} از {checkin_date} تا {checkout_date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره اقامتگاه در {city} از {checkin_date} تا {checkout_date} پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE villa/accommodation scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده اقامتگاه رخ داد: {str(e)}"

# به‌روزرسانی wrapper برای استفاده از نسخه sync جدید
def search_alibaba_villa_info(city: str, checkin_date: str, checkout_date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, search_villa_info_simple, city, checkin_date, checkout_date)

# --- Train Search ---

def search_train_schedules_simple(origin: str, destination: str, date: str) -> str:
    """
    نسخه ساده (sync) از جستجوی قطار برای تست.
    Simple (sync) version of train search for testing.
    """
    logger.info(f"Starting search with parameters: origin={origin}, destination={destination}, date={date}")
    # تبدیل تاریخ به فرمت مورد نیاز سایت (اگر لازم باشه)
    # مثلاً اگه date = "1403/07/15" باشه، باید "15" رو استخراج کنیم
    # این یه ساده‌سازی هست. در عمل ممکنه به تبدیل دقیق‌تری نیاز باشه.
    try:
        day = date.split('/')[-1] # گرفتن آخرین بخش تاریخ که روز هست
        logger.info(f"Extracted day for date picker: {day}")
    except:
        logger.error(f"Could not extract day from date: {date}")
        day = date # اگه نتونه، خود تاریخ رو می‌فرسته

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/train-ticket"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. پر کردن مبدا
            logger.info("Filling origin field...")
            page.get_by_role("textbox", name="مبدا (شهر)").click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر مبدا از suggestion
            logger.info(f"Selecting origin: {origin}")
            # تغییر: جستجو برای المنت‌هایی که حاوی origin هستن
            try:
                page.locator('a').filter(has_text=lambda text: origin in text).first.click()
            except:
                logger.warning(f"Could not find suggestion for origin '{origin}' with partial match. Trying exact match...")
                # اگه روش بالا جواب نداد، سعی می‌کنه المنتی با متن دقیق origin پیدا کنه
                page.locator('a').filter(has_text=origin).first.click()

            # 2. پر کردن مقصد
            logger.info("Filling destination field...")
            # فرض می‌کنیم فیلد مقصد هم به همین شکل هست (باید چک بشه)
            # اگه فیلد مقصد یه textbox دیگه هست، باید selector ش رو پیدا کنیم.
            # برای حالات مختلف، می‌تونیم از filter یا nth استفاده کنیم.
            # فرض کنیم دومین textbox فیلد مقصد هست:
            page.get_by_role("textbox", name="مقصد (شهر)").click() # یا nth=1
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر مقصد از suggestion
            logger.info(f"Selecting destination: {destination}")
             # تغییر: جستجو برای المنت‌هایی که حاوی destination هستن
            try:
                page.locator('a').filter(has_text=lambda text: destination in text).first.click()
            except:
                logger.warning(f"Could not find suggestion for destination '{destination}' with partial match. Trying exact match...")
                # اگه روش بالا جواب نداد، سعی می‌کنه المنتی با متن دقیق destination پیدا کنه
                page.locator('a').filter(has_text=destination).first.click()

            # 3. انتخاب تاریخ
            logger.info("Selecting date...")
            # کلیک روی input تاریخ برای باز کردن datepicker
            # فرض کنیم سومین textbox فیلد تاریخ هست:
            page.get_by_role("textbox", name="تاریخ رفت").click() # یا nth=2 یا placeholder خاص
            # صبر کمی برای باز شدن تقویم
            page.wait_for_timeout(1000)
            # کلیک روی روز مورد نظر
            logger.info(f"Clicking on day: {day}")
            page.get_by_text(day).first.click()

            # 4. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که تو کد recorder ظاهر می‌شد به عنوان نشانه
            # این یه رشته منحصر به فرد از نتایج هست.
            page.wait_for_selector("div:has-text('تومانانتخاب بلیط')", timeout=30000)

            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []
            # روش 1: پیدا کردن همه المنت‌هایی که اطلاعات بلیط توشه
            # دوباره از المنتی که قبلاً استفاده کردیم به عنوان پایه استفاده می‌کنیم
            ticket_containers = page.locator("div:has-text('تومانانتخاب بلیط')")
            count = ticket_containers.count()
            logger.info(f"Found {count} ticket containers.")
            
            if count == 0:
                results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
            else:
                # پردازش تا 3 تا از اولین نتایج
                for i in range(min(count, 3)):
                    try:
                        container = ticket_containers.nth(i)
                        # استخراج اطلاعات از هر container
                        # این قسمت کمی tricky هست چون باید داخل container جستجو کنیم.
                        # فرض کنیم قیمت و شماره صندلی و ... تو یه ساختار مشابه هستن.
                        
                        # یه راه ساده‌تر: گرفتن تمام متن container و پردازش متنی
                        full_text = container.text_content()
                        if full_text:
                            # یه پردازش ساده متن برای استخراج اطلاعات کلیدی
                            # این فقط یه مثال هست و باید با دقت بیشتری انجام بشه
                            lines = full_text.strip().split('\n')
                            # فیلتر کردن خطوط خالی
                            lines = [line.strip() for line in lines if line.strip()]
                            
                            # فرض کنیم خط اول اسم قطار یا شماره بلیط هست
                            name = lines[0] if lines else "قطار نامشخص"
                            # فرض کنیم خطی که "تومان" توشه، قیمت هست
                            price_line = next((line for line in lines if "تومان" in line), "قیمت نامشخص")
                            # فرض کنیم خطی که "صندلی" توشه، اطلاعات صندلی هست
                            seat_line = next((line for line in lines if "صندلی" in line), "")
                            
                            results.append(f"قطار: {name}, {price_line} {seat_line}")
                        else:
                            results.append(f"خطا در استخراج اطلاعات بلیط {i+1}.")
                    except Exception as e:
                        logger.warning(f"Error extracting data from ticket container {i+1}: {e}")
                        results.append(f"خطا در استخراج اطلاعات بلیط {i+1}.")

            browser.close()
            logger.info("Browser closed (SIMPLE).")

            if results:
                return f"🚆 نتایج جستجوی قطار از {origin} به {destination} در تاریخ {date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره قطار از {origin} به {destination} در تاریخ {date} پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE train schedule scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده زمانبندی قطار رخ داد: {str(e)}"

# wrapper نهایی (همون قبلی)
def search_aliababa_train_schedules(origin: str, destination: str, date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, search_train_schedules_simple, origin, destination, date)


# --BusSreach-- 

def search_bus_schedules_simple(origin: str, destination: str, date: str) -> str:
    """
    نسخه ساده (sync) از جستجوی اتوبوس برای تست.
    Simple (sync) version of bus search for testing.
    """
    logger.info(f"Starting search with parameters: origin={origin}, destination={destination}, date={date}")
    # تبدیل تاریخ به فرمت مورد نیاز سایت (اگر لازم باشه)
    try:
        day = date.split('/')[-1] # گرفتن آخرین بخش تاریخ که روز هست
        logger.info(f"Extracted day for date picker: {day}")
    except:
        logger.error(f"Could not extract day from date: {date}")
        day = date # اگه نتونه، خود تاریخ رو می‌فرسته

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/bus-ticket"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. پر کردن مبدا
            logger.info("Filling origin field...")
            # استفاده از selector از recorder
            page.locator('div').filter(has_text=r'^مقصد \(شهر، پایانه\)$').locator('div').click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر مبدا از suggestion
            # فرض: suggestion شامل نام شهر و استان هست (مثلاً "اصفهان همه پایانه هااصفهان")
            # برای سادگی، اول سعی می‌کنیم متنی پیدا کنیم که فقط نام شهر توشه.
            logger.info(f"Selecting origin: {origin}")
            try:
                page.locator('a').filter(has_text=origin).first.click()
            except:
                logger.warning(f"Could not find suggestion for origin '{origin}' with simple filter. Trying partial match...")
                # اگه نشد، سعی می‌کنیم هر المنتی که شامل origin هست رو پیدا کنیم
                page.locator('a').filter(has_text=lambda text: origin in text).first.click()

            # 2. پر کردن مقصد
            logger.info("Filling destination field...")
            # فرض: فیلد مقصد یه textbox ساده هست. این باید با inspect کردن صفحه واقعی بررسی بشه.
            # برای حالات مختلف، می‌تونیم از filter یا nth استفاده کنیم.
            # فرض کنیم دومین div.filter مربوط به مقصد هست:
            page.locator('div').filter(has_text=r'^مقصد \(شهر، پایانه\)$').locator('div').click()
            # صبر کمی برای ظاهر شدن suggestion
            page.wait_for_timeout(1000)
            # انتخاب شهر مقصد از suggestion
            logger.info(f"Selecting destination: {destination}")
            try:
                page.locator('a').filter(has_text=destination).first.click()
            except:
                logger.warning(f"Could not find suggestion for destination '{destination}' with simple filter. Trying partial match...")
                page.locator('a').filter(has_text=lambda text: destination in text).first.click()

            # 3. انتخاب تاریخ
            logger.info("Selecting date...")
            # کلیک روی input تاریخ برای باز کردن datepicker
            # فرض: input تاریخ یه textbox با name خاص هست
            page.get_by_role("textbox", name="تاریخ حرکت").click() # یا placeholder خاص
            # صبر کمی برای باز شدن تقویم
            page.wait_for_timeout(1000)
            # کلیک روی روز مورد نظر
            logger.info(f"Clicking on day: {day}")
            page.get_by_text(day).first.click()

            # 4. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که تو کد recorder ظاهر می‌شد به عنوان نشانه
            # این یه رشته منحصر به فرد از نتایج هست.
            page.wait_for_selector("text=بین‌راهی", timeout=30000) # یا "text=تکمیل ظرفیت"

            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []
            # روش 1: پیدا کردن همه المنت‌هایی که اطلاعات بلیط توشه
            # دوباره از المنتی که قبلاً استفاده کردیم به عنوان پایه استفاده می‌کنیم
            # این یه فرض اولیه هست. باید با inspect کردن صفحه نتایج واقعی بررسی بشه.
            # فرض کنیم هر نتیجه تو یه div با کلاس خاص هست.
            bus_items = page.locator(".bus-item, .BusCard, [class*='bus'], [class*='Bus']") # این selector باید تغییر کنه
            count = bus_items.count()
            logger.info(f"Found {count} potential bus items.")
            
            if count == 0:
                 # اگه روش بالا جواب نداد، روش قبلی (جستجو برای "اتوبوس") رو امتحان کن
                 logger.info("Trying alternative selector for bus results...")
                 # فرض کنیم نتایج تو یه div با کلاس خاص هستن
                 bus_cards = page.locator(".bus-search-result-item, .available-bus, [data-test*='bus']")
                 count = bus_cards.count()
                 logger.info(f"Found {count} bus cards with alternative selector.")
                 if count == 0:
                      results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
                 else:
                      # پردازش bus_cards
                      for i in range(min(count, 3)):
                          try:
                              card = bus_cards.nth(i)
                              # استخراج اطلاعات از card
                              # این selector ها باید با inspect کردن صفحه واقعی پیدا بشن.
                              # مثلاً:
                              company_elem = card.locator(".company-name, .bus-company, [class*='company']")
                              departure_elem = card.locator(".departure-time, .bus-departure, [class*='departure']")
                              arrival_elem = card.locator(".arrival-time, .bus-arrival, [class*='arrival']")
                              price_elem = card.locator(".price, .bus-price, [class*='price']")
                              seats_elem = card.locator(".seats-left, .bus-seats, [class*='seats']")
                              
                              def safe_text_content(locator_obj):
                                  try:
                                      if locator_obj.count() > 0:
                                          return locator_obj.first.text_content(timeout=2000).strip()
                                      else:
                                          return ""
                                  except:
                                      return ""
                              
                              company = safe_text_content(company_elem) or "شرکت نامشخص"
                              departure = safe_text_content(departure_elem) or "زمان حرکت نامشخص"
                              arrival = safe_text_content(arrival_elem) or "زمان رسیدن نامشخص"
                              price = safe_text_content(price_elem) or "قیمت نامشخص"
                              seats = safe_text_content(seats_elem) or ""
                              
                              results.append(f"🚌 {company} - {departure} -> {arrival} - {price} ({seats})")
                          except Exception as e:
                              logger.warning(f"Error extracting data from bus card {i+1}: {e}")
                              results.append(f"خطا در استخراج اطلاعات اتوبوس {i+1}.")
            else:
                # پردازش bus_items
                 for i in range(min(count, 3)):
                     try:
                         item = bus_items.nth(i)
                         # استخراج اطلاعات از item
                         # selector ها باید با inspect کردن صفحه واقعی پیدا بشن.
                         company_elem = item.locator(".company-name, .bus-company")
                         departure_elem = item.locator(".departure-time, .bus-departure")
                         arrival_elem = item.locator(".arrival-time, .bus-arrival")
                         price_elem = item.locator(".price, .bus-price").first
                         seats_elem = item.locator(".seats-left, .bus-seats")
                         
                         def safe_text_content_sync(locator_obj):
                             try:
                                 if locator_obj.count() > 0:
                                     return locator_obj.text_content(timeout=2000).strip() # برای sync
                                 else:
                                     return ""
                             except:
                                 return ""
                         
                         company = safe_text_content_sync(company_elem) or "شرکت نامشخص"
                         departure = safe_text_content_sync(departure_elem) or "زمان حرکت نامشخص"
                         arrival = safe_text_content_sync(arrival_elem) or "زمان رسیدن نامشخص"
                         price = safe_text_content_sync(price_elem) or "قیمت نامشخص"
                         seats = safe_text_content_sync(seats_elem) or ""
                         
                         results.append(f"🚌 {company} - {departure} -> {arrival} - {price} ({seats})")
                     except Exception as e:
                         logger.warning(f"Error extracting data from bus item {i+1}: {e}")
                         results.append(f"خطا در استخراج اطلاعات اتوبوس {i+1}.")

            browser.close()
            logger.info("Browser closed (BUS SIMPLE).")

            if results:
                return f"🚌 نتایج جستجوی اتوبوس از {origin} به {destination} در تاریخ {date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره اتوبوس از {origin} به {destination} در تاریخ {date} پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE bus schedule scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده زمانبندی اتوبوس رخ داد: {str(e)}"

# به‌روزرسانی wrapper برای استفاده از نسخه sync جدید
def search_aliaba_bus_schedules(origin: str, destination: str, date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, search_bus_schedules_simple, origin, destination, date)

# --TourSearch--

def search_tour_info_simple(origin: str, destination: str, start_date: str, end_date: str) -> str:
    """
    نسخه ساده (sync) از جستجوی تور برای تست.
    Simple (sync) version of tour search for testing.
    """
    logger.info(f"Starting tour search with parameters: origin={origin}, destination={destination}, start_date={start_date}, end_date={end_date}")
    # تبدیل تاریخ به فرمت مورد نیاز سایت (اگر لازم باشه)
    try:
        start_day = start_date.split('/')[-1]
        end_day = end_date.split('/')[-1]
        logger.info(f"Extracted days for date pickers: start={start_day}, end={end_day}")
    except:
        logger.error(f"Could not extract days from dates: start={start_date}, end={end_date}")
        start_day = start_date
        end_day = end_date

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})

            url = "https://www.alibaba.ir/tour"
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until='networkidle')

            # === پر کردن فرم ===
            # 1. پر کردن مبدا
            logger.info("Filling origin field...")
            page.get_by_role("textbox", name="مبدا (شهر)").click()
            page.wait_for_timeout(1000)
            logger.info(f"Selecting origin: {origin}")
            page.locator('a').filter(has_text=f"^{origin}$").click() # فرض: متن دقیق شهر

            # 2. پر کردن مقصد
            logger.info("Filling destination field...")
            # فرض: فیلد مقصد هم یه textbox با name خاص هست
            page.get_by_role("textbox", name="مقصد (شهر)").click() # یا placeholder خاص
            page.wait_for_timeout(1000)
            logger.info(f"Selecting destination: {destination}")
            page.locator('a').filter(has_text=f"^{destination}$").click() # فرض: متن دقیق شهر

            # 3. (اختیاری) انتخاب نوع تور - فعلاً این مرحله رو رد می‌کنیم
            # logger.info("Selecting tour type...")
            # page.locator('label').filter({ hasText: 'تور گردشگری ...' }).locator('div span').click()

            # 4. انتخاب تاریخ رفت
            logger.info("Selecting start date...")
            page.get_by_role("textbox", name="تاریخ رفت").click()
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on start day: {start_day}")
            page.get_by_text(start_day, exact=True).first.click()

            # 5. انتخاب تاریخ برگشت
            logger.info("Selecting end date...")
            # فرض: تقویم هنوز باز هست یا دوباره باز می‌شه.
            # page.get_by_role("textbox", name="تاریخ برگشت").click() # اگه نیاز به کلیک داره
            page.wait_for_timeout(1000)
            logger.info(f"Clicking on end day: {end_day}")
            page.get_by_text(end_day).nth(1).click() # nth(1) برای دومین تاریخ

            # 6. (اختیاری) انتخاب تعداد مسافران - فعلاً این مرحله رو رد می‌کنیم
            # logger.info("Selecting passengers...")
            # page.get_by_role("textbox", name="مسافران").click()

            # 7. کلیک روی دکمه جستجو
            logger.info("Clicking search button...")
            page.get_by_role("button", name="جستجو").click()

            # === صبر کردن برای نتایج ===
            logger.info("Waiting for results...")
            # استفاده از المنتی که تو کد recorder ظاهر می‌شد به عنوان نشانه
            page.wait_for_selector("text=ستاره", timeout=30000) # یا "text=تومان"

            # === استخراج اطلاعات ===
            logger.info("Extracting results...")
            results = []
            # روش 1: پیدا کردن همه المنت‌هایی که اطلاعات تور توشه
            # فرض کنیم هر نتیجه تو یه div با کلاس خاص هست.
            tour_items = page.locator(".tour-item, .TourCard, [class*='tour'], [class*='Tour']") # این selector باید تغییر کنه
            count = tour_items.count()
            logger.info(f"Found {count} potential tour items.")
            
            if count == 0:
                 # اگه روش بالا جواب نداد، روش قبلی (جستجو برای "تور") رو امتحان کن
                 logger.info("Trying alternative selector for tour results...")
                 tour_cards = page.locator(".tour-search-result-item, .available-tour, [data-test*='tour']")
                 count = tour_cards.count()
                 logger.info(f"Found {count} tour cards with alternative selector.")
                 if count == 0:
                      results.append("نتیجه‌ای یافت نشد یا ساختار صفحه تغییر کرده.")
                 else:
                      for i in range(min(count, 3)):
                          try:
                              card = tour_cards.nth(i)
                              # استخراج اطلاعات از card
                              name_elem = card.locator(".tour-name, .TourCard__name, h3, [class*='name']")
                              price_elem = card.locator(".price, .TourCard__price, [class*='price']")
                              rating_elem = card.locator(".rating, .TourCard__rating, [class*='rating']")
                              duration_elem = card.locator(".duration, .TourCard__duration, [class*='duration']")
                              
                              def safe_text_content(locator_obj):
                                  try:
                                      if locator_obj.count() > 0:
                                          return locator_obj.first.text_content(timeout=2000).strip()
                                      else:
                                          return ""
                                  except:
                                      return ""
                              
                              name = safe_text_content(name_elem) or "تور نامشخص"
                              price = safe_text_content(price_elem) or "قیمت نامشخص"
                              rating = safe_text_content(rating_elem) or ""
                              duration = safe_text_content(duration_elem) or ""
                              
                              results.append(f"🌍 {name} - {price} ({rating}) - {duration}")
                          except Exception as e:
                              logger.warning(f"Error extracting data from tour card {i+1}: {e}")
                              results.append(f"خطا در استخراج اطلاعات تور {i+1}.")
            else:
                # پردازش tour_items
                 for i in range(min(count, 3)):
                     try:
                         item = tour_items.nth(i)
                         # استخراج اطلاعات از item
                         name_elem = item.locator(".tour-name, .TourCard__name")
                         price_elem = item.locator(".price, .TourCard__price").first
                         rating_elem = item.locator(".rating, .TourCard__rating")
                         duration_elem = item.locator(".duration, .TourCard__duration")
                         
                         def safe_text_content_sync(locator_obj):
                             try:
                                 if locator_obj.count() > 0:
                                     return locator_obj.text_content(timeout=2000).strip() # برای sync
                                 else:
                                     return ""
                             except:
                                 return ""
                         
                         name = safe_text_content_sync(name_elem) or "تور نامشخص"
                         price = safe_text_content_sync(price_elem) or "قیمت نامشخص"
                         rating = safe_text_content_sync(rating_elem) or ""
                         duration = safe_text_content_sync(duration_elem) or ""
                         
                         results.append(f"🌍 {name} - {price} ({rating}) - {duration}")
                     except Exception as e:
                         logger.warning(f"Error extracting data from tour item {i+1}: {e}")
                         results.append(f"خطا در استخراج اطلاعات تور {i+1}.")

            browser.close()
            logger.info("Browser closed (TOUR SIMPLE).")

            if results:
                return f"🌍 نتایج جستجوی تور از {origin} به {destination} از {start_date} تا {end_date}:\n" + "\n".join(results)
            else:
                return f"اطلاعاتی درباره تور از {origin} به {destination} از {start_date} تا {end_date} پیدا نکردم."

    except Exception as e:
        logger.error(f"Error during SIMPLE tour info scraping: {e}", exc_info=True)
        return f"❌ خطایی در جستجوی ساده اطلاعات تور رخ داد: {str(e)}"

# اضافه کردن wrapper برای ابزار تور
def search_alibaba_tour_info(origin: str, destination: str, start_date: str, end_date: str) -> str:
    """
    Wrapper نهایی که تابع sync رو تو یه thread جدا اجرا می‌کنه.
    Final wrapper that runs the sync function in a separate thread.
    """
    loop = asyncio.get_event_loop()
    # توجه: این تابع 4 آرگومان می‌گیره، در حالی که wrapper قبلی‌ها 3 تا می‌گرفتن
    # باید یه تابع lambda یا partial بسازیم تا آرگومان‌ها رو درست بفرستیم
    from functools import partial
    return loop.run_in_executor(None, partial(search_tour_info_simple, origin=origin, destination=destination, start_date=start_date, end_date=end_date))


