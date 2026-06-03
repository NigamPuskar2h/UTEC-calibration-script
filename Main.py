import logic
import os
import glob

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matches = glob.glob(os.path.join(script_dir, "*.xlsx"))

    if not matches:
        print("no input files found")
    else:
        xlsx_path = matches[0]
        print(f"Found: {xlsx_path}")
    logic.main_logic()

if __name__ == "__main__":
    main()