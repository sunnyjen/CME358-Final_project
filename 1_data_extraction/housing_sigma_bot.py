from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
current_dir = Path.cwd()

PHONE_NUMBER = "6473230251"
PASSWORD = "Jenn2015"
def extract_listings(html_content):

    soup = BeautifulSoup(html_content, "html.parser")
    data = []

    # Find all listing containers
    listings = soup.find_all("article", class_="pc-listing-card")

    for listing in listings:
        # Extract the link
        link_tag = listing.find("a", class_="photo-wrapper")
        link = link_tag["href"] if link_tag else None

        # Extract the strikethrough price
        strikethrough_price_tag = listing.find("span", class_="line-through")
        strikethrough_price = strikethrough_price_tag.text.strip() if strikethrough_price_tag else None

        # Extract the sold price
        sold_price_tag = listing.find("span", class_="special")
        sold_price = sold_price_tag.text.strip() if sold_price_tag else None

        # Extract the property type
        property_type_tag = listing.find("p", class_="type")
        property_type = property_type_tag.text.strip() if property_type_tag else None

        # Extract the address
        address_tag = listing.find("h3", class_="address")
        address = address_tag.text.strip() if address_tag else None

        date_tag = listing.find("div", class_="date-preview")
        date_text = date_tag.text.strip() if date_tag else None

        # Extract bedrooms, bathrooms, and garages
        bedrooms_tag = listing.find("p", string=lambda text: text and "bedroom" in text.lower())
        bedrooms = bedrooms_tag.text.split("-")[1].strip() if bedrooms_tag else None

        bathrooms_tag = listing.find("p", string=lambda text: text and "bathroom" in text.lower())
        bathrooms = bathrooms_tag.text.split("-")[1].strip() if bathrooms_tag else None

        garages_tag = listing.find("p", string=lambda text: text and "garage" in text.lower())
        garages = garages_tag.text.split("-")[1].strip() if garages_tag else None

        # Append extracted data to the list
        data.append({
            "link": link,
            "strikethrough_price": strikethrough_price,
            "sold_price": sold_price,
            "property_type": property_type,
            "address": address,
            'date':date_text
        })

    # Return the extracted data as a DataFrame
    return pd.DataFrame(data)


def login_to_site(page, phone_number, password):
                # Step 1: Click the first "Log In" box
            button_selector = "button.app-btn.round.regular.pressed-down.btn"
            page.wait_for_selector(button_selector, timeout=10000)
            page.click(button_selector)
            # print("Specific button clicked.")

            # Step 2: Click the "Mobile Phone" span
            mobile_phone_span_selector = "span.text:has-text('Mobile Phone')"
            page.wait_for_selector(mobile_phone_span_selector, timeout=10000)
            page.click(mobile_phone_span_selector)
            # print("Mobile Phone span clicked.")

            # Step 3: Fill the phone number field
            phone_selector = "input[placeholder='Phone number']"
            page.wait_for_selector(phone_selector, timeout=10000)
            page.fill(phone_selector, f"{phone_number}")
            # print("Phone number field filled.")

            # Step 4: Fill the password field
            password_selector = "input[placeholder='Enter password']"
            page.wait_for_selector(password_selector, timeout=10000)
            page.fill(password_selector, f"{password}")
            # print("Password field filled.")

            # Step 5: Click the final "Log In" button
            final_login_button_selector = "button.app-btn[data-v-122714ca][data-v-bd8aee76]"
            page.wait_for_selector(final_login_button_selector, timeout=10000)
            page.click(final_login_button_selector)
            # print("Final Log In button clicked.")
def navigate_to_url(page, url):
    """Navigates to the specified URL."""
    page.goto(url)
    print(f"Navigated to URL: {url}")


def select_property_types(page, excluded_texts):
    """Selects the desired property types, excluding certain options."""
    page.locator('span.title:has-text("All property types")').click()
    page.wait_for_timeout(5000)  # Wait for options to load

    house_types = page.locator('div.checkbox-item')
    for i in range(house_types.count()):
        p_text = house_types.nth(i).locator('p[data-v-3c33e202]').text_content().strip()
        print(f"Found property type: {p_text}")
        if all(excluded not in p_text for excluded in excluded_texts):
            house_types.nth(i).click()
            print(f"Selected property type: {p_text}")


def select_time_frame(page):
    """Selects a 90-day timeframe."""
    dropdown_element = page.locator(
        'div.app-dropdown-item-title.title.actived.text-align-undefined:has(span:has-text("90d"))'
    )
    dropdown_element.wait_for(state="visible")
    dropdown_element.click()
    print("Selected 90-day timeframe.")


def iterate_years_and_extract_data(page):
    """Iterates through available years and extracts listing data."""
    all_data = pd.DataFrame()
    year_elements = page.locator('div.app-single-option')

    for i in range(year_elements.count()):
        year_element = year_elements.nth(i)
        year_text = year_element.locator('span.content').text_content().strip()
        print(f"Processing year: {year_text}")

        if year_text.startswith("Year"):
            year_element.click()
            print(f"Clicked year: {year_text}")
            page.wait_for_timeout(500)  # Optional delay between clicks

            all_data = extract_listings_from_pages(page, all_data, year_text)
            dropdown_element = page.locator(
            f'div.app-dropdown-item-title.title.actived.text-align-undefined:has(span:has-text("{year_text[-4]}"))')
            dropdown_element.click()

    return all_data


