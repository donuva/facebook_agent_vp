# Import các thư viện cần thiết
import os
import requests
import json
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api._context_manager import PlaywrightContextManager

# Định nghĩa các hằng số đường dẫn và URL cơ bản
SAVE_DIR = "cloned_site"
URL_BASE = "https://www.vpbank.com.vn/"

# Tạo thư mục lưu kết quả theo thời gian crawl
timestamp = datetime.now()
date_str = timestamp.strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join("crawl_data", date_str)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hàm lưu nội dung văn bản vào file
def save_content(content, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Hàm crawl nội dung chi tiết của từng trang
def crawl_content(text: str, url: str, p: PlaywrightContextManager):
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")

    results = {"title": text, "data": [], "documents": []}
    items = page.locator(".card-detail-content__body__item")
    count = items.count()

    for i in range(count):
        item = items.nth(i)
        try:
            title = item.get_attribute("id")
            if not title:
                continue
        except:
            continue

        # Nếu là phần câu hỏi thường gặp (FAQ)
        if title == "faqs":
            faq_list = []
            faq_cards = item.locator(".basic-accordion__card")
            faq_count = faq_cards.count()

            for j in range(faq_count):
                card = faq_cards.nth(j)
                try:
                    # Lấy câu hỏi
                    question = (
                        card.locator(".basic-accordion__card__header__text a")
                        .inner_text()
                        .strip()
                    )
                    # Lấy câu trả lời
                    answer = (
                        card.locator(".basic-accordion__card__collapse__content")
                        .inner_text()
                        .strip()
                    )
                    if question and answer:
                        faq_list.append({"question": question, "answer": answer})
                except:
                    continue

            if faq_list:
                results["data"].append({title: faq_list})

        # Nếu là phần tài liệu (documents)
        elif title == "documents":
            documents_info = []
            doc_links = item.locator(".card-detail-content__body__item__right a")
            doc_count = doc_links.count()

            for j in range(doc_count):
                try:
                    link = doc_links.nth(j)
                    href = link.get_attribute("href")
                    filename = os.path.basename(href)
                    pdf_path = os.path.join(OUTPUT_DIR, filename)
                    # Nếu là file PDF thì tải về
                    if filename.endswith(".pdf"):
                        r = requests.get(URL_BASE + href)
                        with open(pdf_path, "wb") as f:
                            f.write(r.content)
                            documents_info.append(
                                {
                                    "title": filename,
                                    "url": href,
                                    "local_file": filename,
                                }
                            )
                except Exception as e:
                    print(f"❌ Lỗi khi xử lý document link: {e}")
                    continue

            # Nếu có nội dung văn bản thì lưu vào results
            if content_texts:
                results["data"].append({title: documents_info})

        # Nếu là phần nội dung văn bản thông thường
        else:
            content_texts = []
            paragraphs = item.locator(".card-detail-content__body__item__right li")
            li_count = paragraphs.count()

            if li_count:
                for j in range(li_count):
                    try:
                        text_p = paragraphs.nth(j).inner_text().strip()
                        if text_p:
                            content_texts.append(text_p)
                    except:
                        continue
            else:
                try:
                    content = (
                        item.locator(".card-detail-content__body__item__right")
                        .inner_text()
                        .strip()
                    )
                    if content:
                        content_texts.append(content)
                except:
                    pass

            if content_texts:
                results["data"].append({title: content_texts})

    browser.close()
    return results

# Hàm crawl từng trang chuyên mục cụ thể
def crawl_page(text: str, url: str, p: PlaywrightContextManager):
    try:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL_BASE + url, wait_until="networkidle")

        item_links = page.locator(".card-item__description")
        count = item_links.count()

        if count == 0:
            print("❌ Không tìm thấy phần tử nào.")
            return

        all_results = []

        for i in range(count):
            item = item_links.nth(i)

            a_tag = item.locator("h3.name a")
            name = a_tag.inner_text()
            href = a_tag.get_attribute("href")

            # Gọi hàm crawl chi tiết
            results = crawl_content(name, href, p)
            if results:
                all_results.append(results)

        # Lưu kết quả vào file JSON
        file_name = f"{OUTPUT_DIR}/{text}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"✅ Đã lưu vào file: {file_name}")
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi trong quá trình crawl trang: {e}")
    finally:
        if browser:
            browser.close()

# Chạy chính - bắt đầu từ sitemap để lấy các liên kết trang con
with sync_playwright() as p:
    browser = p.chromium.launch()

    # Mở sitemap để lấy danh sách các chuyên mục người dùng
    page = browser.new_page()
    page.goto(URL_BASE + "sitemap", wait_until="networkidle")

    category_locator = page.locator(".category")

    sitemap = category_locator.nth(0)  # có thể là phần tổng thể
    user_partition = category_locator.nth(1)  # phần cho người dùng cá nhân

    # Lấy tất cả các liên kết trong chuyên mục người dùng, loại bỏ các thẻ tiêu đề
    links = user_partition.locator(":not(h1):not(h2):not(h3):not(h4):not(h5):not(h6) a")
    print(links.count())

    for j in range(links.count()):
        print(j)
        href = links.nth(j).get_attribute("href")
        text = links.nth(j).inner_text()
        print(f"🔗 {text} --> {href}")

        # Crawl từng trang chuyên mục
        crawl_page(text, href, p)
