"""
Cleanup Script - Remove Unnecessary Files

This script removes duplicate/debug files that are no longer needed.
The essential working files are kept.

Run this to clean up the project directory.
"""

import os

# Files to remove (duplicates, debug files, redundant documentation)
files_to_remove = [
    # Duplicate app files
    "app.py",                    # Use app_debug.py instead
    "app_standalone.py",         # Use app_debug.py instead
    
    # Duplicate test files
    "simple_test.py",            # Use test_final.py instead
    "test_api.py",               # Use test_final.py instead
    "test_working.py",           # Use test_final.py instead
    "test_detailed.py",          # Debug only
    
    # Debug/utility files
    "inspect_orders.py",         # Debug only
    "reproduce_pandas.py",       # Debug only
    "restart_server.py",         # Not needed
    
    # Redundant documentation (info consolidated in README.md)
    "QUICKSTART.md",
    "API_USAGE.md",
    "WORKING_SOLUTION.md",
    "SETUP_COMPLETE.md",
    "RESTART.md",
    "USE_STANDALONE.md",
    
    # Output files
    "debug_output.txt",
    "test_output.txt",
    "test_result.txt",
]

def cleanup():
    """Remove unnecessary files"""
    removed = []
    not_found = []
    
    print("\n" + "="*60)
    print("CLEANUP - Removing Unnecessary Files")
    print("="*60 + "\n")
    
    for filename in files_to_remove:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                removed.append(filename)
                print(f"✓ Removed: {filename}")
            except Exception as e:
                print(f"✗ Error removing {filename}: {e}")
        else:
            not_found.append(filename)
    
    print("\n" + "="*60)
    print(f"Summary: {len(removed)} files removed")
    if not_found:
        print(f"({len(not_found)} files already didn't exist)")
    print("="*60 + "\n")
    
    print("Essential files kept:")
    print("  ✓ app_debug.py (main server)")
    print("  ✓ run_me.py (quick start)")
    print("  ✓ test_final.py (API test)")
    print("  ✓ test_direct.py (direct test)")
    print("  ✓ start_all.py (complete setup)")
    print("  ✓ run_etl_debug.py (ETL)")
    print("  ✓ run_training_debug.py (training)")
    print("  ✓ README.md (main documentation)")
    print("  ✓ PROJECT_SUMMARY.md (quick reference)")
    print("  ✓ FILE_INDEX.md (file guide)")
    print("  ✓ All folders (api/, services/, models/, etc.)")
    print("\nCleanup complete! ✨")

if __name__ == "__main__":
    cleanup()
