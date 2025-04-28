import ChemInformant as ci
import pprint # For better dictionary printing
import sys

identifiers = ["Water", 2244] # Keep it simple
print(f"Looking up: {identifiers}")

try:
    results = ci.get_multiple_compounds(identifiers)
    print("\n--- Raw Results ---_-")
    pprint.pprint(results) # Print the raw dictionary

    print("\n--- Type Check ---_-")
    if isinstance(results, dict):
         print("Result IS a dictionary.")
         for key, value in results.items():
             print(f"Input: {repr(key)}, Output Type: {type(value)}")
    else:
         print(f"Result IS NOT a dictionary. Type: {type(results)}")

except Exception as e:
    print(f"\nAn error occurred: {type(e).__name__}: {e}", file=sys.stderr) 