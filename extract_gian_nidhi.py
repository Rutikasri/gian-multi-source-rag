import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# 1. Configuration
# ============================================================

URL = "https://gian.org/gian-nidhi/"

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "gian_nidhi_raw.csv"
)


# ============================================================
# 2. Chrome Driver
# ============================================================

def get_driver():

    options = Options()

    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        options=options
    )

    return driver


# ============================================================
# 3. Clean Text
# ============================================================

def clean_text(value):

    if value is None:
        return ""

    return " ".join(
        str(value).split()
    ).strip()


# ============================================================
# 4. Extract Current Page
# ============================================================

def extract_current_page(driver):

    rows_data = []

    # Wait until at least one table row exists.
    try:

        WebDriverWait(
            driver,
            20
        ).until(
            lambda d: len(
                d.find_elements(
                    By.CSS_SELECTOR,
                    "table tbody tr"
                )
            ) > 0
        )

    except Exception:

        print(
            "  WARNING: No table rows detected after waiting."
        )

        return rows_data

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table tbody tr"
    )

    print(
        f"  HTML table rows detected: {len(rows)}"
    )

    for row in rows:

        cells = row.find_elements(
            By.TAG_NAME,
            "td"
        )

        if len(cells) < 7:
            continue

        values = [
            clean_text(cell.text)
            for cell in cells[:7]
        ]

        # ----------------------------------------------------
        # Debug only known problematic IDs
        # ----------------------------------------------------

        if values[0] in [
            "171",
            "173",
            "426"
        ]:

            print()
            print("=" * 70)
            print(
                f"DEBUG ROW: {values[0]}"
            )
            print(
                f"Number of cells: {len(cells)}"
            )

            for i, cell in enumerate(cells):

                print(
                    f"\nCELL {i}"
                )

                print(
                    "TEXT:",
                    repr(
                        clean_text(
                            cell.text
                        )
                    )
                )

                html = cell.get_attribute(
                    "outerHTML"
                )

                print(
                    "HTML:",
                    html[:1000]
                )

            print("=" * 70)
            print()

        # Only accept actual numeric IDs.
        if not values[0].isdigit():
            continue

        record = {
            "id": values[0],
            "column_status": values[1],
            "sr_no": values[2],
            "project_name": values[3],
            "participants": values[4],
            "abstract": values[5],
            "college_status": values[6]
        }

        rows_data.append(
            record
        )

    return rows_data


