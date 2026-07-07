import pandas as pd

files = {
    "Business Licences": "data/raw/business_licences.csv",
    "Building Permits": "data/raw/issued_building_permits.csv",
    "Parking Tickets": "data/raw/parking_tickets.csv",
    "Property Tax": "data/raw/property_tax_report.csv",
}

for name, path in files.items():
    print("=" * 60)
    print(name)
    print("=" * 60)

    try:
        df = pd.read_csv(path, sep=None, engine="python")

        print(f"Shape: {df.shape}")
        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nFirst 5 Rows:")
        print(df.head())

    except Exception as e:
        print(f"Error loading {name}: {e}")

    print("\n")