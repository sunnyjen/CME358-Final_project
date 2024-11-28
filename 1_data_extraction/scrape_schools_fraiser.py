
from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_secondary_schools():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--use-fake-ui-for-media-stream"]  # Automatically approve geolocation
        )
        context = browser.new_context(
            permissions=["geolocation"],  # Allow geolocation
            geolocation={"latitude": 43.65107, "longitude": -79.347015},  # Example: Toronto, Canada
        )

        page = context.new_page()
        page.goto("https://www.compareschoolrankings.org/")
        page.wait_for_load_state("networkidle")

        # Step 2: Allow location access
        page.context.set_geolocation({"latitude": 43.65107, "longitude": -79.347015})  # Example: Toronto, Canada
        print("Location access allowed.")

                        

        # # Step 4: Select the desired province
        # desired_province_selector = "div.v-list-item:has-text('Ontario')"  # Update 'Ontario' to your province
        # page.wait_for_selector(desired_province_selector)
        # page.click(desired_province_selector)
        # print("Province selected.")

        # Step 5: Click "Secondary Schools" tab
        secondary_tab_selector = "a.v-tabs__item[href='#secondary']"
        page.wait_for_selector(secondary_tab_selector)
        page.click(secondary_tab_selector)

 
        # Step 7: Click "List View"
        list_view_selector = "div.text:has-text('List view')"
        page.wait_for_selector(list_view_selector)
        page.click(list_view_selector)
        page.wait_for_load_state("networkidle")  # Wait for the table to load

        # Step 6: Click "Show All Schools"
        show_all_selector = "label.show-all-schools-label"
        page.wait_for_selector(show_all_selector)
        page.click(show_all_selector)
        page.wait_for_load_state("networkidle")  # Wait for data to load


     # Step 6: Initialize an empty DataFrame
        all_data = pd.DataFrame()

        while True:
            # Step 7: Scrape the table
            print("Scraping the table...")
            rows = page.locator(f"table tr")  # Locate all rows in the table
            table_data = []

            for i in range(rows.count()):
                row = rows.nth(i)
                cols = row.locator("td")  # Locate all columns within a row
                table_data.append([cols.nth(j).inner_text().strip() for j in range(cols.count())])


            # Convert table data to a temporary DataFrame
            df = pd.DataFrame(table_data)
            pd.set_option('display.max_rows', None)

            print(df)
            print("Table scraped successfully.")

            # Append the current page's data to the main DataFrame
            all_data = pd.concat([all_data, df], ignore_index=True)

            # Step 8: Check if "Next" button is available
            next_button_selector = "a:has-text('NEXT')"
            if page.locator(next_button_selector).is_visible():
                print("Navigating to the next page...")
                page.click(next_button_selector)
                page.wait_for_load_state("networkidle")  # Wait for the next page to load
            else:
                print("No more pages to navigate.")
                break

        # Save the combined data to a CSV file
        all_data.to_csv("data/csv/secondary_schools_combined.csv", index=False)
        print("All tables saved as 'secondary_schools_combined.csv'.")

        # Close the browser
        browser.close()

# Run the function
scrape_secondary_schools()



