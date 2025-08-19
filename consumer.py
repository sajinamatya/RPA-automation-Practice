import requests
from robocorp import workitems
from robocorp.tasks import task
# consumer task
@task
def consume_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Consumes traffic data work items.
    """
    print("consume")
    process_transformed_traffic_data()


def process_transformed_traffic_data():
    """
    Process the transformed traffic data work items.
    """
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"]
        valid = validate_traffic_data(traffic_data)
        if valid:
            status,return_json = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
            else:
                item.fail(exception_type="APPLICATION",
                    code="TRAFFIC_DATA_POST_FAILED",
                    message=return_json["message"],
                )
        else:
            item.fail(
                exception_type="BUSINESS",
                code="INVALID_TRAFFIC_DATA",
                message=item.payload,
            )


# Post the traffic data to the sales system
def post_traffic_data_to_sales_system(data):
    """Post  the traffic data to the sales system API using post request"""
    url = "https://robocorp.com/inhuman-insurance-inc/sales-system-api"
    response = requests.post(url, json=data)  # Send the POST request
    return response.status_code,response.json()  # Raise an error for HTTP errors


# Validate the traffic data 
def validate_traffic_data(traffic_data):
    """ function which returns true if the country code is valied i.e 3 codes"""
    return len(traffic_data["country"]) == 3 # return True if the country code is valid else false 

