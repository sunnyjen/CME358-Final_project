from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
current_dir = Path.cwd()

PHONE_NUMBER = "6473230251"
PASSWORD = "Jenn2015"
def extract_listings(html_content):
    """
    Extracts property listings from the given HTML content and returns a DataFrame.

    Parameters:
        html_content (str): The HTML content to parse.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted property data.
    """
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

# def page_through_and_extract(page):
#         # Login and navigate to the desired URL
#     url = "https://housesigma.com/on/toronto-real-estate/sold/map/?center_marker=43.6668217,-79.3535575&view=map&municipality=10343&status=sold&lat=43.713580&lon=-79.336830&zoom=9.8&page=1"
#     page.goto(url)
#     all_data = pd.DataFrame()
    

#     while True:
#         # Wait for the page to load completely
#         page.wait_for_load_state("networkidle")

#         # Extract HTML content
#         page_content = page.content()
#         df = extract_listings(page_content)

#         # Append data to the master DataFrame
#         all_data = pd.concat([all_data, df], ignore_index=True)


#         try:
#             next_button = page.locator("span:has-text('>')")  # Adjust selector for the "next page" button

#             # Scroll until the button is visible
#             for _ in range(20):  # Set a maximum number of scroll attempts to avoid infinite loops
#                 if next_button.is_visible():
#                     break
#                 # Scroll down the page
#                 page.evaluate("window.scrollBy(0, 300)")  # Adjust scroll step as needed
#                 page.wait_for_timeout(500)  # Add a small delay between scrolls

#             if next_button.is_visible():
#                 # Click the button to navigate to the next page
#                 next_button.click()
#                 # print("Navigated to the next page.")
#             else:
#                 # print("Next page button not found after scrolling.")
#                 break  # Exit the loop if the button is not found
#         except Exception as e:
#             # print("No more pages or error navigating to next page:", e)
#             break


    
#         if not all_data.empty:
#             try:
#                 all_data.to_csv("extracted_houses_housesigma.csv", index=False)
#             except Exception as e:
#                 print("Error saving data to CSV:")
#         else:
#             print("No data extracted. CSV file not created.")


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
        # page_through_and_extract(page)
        housing_data_df = pd.read_csv('house_data/link_hood_add.csv')
        housing_data_df = housing_data_df[housing_data_df['link'].notna()]
        housing_data_df = housing_data_df[housing_data_df['link'] != '']
        print(housing_data_df.shape)

        mega_df = []
        csv_path = current_dir/'properties_housesigma.csv'
        for link in housing_data_df['link']:
            html_data = get_data(link, page, current_dir, wait_time=5000, filename="page_content.html")
            property_data = extract_property_data(html_data)
            # Add the link to the extracted data
            property_data['link'] = link
            property_data_df = pd.DataFrame([property_data])

            property_data_df.to_csv(csv_path, mode='a', header=False, index=False, encoding="utf-8")


 

if __name__ == "__main__":
    main()



