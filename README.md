
# ChemInformant

<img src="/images/logo.png" alt="ChemInformant Logo" style="margin-left: 10%; width: 220px;">








**ChemInformant** is a Python-based tool that simplifies the process of retrieving and integrating chemical compound data from the PubChem database. With a simple API, you can easily fetch compound identifiers, chemical properties, and integrate this data with other external sources. Whether you're a researcher, educator, or someone with an interest in chemical informatics, ChemInformant streamlines your workflow.


## Features

- **All-in-One Data Retrieval**: Retrieve multiple chemical properties (e.g., molecular formula, weight, synonyms) using a single method call.
- **Simple API**: Access chemical data with short, easy-to-use function names like `ChemInfo.cid("Aspirin")`.
- **Legacy Support**: Still supports the original longer function names for backward compatibility.
- **Error Handling**: Built-in error handling ensures graceful fallback in case of missing data or API errors.


## Getting Started

### Prerequisites

- Python 3.6 or higher
- `pip` for installing dependencies


### Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/HzaCode/ChemInformant.git
    ```

2. Navigate to the project directory:

    ```bash
    cd ChemInformant
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

ChemInformant provides a concise, intuitive API that simplifies access to chemical data. Below are examples of how you can retrieve various types of information:

| Short Method | Legacy Method | Description | Example |
| --- | --- | --- | --- |
| `cid()` | `CID()` | Get PubChem Compound ID | `ChemInfo.cid("Aspirin")` |
| `cas()` | `CAS()` | Get CAS Registry Number | `ChemInfo.cas("Ibuprofen")` |
| `uni()` | `UNII()` | Get UNII identifier | `ChemInfo.uni("Paracetamol")` |
| `form()` | `formula()` | Get molecular formula | `ChemInfo.form("Caffeine")` |
| `wgt()` | `weight()` | Get molecular weight | `ChemInfo.wgt("Glucose")` |
| `smi()` | `smiles()` | Get SMILES notation | `ChemInfo.smi("Vitamin C")` |
| `iup()` | `iupac_name()` | Get IUPAC name | `ChemInfo.iup("Naproxen")` |
| `dsc()` | `description()` | Get compound description | `ChemInfo.dsc("Penicillin")` |
| `syn()` | `synonyms()` | Get list of synonyms | `ChemInfo.syn("Acetaminophen")` |
| `all()` | `all()` | Get all available information | `ChemInfo.all("Aspirin")` |

### Example Usage

You can use the methods with either compound names or PubChem CIDs:

```python
# Using compound name
cid = ChemInfo.cid("Aspirin")
form = ChemInfo.form("Aspirin")
wgt = ChemInfo.wgt("Aspirin")

# Using CID directly
cid_value = 2244  # CID for Aspirin
form = ChemInfo.form(cid_value)
wgt = ChemInfo.wgt(cid_value)
```

### Sample Return Values

The `ChemInfo.all("Aspirin")` method will return a dictionary like this:

```python
{
    "Common Name": "Aspirin",
    "CID": 2244,
    "CAS": "50-78-2",
    "UNII": "R16CO5Y76E",
    "MolecularFormula": "C9H8O4",
    "MolecularWeight": 180.16,
    "CanonicalSMILES": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "IUPACName": "2-acetyloxybenzoic acid",
    "Description": "Aspirin, also known as acetylsalicylic acid (ASA), is a medication used to reduce pain, fever, or inflammation...",
    "Synonyms": ["aspirin", "Acetylsalicylic acid", "2-Acetoxybenzoic acid", "ASA"]
}
```

### Error Handling

If a compound is not found or an API error occurs:

- For missing identifiers or properties, "Not found" or "N/A" is returned.
- For missing descriptions, "No description available" is returned.
- For missing synonyms, an empty list is returned.
- For the `all()` method, a dictionary with an error message is returned.

---

### Legacy Method Support

To maintain backward compatibility with older code, the original longer method names are still supported:

```python
# Legacy methods still work
formula = ChemInfo.formula("Caffeine")
weight = ChemInfo.weight("Glucose")
smiles = ChemInfo.smiles("Vitamin C")
iupac_name = ChemInfo.iupac_name("Naproxen")
```

## How It Works

ChemInformant works by:

1. Converting compound names to PubChem CIDs when needed.
2. Making HTTP requests to the PubChem REST API.
3. Parsing JSON responses to extract relevant chemical data.
4. Returning results in a user-friendly format, including graceful error handling.

## Contributing

We welcome contributions! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## License

Distributed under the MIT License. See the `LICENSE` file for more information.

## Contact

- Project Link: https://github.com/HzaCode/ChemInformant

