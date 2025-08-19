# importing the robocorp required module 
from robocorp.tasks import task # its is used to mark the function as the robocorps task
from RPA.HTTP import HTTP  # Importing HTTP module for making HTTP requests
from RPA.JSON import JSON  # Importing JSON module for handling JSON data
from RPA.Tables import Tables  # Importing Tables module for handling tabular data
from robocorp import workitems # Importing workitems module for handling work items
import requests  # Importing requests module for making HTTP requests



json = JSON()  # Creating an instance of the JSON class
table = Tables()  # Creating an instance of the Tables class
http = HTTP()  # Creating an instance of the HTTP class
TRAFFIC_JSON_FILE_PATH = "output/traffic.json"

# JSON data keys
COUNTRY_KEY = "SpatialDim"
YEAR_KEY = "TimeDim"
RATE_KEY = "NumericValue"
GENDER_KEY = "Dim1"

# Main task defination 
# producer and consumer pattern, Separate task for the produce and consume work

@task
# producer task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    print("produce")
    download_traffic_data()  # Download the traffic data

    traffic_data = load_traffic_data_as_table() # load the traffic data to RPA.Tables
    table.write_table_to_csv(traffic_data, "output/test.csv") 
    filtered_data = filter_and_sort_traffic_data(traffic_data) # filter and sort the traffic data , traffic_data is passed as a argument
    filtered_data = get_latest_data_by_country(filtered_data) # Get the latest data by country.
    payloads = create_work_item_payloads(filtered_data) # Create the payloads dictionary for the filtered data
    save_work_item_payloads(payloads) # Save the payloads as work items in the workitems module

 
#

 
def download_traffic_data():
    """
    Download the traffic data from the specified URL using http requests.
    """
    # download the traffic data form the url specified
    http.download(
        url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
        target_file="output/traffic.json",
        overwrite=True
    )


# Load the traffic data as table
def load_traffic_data_as_table():
    """Load the traffic data from the specified JSON file as table."""
    json_data = json.load_json_from_file("output/traffic.json") # load json from the file 
    
    return  table.create_table(json_data["value"]) # return the converted the JSON format into a Table format.



# Filter and sort the traffic data
def filter_and_sort_traffic_data(data):
    """ Filter and sort the traffic data as per the businesss logic."""
    '''
    rate_key = "NumericValue"
    max_rate = 5.0
    gender_key = "Dim1"
    both_genders = "BTSX"
    year_key = "TimeDim"
    ''' 
    # filter_table_by_column() is a method from the RPA.Table which is used to filter the data of the table as per the given conditions.
    # filter_table_by_column(tabledata,<column_name>,<operator>,<value>)
    # filtering the data where the numericValue column is less than 5 
    table.filter_table_by_column(data,"NumericValue","<", 5.0)
    # filtering the data where the Dim1 column is equal to BTSX
    table.filter_table_by_column(data,"Dim1", "==", "BTSX")
    # sorting the data by the TimeDim column in descending order
    # sort_table_by_column(tabledata,<column_name>,<ascending> True, ,descending false)
    table.sort_table_by_column(data, "TimeDim", False)
    return data



# Get the latest data by country
def get_latest_data_by_country(data):
    """Get the latest traffic data by country. the Tables data are grouped by country then, iterating over each group and taking the latest entry. the first row and appending in to the list to get the latest data"""
    country_key = "SpatialDim" # The column name used to group the data by country

    # group_table_by_column(tabledata,<column_name>)

    data = table.group_table_by_column(data, country_key) # Group the data by country
    latest_data_by_country = []     # List to hold the latest data for each country
    for group in data: # Iterate over each group (country)
        first_row = table.pop_table_row(group) # Get the latest data for the country
        latest_data_by_country.append(first_row) # Append the latest data for the country
    return latest_data_by_country





# convert the data into suitable format acceptable by the API. 
def create_work_item_payloads(traffic_data):
    """Create work item payloads from the traffic data., the API expects the payloads 
    to be in a specific format. {
        "country": "VCT",
        "year": 2011,
        "rate": 3.69293
            } """
    payloads = []  # List to hold the payloads
    for row in traffic_data:  # Iterate over each row in the traffic data
        # Create a payload dictionary for each row 
        payload = dict(
            country=row[COUNTRY_KEY],  # Country code
            year=row[YEAR_KEY],         # Year
            rate=row[RATE_KEY]     # Rate
        )
        payloads.append(payload)  # Append the payload to the list
    return payloads  # Return the list of payloads


# save work item for each payloads so that it can be comsumed by the consumer process later 
def save_work_item_payloads(payloads):
    for payload in payloads:
        variables = dict(traffic_data=payload)
        workitems.outputs.create(variables)