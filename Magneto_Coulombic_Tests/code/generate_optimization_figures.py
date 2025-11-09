#!/usr/bin/env python3
"""
Generate visualization figures for parameter sweep optimization results
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Load results
results_file = Path(__file__).parent.parent / "results" / "parameter_sweep_results.json"
with open(results_file, 'r') as f:
    data = json.load(f)

# Set up plotting style
plt.style.use('seaborn-v0_8-darkgrid')
colors = plt.cm.viridis(np.linspace(0, 1, 6))

# Create output directory for figures
fig_dir = Path(__file__).parent.parent / "results" / "optimization_figures"
fig_dir.mkdir(exist_ok=True, parents=True)

#=============================================================================
# Figure 1: Parameter Sweep Summary (4 panels)
#=============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Parameter Sweep Results: Path to Feasibility', fontsize=16, fontweight='bold')

# Panel 1: Charge vs Mission Time
ax = axes[0, 0]
charge_data = data['charge_sweep']
charges = [d['charge_uC'] for d in charge_data]
times = [d['total_mission_years'] for d in charge_data]
ax.plot(charges, times, 'o-', linewidth=2, markersize=8, color=colors[0])
ax.set_xlabel('Charge per Shell (μC)', fontsize=11)
ax.set_ylabel('Mission Time (years)', fontsize=11)
ax.set_title('Effect of Charge Level', fontweight='bold')
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='1 year target')
ax.legend()

# Panel 2: Number of Shells vs Mission Time
ax = axes[0, 1]
shell_data = data['shell_sweep']
shells = [d['n_shells'] for d in shell_data]
times = [d['total_mission_years'] for d in shell_data]
ax.plot(shells, times, 's-', linewidth=2, markersize=8, color=colors[1])
ax.set_xlabel('Number of Coulomb Shells', fontsize=11)
ax.set_ylabel('Mission Time (years)', fontsize=11)
ax.set_title('Effect of Shell Configuration', fontweight='bold')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='1 year target')
ax.legend()

# Panel 3: Spacecraft Mass vs Mission Time
ax = axes[1, 0]
mass_data = data['mass_sweep']
masses = [d['mass_kg'] for d in mass_data]
times = [d['total_mission_years'] for d in mass_data]
ax.plot(masses, times, '^-', linewidth=2, markersize=8, color=colors[2])
ax.set_xlabel('Spacecraft Mass (kg)', fontsize=11)
ax.set_ylabel('Mission Time (years)', fontsize=11)
ax.set_title('Effect of Spacecraft Mass (CRITICAL!)', fontweight='bold')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='1 year target')
ax.axhline(y=0.1, color='green', linestyle='--', alpha=0.5, label='Feasible (<2 months)')
ax.legend()

# Highlight the breakthrough
for i, (mass, time) in enumerate(zip(masses, times)):
    if time < 0.1:
        ax.annotate(f'{time*365:.0f} days!', xy=(mass, time), xytext=(mass+5, time*2),
                   arrowprops=dict(arrowstyle='->', color='green', lw=2),
                   fontsize=9, color='green', fontweight='bold')

# Panel 4: Altitude vs Mission Time
ax = axes[1, 1]
alt_data = data['altitude_sweep']
alts = [d['altitude_km'] for d in alt_data]
times = [d['total_mission_years'] for d in alt_data]
b_fields = [d['b_field_uT'] for d in alt_data]
ax.plot(alts, times, 'D-', linewidth=2, markersize=8, color=colors[3])
ax.set_xlabel('Orbital Altitude (km)', fontsize=11)
ax.set_ylabel('Mission Time (years)', fontsize=11)
ax.set_title('Effect of Orbital Altitude', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='Highly Feasible')
ax.legend()

# Add B-field strength on secondary axis
ax2 = ax.twinx()
ax2.plot(alts, b_fields, 'o--', color='orange', alpha=0.5, label='B-field')
ax2.set_ylabel('Magnetic Field (μT)', fontsize=11, color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

plt.tight_layout()
plt.savefig(fig_dir / 'parameter_sweep_summary.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'parameter_sweep_summary.png'}")
plt.close()

#=============================================================================
# Figure 2: Baseline vs Optimal Comparison
#=============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Baseline vs Optimal Configuration Comparison', fontsize=16, fontweight='bold')

optimal = data['optimal_configuration']

# Comparison data
categories = ['Force\n(μN)', 'Acceleration\n(nm/s²)', 'Mission Time\n(days)']
baseline_vals = [6.42, 5.06, 113223 * 365.25]  # Convert years to days
optimal_vals = [optimal['force_uN'], optimal['acceleration_nm_s2'], optimal['total_mission_days']]

# Panel 1: Force Comparison
ax = axes[0]
x = np.arange(1)
width = 0.35
ax.bar(x - width/2, [baseline_vals[0]], width, label='Baseline (1270 kg)', color='red', alpha=0.7)
ax.bar(x + width/2, [optimal_vals[0]], width, label='Optimal (10 kg)', color='green', alpha=0.7)
ax.set_ylabel('Force (μN)', fontsize=12, fontweight='bold')
ax.set_title(f'Force: {optimal_vals[0]/baseline_vals[0]:.0f}× Improvement', fontweight='bold')
ax.set_xticks([])
ax.legend()
ax.set_yscale('log')
ax.grid(True, alpha=0.3, axis='y')

# Panel 2: Acceleration Comparison
ax = axes[1]
ax.bar(x - width/2, [baseline_vals[1]], width, label='Baseline', color='red', alpha=0.7)
ax.bar(x + width/2, [optimal_vals[1]], width, label='Optimal', color='green', alpha=0.7)
ax.set_ylabel('Acceleration (nm/s²)', fontsize=12, fontweight='bold')
ax.set_title(f'Accel: {optimal_vals[1]/baseline_vals[1]:.0f}× Faster', fontweight='bold')
ax.set_xticks([])
ax.legend()
ax.set_yscale('log')
ax.grid(True, alpha=0.3, axis='y')

# Panel 3: Mission Time Comparison
ax = axes[2]
ax.bar(x - width/2, [baseline_vals[2]/365.25], width, label='Baseline\n(113,223 years)', color='red', alpha=0.7)
ax.bar(x + width/2, [optimal_vals[2]/365.25], width, label='Optimal\n(0.54 days)', color='green', alpha=0.7)
ax.set_ylabel('Mission Time (years)', fontsize=12, fontweight='bold')
improvement = baseline_vals[2] / optimal_vals[2]
ax.set_title(f'Time: {improvement:.0e}× Faster', fontweight='bold')
ax.set_xticks([])
ax.legend()
ax.set_yscale('log')
ax.grid(True, alpha=0.3, axis='y')

# Add annotation showing actual mission time
ax.annotate('13 hours!', xy=(x + width/2, optimal_vals[2]/365.25),
           xytext=(0.3, optimal_vals[2]/365.25*10),
           arrowprops=dict(arrowstyle='->', color='green', lw=3),
           fontsize=14, color='green', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig(fig_dir / 'baseline_vs_optimal.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'baseline_vs_optimal.png'}")
plt.close()

#=============================================================================
# Figure 3: Top 10 Configurations
#=============================================================================
fig, ax = plt.subplots(figsize=(14, 8))

all_configs = data['all_configurations']
# Sort by mission time and get top 10
all_configs_sorted = sorted(all_configs, key=lambda x: x['total_mission_days'])[:10]

ranks = np.arange(1, 11)
mission_times_hours = [c['total_mission_days'] * 24 for c in all_configs_sorted]
config_labels = [f"{c['charge_uC']}μC, {c['n_shells']}sh,\n{c['mass_kg']}kg, {c['altitude_km']}km"
                for c in all_configs_sorted]

bars = ax.barh(ranks, mission_times_hours, color=plt.cm.RdYlGn_r(np.linspace(0.8, 0.2, 10)))
ax.set_yticks(ranks)
ax.set_yticklabels([f"#{r}" for r in ranks])
ax.set_xlabel('Mission Time (hours)', fontsize=13, fontweight='bold')
ax.set_ylabel('Configuration Rank', fontsize=13, fontweight='bold')
ax.set_title('Top 10 Configurations by Mission Time', fontsize=15, fontweight='bold')
ax.invert_yaxis()
ax.grid(True, alpha=0.3, axis='x')

# Add configuration details as text annotations
for i, (rank, time, label) in enumerate(zip(ranks, mission_times_hours, config_labels)):
    ax.text(time + 0.5, rank, f' {time:.1f}h - {label.replace(chr(10), ", ")}',
           va='center', fontsize=9)

# Highlight the best
ax.axvline(x=24, color='green', linestyle='--', alpha=0.5, linewidth=2, label='24 hours')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig(fig_dir / 'top_10_configurations.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'top_10_configurations.png'}")
plt.close()

#=============================================================================
# Figure 4: Mission Phase Breakdown (Optimal Config)
#=============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Optimal Configuration: Mission Phase Breakdown', fontsize=16, fontweight='bold')

# Phase times for optimal config
phases = ['Approach\n(10 km)', 'Rendezvous\n(1 m/s Δv)', 'Deorbit\n(100 m/s Δv)']
times_days = [optimal['approach_days'], optimal['rendezvous_days'], optimal['deorbit_days']]
times_hours = [t * 24 for t in times_days]

# Panel 1: Phase times as bar chart
colors_phases = ['#3498db', '#e74c3c', '#f39c12']
bars = ax1.bar(phases, times_hours, color=colors_phases, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Phase Duration (hours)', fontsize=12, fontweight='bold')
ax1.set_title('Time per Mission Phase', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, time in zip(bars, times_hours):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{time:.2f}h\n({time*60:.1f}min)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Panel 2: Phase times as pie chart
ax2.pie(times_hours, labels=phases, autopct='%1.1f%%', startangle=90,
       colors=colors_phases, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title(f'Total Mission: {sum(times_hours):.2f} hours', fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'mission_phase_breakdown.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'mission_phase_breakdown.png'}")
plt.close()

#=============================================================================
# Figure 5: Configuration Parameter Heatmap
#=============================================================================
fig, ax = plt.subplots(figsize=(12, 10))

# Extract data for heatmap
# Use mass vs charge with shells fixed
mass_vals = [10, 25, 50]
charge_vals = [100, 500, 1000]
alt_vals = [200, 250, 300]

# Create 3D array for mission times
# Dimensions: [mass, charge, altitude]
mission_times_grid = np.zeros((len(mass_vals), len(charge_vals)))

for config in all_configs:
    if config['n_shells'] == 100:  # Fix shells at 100
        if config['mass_kg'] in mass_vals and config['charge_uC'] in charge_vals and config['altitude_km'] == 200:
            i = mass_vals.index(config['mass_kg'])
            j = charge_vals.index(config['charge_uC'])
            mission_times_grid[i, j] = config['total_mission_days'] * 24  # Convert to hours

# Create heatmap
im = ax.imshow(mission_times_grid, cmap='RdYlGn_r', aspect='auto', interpolation='nearest')

# Set ticks and labels
ax.set_xticks(np.arange(len(charge_vals)))
ax.set_yticks(np.arange(len(mass_vals)))
ax.set_xticklabels([f'{c} μC' for c in charge_vals])
ax.set_yticklabels([f'{m} kg' for m in mass_vals])

# Rotate the tick labels and set their alignment
plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=11)
plt.setp(ax.get_yticklabels(), fontsize=11)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Mission Time (hours)', fontsize=12, fontweight='bold')

# Add text annotations
for i in range(len(mass_vals)):
    for j in range(len(charge_vals)):
        if mission_times_grid[i, j] > 0:
            text = ax.text(j, i, f'{mission_times_grid[i, j]:.1f}h',
                          ha="center", va="center", color="black", fontsize=11, fontweight='bold')

ax.set_xlabel('Charge per Shell', fontsize=13, fontweight='bold')
ax.set_ylabel('Spacecraft Mass', fontsize=13, fontweight='bold')
ax.set_title('Mission Time Heatmap\n(100 shells, 200 km altitude)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'configuration_heatmap.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'configuration_heatmap.png'}")
plt.close()

#=============================================================================
# Figure 6: Feasibility Evolution
#=============================================================================
fig, ax = plt.subplots(figsize=(14, 8))

# Show how mission time decreases as we optimize each parameter
stages = [
    'Baseline\n(1270kg, 6sh, 1μC, 600km)',
    'High Charge\n(1270kg, 6sh, 1000μC, 600km)',
    '+ More Shells\n(1270kg, 100sh, 1000μC, 600km)',
    '+ Lower Altitude\n(1270kg, 100sh, 1000μC, 200km)',
    '+ Lightweight\n(10kg, 100sh, 1000μC, 200km)\nOPTIMAL'
]

# Approximate mission times for each stage
stage_times_years = [
    113223,  # Baseline
    3.43,     # High charge (from test 1)
    2.06,     # + 100 shells (from test 2)
    2.06 * (474.55/527.06),  # + lower altitude (estimate)
    0.00147   # Optimal (0.54 days)
]

# Convert to days for better visualization
stage_times_days = [t * 365.25 for t in stage_times_years]

x = np.arange(len(stages))
colors_stages = ['red', 'orange', 'yellow', 'lightgreen', 'darkgreen']

bars = ax.bar(x, stage_times_days, color=colors_stages, alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('Mission Time (days)', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=10)
ax.set_title('Evolution of Mission Feasibility Through Parameter Optimization', fontsize=15, fontweight='bold')
ax.set_yscale('log')
ax.grid(True, alpha=0.3, axis='y')

# Add horizontal line at 60 days (2 months - target)
ax.axhline(y=60, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Target (2 months)')

# Add value labels
for bar, time_days, time_years in zip(bars, stage_times_days, stage_times_years):
    height = bar.get_height()
    if time_years >= 1:
        label_text = f'{time_years:.0f} years'
    elif time_days >= 1:
        label_text = f'{time_days:.1f} days'
    else:
        label_text = f'{time_days*24:.1f} hours'

    ax.text(bar.get_x() + bar.get_width()/2., height * 2,
           label_text,
           ha='center', va='bottom', fontsize=11, fontweight='bold', rotation=0)

# Highlight the breakthrough
ax.annotate('FEASIBLE!', xy=(4, stage_times_days[4]), xytext=(3.5, stage_times_days[4]*100),
           arrowprops=dict(arrowstyle='->', color='darkgreen', lw=4),
           fontsize=16, color='darkgreen', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', edgecolor='darkgreen', linewidth=3))

ax.legend(fontsize=12)

plt.tight_layout()
plt.savefig(fig_dir / 'feasibility_evolution.png', dpi=300, bbox_inches='tight')
print(f"Saved: {fig_dir / 'feasibility_evolution.png'}")
plt.close()

print("\n" + "="*80)
print("All optimization figures generated successfully!")
print(f"Location: {fig_dir}")
print("="*80)
