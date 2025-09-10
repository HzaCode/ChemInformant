"""
Centralised property lists and aliases for the get_properties() function.
This file establishes snake_case as the canonical internal format.
"""
import re

# --- 1. Master List of all Official PubChem Property Tags (in CamelCase) ---
# This list represents the exact tags the PubChem API uses.
ALL_PROPS_CAMEL: list[str] = [
    "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IsomericSMILES",
    "InChI", "InChIKey", "IUPACName", "XLogP", "ExactMass", "MonoisotopicMass",
    "TPSA", "Complexity", "Charge", "HBondDonorCount", "HBondAcceptorCount",
    "RotatableBondCount", "HeavyAtomCount", "IsotopeAtomCount", "AtomStereoCount",
    "DefinedAtomStereoCount", "UndefinedAtomStereoCount", "BondStereoCount",
    "DefinedBondStereoCount", "UndefinedBondStereoCount", "CovalentUnitCount",
    "Volume3D", "XStericQuadrupole3D", "YStericQuadrupole3D",
    "ZStericQuadrupole3D", "FeatureCount3D", "FeatureAcceptorCount3D",
    "FeatureDonorCount3D", "FeatureAnionCount3D", "FeatureCationCount3D",
    "FeatureRingCount3D", "FeatureHydrophobeCount3D", "ConformerModelRMSD3D",
    "EffectiveRotorCount3D", "ConformerCount3D"
]

def _snake_case(s: str) -> str:
    """Converts CamelCase to snake_case, handling specifics like '3D'."""
    # First handle 3D suffix specifically
    s = s.replace('3D', '_3D')

    # Standard CamelCase to snake_case conversion
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s2 = re.sub('([A-Z])([A-Z][a-z])', r'\1_\2', s1)

    # Convert to lowercase and clean up any double underscores
    result = s2.lower().replace('__', '_')

    return result

# --- 2. Standardized snake_case Property Lists (Canonical Internal Format) ---
# All functions and returned DataFrames will use these snake_case names.
CAMEL_TO_SNAKE = {camel: _snake_case(camel) for camel in ALL_PROPS_CAMEL}
SNAKE_TO_CAMEL = {v: k for k, v in CAMEL_TO_SNAKE.items()}

# Manual mappings for user-friendly property names
SNAKE_TO_CAMEL["xlogp"] = "XLogP"  # Use user-friendly 'xlogp' instead of 'x_log_p'

# Add special properties (CAS and synonyms) that don't come from PubChem property API
SPECIAL_PROPERTIES = ["cas", "synonyms"]
ALL_PROPS: list[str] = sorted(SNAKE_TO_CAMEL.keys()) + SPECIAL_PROPERTIES

THREED_PROPS_SET = {
    "volume_3d", "x_steric_quadrupole_3d", "y_steric_quadrupole_3d",
    "z_steric_quadrupole_3d", "feature_count_3d", "feature_acceptor_count_3d",
    "feature_donor_count_3d", "feature_anion_count_3d", "feature_cation_count_3d",
    "feature_ring_count_3d", "feature_hydrophobe_count_3d",
    "conformer_model_rmsd_3d", "effective_rotor_count_3d", "conformer_count_3d",
}

# Define core properties - the most commonly needed chemical properties
CORE_PROPS_SET = {
    # Basic molecular information
    "molecular_formula", "molecular_weight", "exact_mass", "monoisotopic_mass",

    # SMILES representations
    "canonical_smiles", "isomeric_smiles",

    # Chemical identifiers and names
    "iupac_name", "cas", "synonyms",

    # Key molecular descriptors for drug discovery and chemical analysis
    "xlogp", "tpsa", "complexity",

    # Hydrogen bonding and basic molecular features
    "h_bond_donor_count", "h_bond_acceptor_count", "rotatable_bond_count",
    "heavy_atom_count", "charge",

    # Chemical structure details
    "atom_stereo_count", "bond_stereo_count", "covalent_unit_count",

    # InChI identifiers (standard chemical identifier)
    "in_ch_i", "in_ch_i_key"
}

CORE_PROPS: list[str] = sorted([p for p in ALL_PROPS if p in CORE_PROPS_SET])
THREED_PROPS: list[str] = sorted([p for p in ALL_PROPS if p in THREED_PROPS_SET])

# All other properties not in core or 3D categories
OTHER_PROPS: list[str] = sorted([p for p in ALL_PROPS if p not in CORE_PROPS_SET and p not in THREED_PROPS_SET])

# --- 3. Alias Map -> Maps any user input to the standardized snake_case name ---
PROPERTY_ALIASES: dict[str, str] = {p: p for p in ALL_PROPS} # snake_case -> snake_case
PROPERTY_ALIASES.update(dict(CAMEL_TO_SNAKE.items())) # CamelCase -> snake_case
PROPERTY_ALIASES.update({camel.lower(): snake for camel, snake in CAMEL_TO_SNAKE.items()}) # lowercase -> snake_case
PROPERTY_ALIASES.update({snake.replace('_', ''): snake for snake in ALL_PROPS}) # flatcase -> snake_case

# Add special and legacy aliases, ensuring they also map to snake_case
PROPERTY_ALIASES.update({
    "cas": "cas",
    "synonyms": "synonyms",
    "smiles": "canonical_smiles",  # User-friendly alias for canonical SMILES
    # Add common H-bond aliases for better usability
    "hbond_donor_count": "h_bond_donor_count",
    "hbond_acceptor_count": "h_bond_acceptor_count",
    "hbonddonorcount": "h_bond_donor_count",
    "hbondacceptorcount": "h_bond_acceptor_count",
    # Add rotatable bond aliases
    "rotatable_bonds": "rotatable_bond_count",
    "rotatablebond": "rotatable_bond_count",
    "rotatalbebonds": "rotatable_bond_count",
    # Add LogP aliases for user convenience
    "x_log_p": "xlogp",  # Legacy snake_case alias mapping to standard xlogp
    "logp": "xlogp",     # User-friendly alias for standard xlogp
})
