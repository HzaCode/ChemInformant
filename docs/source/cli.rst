===============================
Command-Line Interface (CLI)
===============================

ChemInformant provides a suite of command-line interface (CLI) tools, designed to enable users to interact directly with the PubChem database from a terminal environment. This suite includes `chemfetch` for data retrieval and `chemdraw` for structure visualization. They are designed as standalone, powerful programs that can be easily integrated into automation scripts and data analysis workflows.

.. contents::
   :local:

`chemfetch`
-----------

`chemfetch` is ChemInformant's core data retrieval tool. Its primary responsibility is to accept one or more chemical identifiers provided by the user, initiate a request to the PubChem API to fetch specified chemical properties, and return the results to standard output or a file in a user-selected format. The tool can automatically recognize various identifier types and robustly handle batch requests that include invalid identifiers.

**Usage**

.. code-block:: bash

   chemfetch [identifiers...] [options]

**Parameters and Options**

.. option:: identifiers

   One or more required chemical identifiers, separated by spaces. The internal logic of `chemfetch` will attempt to parse the type of each identifier:

   * **Name:** e.g., ``aspirin``, ``caffeine``, ``water``. The tool uses these names to search in PubChem.
   * **PubChem Compound ID (CID):** e.g., ``2244`` for aspirin. This is a specific and unambiguous identifier.
   * **SMILES String:** e.g., ``"CC(=O)Oc1ccccc1C(=O)O"``. This is a linear notation for describing a compound's structure.

   .. note::
      When a provided SMILES string contains characters that might be interpreted by the shell as special operators (e.g., `(`, `)`, `=`, `#`), it is strongly recommended to enclose the entire string in single or double quotes to ensure it is passed as a single, complete argument to `chemfetch`.

.. option:: --props <property_list>

   A comma-separated list of properties to precisely specify which data to retrieve for each identifier. If the user does not provide this option, `chemfetch` will use a default set of properties: ``cas,molecular_weight,iupac_name``.

   The complete list of available properties includes:

   * ``cas``: CAS Registry Number, a common chemical identifier.
   * ``molecular_weight``: Molecular weight, in g/mol.
   * ``molecular_formula``: Molecular formula, indicating the number of atoms of each element in the compound.
   * ``canonical_smiles``: Canonical SMILES string.
   * ``isomeric_smiles``: Isomeric SMILES string.
   * ``iupac_name``: The systematic name established by IUPAC.
   * ``xlogp``: Calculated octanol-water partition coefficient.
   * ``synonyms``: A list of all known synonyms.

.. option:: -f, --format <format_type>

   This option controls the format of the output. Default is ``table``.

   * ``table``: Human-readable aligned table.
   * ``csv``: Comma-separated values.
   * ``json``: JSON array output.
   * ``sql``: Writes to a SQLite database (requires ``--output``).

.. option:: -o, --output <file_path>

   Specifies the path for the output file. Required for ``--format sql`` and ignored otherwise.

**Basic Examples**

1. **Basic Query**

   .. code-block:: bash

      chemfetch aspirin caffeine

   Output:

   .. code-block:: text

      input_identifier   cid      status  cas       molecular_weight iupac_name
      aspirin            2244     OK      50-78-2   180.16           2-(acetyloxy)benzoic acid
      caffeine           2519     OK      58-08-2   194.19           1,3,7-trimethylpurine-2,6-dione

2. **Valid and Invalid Identifiers**

   .. code-block:: bash

      chemfetch caffeine "ThisIsA_FakeCompound" 999999999

   Output:

   .. code-block:: text

      input_identifier         cid   status         cas     molecular_weight  iupac_name
      caffeine                 2519  OK             58-08-2 194.19            1,3,7-trimethylpurine-2,6-dione
      ThisIsA_FakeCompound     <NA>  NotFoundError  <NA>    NaN               <NA>
      999999999                <NA>  NotFoundError  <NA>    NaN               <NA>

**Using `chemfetch` in Data Processing Pipelines**

You can pipe structured output (`json`, `csv`, or `sql`) into external tools.

**Scenario 1: JSON + jq**

.. code-block:: bash

   chemfetch aspirin caffeine --props cas,molecular_weight --format json

.. code-block:: bash

   chemfetch aspirin caffeine --props cas,molecular_weight --format json | jq -r '.[] | select(.status == "OK") | .cas'

Output:

.. code-block:: text

   50-78-2
   58-08-2

**Scenario 2: CSV + awk**

.. code-block:: bash

   chemfetch aspirin caffeine ethanol --props molecular_weight --format csv | awk -F, 'NR > 1 {print "Compound:", $1, "| Weight:", $4}'

Output:

.. code-block:: text

   Compound: aspirin | Weight: 180.16
   Compound: caffeine | Weight: 194.19
   Compound: ethanol | Weight: 46.07

**Scenario 3: Save as SQLite**

.. code-block:: bash

   chemfetch aspirin caffeine ethanol --props cas,molecular_weight --format sql -o chemicals.db

Terminal output:

.. code-block:: text

   Writing data to table 'results' in database 'chemicals.db'...
   Done.

Query:

.. code-block:: bash

   sqlite3 chemicals.db "SELECT * FROM results;"

Output:

.. code-block:: text

   aspirin|2244|OK|50-78-2|180.16
   caffeine|2519|OK|58-08-2|194.19
   ethanol|702|OK|64-17-5|46.07

`chemdraw`
----------

The `chemdraw` tool provides a quick way to invoke and display a compound's 2D structure from the terminal.

.. warning::

   This feature depends on optional plotting libraries (`matplotlib` and `Pillow`). You must install them via:

   .. code-block:: bash

      pip install ChemInformant[plot]

**Usage**

.. code-block:: bash

   chemdraw [identifier]

**Parameters**

.. option:: identifier

   A chemical identifier (name, CID, or SMILES) of the compound to draw.

**Examples**

1. **By Name**

   .. code-block:: bash

      chemdraw "Vanillin"

   .. image:: /_static/2025-07-22-103832.jpg
      :width: 300px
      :align: center

2. **By SMILES**

   .. code-block:: bash

      chemdraw "c1ccc(cc1)C(=O)O"

   .. image:: /_static/Figure_1.png
      :width: 500px
      :align: center

3. **Invalid Identifier**

   .. code-block:: bash

      chemdraw "MyImaginaryMolecule"

   .. code-block:: text

      Attempting to draw structure for 'MyImaginaryMolecule'...
      [ChemInformant] Error: Identifier 'MyImaginaryMolecule' was not found in PubChem.
