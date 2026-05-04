# project - Nodal-power-market-simulator (Delhi vs Mumbai 2 bus electricity Market Model)
import pypsa                                # THE power grid toolkit — builds the network, runs the LP optimization, and gives us the results
import pandas as pd                         # handles tables and time-series data 
import plotly.graph_objects as go           # makes interactive web charts
from plotly.subplots import make_subplots   #  put 4 charts in one figure
import numpy as np                          # fast maths on arrays of numbers
import webbrowser , os                      # to open the dashboard in your web browser

print("Delhi-Mumbai Electricity Market Model")

# ── STEP 1: CREATE THE NETWORK ──
n = pypsa.Network()                          # n = empty grid world.
snapshots = pd.date_range("2024-01-15", periods=24, freq="h")  # 24 hourly snapshots for one day (Jan 15, 2024),"periods=24" = 24 items.  "freq=h" = hourly spacing
n.set_snapshots(snapshots)                     # Set the time steps for our model. This creates a time index that we can use to assign time-varying data (like demand and renewable output) later on.
print("\n[1] Network created. solving for : jan 15, 2024")

# ── STEP 2: ADD BUSES (Cities) ───

n.add("Bus",
      "Delhi",
      x=77.21,
      y=28.61,
      v_nom=400
      )
n.add("Bus",
      "Mumbai",
      x=72.87,
      y=19.07,
      v_nom=400
      )
print("\n[2] Added 2 buses:")
print(n.buses[["x", "y", "v_nom"]].to_string())

# ── STEP 3: ADD ELECTRICITY DEMAND (Loads) ───
n.add("Load",
      "Delhi demand",
      bus="Delhi",
     carrier="AC"        
      )
n.add("Load",
      "Mumbai demand",
      bus="Mumbai",
      carrier="AC"         
      )
# THE ACTUAL DEMAND DATA — these are synthetic hourly demand profiles for Delhi and Mumbai, based on typical daily patterns. In a real model, you would use actual historical data or forecasts.
delhi_load = [6000,5800,5600,5500,5400,5500,6000,6500,7000,7200,7400,7600,
              7800,8000,8200,8400,8600,8800,9000,8800,8500,8000,7500,7000]

mumbai_load = [3500,3400,3300,3200,3100,3200,3500,3800,4200,4500,4700,4800,
               4900,5000,5100,5200,5300,5400,5500,5300,5000,4700,4500,4200]

n.loads_t.p_set["Delhi demand"] = pd.Series(delhi_load, index=n.snapshots) # Assign the hourly demand profile to the "Delhi demand" load.
n.loads_t.p_set["Mumbai demand"] = pd.Series(mumbai_load, index=n.snapshots) # Assign the hourly demand profile to the "Mumbai demand" load.
total_demand_series = n.loads_t.p_set["Delhi demand"] + n.loads_t.p_set["Mumbai demand"] # Create a new series that sums the demand from both cities for each hour. 
print("\n[3] Demand Summary (24h):")
print(f"Peak: {total_demand_series.max():,.0f} MW")
print(f"Avg: {total_demand_series.mean():,.0f} MW")
print(f"Total Energy: {total_demand_series.sum()/1000:.2f} GWh")

# ── STEP 4: ADD GENERATORS (Power Plants) ──
# delhi
n.add("Generator",
      "Delhi Coal (Dadri NTPC)",
      bus="Delhi",
      p_nom=22637,                   # 22637 MW (actual Dadri capacity)
      marginal_cost=2200,           # ₹/MWh variable cost (CERC tariff order)
      carrier="coal",
      )
 
# Gas: Pragati Power Station, Delhi
n.add("Generator",
      "Delhi Gas (Pragati)",
      bus="Delhi",
      p_nom=1500,
      marginal_cost=6500,           # ₹/MWh — gas is expensive! (imported LNG)
      carrier="gas",
     )
 
# Solar: Rewa-like purchase + Delhi rooftop (aggregated)
n.add("Generator",
      "Delhi Solar (Rewa PPA)",
      bus="Delhi",
      p_nom=1200,
      marginal_cost=0,              # Solar has ZERO fuel cost (sunshine is free!)
      # Note: there is capital cost, but that's already paid. Variable cost = 0.
      carrier="solar")
 
