from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_classcentral_courses(query, pages=1):
    options = Options()
    options.add_argument("--headless")  # For no GUI on Railway
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error launching browser in scraper: {e}")
        return {"error": f"Could not launch browser in scraper: {e}"}

    courses_data = []

    try:
        for page in range(1, int(pages) + 1):
            url = f"https://www.classcentral.com/search?q={query}&page={page}"
            driver.get(url)

            try:
                WebDriverWait(driver, 20).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "li.course-list-course"))
                )
            except TimeoutException:
                print(f"Timeout while waiting for page {page} to load.")
                continue

            courses = driver.find_elements(By.CSS_SELECTOR, "li.course-list-course")
            for course in courses:
                try:
                    title = course.find_element(By.CSS_SELECTOR, "h2.text-1.weight-semi.line-tight.margin-bottom-xxsmall").text.strip()
                    description = course.find_element(By.CSS_SELECTOR, "p.text-2.margin-bottom-xsmall a").text.strip()

                    try:
                        image = course.find_element(By.CSS_SELECTOR, "img.absolute.top.left.width-100.height-100.cover.block").get_attribute("src")
                    except NoSuchElementException:
                        image = None

                    # Extract details
                    details = {}
                    details_list = course.find_elements(By.CSS_SELECTOR, "ul.margin-top-small li")
                    for item in details_list:
                        try:
                            icon_class = item.find_element(By.CSS_SELECTOR, "i").get_attribute("class")
                            text_element = item.find_element(By.CSS_SELECTOR, "span.text-3, a.text-3")
                            text = text_element.text.strip()

                            if "icon-provider" in icon_class:
                                details["provider"] = text
                            elif "icon-clock" in icon_class:
                                details["duration"] = text
                            elif "icon-calendar" in icon_class:
                                details["start_date"] = text
                            elif "icon-dollar" in icon_class:
                                details["pricing"] = text
                        except NoSuchElementException:
                            text = item.text.strip()
                            if "On-Demand" in text or "Starts" in text:
                                details["start_date"] = text
                            elif "week" in text or "hour" in text or "day" in text:
                                details["duration"] = text
                            elif "Free" in text or "Paid" in text:
                                details["pricing"] = text

                    courses_data.append({
                        "title": title,
                        "description": description,
                        "image": image,
                        "details": details
                    })

                except Exception as e:
                    print(f"Error parsing course: {e}")
                    continue

    finally:
        driver.quit()

    return courses_data
