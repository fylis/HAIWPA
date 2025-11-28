#!/usr/bin/env python3
"""
Simple script to load a Prolog file and query it using PySwip
Usage: python prolog_query.py <path_to_prolog_file.pl>
Done with claude.ai
"""

import sys
from pyswip import Prolog

def main():
    if len(sys.argv) != 2:
        print("Usage: python prolog_query.py <path_to_prolog_file.pl>")
        sys.exit(1)
    
    prolog_file = sys.argv[1]
    
    try:
        # Create Prolog instance
        prolog = Prolog()
        
        # Load the Prolog file
        print(f"Loading Prolog file: {prolog_file}")
        prolog.consult(prolog_file)
        print("File loaded successfully!\n")
        
        # Query likes(sam, X)
        print("Querying: likes(sam, X)")
        print("-" * 40)
        
        # Get all solutions
        solutions = list(prolog.query("likes(sam, X), chinese(X)"))
        
        if solutions:
            print(f"Found {len(solutions)} result(s):\n")
            for i, solution in enumerate(solutions, 1):
                print(f"{i}. Sam likes: {solution['X']}")
        else:
            print("No results found. Sam doesn't like anything!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()