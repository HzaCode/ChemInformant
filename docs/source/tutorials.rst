======================
Interactive Tutorial
======================

To truly master ``ChemInformant``, we highly recommend using the interactive user manual. It's a live Jupyter Notebook environment hosted on Google Colab, designed to bridge the gap between theory and practice.

**Click the badge below to launch the tutorial now:**

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/HzaCode/ChemInformant/blob/main/examples/ChemInformant_User_Manual_v1.0.ipynb
   :alt: Open in Colab

--------------------
**Quick Start Guide**
--------------------

To ensure the best experience and to save your progress, please follow these steps:

**1. Save a Personal Copy**
   Once the notebook opens in Colab, immediately go to the menu and click **``File -> Save a copy in Drive``**. This creates a personal, editable copy in your own Google Drive.

**2. Execute Cells in Order**
   The tutorial is designed to be followed sequentially. Run each code cell from top to bottom by clicking the "▶️" play button or using the shortcut ``Shift + Enter``.

**3. Interact and Experiment**
   Don't hesitate to modify the code! Try different compound names, request other properties, and observe how the output changes. This is the best way to learn how to apply ``ChemInformant`` to your own work.

--------------------------
**What You Will Learn**
--------------------------

This hands-on manual covers the entire workflow, from installation to advanced data analysis. Specifically, you will learn to:

*   **Setup the Environment**:
    Install ``ChemInformant`` with all necessary extras and import required libraries in a single step.

*   **Master Core Functions**:
    Use the powerful ``get_properties`` function to retrieve data for multiple compounds and properties at once, directly into a Pandas DataFrame.

*   **Leverage the Convenience API**:
    Perform quick lookups for single properties like molecular weight, SMILES, or IUPAC names using simple, intuitive functions (e.g., ``get_weight()``, ``get_cas()``).

*   **Perform Batch Data Analysis**:
    Retrieve, clean, and analyze data for a list of common drugs, then visualize physicochemical properties like molecular weight distribution and lipophilicity.

*   **Apply Advanced Use Cases**:
    - **Drug-Likeness Assessment**: Implement and visualize Lipinski's Rule of Five to assess compounds.
    - **Machine Learning Clustering**: Use K-Means to cluster drugs based on their properties and visualize the results.

*   **Export Your Results**:
    Save your analysis into common formats like CSV, multi-sheet Excel files, and SMILES files for use in other cheminformatics software.
