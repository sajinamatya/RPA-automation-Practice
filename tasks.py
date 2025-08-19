from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robot_from_RobotSpareBin():
  
	browser.configure(slowmo=200)
	open_robot_order_website()
	download_orders_file()
	fill_form_with_csv_data()
	zip_receipts()
	


def open_robot_order_website():

	browser.goto("https://robotsparebinindustries.com/#/robot-order")
	page = browser.page()
	page.click('text=OK')


def download_orders_file():
 
	http = HTTP()
	http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)


def order_another_bot():

	page = browser.page()
	page.click("#order-another")


def clicks_ok_button():
	page = browser.page()
	page.click('text=OK')


def fill_and_submit_robot_data(order):
    """Fill and submit robot order data with retry logic"""
    page = browser.page()

 
    page.select_option("#head", order["Head"])
    page.click(f"#id-body-{order['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")


    while True:
        page.click("#order")

        if page.query_selector("#receipt"):  # Success
            order_num = int(order["Order number"])
            pdf_path = receipt_in_pdf(order_num)
            screenshot_path = screenshot_robot(order_num)
            attach_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_bot()
            clicks_ok_button()
            break

        if not page.query_selector(".alert-danger"):  
            break  # No receipt and no error → exit


def receipt_in_pdf(order_number):
	
	page = browser.page()
	order_receipt_html = page.locator("#receipt").inner_html()
	pdf = PDF()
	pdf_path = "output/receipts/{0}.pdf".format(order_number)
	pdf.html_to_pdf(order_receipt_html, pdf_path)
	return pdf_path

def fill_form_with_csv_data():
	"""Read data from csv and fill in the robot order form"""
	csv_file = Tables()
	robot_orders = csv_file.read_table_from_csv("orders.csv")
	for order in robot_orders:
		fill_and_submit_robot_data(order)
		  
def screenshot_robot(order_number):
	"""Takes screenshot of the ordered bot image"""
	page = browser.page()
	screenshot_path = "output/screenshots/{0}.png".format(order_number)
	page.locator("#robot-preview-image").screenshot(path=screenshot_path)
	return screenshot_path

def attach_screenshot_to_receipt(screenshot_path, pdf_path):
	"""Embeds the screenshot to the bot receipt"""
	pdf = PDF()
	pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
								   source_path=pdf_path, 
								   output_path=pdf_path)
	
def zip_receipts():
	""" receipt pdfs into a single zip archive"""
	lib = Archive()
	lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")







   