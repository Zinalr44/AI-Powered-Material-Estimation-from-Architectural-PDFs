import os
import subprocess

scripts = [
    "extract_text.py",
    "extract_tables.py",
    "extract_ocr.py",
    "extract_vector.py",
    "extract_cad.py",
    "material_estimation.py",
    "generate_report.py"
]

for script in scripts:
    print(f"\nRunning {script}...\n")
    result = subprocess.run(["python", f"scripts/{script}"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Error running {script}: {result.stderr}")
