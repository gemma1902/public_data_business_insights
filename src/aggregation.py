import pandas as pd

def normalize_area(s):
    if pd.isna(s):
        return None
    return s.strip().replace('-', ' ').upper()



# --- Business licences: competitor density ---
licences = pd.read_csv("data/raw/business_licences.csv", sep=';', low_memory=False)
licences['LocalArea'] = licences['LocalArea'].apply(normalize_area) 

target_categories = ['Restaurant', 'Limited Service Food Establishment']
competitor_counts = (
    licences[licences['BusinessType'].isin(target_categories)]
    .groupby('LocalArea').size().reset_index(name='competitor_count')
)

# --- Parking tickets: traffic proxy ---
tickets = pd.read_csv("data/raw/parking_tickets_with_area.csv", low_memory=False)
tickets['LocalArea'] = tickets['LocalArea'].apply(normalize_area)

traffic = tickets.groupby('LocalArea').size().reset_index(name='ticket_volume')

# --- Property tax: occupancy cost ---
tax = pd.read_csv("data/raw/property_tax_with_area.csv", low_memory=False)
tax['LocalArea'] = tax['LocalArea'].apply(normalize_area)

tax['total_value'] = tax['CURRENT_LAND_VALUE'] + tax['CURRENT_IMPROVEMENT_VALUE']
cost = tax.groupby('LocalArea')['total_value'].mean().reset_index(name='avg_property_value')

# --- Building permits: momentum (recent years vs earlier) ---
permits = pd.read_csv("data/raw/issued_building_permits.csv", sep=';', low_memory=False)
permits['GeoLocalArea'] = permits['GeoLocalArea'].apply(normalize_area)

recent = permits[permits['IssueYear'] >= permits['IssueYear'].max() - 2]
momentum = recent.groupby('GeoLocalArea').size().reset_index(name='recent_permit_count')
momentum = momentum.rename(columns={'GeoLocalArea': 'LocalArea'})

# --- Combine into one table ---
combined = competitor_counts.merge(traffic, on='LocalArea', how='outer') \
    .merge(cost, on='LocalArea', how='outer') \
    .merge(momentum, on='LocalArea', how='outer')

combined = combined[combined['LocalArea'] != 'OUT OF TOWN']

# --- Convert each metric to a 0-100 percentile rank ---
combined['competitor_pctl'] = combined['competitor_count'].rank(pct=True) * 100
combined['traffic_pctl'] = combined['ticket_volume'].rank(pct=True) * 100
combined['cost_pctl'] = combined['avg_property_value'].rank(pct=True) * 100
combined['momentum_pctl'] = combined['recent_permit_count'].rank(pct=True) * 100

# --- Combine into one weighted opportunity score ---
combined['opportunity_score'] = (
    (100 - combined['competitor_pctl']) * 0.3 +
    combined['traffic_pctl'] * 0.3 +
    (100 - combined['cost_pctl']) * 0.2 +
    combined['momentum_pctl'] * 0.2
)

combined_sorted = combined.sort_values('opportunity_score', ascending=False)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(combined_sorted[['LocalArea', 'opportunity_score', 'competitor_count', 'ticket_volume', 'avg_property_value', 'recent_permit_count']].to_string())

combined.to_csv("data/processed/opportunity_metrics_by_area.csv", index=False)