# Hydro from Bhakra (imported via northern grid)
n.add("Generator",
      "Delhi Hydro (Bhakra)",
      bus="Delhi",
      p_nom=800,
      marginal_cost=500,            # very cheap — just O&M cost
      carrier="hydro")

# -- MUMBAI GENERATORS --------------------------------------------------------
# Mumbai Metropolitan Region power sources (Tata Power, Adani, MSEB data)
 
# Coal: Trombay TPS (Tata Power) + Chandrapur aggregated
n.add("Generator",
      "Mumbai Coal (Trombay)",
      bus="Mumbai",
      p_nom=22800,
      marginal_cost=2400,           # slightly more expensive (older plant)
      carrier="coal")
 
# Nuclear: Tarapur APS (real plant, 80 km from Mumbai)
n.add("Generator",
      "Mumbai Nuclear (Tarapur)",
      bus="Mumbai",
      p_nom=1400,
      marginal_cost=800,            # nuclear has very low variable cost
      carrier="nuclear")
 
# Solar: Adani/ReNew Maharashtra solar PPAs
n.add("Generator",
      "Mumbai Solar (ReNew)",
      bus="Mumbai",
      p_nom=600,
      marginal_cost=0,
      carrier="solar")
 
# Gas: Uran Gas Station (NTPC, near Mumbai)
n.add("Generator",
      "Mumbai Gas (Uran)",
      bus="Mumbai",
      p_nom=900,
      marginal_cost=6800,           # expensive gas — peaker plant
      carrier="gas")
 
# Wind: Maharashtra offshore + onshore
n.add("Generator",
      "Mumbai Wind (Maharashtra)",
      bus="Mumbai",
      p_nom= 450,
      marginal_cost=0,              # wind is free to run!
      carrier="wind")

# SOLAR AND WIND PROFILES 
solar_profile = [0,0,0,0,0,0.1,0.3,0.5,0.7,0.85,0.95,1.0,
                 1.0,0.95,0.85,0.7,0.5,0.3,0.1,0,0,0,0,0]
wind_profile = [0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.85,0.8,0.75,0.7,0.65,
                0.6,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.85,0.75,0.7]

# Real output ≤ p_max_pu × p_nom at each hour
n.generators_t.p_max_pu["Delhi Solar (Rewa PPA)"] = solar_profile
n.generators_t.p_max_pu["Mumbai Solar (ReNew)"] = solar_profile
n.generators_t.p_max_pu["Mumbai Wind (Maharashtra)"] = wind_profile
 
print(f"\n[4] Added {len(n.generators)} generators:")
print(n.generators[["bus", "p_nom", "marginal_cost", "carrier"]].to_string())

# ── STEP 5: ADD TRANSMISSION LINE ────
n.add("Line",
      "Delhi-Mumbai Grid",
      bus0="Delhi",   # sending end — power leaves from here
      bus1="Mumbai",  # receiving end — power arrives here
      s_nom=2000,     # thermal rating = 2,000 MW hard limit
      x=1.0,          # reactance 
      r=0.5,          # resistance
      efficiency=0.97)  # 97% efficient (3% losses)

print(f"\n[5] Added transmission line: Delhi to Mumbai (2,000 MW capacity)")

# ── STEP 6: RUN THE OPTIMISATION ───
n.optimize(solver_name="highs",
           log_to_console=False)
print(" optimisation complete!")

# ── STEP 7: READ THE RESULTS ───

#Generator dispatch (MW)
# 1. Generator dispatch — how much each plant produced at each of the 24 hours
dispatch = n.generators_t.p.T  # Transpose to get generators as rows and time as columns for easier analysis
dispatch["Total Generation (MWh)"] = dispatch.sum(axis=1) # sum all 24 hour columns
dispatch["Avg Dispatch (MW)"] = dispatch.mean(axis=1)     # mean of all 24 hour columns
dispatch["Capacity (MW)"] = n.generators["p_nom"]         # name of the column in n.generators that has the capacity (p_nom)
dispatch["Utilisation (%)"] = (dispatch["Avg Dispatch (MW)"] / dispatch["Capacity (MW)"] * 100).round(1)  # utilisation = (average dispatch / capacity) * 100 to get percentage.
dispatch["City"] = n.generators["bus"]  # add a column for the city (bus) that each generator is located at, by looking it up from n.generators["bus"]
print("\nGenerator Dispatch:")
print(dispatch.to_string())
print(dispatch[[
    "Total Generation (MWh)",
    "Avg Dispatch (MW)",
    "Capacity (MW)",
    "Utilisation (%)",
    "City"
]].to_string())

