#!/usr/bin/env python3
"""
Visualization Script for High-Charge Variable Separation Results
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Set directories
RESULTS_DIR = '../results'
FIGURES_DIR = '../figures'

# Load results
with open(os.path.join(RESULTS_DIR, 'high_charge_variable_separation_results.json'), 'r') as f:
    results = json.load(f)

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
colors_10kg = '#1f77b4'  # Blue
colors_25kg = '#ff7f0e'  # Orange

# Create comprehensive figure set
fig = plt.figure(figsize=(20, 24))

# ============================================================================
# FIGURE 1: Force vs Charge Level
# ============================================================================
ax1 = plt.subplot(5, 2, 1)
charges = results['test_1']['charge_levels']
forces_10kg = results['test_1']['chaser_10kg']['forces']
forces_25kg = results['test_1']['chaser_25kg']['forces']

ax1.plot(charges, forces_10kg, 'o-', linewidth=2, markersize=8,
         color=colors_10kg, label='10 kg chaser')
ax1.plot(charges, forces_25kg, 's-', linewidth=2, markersize=8,
         color=colors_25kg, label='25 kg chaser')
ax1.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Force (N)', fontsize=12, fontweight='bold')
ax1.set_title('Force vs Charge Level (600 km altitude)', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# ============================================================================
# FIGURE 2: Acceleration vs Charge Level
# ============================================================================
ax2 = plt.subplot(5, 2, 2)
accel_10kg = results['test_1']['chaser_10kg']['accelerations']
accel_25kg = results['test_1']['chaser_25kg']['accelerations']

ax2.plot(charges, accel_10kg, 'o-', linewidth=2, markersize=8,
         color=colors_10kg, label='10 kg chaser')
ax2.plot(charges, accel_25kg, 's-', linewidth=2, markersize=8,
         color=colors_25kg, label='25 kg chaser')
ax2.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Acceleration (m/s²)', fontsize=12, fontweight='bold')
ax2.set_title('Acceleration vs Charge Level', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# ============================================================================
# FIGURE 3: Acceleration at Different Altitudes (10kg chaser)
# ============================================================================
ax3 = plt.subplot(5, 2, 3)
charges_alt = results['test_3']['charge_levels']

for alt in results['test_3']['altitudes']:
    accel = results['test_3']['data'][f'{alt}km']['10kg']['accelerations']
    ax3.plot(charges_alt, accel, 'o-', linewidth=2, markersize=8, label=f'{alt} km')

ax3.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Acceleration (m/s²)', fontsize=12, fontweight='bold')
ax3.set_title('10kg Chaser: Acceleration at Different Altitudes', fontsize=14, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# ============================================================================
# FIGURE 4: Acceleration at Different Altitudes (25kg chaser)
# ============================================================================
ax4 = plt.subplot(5, 2, 4)

for alt in results['test_3']['altitudes']:
    accel = results['test_3']['data'][f'{alt}km']['25kg']['accelerations']
    ax4.plot(charges_alt, accel, 's-', linewidth=2, markersize=8, label=f'{alt} km')

ax4.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Acceleration (m/s²)', fontsize=12, fontweight='bold')
ax4.set_title('25kg Chaser: Acceleration at Different Altitudes', fontsize=14, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# ============================================================================
# FIGURE 5: Delta-v Accumulation (10kg, 1C)
# ============================================================================
ax5 = plt.subplot(5, 2, 5)
duration_days = [d/86400 for d in results['test_4']['duration_seconds']]

for charge in [1, 3, 5]:
    key = f'10kg_{charge}C'
    delta_v = results['test_4']['data'][key]['delta_v_km_s']
    ax5.plot(duration_days, delta_v, 'o-', linewidth=2, markersize=8, label=f'{charge} C/shell')

ax5.set_xlabel('Time (days)', fontsize=12, fontweight='bold')
ax5.set_ylabel('Delta-v (km/s)', fontsize=12, fontweight='bold')
ax5.set_title('10kg Chaser: Delta-v Accumulation', fontsize=14, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)
ax5.set_xlim(0, 14)

# ============================================================================
# FIGURE 6: Delta-v Accumulation (25kg)
# ============================================================================
ax6 = plt.subplot(5, 2, 6)

for charge in [1, 3, 5]:
    key = f'25kg_{charge}C'
    delta_v = results['test_4']['data'][key]['delta_v_km_s']
    ax6.plot(duration_days, delta_v, 's-', linewidth=2, markersize=8, label=f'{charge} C/shell')

ax6.set_xlabel('Time (days)', fontsize=12, fontweight='bold')
ax6.set_ylabel('Delta-v (km/s)', fontsize=12, fontweight='bold')
ax6.set_title('25kg Chaser: Delta-v Accumulation', fontsize=14, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 14)

# ============================================================================
# FIGURE 7: Force Matrix Heatmap
# ============================================================================
ax7 = plt.subplot(5, 2, 7)
force_matrix = np.array(results['test_5']['force_matrix'])
separations = results['test_5']['separations']
charges_opt = results['test_5']['charges']

im = ax7.imshow(force_matrix, aspect='auto', cmap='hot', origin='lower')
ax7.set_xticks(range(len(charges_opt)))
ax7.set_xticklabels([f'{c:.0f}' for c in charges_opt])
ax7.set_yticks(range(len(separations)))
ax7.set_yticklabels([f'{s:.1f}' for s in separations])
ax7.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax7.set_ylabel('Shell Separation (m)', fontsize=12, fontweight='bold')
ax7.set_title('Force Matrix (N)', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax7, label='Force (N)')

# Add text annotations
for i in range(len(separations)):
    for j in range(len(charges_opt)):
        text = ax7.text(j, i, f'{force_matrix[i, j]:.2f}',
                       ha="center", va="center", color="white", fontsize=8)

# ============================================================================
# FIGURE 8: Energy Requirements
# ============================================================================
ax8 = plt.subplot(5, 2, 8)
charges_energy = results['test_6']['charge_levels']
total_energy = np.array(results['test_6']['total_energy_6_shells']) / 1000  # kJ

ax8.bar(charges_energy, total_energy, color='steelblue', alpha=0.7, edgecolor='black')
ax8.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax8.set_ylabel('Total Energy (kJ)', fontsize=12, fontweight='bold')
ax8.set_title('Energy Requirements (6 shells)', fontsize=14, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')

# Add values on top of bars
for i, (c, e) in enumerate(zip(charges_energy, total_energy)):
    ax8.text(c, e, f'{e:.1f} kJ', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ============================================================================
# FIGURE 9: Comparison at 1 Week Operation
# ============================================================================
ax9 = plt.subplot(5, 2, 9)
configurations = []
delta_v_week = []

for mass in [10, 25]:
    for charge in [1, 3, 5]:
        key = f'{mass}kg_{charge}C'
        dv = results['test_4']['data'][key]['delta_v_km_s'][4]  # 1 week index
        configurations.append(f'{mass}kg\n{charge}C')
        delta_v_week.append(dv)

colors = [colors_10kg]*3 + [colors_25kg]*3
bars = ax9.bar(range(len(configurations)), delta_v_week, color=colors, alpha=0.7, edgecolor='black')
ax9.set_xticks(range(len(configurations)))
ax9.set_xticklabels(configurations, fontsize=9)
ax9.set_ylabel('Delta-v (km/s)', fontsize=12, fontweight='bold')
ax9.set_title('Delta-v After 1 Week of Operation', fontsize=14, fontweight='bold')
ax9.grid(True, alpha=0.3, axis='y')

# Add values on bars
for i, (bar, dv) in enumerate(zip(bars, delta_v_week)):
    ax9.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'{dv:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# ============================================================================
# FIGURE 10: Power Requirements
# ============================================================================
ax10 = plt.subplot(5, 2, 10)
power = results['test_6']['power_for_1hr_charge']

ax10.bar(charges_energy, power, color='darkgreen', alpha=0.7, edgecolor='black')
ax10.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax10.set_ylabel('Power (W)', fontsize=12, fontweight='bold')
ax10.set_title('Power for 1-Hour Charging', fontsize=14, fontweight='bold')
ax10.grid(True, alpha=0.3, axis='y')

# Add values on bars
for c, p in zip(charges_energy, power):
    ax10.text(c, p, f'{p:.1f} W', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'high_charge_comprehensive_analysis.png'),
            dpi=300, bbox_inches='tight')
print(f"Saved: {os.path.join(FIGURES_DIR, 'high_charge_comprehensive_analysis.png')}")

# ============================================================================
# Create summary statistics figure
# ============================================================================
fig2, axes = plt.subplots(2, 2, figsize=(16, 12))

# Performance comparison table
ax_table = axes[0, 0]
ax_table.axis('tight')
ax_table.axis('off')

table_data = [
    ['Configuration', 'Force (N)', 'Accel (m/s²)', 'Δv/week (km/s)'],
    ['', '', '', ''],
    ['10 kg, 1 C', f"{results['test_1']['chaser_10kg']['forces'][0]:.3f}",
     f"{results['test_1']['chaser_10kg']['accelerations'][0]:.4f}",
     f"{results['test_4']['data']['10kg_1C']['delta_v_km_s'][4]:.1f}"],
    ['10 kg, 3 C', f"{results['test_1']['chaser_10kg']['forces'][2]:.3f}",
     f"{results['test_1']['chaser_10kg']['accelerations'][2]:.4f}",
     f"{results['test_4']['data']['10kg_3C']['delta_v_km_s'][4]:.1f}"],
    ['10 kg, 5 C', f"{results['test_1']['chaser_10kg']['forces'][4]:.3f}",
     f"{results['test_1']['chaser_10kg']['accelerations'][4]:.4f}",
     f"{results['test_4']['data']['10kg_5C']['delta_v_km_s'][4]:.1f}"],
    ['', '', '', ''],
    ['25 kg, 1 C', f"{results['test_1']['chaser_25kg']['forces'][0]:.3f}",
     f"{results['test_1']['chaser_25kg']['accelerations'][0]:.4f}",
     f"{results['test_4']['data']['25kg_1C']['delta_v_km_s'][4]:.1f}"],
    ['25 kg, 3 C', f"{results['test_1']['chaser_25kg']['forces'][2]:.3f}",
     f"{results['test_1']['chaser_25kg']['accelerations'][2]:.4f}",
     f"{results['test_4']['data']['25kg_3C']['delta_v_km_s'][4]:.1f}"],
    ['25 kg, 5 C', f"{results['test_1']['chaser_25kg']['forces'][4]:.3f}",
     f"{results['test_1']['chaser_25kg']['accelerations'][4]:.4f}",
     f"{results['test_4']['data']['25kg_5C']['delta_v_km_s'][4]:.1f}"],
]

table = ax_table.table(cellText=table_data, cellLoc='center', loc='center',
                       colWidths=[0.3, 0.2, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Style header row
for i in range(4):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style data rows
for i in range(2, 9):
    if i in [1, 5]:  # Separator rows
        for j in range(4):
            table[(i, j)].set_facecolor('#f0f0f0')
    elif i < 5:  # 10kg rows
        for j in range(4):
            table[(i, j)].set_facecolor('#e3f2fd')
    else:  # 25kg rows
        for j in range(4):
            table[(i, j)].set_facecolor('#fff3e0')

ax_table.set_title('Performance Summary (600 km altitude)', fontsize=14, fontweight='bold', pad=20)

# Acceleration ratio plot
ax_ratio = axes[0, 1]
mass_ratio = 25.0 / 10.0
accel_10kg_plot = results['test_1']['chaser_10kg']['accelerations']
accel_25kg_plot = results['test_1']['chaser_25kg']['accelerations']
accel_ratio = [a10/a25 for a10, a25 in zip(accel_10kg_plot, accel_25kg_plot)]

ax_ratio.plot(charges, accel_ratio, 'o-', linewidth=3, markersize=10, color='purple')
ax_ratio.axhline(y=mass_ratio, color='red', linestyle='--', linewidth=2, label=f'Mass ratio ({mass_ratio:.1f})')
ax_ratio.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax_ratio.set_ylabel('Acceleration Ratio (10kg/25kg)', fontsize=12, fontweight='bold')
ax_ratio.set_title('Acceleration Ratio Verification', fontsize=14, fontweight='bold')
ax_ratio.legend(fontsize=10)
ax_ratio.grid(True, alpha=0.3)

# Mission timeline comparison
ax_timeline = axes[1, 0]
time_labels = results['test_4']['durations']
time_indices = range(len(time_labels))

# Plot for best configurations
delta_v_10kg_5C = results['test_4']['data']['10kg_5C']['delta_v_km_s']
delta_v_25kg_5C = results['test_4']['data']['25kg_5C']['delta_v_km_s']

width = 0.35
ax_timeline.bar([x - width/2 for x in time_indices], delta_v_10kg_5C, width,
                label='10 kg, 5C', color=colors_10kg, alpha=0.7)
ax_timeline.bar([x + width/2 for x in time_indices], delta_v_25kg_5C, width,
                label='25 kg, 5C', color=colors_25kg, alpha=0.7)

ax_timeline.set_xlabel('Mission Duration', fontsize=12, fontweight='bold')
ax_timeline.set_ylabel('Accumulated Delta-v (km/s)', fontsize=12, fontweight='bold')
ax_timeline.set_title('Maximum Performance Configurations (5 C/shell)', fontsize=14, fontweight='bold')
ax_timeline.set_xticks(time_indices)
ax_timeline.set_xticklabels(time_labels, rotation=45, ha='right')
ax_timeline.legend(fontsize=10)
ax_timeline.grid(True, alpha=0.3, axis='y')

# Energy efficiency plot
ax_efficiency = axes[1, 1]
charges_eff = charges_energy
delta_v_per_kJ_10kg = []
delta_v_per_kJ_25kg = []

for i, charge in enumerate([1, 3, 5]):
    idx = [0, 2, 4][i]  # Indices for 1C, 3C, 5C
    energy_kJ = results['test_6']['total_energy_6_shells'][idx] / 1000.0

    # Delta-v after 1 day per kJ of stored energy
    dv_10kg_day = results['test_4']['data'][f'10kg_{int(charge)}C']['delta_v_km_s'][2]  # 1 day
    dv_25kg_day = results['test_4']['data'][f'25kg_{int(charge)}C']['delta_v_km_s'][2]

    delta_v_per_kJ_10kg.append(dv_10kg_day / energy_kJ)
    delta_v_per_kJ_25kg.append(dv_25kg_day / energy_kJ)

x_pos = np.array([1, 3, 5])
width = 0.6
ax_efficiency.bar(x_pos - width/2, delta_v_per_kJ_10kg, width,
                  label='10 kg', color=colors_10kg, alpha=0.7)
ax_efficiency.bar(x_pos + width/2, delta_v_per_kJ_25kg, width,
                  label='25 kg', color=colors_25kg, alpha=0.7)

ax_efficiency.set_xlabel('Charge per Shell (C)', fontsize=12, fontweight='bold')
ax_efficiency.set_ylabel('Δv per kJ (km/s / kJ)', fontsize=12, fontweight='bold')
ax_efficiency.set_title('Energy Efficiency (1-day mission)', fontsize=14, fontweight='bold')
ax_efficiency.set_xticks([1, 3, 5])
ax_efficiency.legend(fontsize=10)
ax_efficiency.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'high_charge_summary_statistics.png'),
            dpi=300, bbox_inches='tight')
print(f"Saved: {os.path.join(FIGURES_DIR, 'high_charge_summary_statistics.png')}")

print("\nVisualization complete!")
print(f"Figures saved to: {FIGURES_DIR}")
