=======================================================
Application in Real-World Scientific Workflows
=======================================================

The core value of ChemInformant lies in its role as a starting point for data science workflows, seamlessly injecting chemical data into Python's powerful scientific computing ecosystem. This page will demonstrate through three cases that more closely resemble real-world research scenarios how ChemInformant can be combined with advanced libraries like **RDKit**, **Scikit-learn**, and **NetworkX** to accomplish diverse tasks ranging from data preprocessing and multi-class classification to community detection.

.. note::
   The examples on this page depend on additional specialized libraries.

   .. code-block:: bash

      pip install rdkit-pypi scikit-learn networkx



.. _rdkit_integration:

Example 1: Batch Preprocessing and Analysis with RDKit
-------------------------------------------------------

In chemical analysis, it is often necessary to first standardize raw molecules obtained from a database, for example, by "desalting". In this scenario, we **use ChemInformant to obtain the SMILES for a set of non-steroidal anti-inflammatory drugs (NSAIDs)**, then hand them over to RDKit for desalting, and further analyze whether they contain a benzene ring, a common chemical feature.

.. code-block:: python
   :emphasize-lines: 1, 9, 10, 14

   import ChemInformant as ci
   from rdkit import Chem
   from rdkit.Chem import SaltRemover
   import pandas as pd

   # 1. Use ci to get SMILES for a set of NSAIDs
   identifiers = ['aspirin', 'ibuprofen', 'naproxen', 'diclofenac',
                  'ketoprofen', 'celecoxib', 'indomethacin']
   df = ci.get_properties(identifiers, ['isomeric_smiles', 'input_identifier'])
   df_clean = df[df['status'] == 'OK'].copy()

   # 2. Use RDKit's SaltRemover to preprocess the data
   remover = SaltRemover.SaltRemover()
   df_clean['clean_smiles'] = df_clean['isomeric_smiles'].apply(
       lambda s: Chem.MolToSmiles(remover.StripMol(Chem.MolFromSmiles(s)))
   )
   
   # 3. Perform substructure analysis based on the preprocessed data
   pattern = Chem.MolFromSmarts('c1ccccc1')
   df_clean['has_benzene'] = df_clean['clean_smiles'].apply(
       lambda s: Chem.MolFromSmiles(s).HasSubstructMatch(pattern)
   )
   
   print(">>> RDKit Substructure Analysis: Do NSAIDs contain a benzene ring?")
   print(df_clean[['input_identifier', 'has_benzene']])


Output:

.. code-block:: text

   >>> RDKit Substructure Analysis: Do NSAIDs contain a benzene ring?
     input_identifier  has_benzene
   0          aspirin         True
   1        ibuprofen         True
   2         naproxen         True
   3       diclofenac         True
   4       ketoprofen         True
   5        celecoxib         True
   6     indomethacin         True



.. _sklearn_integration:

Example 2: Multi-Class Classification with Scikit-learn
---------------------------------------------------------

We can use the **data obtained from ChemInformant** as features to train a machine learning model to distinguish between different classes of drugs. This example will differentiate between three classes of drugs: statins, NSAIDs, and antibiotics.

.. admonition:: For workflow demonstration only
   :class: caution

   The core purpose of this example is to demonstrate how to smoothly pass data from **ChemInformant** into Scikit-learn for cross-validation.

.. code-block:: python
   :emphasize-lines: 1, 21, 22, 23

   import ChemInformant as ci
   import pandas as pd
   from rdkit import Chem
   from rdkit.Chem import rdMolDescriptors
   from sklearn.ensemble import RandomForestClassifier
   from sklearn.model_selection import StratifiedKFold, cross_val_score
   from collections import Counter

   # 1. Define three classes of drugs
   classes = {
       'Statin': ['simvastatin', 'atorvastatin', 'pravastatin', 'rosuvastatin'],
       'NSAID': ['aspirin', 'ibuprofen', 'naproxen', 'diclofenac'],
       'Antibiotic': ['amoxicillin', 'ciprofloxacin', 'azithromycin', 'doxycycline']
   }
   labels, ids = [], []
   for cls, drugs in classes.items():
       ids.extend(drugs)
       labels.extend([cls] * len(drugs))

   # 2. Use ci to get feature data and calculate TPSA with RDKit
   df_feat = ci.get_properties(ids, ['molecular_weight', 'xlogp', 'isomeric_smiles'])
   df_feat_clean = df_feat[df_feat['status'] == 'OK'].copy()
   df_feat_clean['tpsa'] = df_feat_clean['isomeric_smiles'].apply(
       lambda s: rdMolDescriptors.CalcTPSA(Chem.MolFromSmiles(s))
   )

   # 3. Prepare training data and perform cross-validation
   features = ['molecular_weight', 'xlogp', 'tpsa']
   X = df_feat_clean[features].values
   y = pd.Categorical(pd.Series(labels).loc[df_feat_clean.index]).codes
   
   counts = Counter(y)
   min_class_count = min(counts.values()) if counts else 1
   n_splits = min(5, min_class_count)
   
   cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
   clf = RandomForestClassifier(n_estimators=100, random_state=42)
   acc = cross_val_score(clf, X, y, cv=cv, scoring='accuracy')

   print(f">>> Multi-class accuracy {n_splits}-fold CV: {acc.mean():.2%} ± {acc.std():.2%}")

Output:

.. code-block:: text

   >>> Multi-class accuracy 4-fold CV: 91.67% ± 14.43%



.. _networkx_integration:

Example 3: Similarity Networking and Community Detection with NetworkX
--------------------------------------------------------------------------

This is a more advanced application that translates chemical similarity into a network relationship. We **use ChemInformant to retrieve molecular information**, use RDKit to calculate fingerprint similarity, and then use NetworkX to build a network graph and perform community detection (i.e., find subgroups of the most structurally similar compounds in the network).

.. code-block:: python
   :emphasize-lines: 1, 10, 11

   import ChemInformant as ci
   from rdkit import Chem
   from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
   from rdkit.DataStructs import TanimotoSimilarity
   import networkx as nx
   from networkx.algorithms import community

   # 1. Use ci to get SMILES for NSAIDs to generate fingerprints
   ids_net = ['aspirin', 'ibuprofen', 'naproxen', 'diclofenac']
   df_net = ci.get_properties(ids_net, ['isomeric_smiles', 'input_identifier'])
   df_net_clean = df_net[df_net['status'] == 'OK'].copy()

   # 2. Generate fingerprints using RDKit
   fpgen = GetMorganGenerator(radius=2, fpSize=1024)
   fps = [fpgen.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_net_clean['isomeric_smiles']]

   # 3. Build a graph with NetworkX and add edges based on similarity
   G = nx.Graph()
   for name in df_net_clean['input_identifier']:
       G.add_node(name)

   # Use .iloc to ensure index alignment
   for i in range(len(df_net_clean)):
       for j in range(i + 1, len(df_net_clean)):
           sim = TanimotoSimilarity(fps[i], fps[j])
           if sim >= 0.2:
               G.add_edge(df_net_clean.iloc[i]['input_identifier'], 
                          df_net_clean.iloc[j]['input_identifier'], 
                          weight=sim)
   
   # 4. Perform community detection
   communities = community.greedy_modularity_communities(G, weight='weight')

   print("\n>>> NSAIDs Similarity Network Community Grouping:")
   for idx, comm in enumerate(communities, 1):
       print(f"  Community {idx}: {sorted(comm)}")

Output:

.. code-block:: text

   >>> NSAIDs Similarity Network Community Grouping:
     Community 1: ['ibuprofen', 'naproxen']
     Community 2: ['aspirin', 'diclofenac']