# 2.Total cost - multiply each plant's output × its cost, sum everything
total_cost = (n.generators_t.p * n.generators["marginal_cost"]).sum().sum()       #first .sum() for total cost per generator (sum across time), second .sum() to get total cost across all generators.
print(f"\nTotal operating cost for 24 hour: ${total_cost:,.0f}")
print(f" That's approximately ${total_cost/1e7:.2f} Crore per day")

# 3.Transmission flow
flow = n.lines_t.p0["Delhi-Mumbai Grid"] # positive flow means Delhi → Mumbai, negative flow means Mumbai → Delhi
print("\nTransmission Flow (24h):")
print(flow.to_string())
print(f"\nAvg Flow: {flow.mean():.0f} MW")
print(f"Max Flow: {flow.max():.0f} MW")
print(f"Min Flow: {flow.min():.0f} MW")
print(f"\nFlow at last hour: {flow.iloc[-1]:.0f} MW")
export_hours = (flow > 0).sum()
import_hours = (flow < 0).sum()
zero_hours   = (flow == 0).sum()
print(f"\nDelhi → Mumbai flow hours : {export_hours}")
print(f"Mumbai → Delhi flow hours : {import_hours}")
print(f"No flow hours             : {zero_hours}")

# 4. Electricity price (shadow price / marginal price at each bus)
prices = n.buses_t.marginal_price # This gives us the marginal price at each bus (city) for each hour. 
print("\nElectricity Prices (24h):")
print(prices.to_string())
print(f"\n Electricity Prices:")
print(f"Delhi Avg Price: ₹{prices['Delhi'].mean():.2f}/MWh")
print(f"Mumbai Avg Price: ₹{prices['Mumbai'].mean():.2f}/MWh")
print(f" Delhi 00:00 : ₹{prices['Delhi'].iloc[0]:.2f}/MWh (${prices['Delhi'].iloc[0]/1000:.2f}/kwh)")
print(f" Mumbai 00:00 : ₹{prices['Mumbai'].iloc[0]:.2f}/MWh (${prices['Mumbai'].iloc[0]/1000:.2f}/kwh)")
print(f"Delhi Max Price  : ₹{prices['Delhi'].max():.2f}/MWh")
print(f"Mumbai Max Price : ₹{prices['Mumbai'].max():.2f}/MWh")
price_diff = prices['Delhi'] - prices['Mumbai']

if (price_diff != 0).any():
    print("Price divergence exists → congestion present")
    print(f"   In real IEX, this congestion leads to 'price divergence'")

# ── STEP 8: BUILD THE RESULTS DASHBOARD ───

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Generator Dispatch by City (MW)",
        "Cost Stack — Who's Cheapest?",
        "Merit Order Curve (Delhi)",
        "Merit Order Curve (Mumbai)",
    ),
     vertical_spacing=0.18,
    horizontal_spacing=0.12,
)

#Carrier colours
carrier_colors ={
    "solar":   "#F4A623",
    "wind" :   "#27AE60",
    "hydro":   "#2980B9",
    "nuclear": "#8E44AD",
    "coal":    "#4A4A4A",
    "gas":     "#E67E22",
}

# chart 1 : stacked bar - dispatch by city
for city in ["Delhi", "Mumbai"]:
    city_gen = dispatch[dispatch["City"] == city]
    for _, row in city_gen.iterrows():
        carrier = n.generators.loc[row.name, "carrier"]
        fig.add_trace(go.Bar(
            x=[city],y=[row["Avg Dispatch (MW)"]],
            name=carrier,   
            marker_color=carrier_colors.get(carrier, "#999"),
            text=f"{row['Avg Dispatch (MW)']:.0f}",          textposition="inside",
            hovertemplate=f"<b>{row.name}</b><br>Avg Dispatch: {row['Avg Dispatch (MW)']:.0f} MW<extra></extra",
            showlegend=(city == "Delhi"),
            legendgroup=carrier,
        ), row=1, col=1)

