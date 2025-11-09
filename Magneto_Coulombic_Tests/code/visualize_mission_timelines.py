#!/usr/bin/env python3
"""
Visualize Mission Timelines
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Load timeline data
with open('../results/mission_timelines.json', 'r') as f:
    timelines = json.load(f)

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')

# Create comprehensive timeline figure
fig = plt.figure(figsize=(18, 14))

# ============================================================================
# FIGURE 1: Total Mission Time Breakdown
# ============================================================================
ax1 = plt.subplot(3, 2, 1)

configs = list(timelines.keys())
rendezvous_times = [timelines[c]['total_rendezvous']['hours'] for c in configs]
burn_times = [timelines[c]['phase6_deorbit']['burn_time'] / 3600 for c in configs]
decay_times = [timelines[c]['phase6_deorbit']['decay_time'] / 3600 for c in configs]

x = np.arange(len(configs))
width = 0.6

# Stacked bar chart
p1 = ax1.bar(x, rendezvous_times, width, label='Rendezvous', color='#2E86AB', alpha=0.8)
p2 = ax1.bar(x, burn_times, width, bottom=rendezvous_times, label='Deorbit Burn', color='#A23B72', alpha=0.8)
p3 = ax1.bar(x, burn_times, width,
             bottom=[r+b for r,b in zip(rendezvous_times, burn_times)],
             label='Atmospheric Decay', color='#F18F01', alpha=0.8)

# Add decay time bars (48 hours)
for i in range(len(configs)):
    ax1.bar(x[i], 48, width,
           bottom=rendezvous_times[i]+burn_times[i],
           color='#F18F01', alpha=0.8)

ax1.set_ylabel('Time (hours)', fontsize=12, fontweight='bold')
ax1.set_title('Mission Time Breakdown', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(configs, rotation=45, ha='right')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# Add total time labels
for i, config in enumerate(configs):
    total = timelines[config]['total_mission']['hours']
    ax1.text(i, total + 2, f'{total:.1f}h', ha='center', fontsize=9, fontweight='bold')

# ============================================================================
# FIGURE 2: Rendezvous Phase Breakdown
# ============================================================================
ax2 = plt.subplot(3, 2, 2)

# Use one config as example (10kg_5C - fastest)
config = '10kg_5C'
tl = timelines[config]

phases = ['Transfer', 'Approach', 'Proximity', 'Detumble', 'Capture']
times_min = [
    tl['phase1_transfer']['total_time'] / 60,
    tl['phase2_approach']['time'] / 60,
    tl['phase3_proximity']['time'] / 60,
    tl['phase4_detumble']['time'] / 60,
    tl['phase5_capture']['time'] / 60
]

colors_phases = ['#06A77D', '#3CAEA3', '#20639B', '#173F5F', '#ED553B']

wedges, texts, autotexts = ax2.pie(times_min, labels=phases, autopct='%1.1f%%',
                                     colors=colors_phases, startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

ax2.set_title(f'Rendezvous Phase Breakdown ({config})\nTotal: {tl["total_rendezvous"]["hours"]:.2f} hours',
              fontsize=14, fontweight='bold')

# ============================================================================
# FIGURE 3: Rendezvous Time Comparison
# ============================================================================
ax3 = plt.subplot(3, 2, 3)

rendezvous_hours = [timelines[c]['total_rendezvous']['hours'] for c in configs]
colors = ['#1f77b4']*3 + ['#ff7f0e']*3

bars = ax3.barh(configs, rendezvous_hours, color=colors, alpha=0.7, edgecolor='black')
ax3.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax3.set_title('Rendezvous Time Comparison', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# Add time labels
for i, (bar, time) in enumerate(zip(bars, rendezvous_hours)):
    ax3.text(time + 0.02, bar.get_y() + bar.get_height()/2,
             f'{time:.2f}h', va='center', fontsize=10, fontweight='bold')

# ============================================================================
# FIGURE 4: Deorbit Burn Time Comparison
# ============================================================================
ax4 = plt.subplot(3, 2, 4)

deorbit_burn_hours = [timelines[c]['phase6_deorbit']['burn_time'] / 3600 for c in configs]

bars = ax4.barh(configs, deorbit_burn_hours, color=colors, alpha=0.7, edgecolor='black')
ax4.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax4.set_title('Deorbit Burn Time Comparison', fontsize=14, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

# Add time labels
for i, (bar, time) in enumerate(zip(bars, deorbit_burn_hours)):
    ax4.text(time + 0.05, bar.get_y() + bar.get_height()/2,
             f'{time:.2f}h', va='center', fontsize=10, fontweight='bold')

# ============================================================================
# FIGURE 5: Total Mission Time (Days)
# ============================================================================
ax5 = plt.subplot(3, 2, 5)

total_days = [timelines[c]['total_mission']['days'] for c in configs]

bars = ax5.bar(range(len(configs)), total_days, color=colors, alpha=0.7, edgecolor='black', width=0.6)
ax5.set_ylabel('Time (days)', fontsize=12, fontweight='bold')
ax5.set_title('Total Mission Duration', fontsize=14, fontweight='bold')
ax5.set_xticks(range(len(configs)))
ax5.set_xticklabels(configs, rotation=45, ha='right')
ax5.grid(True, alpha=0.3, axis='y')

# Add labels
for i, (bar, days) in enumerate(zip(bars, total_days)):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{days:.2f}d', ha='center', fontsize=10, fontweight='bold')

# Add reference line at 2 days
ax5.axhline(y=2.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='2-day baseline')
ax5.legend(fontsize=10)

# ============================================================================
# FIGURE 6: Timeline Gantt Chart (Example Mission)
# ============================================================================
ax6 = plt.subplot(3, 2, 6)

# Use 10kg_5C as example (fastest config)
config = '10kg_5C'
tl = timelines[config]

# Create Gantt chart
phases_gantt = ['Phase 1:\nTransfer', 'Phase 2:\nApproach', 'Phase 3:\nProximity',
                'Phase 4:\nDetumble', 'Phase 5:\nCapture', 'Phase 6a:\nDeorbit Burn',
                'Phase 6b:\nDecay']

start_times = [0]
durations = [
    tl['phase1_transfer']['total_time'] / 3600,
    tl['phase2_approach']['time'] / 3600,
    tl['phase3_proximity']['time'] / 3600,
    tl['phase4_detumble']['time'] / 3600,
    tl['phase5_capture']['time'] / 3600,
    tl['phase6_deorbit']['burn_time'] / 3600,
    tl['phase6_deorbit']['decay_time'] / 3600
]

# Calculate cumulative start times
for i in range(len(durations) - 1):
    start_times.append(start_times[-1] + durations[i])

colors_gantt = ['#06A77D', '#3CAEA3', '#20639B', '#173F5F', '#ED553B', '#A23B72', '#F18F01']

for i, (phase, start, duration, color) in enumerate(zip(phases_gantt, start_times, durations, colors_gantt)):
    ax6.barh(i, duration, left=start, height=0.8, color=color, alpha=0.8, edgecolor='black')

    # Add duration labels
    if duration > 0.5:  # Only label if bar is wide enough
        ax6.text(start + duration/2, i, f'{duration:.2f}h',
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')

ax6.set_yticks(range(len(phases_gantt)))
ax6.set_yticklabels(phases_gantt, fontsize=9)
ax6.set_xlabel('Cumulative Time (hours)', fontsize=12, fontweight='bold')
ax6.set_title(f'Mission Timeline Gantt Chart ({config})\nTotal: {tl["total_mission"]["hours"]:.1f} hours',
              fontsize=14, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='x')

# Mark rendezvous completion
rendezvous_end = tl['total_rendezvous']['hours']
ax6.axvline(x=rendezvous_end, color='green', linestyle='--', linewidth=2, alpha=0.7,
            label=f'Rendezvous Complete ({rendezvous_end:.2f}h)')
ax6.legend(fontsize=9, loc='lower right')

plt.tight_layout()
plt.savefig('../figures/mission_timelines.png', dpi=300, bbox_inches='tight')
print(f"Saved: ../figures/mission_timelines.png")

# ============================================================================
# Create comparison table figure
# ============================================================================
fig2, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')

# Create detailed table
table_data = [
    ['Config', 'Transfer', 'Approach', 'Proximity', 'Detumble', 'Capture',
     'Total\nRendezvous', 'Deorbit\nBurn', 'Total\nMission'],
    ['', '(min)', '(min)', '(min)', '(min)', '(sec)', '(hours)', '(min)', '(days)']
]

for config in configs:
    tl = timelines[config]
    row = [
        config,
        f"{tl['phase1_transfer']['total_time']/60:.1f}",
        f"{tl['phase2_approach']['time']/60:.1f}",
        f"{tl['phase3_proximity']['time']/60:.2f}",
        f"{tl['phase4_detumble']['time']/60:.1f}",
        f"{tl['phase5_capture']['time']:.1f}",
        f"{tl['total_rendezvous']['hours']:.2f}",
        f"{tl['phase6_deorbit']['burn_time']/60:.1f}",
        f"{tl['total_mission']['days']:.2f}"
    ]
    table_data.append(row)

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.10, 0.10, 0.10, 0.10, 0.10, 0.08, 0.12, 0.10, 0.10])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header rows
for j in range(9):
    table[(0, j)].set_facecolor('#4CAF50')
    table[(0, j)].set_text_props(weight='bold', color='white')
    table[(1, j)].set_facecolor('#81C784')
    table[(1, j)].set_text_props(weight='bold', color='white', fontsize=9)

# Style data rows
for i in range(2, len(table_data)):
    color = '#E3F2FD' if i <= 4 else '#FFF3E0'  # Blue for 10kg, Orange for 25kg
    for j in range(9):
        table[(i, j)].set_facecolor(color)

    # Highlight total mission column
    table[(i, 8)].set_facecolor('#FFD54F')
    table[(i, 8)].set_text_props(weight='bold')

ax.set_title('Detailed Mission Timeline Comparison\nAll Times Shown',
             fontsize=16, fontweight='bold', pad=20)

plt.savefig('../figures/mission_timeline_table.png', dpi=300, bbox_inches='tight')
print(f"Saved: ../figures/mission_timeline_table.png")

print("\nTimeline visualizations complete!")
