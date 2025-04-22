import os
import pandas as pd

if __name__ == "__main__":
    roomwise_materials_file = "extracted_data/sample_roomwise_material_estimation.csv"
    final_report_csv = "extracted_data/final_project_report.csv"
    final_report_excel = "extracted_data/final_project_report.xlsx"

    if not os.path.exists(roomwise_materials_file):
        print(f"❌ Error: {roomwise_materials_file} not found.")
        exit(1)

    try:
        report_df = pd.read_csv(roomwise_materials_file)

        report_df.to_csv(final_report_csv, index=False)
        report_df.to_excel(final_report_excel, index=False)

        print(f"✅ Final report saved: {final_report_csv}")
        print(f"✅ Final report saved: {final_report_excel}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
