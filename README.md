



# ChemInformant

ChemInformant is a Python-based project aimed at facilitating the retrieval and integration of chemical compound information from the PubChem database. It provides a set of tools for fetching compound identifiers, chemical properties, and integrating this data with additional sources, making it invaluable for researchers, educators, and anyone interested in chemical informatics.

## Features

- **Compound Identification**: Retrieve unique identifiers (CIDs) for chemical compounds based on their names.
- **Chemical Properties**: Fetch various chemical properties including CAS numbers, molecular formulas, and more.
- **Synonyms and Descriptions**: Access detailed descriptions and synonyms for a wide range of compounds.
- **Data Integration**: Combine chemical compound data from PubChem with external data sources seamlessly.
- **Data Saving**: Functionality to save the integrated data back to a server for further use.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- pip for installing dependencies

### Installation

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/HzaCode/ChemInformant.git
   ```
2. Navigate to the project directory:
   ```
   cd ChemInformant
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The project is structured into modules, each serving a specific functionality within the data retrieval and integration process:

- `src/api_helpers.py`: Functions for direct interaction with the PubChem API.
- `src/compound_details.py`: Aggregates detailed information about compounds from various sources.
- `src/drug_data_integration.py`: Demonstrates fetching drug names from a server, retrieving their details, and saving the data.

To see the project in action, refer to the example script provided in the `examples` directory:

```
python examples/example_usage.py
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Link: [https://github.com/HzaCode/ChemInformant](https://github.com/HzaCode/ChemInformant)