def extract_listings_from_pages(page, all_data, year):
    """Extracts listings from multiple pages for a given year."""
    while True:
        page.wait_for_load_state("networkidle")  # Ensure the page is fully loaded
        page_content = page.content()
        print(f"{year}")
        df = extract_listings(page_content)  # Call to your existing extract_listings function

        all_data = pd.concat([all_data, df], ignore_index=True)

        try:
            next_button = page.locator("span:has-text('>')")
            if next_button.is_visible():
                next_button.click()
                print("Navigated to the next page.")
            else:
                print("No more pages to navigate.")
                break
        except Exception as e:
            print(f"Error navigating pages: {e}")
            break

    save_data_to_csv(all_data, year)
    return all_data


def save_data_to_csv(data, year):
    """Saves the extracted data to a CSV file."""
    if not data.empty:
        file_name = f"0_raw_data/house_data/extracted_houses_housesigma_{year}.csv"
        data.to_csv(file_name, index=False)
        print(f"Data saved to {file_name}.")
    else:
        print("No data to save.")


def page_through_and_extract(page):
    """Main function to extract data by navigating through pages."""
    url = "https://housesigma.com/on/sold/map/?status=sold&lat=43.680521&lon=-79.457590&zoom=10.3"
    excluded_texts = ["Condo Apt", "Multiplex", "Vacant Land", "Other"]

    navigate_to_url(page, url)
    select_property_types(page, excluded_texts)
    select_time_frame(page)
    all_data = iterate_years_and_extract_data(page)

    print("Data extraction complete.")

def get_data(link, page, save_dir, wait_time=5000, filename="page_content.html"):



    try:
        # Navigate to the link
        page.goto(f"https://housesigma.com{link}", timeout=60000)  # Set a generous timeout for loading
        page.content()

        return page.locator('section.pc-detail-tab').inner_html()

    except Exception as e:
        return None


from bs4 import BeautifulSoup

def extract_property_data(html_content):
    """
    Extracts data from a specific <section> block in the HTML content.

    Parameters:
        html_content (str): The HTML content as a string.

    Returns:
        dict: Extracted data from the <section>.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    data ={}
    header = soup.find('p', class_='pc-section-sub-header')
    if header:
        data['header'] = header.get_text(strip=True)

    # Extract Key Facts Details
    key_facts = {}
    for item in soup.select('.tab-left .pc-item'):
        key = item.find('span', class_='title')
        value = item.find('dd', class_='item-text')
        if key and value:
            key_facts[key.get_text(strip=True)] = value.get_text(strip=True)
    data['key_facts'] = key_facts

    # Extract Property Details
    property_details = {}
    for item in soup.select('.tab-right .pc-item'):
        key = item.find('span', class_='title')
        value = item.find('dd', class_='item-text')
        if key and value:
            property_details[key.get_text(strip=True)] = value.get_text(strip=True)
    data['property_details'] = property_details

    # Extract Room Details
    room_details = []
    for room in soup.select('.pc-room'):
        room_data = {}
        room_data['type'] = room.find('span', class_='type').get_text(strip=True) if room.find('span', class_='type') else None
        room_data['size'] = room.find('span', class_='size').get_text(strip=True) if room.find('span', class_='size') else None
        room_data['level'] = room.find('span', class_='lv').get_text(strip=True) if room.find('span', class_='lv') else None
        room_data['description'] = room.find('span', class_='dc').get_text(strip=True) if room.find('span', class_='dc') else None
        room_details.append(room_data)
    data['room_details'] = room_details

    # Extract Description
    description = soup.find('p', class_='content')
    if description:
        data['description'] = description.get_text(strip=True)

    # Extract Additional Summary (SEO-friendly text)
    seo_texts = []
    for li in soup.select('.seo-friendly-text ul.content li.part'):
        seo_texts.append(li.get_text(strip=True))
    data['seo_text'] = seo_texts

    return data


def main():
    with sync_playwright() as p:
        # Launch the browser in non-headless mode with stealth techniques
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",  # Bypass bot detection
            ],
        )
        # Set a realistic user-agent to mimic a real browser
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        url = "https://housesigma.com"
        page.goto(url)
        login_to_site(page, PHONE_NUMBER, PASSWORD)
        #commenting out because this function has been ran

        page_through_and_extract(page)
        # for year in range (2003,2024,1):
        #     file_name = f"0_raw_data/house_data/extracted_houses_housesigma_Year {year}.csv"
        #     output_file_name = f"0_raw_data/house_data/extracted_houses_housesigma_{year}_with_properties.csv"
        #     housing_data_df = pd.read_csv(file_name)
        #     housing_data_df = housing_data_df[housing_data_df['link'].notna()]
        #     housing_data_df = housing_data_df[housing_data_df['link'] != '']
        #     print(file_name)

        #     mega_df = []

        #     for link in housing_data_df['link']:
        #         html_data = get_data(link, page, current_dir, wait_time=5000, filename="page_content.html")
        #         property_data = extract_property_data(html_data)
        #         # Add the link to the extracted data
        #         property_data['link'] = link
        #         property_data_df = pd.DataFrame([property_data])
        #         property_data_df.to_csv(output_file_name, mode='a', header=False, index=False, encoding="utf-8")
        #         print(link)


 

if __name__ == "__main__":
    main()



