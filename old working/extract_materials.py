import os
import pandas as pd

# Define material consumption rates per 100 sq ft
MATERIAL_RATES = {
    "Cement (bags)": 8,
    "Paint (gallons)": 1 / 3.5,  # 1 gallon covers 350 sq ft
    "Tiles (boxes)": 1,
    "Bricks (units)": 1200,
    "Sand (cubic meters)": 0.6,
    "Steel (kg)": 10,
    "Concrete (cubic meters)": 0.5,
    "Glass (sq ft)": 2,
    "Wood (sq ft)": 5,
    "Plaster (kg)": 10
}

def estimate_materials(area):
    """Calculate material requirements based on total area (sq ft)."""
    materials = {"Total Area (sq ft)": area}
    for material, rate in MATERIAL_RATES.items():
        materials[material] = (area / 100) * rate  # Convert to total material needed
    return materials

if __name__ == "__main__":
    cad_file = "extracted_data/sample_cad_area.csv"
    room_file = "extracted_data/sample_room_data.csv"
    output_file_total = "extracted_data/sample_material_estimation.csv"
    output_file_room = "extracted_data/sample_room_material_estimation.csv"

    # Ensure CAD data exists
    if not os.path.exists(cad_file):
        print(f"❌ Error: {cad_file} not found. Run `extract_cad.py` first.")
        exit(1)

    # Read CAD area data
    try:
        df_cad = pd.read_csv(cad_file)

        # Check if 'Area (sq ft)' column exists
        if "Area (sq ft)" not in df_cad.columns or df_cad.empty:
            print("❌ No valid area data found in CAD file.")
            exit(1)

        # Calculate total material estimation
        total_area = df_cad["Area (sq ft)"].sum()
        print(f"📏 Total extracted area: {total_area:.2f} sq ft")

        total_materials = estimate_materials(total_area)
        pd.DataFrame([total_materials]).to_csv(output_file_total, index=False)
        print(f"✅ Total material estimation saved: {output_file_total}")

        # Room-wise material estimation (if room data exists)
        if os.path.exists(room_file):
            df_rooms = pd.read_csv(room_file)

            if "Room" in df_rooms.columns and "Area (sq ft)" in df_rooms.columns:
                room_materials = []
                for _, row in df_rooms.iterrows():
                    room_name = row["Room"]
                    room_area = row["Area (sq ft)"]
                    materials = estimate_materials(room_area)
                    materials["Room"] = room_name
                    room_materials.append(materials)

                pd.DataFrame(room_materials).to_csv(output_file_room, index=False)
                print(f"✅ Room-wise material estimation saved: {output_file_room}")
            else:
                print("⚠️ Room data is incomplete. Skipping room-wise material estimation.")
        else:
            print("⚠️ No room data found. Only total material estimation generated.")

    except Exception as e:
        print(f"❌ Error processing material estimation: {e}")
