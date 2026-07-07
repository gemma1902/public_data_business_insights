# Vancouver Business Opportunity Finder

An interactive tool that helps someone decide where in Vancouver to open a restaurant or food business, using four real signals from the City of Vancouver's open data: competitor density, foot traffic, occupancy cost and development momentum.

## The Problem

Choosing a business location often comes down to instinct. This project looks at whether open city data can make that decision a little more evidence-based.

**can public city data — the kind every municipality already publishes — turn that into an evidence-based decision?**

## What It Does

The app compares Vancouver’s 21 local areas and creates an overall opportunity score. The score is not hidden — users can still see the original numbers behind it.

It includes:

- A data table of neighbourhood metrics
- A chart for comparing areas by one metric at a time
- A cost vs traffic scatter plot
- A neighbourhood lookup with rank and key figures
- An Opportunity Builder where users can adjust the scoring weights themselves

## Data Sources

All data is pulled from the [City of Vancouver Open Data Portal](https://opendata.vancouver.ca):

| Dataset | Used for |
|---|---|
| Business Licences | Competitor density (active Restaurant / Limited Service Food Establishment licences) |
| Parking Tickets | Foot traffic proxy (ticket volume as an indicator of area activity) |
| Property Tax Report | Occupancy cost proxy (average assessed land + improvement value) |
| Issued Building Permits | Development momentum (permits issued in the last 3 years) |

## Methodology

1. **Cleaning & joining:** The data was cleaned, joined, and grouped by local area. Some datasets already included neighbourhood names, while others needed a street-to-neighbourhood lookup table. After normalising street names, most records were successfully matched.

2. **Aggregation:** Each dataset is reduced to one metric per neighbourhood.

3. **Scoring:** Each metric was converted into a percentile score from 0–100 so the values could be compared fairly. Lower competition and lower cost were treated as positive (lower = good), while higher traffic and more recent permits increased the score.


## Known Limitations
**This is a decision-support tool, not a perfect prediction model.**

- **Cost is a proxy, not a rent figure.** Property tax assessed value mixes all property types (condos, single-family homes, commercial units) and isn't the same as commercial lease rates, which aren't public data in BC.
- **Traffic is inferred, not measured.** Parking ticket volume is a proxy for area activity, not a direct measure of foot traffic or customer count.
- **A small number of streets (mostly newer, low-density laneways) weren't matched** to a neighbourhood due to sparse coverage in the source data used to build the lookup table — roughly 1–3% of records depending on the dataset.
- **Scoring weights are a judgment call**, not an empirically derived formula — this is why the app includes an adjustable-weight tool rather than presenting one fixed number as definitive.
- **Census/demographic data was considered but excluded** — the most recent local-area-level dataset available was from 2016, and using outdated demographics risked misrepresenting current conditions more than omitting them entirely.

## Tech Stack

- Python, pandas — data cleaning, joining, aggregation
- Streamlit — interactive web app
- Plotly — charts (bar, scatter)

## Running It Locally
```python
pip install streamlit pandas plotly
streamlit run src/app.py
```

## Project Structure
```python
data/
raw/          # original downloaded datasets
processed/    # cleaned, joined, scored output
src/
schema.py             # inspect raw file structure
join_parking_tickets.py
join_property_tax.py
aggregation.py         # builds the final scored dataset
app.py                 # Streamlit app
```