# ============================================================
# 5. Main
# ============================================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    driver = get_driver()

    all_records = []

    visited_pages = set()

    try:

        print("=" * 70)
        print("GIAN NIDHI DATA EXTRACTION")
        print("=" * 70)

        print()

        print("Official source:")
        print(URL)

        print()

        # ----------------------------------------------------
        # Open website
        # ----------------------------------------------------

        driver.get(URL)

        wait = WebDriverWait(
            driver,
            30
        )

        # Wait for table.
        wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "table"
                )
            )
        )

        print(
            "Table element detected."
        )

        # Give DataTables time to render.
        time.sleep(5)

        print(
            "Waiting for table data..."
        )

        # ----------------------------------------------------
        # Wait for actual data rows
        # ----------------------------------------------------

        try:

            wait.until(
                lambda d: len(
                    d.find_elements(
                        By.CSS_SELECTOR,
                        "table tbody tr"
                    )
                ) > 0
            )

        except Exception:

            print(
                "WARNING: table exists but no tbody rows detected."
            )

            print(
                "Trying again after additional wait..."
            )

            time.sleep(5)

        print(
            "Page loaded successfully."
        )

        print()

        page_number = 1

        # ====================================================
        # Pagination
        # ====================================================

        while True:

            print(
                f"Reading page {page_number}..."
            )

            time.sleep(1)

            current_records = extract_current_page(
                driver
            )

            print(
                f"  Records found on this page: "
                f"{len(current_records)}"
            )

            if not current_records:

                print(
                    "  No records found. Stopping."
                )

                break

            # ------------------------------------------------
            # Page signature
            # ------------------------------------------------

            first_id = current_records[0]["id"]

            page_signature = (
                page_number,
                first_id,
                len(current_records)
            )

            if page_signature in visited_pages:

                print(
                    "  Duplicate page detected. Stopping."
                )

                break

            visited_pages.add(
                page_signature
            )

            all_records.extend(
                current_records
            )

            # ------------------------------------------------
            # Find Next button
            # ------------------------------------------------

            next_buttons = driver.find_elements(
                By.XPATH,
                "//a[contains(normalize-space(), 'Next')]"
            )

            if not next_buttons:

                print(
                    "  Next button not found."
                )

                break

            next_button = next_buttons[-1]

            # ------------------------------------------------
            # Check disabled
            # ------------------------------------------------

            class_name = (
                next_button.get_attribute(
                    "class"
                )
                or ""
            ).lower()

            aria_disabled = (
                next_button.get_attribute(
                    "aria-disabled"
                )
            )

            if (
                "disabled" in class_name
                or aria_disabled == "true"
            ):

                print(
                    "  Reached final page."
                )

                break

            # ------------------------------------------------
            # Remember first ID
            # ------------------------------------------------

            old_first_id = (
                current_records[0]["id"]
            )

            # ------------------------------------------------
            # Click Next
            # ------------------------------------------------

            driver.execute_script(
                "arguments[0].click();",
                next_button
            )

            # ------------------------------------------------
            # Wait for new page
            # ------------------------------------------------

            try:

                WebDriverWait(
                    driver,
                    15
                ).until(
                    lambda d: (
                        len(
                            d.find_elements(
                                By.CSS_SELECTOR,
                                "table tbody tr"
                            )
                        ) > 0
                        and
                        clean_text(
                            d.find_elements(
                                By.CSS_SELECTOR,
                                "table tbody tr"
                            )[0]
                            .find_elements(
                                By.TAG_NAME,
                                "td"
                            )[0]
                            .text
                        ) != old_first_id
                    )
                )

            except Exception:

                print(
                    "  Normal page-change wait timed out."
                )

                print(
                    "  Waiting additional time..."
                )

                time.sleep(3)

            page_number += 1

        # ====================================================
        # Finished
        # ====================================================

        print()

        print("=" * 70)
        print("RAW EXTRACTION COMPLETE")
        print("=" * 70)

        print(
            f"Total rows collected: "
            f"{len(all_records)}"
        )

        if not all_records:

            print(
                "ERROR: No records were extracted."
            )

            return

        # ----------------------------------------------------
        # DataFrame
        # ----------------------------------------------------

        df = pd.DataFrame(
            all_records
        )

        # ----------------------------------------------------
        # Source metadata
        # ----------------------------------------------------

        df["source"] = "GIAN Nidhi"

        df["source_url"] = URL

        df["data_category"] = (
            "GIAN Nidhi Project"
        )

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print()

        print(
            f"Saved to: {OUTPUT_FILE}"
        )

        # ====================================================
        # Validation
        # ====================================================

        print()

        print("=" * 70)
        print("VALIDATION")
        print("=" * 70)

        print()

        print(
            "Total rows:",
            len(df)
        )

        print(
            "Unique IDs:",
            df["id"].nunique()
        )

        print(
            "Unique Sr Nos:",
            df["sr_no"].nunique()
        )

        duplicate_ids = df[
            df["id"].duplicated(
                keep=False
            )
        ]["id"].unique()

        print(
            "IDs appearing more than once:",
            len(duplicate_ids)
        )

        # ====================================================
        # Known Record Check
        # ====================================================

        print()

        print("=" * 70)
        print("KNOWN RECORD CHECK")
        print("=" * 70)

        print()

        check_ids = [
            "171",
            "173",
            "426",
            "429"
        ]

        check_df = df[
            df["id"].astype(str).isin(
                check_ids
            )
        ]

        if len(check_df) > 0:

            print(
                check_df[
                    [
                        "id",
                        "project_name",
                        "participants",
                        "abstract",
                        "college_status"
                    ]
                ].to_string(
                    index=False
                )
            )

        else:

            print(
                "Known IDs were not found."
            )

        # ====================================================
        # Missing Values
        # ====================================================

        print()

        print("=" * 70)
        print("MISSING VALUE CHECK")
        print("=" * 70)

        print()

        columns_to_check = [
            "id",
            "column_status",
            "sr_no",
            "project_name",
            "participants",
            "abstract",
            "college_status"
        ]

        for column in columns_to_check:

            missing = (
                df[column]
                .isna()
                .sum()
            )

            empty = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

            print(
                f"{column:20s}"
                f"NaN={missing:4d} "
                f"Empty={empty:4d}"
            )

        # ====================================================
        # First 5
        # ====================================================

        print()

        print("=" * 70)
        print("FIRST 5 RECORDS")
        print("=" * 70)

        print()

        print(
            df[
                [
                    "id",
                    "sr_no",
                    "project_name",
                    "participants",
                    "abstract",
                    "college_status"
                ]
            ]
            .head(5)
            .to_string(
                index=False
            )
        )

        # ====================================================
        # Last 5
        # ====================================================

        print()

        print("=" * 70)
        print("LAST 5 RECORDS")
        print("=" * 70)

        print()

        print(
            df[
                [
                    "id",
                    "sr_no",
                    "project_name",
                    "participants",
                    "abstract",
                    "college_status"
                ]
            ]
            .tail(5)
            .to_string(
                index=False
            )
        )

        print()

        print("=" * 70)
        print("EXTRACTION FINISHED")
        print("=" * 70)

    finally:

        print()

        print(
            "Chrome will remain open for inspection."
        )

        print(
            "Close the Chrome window when finished."
        )


# ============================================================
# 6. Run
# ============================================================

if __name__ == "__main__":
    main()