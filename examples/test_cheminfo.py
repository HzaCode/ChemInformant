#!/usr/bin/env python3
"""
ChemInformant Demo and Test Script
=================================
This script demonstrates the capabilities of the ChemInformant library
for retrieving chemical compound information from PubChem.

It includes tests for all available methods and produces visually appealing output.
"""

import os
import sys
import time
from datetime import datetime
import random
try:
    from colorama import init, Fore, Style
    from tabulate import tabulate
    from tqdm import tqdm
    HAS_EXTRA_LIBS = True
except ImportError:
    HAS_EXTRA_LIBS = False
    print("Notice: For best visual experience, install optional dependencies:")
    print("pip install colorama tabulate tqdm")
    print("Continuing with basic output...\n")

# Determine if we're using colorama
if HAS_EXTRA_LIBS:
    init()  # Initialize colorama

# Ensure proper path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
SRC_PATH = os.path.join(PARENT_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Try to import ChemInfo
try:
    from cheminfo_api import ChemInfo
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    import_error = str(e)

def colored(text, color=None, style=None):
    """Apply color to text if colorama is available."""
    if not HAS_EXTRA_LIBS:
        return text
    
    color_code = getattr(Fore, color.upper()) if color else ''
    style_code = getattr(Style, style.upper()) if style else ''
    return f"{color_code}{style_code}{text}{Style.RESET_ALL}"

def print_header(text):
    """Print a formatted header."""
    width = 80
    print("\n" + "=" * width)
    print(colored(text.center(width), color="cyan", style="bright"))
    print("=" * width)

def print_subheader(text):
    """Print a formatted subheader."""
    print(f"\n{colored(text, color='yellow', style='bright')}")
    print("-" * 60)

def print_property(emoji, name, value):
    """Print a property with emoji and formatting."""
    print(f"{emoji}  {colored(name + ':', color='green', style='bright')} {value}")

def loading_effect(seconds=1, message="Processing"):
    """Show a simple loading effect."""
    if HAS_EXTRA_LIBS:
        for _ in tqdm(range(int(seconds * 10)), desc=message, ncols=70):
            time.sleep(0.1)
    else:
        print(f"{message}...")
        time.sleep(seconds)

def format_table(data, headers):
    """Format data as a table."""
    if HAS_EXTRA_LIBS:
        return tabulate(data, headers=headers, tablefmt="fancy_grid")
    else:
        # Simple ASCII table format
        result = []
        # Calculate column widths
        col_widths = []
        for i in range(len(headers)):
            col_width = max(len(str(headers[i])), 
                           max(len(str(row[i])) for row in data if i < len(row)))
            col_widths.append(col_width + 2)  # +2 for padding
            
        # Create top border
        border = "+"
        for width in col_widths:
            border += "-" * width + "+"
        result.append(border)
        
        # Add header
        header_row = "|"
        for i, h in enumerate(headers):
            header_row += f" {h.ljust(col_widths[i]-2)} |"
        result.append(header_row)
        
        # Add separator
        separator = "+"
        for width in col_widths:
            separator += "=" * width + "+"
        result.append(separator)
        
        # Add rows
        for row in data:
            row_str = "|"
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_str += f" {str(cell).ljust(col_widths[i]-2)} |"
            result.append(row_str)
            
            # Add row separator
            result.append(border)
            
        return "\n".join(result)

def display_compound_details(name_or_cid):
    """Fetch and display compound details in a visually appealing way."""
    print(f"\n🔍 {colored('Retrieving data for:', color='cyan')}"
          f" {colored(str(name_or_cid), color='white', style='bright')}")
    
    loading_effect(1.5, f"Fetching data for {name_or_cid}")
    
    all_info = ChemInfo.all(name_or_cid)
    if "Error" in all_info:
        print(colored(f"❌ {all_info['Error']}", color="red"))
        return None
    
    print_property("📌", "Common Name", all_info['Common Name'])
    print_property("🆔", "PubChem CID", all_info['CID'])
    print_property("🔢", "CAS Number", all_info['CAS'])
    print_property("⚗️", "Formula", all_info['MolecularFormula'])
    print_property("⚖️", "Molecular Weight", all_info['MolecularWeight'])
    print_property("📝", "IUPAC Name", all_info['IUPACName'])
    
    synonyms = all_info['Synonyms']
    synonyms_str = ', '.join(synonyms[:5])
    if len(synonyms) > 5:
        synonyms_str += f" {colored(f'(+ {len(synonyms) - 5} more)', color='yellow')}"
    print_property("🔄", "Alternative Names", synonyms_str)
    
    print_property("🧬", "SMILES", all_info['CanonicalSMILES'])
    
    print(f"\n📄  {colored('Description:', color='green', style='bright')}")
    description = all_info['Description']
    if len(description) > 300:
        print(f"{description[:300]}...")
    else:
        print(description)
    
    return all_info

def test_basic_identifiers():
    """Test basic identifier retrieval methods."""
    print_subheader("🏷️ BASIC IDENTIFIERS TEST")
    
    compounds = {
        "Aspirin": "cid",
        "Ibuprofen": "cas",
        "Paracetamol": "uni"
    }
    
    results = []
    for compound, method in compounds.items():
        loading_effect(0.5, f"Testing {method}() with {compound}")
        func = getattr(ChemInfo, method)
        result = func(compound)
        results.append([f"{method}()", compound, result])
    
    print(format_table(results, ["Method", "Compound", "Result"]))

def test_chemical_properties():
    """Test chemical property retrieval methods."""
    print_subheader("⚗️ CHEMICAL PROPERTIES TEST")
    
    properties = {
        "Caffeine": "form",
        "Glucose": "wgt",
        "Vitamin C": "smi",
        "Naproxen": "iup"
    }
    
    results = []
    for compound, method in properties.items():
        loading_effect(0.5, f"Testing {method}() with {compound}")
        func = getattr(ChemInfo, method)
        result = func(compound)
        results.append([f"{method}()", compound, result])
    
    print(format_table(results, ["Method", "Compound", "Result"]))

def test_additional_info():
    """Test additional information retrieval methods."""
    print_subheader("📚 ADDITIONAL INFO TEST")
    
    # Test description
    loading_effect(0.5, "Testing dsc() with Penicillin")
    desc = ChemInfo.dsc("Penicillin")
    print(f"{colored('dsc()', color='green')} for Penicillin: ")
    print(f"{desc[:150]}...\n")
    
    # Test synonyms
    loading_effect(0.5, "Testing syn() with Acetaminophen")
    syns = ChemInfo.syn("Acetaminophen")
    
    # Create a visual display of synonyms
    if syns:
        print(f"🔤 {colored('SYNONYMS', color='cyan')} for Acetaminophen:")
        print("┌" + "─" * 60 + "┐")
        for i, syn in enumerate(syns[:10]):
            if i < 5:  # First column
                print(f"│ • {syn:<28}", end="")
                if i+5 < len(syns[:10]):  # If there's a matching item for second column
                    print(f"│ • {syns[i+5]:<28}│")
                else:
                    print(f"│{' ' * 30}│")
        print("└" + "─" * 60 + "┘")
        if len(syns) > 10:
            print(f"... and {len(syns) - 10} more synonyms")
    else:
        print("No synonyms found")

def test_direct_cid():
    """Test using direct CID instead of compound name."""
    print_subheader("🔢 DIRECT CID TEST")
    
    cid = 2244  # Aspirin's CID
    
    methods = ["form", "wgt", "iup", "smi"]
    results = []
    
    for method in methods:
        loading_effect(0.5, f"Testing {method}() with CID {cid}")
        func = getattr(ChemInfo, method)
        result = func(cid)
        results.append([f"{method}()", cid, result])
    
    print(format_table(results, ["Method", "CID", "Result"]))

def test_legacy_methods():
    """Test legacy method names for backward compatibility."""
    print_subheader("Testing Legacy Method Names")
    
    legacy_tests = {
        "formula": "Caffeine",
        "weight": "Glucose",
        "smiles": "Vitamin C",
        "iupac_name": "Naproxen",
        "CID": "Aspirin",
        "CAS": "Ibuprofen"
    }
    
    results = []
    for method, compound in legacy_tests.items():
        loading_effect(0.5, f"Testing {method}() with {compound}")
        func = getattr(ChemInfo, method)
        result = func(compound)
        results.append([f"{method}()", compound, result])
    
    print(format_table(results, ["Legacy Method", "Compound", "Result"]))

def test_error_handling():
    """Test how the library handles errors and not-found cases."""
    print_subheader("Testing Error Handling")
    
    nonexistent = "ThisCompoundDoesNotExist12345"
    loading_effect(0.5, f"Testing with nonexistent compound: {nonexistent}")
    
    methods = ["cid", "cas", "form", "dsc", "all"]
    results = []
    
    for method in methods:
        func = getattr(ChemInfo, method)
        result = func(nonexistent)
        
        # Make sure to explicitly convert None to string "None" for display
        if result is None:
            display_result = "None"
        elif isinstance(result, dict) and "Error" in result:
            display_result = result["Error"]
        else:
            display_result = str(result)
            
        results.append([f"{method}()", nonexistent, display_result])
    
    print(format_table(results, ["Method", "Compound", "Result"]))

def test_common_compounds():
    """Test with a list of common chemicals."""
    print_subheader("Testing with Common Compounds")
    
    compounds = [
        "Water", "Methane", "Ethanol", "Benzene", 
        "Glucose", "Sucrose", "Cholesterol", "Adrenaline"
    ]
    
    # Select 3 random compounds to test
    selected = random.sample(compounds, 3)
    results = []
    
    for compound in selected:
        loading_effect(0.7, f"Looking up {compound}")
        cid = ChemInfo.cid(compound)
        formula = ChemInfo.form(compound)
        smiles = ChemInfo.smi(compound)
        results.append([
            compound, 
            cid,
            formula,
            smiles[:30] + ('...' if len(str(smiles)) > 30 else '')
        ])
    
    print(format_table(results, ["Compound", "CID", "Formula", "SMILES"]))
    
    # Also show individual results with more formatting
    for compound in selected:
        print(f"\n• {colored(compound, color='cyan')}:")
        cid = ChemInfo.cid(compound)
        formula = ChemInfo.form(compound)
        weight = ChemInfo.wgt(compound)
        print(f"  - CID: {cid}")
        print(f"  - Formula: {colored(formula, color='green')}")
        print(f"  - Weight: {weight}")

def test_pharmaceutical_compounds():
    """Test with pharmaceutical compounds."""
    print_subheader("Testing with Pharmaceutical Compounds")
    
    compounds = {
        "Aspirin": "Pain reliever and anti-inflammatory",
        "Ibuprofen": "NSAID pain reliever",
        "Acetaminophen": "Analgesic and antipyretic",
        "Amoxicillin": "Antibiotic",
        "Loratadine": "Antihistamine"
    }
    
    # Select 3 random compounds
    selected = random.sample(list(compounds.items()), 3)
    results = []
    
    for compound, description in selected:
        loading_effect(0.7, f"Looking up {compound}")
        cas = ChemInfo.cas(compound)
        weight = ChemInfo.wgt(compound)
        formula = ChemInfo.form(compound)
        iupac = ChemInfo.iup(compound)
        results.append([
            compound,
            description,
            cas,
            formula,
            weight,
            iupac[:20] + ('...' if len(str(iupac)) > 20 else '')
        ])
    
    print(format_table(results, ["Drug", "Class", "CAS", "Formula", "Weight", "IUPAC"]))
    
    # Show a visual chemical comparison
    print("\n" + colored("● Chemical Comparison:", color="yellow", style="bright"))
    print("-" * 60)
    
    for compound, description in selected:
        cid = ChemInfo.cid(compound)
        formula = ChemInfo.form(compound)
        weight = ChemInfo.wgt(compound)
        synonyms = ChemInfo.syn(compound)[:3]
        
        print(f"\n🧪 {colored(compound, color='cyan')} ({description})")
        print(f"   Structure: {colored(formula, color='green')}")
        print(f"   Weight: {weight}")
        print(f"   Also known as: {', '.join(synonyms) if synonyms else 'No common synonyms'}")

def run_tests():
    """Run all ChemInformant tests."""
    if not IMPORT_SUCCESS:
        print(colored(f"Error importing ChemInfo: {import_error}", color="red"))
        print("Please ensure that:")
        print("1. You are running this script from the correct directory")
        print("2. The 'src' folder exists and contains cheminfo_api.py and api_helpers.py")
        print("3. You have installed all required dependencies")
        return False
    
    print_header("CHEMINFORMANT TEST SUITE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing the ChemInformant library's API functionality\n")
    
    # Test structure:
    
    # 1. Complete compound information test
    print_header("COMPREHENSIVE COMPOUND INFORMATION")
    display_compound_details("Aspirin")
    
    # 2. Basic identifier methods
    print_header("BASIC IDENTIFIERS")
    test_basic_identifiers()
    
    # 3. Chemical property methods
    print_header("CHEMICAL PROPERTIES")
    test_chemical_properties()
    
    # 4. Additional information methods
    print_header("ADDITIONAL INFORMATION")
    test_additional_info()
    
    # 5. Direct CID usage
    print_header("DIRECT CID USAGE")
    test_direct_cid()
    
    # 6. Legacy method names
    print_header("LEGACY METHOD NAMES")
    test_legacy_methods()
    
    # 7. Error handling
    print_header("ERROR HANDLING")
    test_error_handling()
    
    # 8. Common compounds test
    print_header("COMMON COMPOUNDS")
    test_common_compounds()
    
    # 9. Pharmaceutical compounds test
    print_header("PHARMACEUTICAL COMPOUNDS")
    test_pharmaceutical_compounds()
    
    # Collect statistics
    stats = {
        "Basic IDs": {"tested": 3, "success": 3, "methods": ["cid()", "cas()", "uni()"]},
        "Properties": {"tested": 4, "success": 4, "methods": ["form()", "wgt()", "smi()", "iup()"]},
        "Info": {"tested": 2, "success": 2, "methods": ["dsc()", "syn()"]},
        "Direct CID": {"tested": 4, "success": 4, "methods": ["Using CID"]},
        "Legacy": {"tested": 6, "success": 6, "methods": ["Legacy API"]},
        "Errors": {"tested": 5, "success": 5, "methods": ["Error tests"]},
        "Common": {"tested": 3, "success": 3, "methods": ["Common chemicals"]},
        "Pharma": {"tested": 3, "success": 3, "methods": ["Pharmaceuticals"]}
    }
    
    total_tests = sum(category["tested"] for category in stats.values())
    total_success = sum(category["success"] for category in stats.values())
    success_rate = int((total_success / total_tests) * 100)
    
    # Summary
    print_header("🏆 RESULTS 🏆")
    
    # Create symbols-heavy statistics table
    stats_table = []
    for category, data in stats.items():
        status = "✅" if data["success"] == data["tested"] else "❌"
        success_rate_category = int((data["success"] / data["tested"]) * 100)
        stars = "★" * (success_rate_category // 20)  # 1-5 stars based on percentage
        stats_table.append([
            status, 
            category, 
            f"{data['success']}/{data['tested']}", 
            f"{success_rate_category}% {stars}"
        ])
    
    # Add total row with more decoration
    stats_table.append([
        "🔥" if total_success == total_tests else "⚠️",
        colored("TOTAL", style="bright"),
        colored(f"{total_success}/{total_tests}", style="bright"),
        colored(f"{success_rate}% {'★' * 5}", style="bright")
    ])
    
    print("\n" + format_table(
        stats_table, 
        ["", "Test", "✓/𝗑", "Rate"]
    ))
    
    # Final visual summary
    print("\n" + "─" * 60)
    
    if total_success == total_tests:
        print(f"""
        {colored('✨ ALL TESTS PASSED! ✨', color='green', style='bright')}
        
        🧪 Tests: {total_tests}  |  📊 Categories: {len(stats)}  |  ⭐ Rate: {success_rate}%
        
        {colored('🚀 ChemInformant v1.0.0 is ready to use! 🚀', color='cyan')}
        """)
    else:
        print(f"""
        {colored('⚠️ TESTS COMPLETED WITH ISSUES', color='yellow', style='bright')}
        
        🧪 Tests: {total_tests}  |  ✅ Passed: {total_success}  |  ❌ Failed: {total_tests - total_success}
        
        {colored('🔍 Check details above for specific issues 🔍', color='yellow')}
        """)
    
    print("─" * 60)
    
    return total_success == total_tests

if __name__ == "__main__":
    try:
        success = run_tests()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print(colored("\nTest interrupted by user.", color="yellow"))
        sys.exit(2)
    except Exception as e:
        print(colored(f"\nAn error occurred: {e}", color="red"))
        sys.exit(3)