# ── Chart 2: Cost comparison — marginal cost of each plant ────────────────────
gen_sorted = n.generators.sort_values("marginal_cost")
fig.add_trace(go.Bar(
    x=gen_sorted.index,
    y=gen_sorted["marginal_cost"],
    marker_color=[carrier_colors.get(c, "#999") for c in gen_sorted["carrier"]],
    hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}/MWh<extra></extra>",
    showlegend=False,
    text=[f"₹{c:,.0f}" for c in gen_sorted["marginal_cost"]],
    textposition="outside",
    textangle=-60,
    textfont=dict(size=9),
), row=1, col=2)

# ── Charts 3 & 4: Merit Order Curves ─────────────────────────────────────────
# A merit order curve shows generators ordered from cheapest to most expensive.
# In a real electricity market, plants are dispatched in this order.
# The price is set by the LAST (most expensive) plant needed to meet demand.
 
for col_idx, city in enumerate(["Delhi", "Mumbai"], start=1):
    city_gen = n.generators[n.generators.bus == city].copy()
    city_gen = city_gen.sort_values("marginal_cost")
 
    # Build step-function coordinates
    cumulative_mw = 0
    x_vals = [0]
    y_vals = [city_gen["marginal_cost"].iloc[0]]
    for _, g in city_gen.iterrows():
        x_vals.extend([cumulative_mw, cumulative_mw + g["p_nom"]])
        y_vals.extend([g["marginal_cost"], g["marginal_cost"]])
        cumulative_mw += g["p_nom"]
 
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(100,149,237,0.15)",
        line=dict(color="#4169E1", width=2.5),
        name=f"{city} merit order",
        showlegend=False,
        hovertemplate="Capacity: %{x:.0f} MW<br>Cost: ₹%{y:,.0f}/MWh<extra></extra>",
    ), row=2, col=col_idx)
 
    # Demand line
    demand = 7000 if city == "Delhi" else 4200
    fig.add_vline(x=demand, line_dash="dash", line_color="red", line_width=2,
                  annotation_text=f"Demand {demand} MW", row=2, col=col_idx)
 
    # Market price line
    price = prices[city].mean()
    fig.add_hline(y=price, line_dash="dot", line_color="green", line_width=2,
                  annotation_text=f"Price ₹{price:.0f}/MWh", row=2, col=col_idx)
    

avg_demand = total_demand_series.mean()
peak_demand = total_demand_series.max()
total_energy = total_demand_series.sum()



# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text=(
            "<b>Delhi–Mumbai Electricity Market Model (PyPSA)</b><br>"
            f"Total Energy: {total_energy/1000:,.1f} GWh |" #
            f"Total Cost: ₹{total_cost/1e7:.1f} Cr/day>"
        ),
        x=0.5, xanchor="center",
        font=dict(size=17, color="#2C3E50"),
    ),
    height=820,
    barmode="stack",
    paper_bgcolor="#F8F9FA",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Arial, sans-serif", size=11),
    legend=dict(
        orientation="h", y=1.04, x=0.5, xanchor="center",
        bgcolor="rgba(255,255,255,0.9)", borderwidth=1,
    ),
)
fig.update_xaxes(showgrid=True, gridcolor="#EEEEEE")
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")
fig.update_yaxes(title_text="Dispatch (MW)", row=1, col=1)
fig.update_yaxes(title_text="Marginal Cost (₹/MWh)", row=1, col=2)
fig.update_xaxes(title_text="Cumulative Capacity (MW)", row=2, col=1)
fig.update_xaxes(title_text="Cumulative Capacity (MW)", row=2, col=2)
fig.update_yaxes(title_text="Marginal Cost (₹/MWh)", row=2, col=1)
fig.update_yaxes(title_text="Marginal Cost (₹/MWh)", row=2, col=2)
fig.update_xaxes(tickangle=-35, row=1, col=2, tickfont=dict(size=9))
 
out = "delhi_mumbai_market.html"
fig.write_html(out, include_plotlyjs=True, config={"scrollZoom": True})
print(f"\n✅ Dashboard saved as '{out}'")
webbrowser.open("file://" + os.path.abspath(out))
 
print("\n KEY INSIGHTS FROM THIS MODEL:")
print("   • Solar and wind always dispatch first — zero marginal cost")
print("   • Nuclear (Tarapur) dispatches next — very cheap")
print("   • Coal dispatches next — moderate cost")
print("   • Gas only dispatches if needed — very expensive (peaker)")
print("   • The merit order curve shows this stacking clearly")
print("   • Electricity price = cost of the LAST plant dispatched")
print("   • If Delhi exports to Mumbai, Delhi price < Mumbai price")


