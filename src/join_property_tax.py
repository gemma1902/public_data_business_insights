import pandas as pd
import re

def normalize_street(s):
    if pd.isna(s):
        return None
    s = s.upper().strip()
    s = re.split(r',\s*VANCOUVER', s)[0]
    s = s.strip().rstrip(',').strip()

    replacements = {
        r'\bSTREET\b': 'ST', r'\bAVENUE\b': 'AVE', r'\bBOULEVARD\b': 'BLVD',
        r'\bDRIVE\b': 'DR', r'\bROAD\b': 'RD', r'\bPLACE\b': 'PL',
        r'\bCRESCENT\b': 'CRES', r'\bHIGHWAY\b': 'HWY',
    }
    for pattern, repl in replacements.items():
        s = re.sub(pattern, repl, s)
    s = re.sub(r'\s+', ' ', s).strip()

    # --- pull out a leading OR trailing direction letter (E/W/N/S) ---
    direction = None
    tokens = s.split(' ')
    if tokens[0] in ('E', 'W', 'N', 'S'):
        direction = tokens[0]
        tokens = tokens[1:]
    elif tokens[-1] in ('E', 'W', 'N', 'S'):
        direction = tokens[-1]
        tokens = tokens[:-1]

    base = ' '.join(tokens)
    # canonical form: always direction as SUFFIX, e.g. "7TH AVE W", "BROADWAY W"
    if direction:
        return f"{base} {direction}"
    return base

# --- Rebuild the lookup table with the fixed normalizer ---
licences = pd.read_csv("data/raw/business_licences.csv", sep=';', low_memory=False)
permits = pd.read_csv("data/raw/issued_building_permits.csv", sep=';', low_memory=False)

lic_pairs = licences[['Street', 'LocalArea']].dropna().copy()
lic_pairs['Street_clean'] = lic_pairs['Street'].apply(normalize_street)
lic_pairs = lic_pairs[['Street_clean', 'LocalArea']]

permits_clean = permits[['Address', 'GeoLocalArea']].dropna().copy()
permits_clean['Street_raw'] = permits_clean['Address'].str.replace(r'^\d+\s*', '', regex=True)
permits_clean['Street_clean'] = permits_clean['Street_raw'].apply(normalize_street)
permits_clean = permits_clean.rename(columns={'GeoLocalArea': 'LocalArea'})[['Street_clean', 'LocalArea']]

combined = pd.concat([lic_pairs, permits_clean], ignore_index=True).dropna()

street_area_counts = combined.groupby(['Street_clean', 'LocalArea']).size().reset_index(name='count')
lookup = (
    street_area_counts
    .sort_values('count', ascending=False)
    .drop_duplicates(subset='Street_clean', keep='first')[['Street_clean', 'LocalArea']]
)
lookup.to_csv("data/raw/street_to_localarea_lookup.csv", index=False)
print(f"Lookup rebuilt: {len(lookup)} streets")

# --- Reapply to property tax ---
tax = pd.read_csv("data/raw/property_tax_report.csv", sep=';', low_memory=False)
tax['Street_clean'] = tax['STREET_NAME'].apply(normalize_street)
tax_with_area = tax.merge(lookup, on='Street_clean', how='left')

matched = tax_with_area['LocalArea'].notna().sum()
total = len(tax_with_area)
print(f"Matched: {matched}/{total} ({matched/total*100:.1f}%)")

unmatched = tax_with_area[tax_with_area['LocalArea'].isna()]['STREET_NAME'].value_counts().head(20)
print(f"\nTop unmatched streets:")
print(unmatched)

tax_with_area.to_csv("data/raw/property_tax_with_area.csv", index=False)