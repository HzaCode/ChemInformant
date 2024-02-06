import requests
from compound_details import get_compound_details

def fetch_drug_names_from_server(server_url):
    """
    Fetches a list of drug names from a server.

    Parameters:
    - server_url: The URL of the server endpoint that returns a list of drug names.

    Returns:
    A list of drug names.
    """
    response = requests.get(server_url)
    if response.status_code == 200:
        drug_names = response.json()  # Assuming the server returns a JSON list of drug names
        return drug_names
    else:
        raise Exception("Failed to fetch drug names from server")

def save_data_to_server(server_url, data):
    """
    Saves data back to the server.

    Parameters:
    - server_url: The URL of the server endpoint that accepts data to be saved.
    - data: The data to be saved, typically a JSON object or a list of objects.

    Returns:
    The response from the server.
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.post(server_url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        print("Successfully saved data to the server.")
    else:
        print(f"Failed to save data with status code {response.status_code}: {response.text}")

def integrate_and_save_drug_data(fetch_url, save_url):
    """
    Integrates drug data from PubChem and saves it to a server.

    Parameters:
    - fetch_url: The URL to fetch drug names from.
    - save_url: The URL to save the integrated drug data to.
    """
    try:
        drug_names = fetch_drug_names_from_server(fetch_url)
        drug_details = [get_compound_details(name) for name in drug_names]

        # Save the details back to the server
        save_data_to_server(save_url, drug_details)
    except Exception as e:
        print(f"An error occurred during integration and saving: {e}")

def main():
    server_fetch_url = "https://yourserver.com/api/drug_names"  # Placeholder URL for fetching drug names
    server_save_url = "https://yourserver.com/api/save_details"  # Placeholder URL for saving drug details
    
    # Execute the integration and saving process
    integrate_and_save_drug_data(server_fetch_url, server_save_url)

if __name__ == "__main__":
    main()
