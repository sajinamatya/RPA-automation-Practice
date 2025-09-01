"""
Robot Order Automation Script
============================

This script automates the process of ordering robots from RobotSpareBin Industries website.
It downloads order data from a CSV file, fills out robot order forms, captures receipts,
and packages everything into a zip archive.

Dependencies:
- robocorp.tasks: Task execution framework
- robocorp.browser: Browser automation
- RPA.HTTP: HTTP operations for file downloads
- RPA.Tables: CSV data processing
- RPA.PDF: PDF generation and manipulation
- RPA.Archive: File archiving operations

Author: [Your Name]
Date: [Current Date]
Version: 1.0
"""

from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil


@task
def order_robot_from_RobotSpareBin():
    """
    Main task function that orchestrates the entire robot ordering process.
    
    This function executes the complete workflow:
    1. Opens the robot order website
    2. Downloads the orders CSV file
    3. Processes each order from the CSV
    4. Creates a zip archive of all receipts
    
    The browser is configured with a 200ms slowmo for better reliability.
    """
    browser.configure(slowmo=200)
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    zip_receipts()


def open_robot_order_website():
    """
    Opens the RobotSpareBin Industries robot order website and handles initial popup.
    
    Navigates to the robot order page and dismisses the initial terms popup
    by clicking the "OK" button.
    
    URL: https://robotsparebinindustries.com/#/robot-order
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')


def download_orders_file():
    """
    Downloads the orders CSV file from the RobotSpareBin website.
    
    Downloads the orders.csv file containing robot order specifications.
    The file is saved locally and will overwrite any existing file with the same name.
    
    Source URL: https://robotsparebinindustries.com/orders.csv
    """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)


def order_another_bot():
    """
    Clicks the 'Order another robot' button to reset the form for the next order.
    
    This function is called after successfully completing an order to prepare
    the form for processing the next robot order.
    """
    page = browser.page()
    page.click("#order-another")


def clicks_ok_button():
    """
    Clicks the OK button to dismiss any modal dialogs or popups.
    
    This is typically used after clicking 'Order another robot' to dismiss
    the confirmation popup that appears.
    """
    page = browser.page()
    page.click('text=OK')


def fill_and_submit_robot_data(order):
    """
    Fill and submit robot order data with retry logic for order submission.
    
    This function handles the complete process of filling out a single robot order:
    1. Selects the robot head type
    2. Selects the robot body type
    3. Enters the legs part number
    4. Fills in the shipping address
    5. Previews the robot configuration
    6. Submits the order with retry logic
    7. Processes the receipt and screenshot
    8. Prepares for the next order
    
    Args:
        order (dict): Dictionary containing order data with keys:
            - "Head": Robot head selection option
            - "Body": Robot body type number
            - "Legs": Part number for robot legs
            - "Address": Shipping address
            - "Order number": Unique order identifier
    
    The function includes retry logic for order submission, as the order button
    may need to be clicked multiple times due to server-side validation.
    """
    page = browser.page()
    
    # Fill out the robot configuration form
    page.select_option("#head", order["Head"])
    page.click(f"#id-body-{order['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    
    # Preview the robot before ordering
    page.click("#preview")
    
    # Submit order with retry logic
    while True:
        page.click("#order")
        
        if page.query_selector("#receipt"):  # Order successful - receipt appeared
            order_num = int(order["Order number"])
            pdf_path = receipt_in_pdf(order_num)
            screenshot_path = screenshot_robot(order_num)
            attach_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_bot()
            clicks_ok_button()
            break
            
        if not page.query_selector(".alert-danger"):  # No error message
            break  # Exit if no receipt and no error (unexpected state)


def receipt_in_pdf(order_number):
    """
    Converts the order receipt HTML to PDF format.
    
    Extracts the receipt HTML content from the page and converts it to a PDF file.
    The PDF is saved in the output/receipts directory with the order number as filename.
    
    Args:
        order_number (int): The order number used for naming the PDF file
        
    Returns:
        str: Path to the generated PDF file
        
    Output:
        Creates PDF file at: output/receipts/{order_number}.pdf
    """
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path


def fill_form_with_csv_data():
    """
    Read robot order data from CSV file and process each order.
    
    Reads the orders.csv file downloaded earlier and iterates through each order,
    calling fill_and_submit_robot_data() for each row to complete the ordering process.
    
    The CSV file should contain columns for:
    - Order number
    - Head (robot head type)
    - Body (robot body type)  
    - Legs (part number for legs)
    - Address (shipping address)
    """
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_and_submit_robot_data(order)


def screenshot_robot(order_number):
    """
    Captures a screenshot of the ordered robot preview image.
    
    Takes a screenshot of the robot preview image after order completion
    and saves it to the output/screenshots directory.
    
    Args:
        order_number (int): The order number used for naming the screenshot file
        
    Returns:
        str: Path to the generated screenshot file
        
    Output:
        Creates PNG file at: output/screenshots/{order_number}.png
    """
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def attach_screenshot_to_receipt(screenshot_path, pdf_path):
    """
    Embeds the robot screenshot as a watermark into the receipt PDF.
    
    Takes the robot preview screenshot and adds it as a watermark/image
    to the corresponding receipt PDF, creating a complete order record
    that includes both the receipt details and visual confirmation of the robot.
    
    Args:
        screenshot_path (str): Path to the robot screenshot PNG file
        pdf_path (str): Path to the receipt PDF file to be modified
        
    The modified PDF overwrites the original receipt file.
    """
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)


def zip_receipts():
    """
    Archives all receipt PDFs into a single zip file for easy distribution.
    
    Creates a zip archive containing all the generated receipt PDFs from
    the output/receipts directory. This provides a convenient way to package
    all order confirmations for delivery or storage.
    
    Output:
        Creates zip file at: output/receipts.zip
        Contains: All PDF files from output/receipts/ directory
    """
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")
