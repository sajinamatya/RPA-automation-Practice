# importing the robocorp required module 
from robocorp.tasks import task # its is used to mark the function as the robocorps task
from RPA.HTTP import HTTP  # Importing HTTP module for making HTTP requests

http = HTTP()  # Creating an instance of the HTTP class


# Main task defination 
# producer and consumer pattern, Separate task for the produce and consume work
@task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    print("produce")


@task
def consume_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Consumes traffic data work items.
    """
    print("consume")


def download_traffic_data():
    """
    Download the traffic data from the specified URL using http requests.
    """
    http.download(
        url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
        target_file="output/traffic.json",
        overwrite=True,
    )