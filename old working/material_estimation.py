import os
import pandas as pd

MATERIAL_RATES = {
    "Cement (bags)": 8,
    "Paint (gallons)": 1 / 3.5,  
    "Tiles (boxes)": 1,
    "Bricks (units)": 1200,
    "Sand (cubic meters)": 0.6,
    "Steel (kg)": 10,
    "Concrete (cubic meters)": 0.5,
    "Glass (sq ft)": 2,
    "Wood (sq ft)": 5,
    "Plaster (kg)": 10
}

def estimate_materials(room_data):
    """Calculate material requirements for each room based on its area."""
    materials = []

    for _, row in room_data.iterrows():
        room_materials = {"Room": row["Room Name"], "Area (sq ft)": row["Area (sq ft)"]}
        for material, rate in MATERIAL_RATES.items():
            room_materials[material] = (row["Area (sq ft)"] / 100) * rate  
        materials.append(room_materials)

    return pd.DataFrame(materials)

if __name__ == "__main__":
    input_file = "extracted_data/sample_room_data.csv"
    output_file = "extracted_data/sample_roomwise_material_estimation.csv"

    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found. Run `extract_cad.py` first.")
        exit(1)

    try:
        df = pd.read_csv(input_file)

        if df.empty or "Area (sq ft)" not in df.columns:
            print("❌ No valid room area data found.")
            exit(1)

        material_df = estimate_materials(df)

        material_df.to_csv(output_file, index=False)
        print(f"✅ Room-wise material estimation saved: {output_file}")

    except Exception as e:
        print(f"❌ Error processing room-wise material estimation: {e}")
