#!/usr/bin/env python3
"""
Generate Comprehensive Figures for Magneto-Coulombic Test Results
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Set matplotlib parameters for better plots
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.grid'] = True

RESULTS_DIR = '../results'
FIGURES_DIR = '../figures'

def load_results():
    """Load test results from JSON"""
    filepath = os.path.join(RESULTS_DIR, 'test_results.json')
    with open(filepath, 'r') as f:
        results = json.load(f)
    return results

def plot_test1_altitude_effects(results):
    """Plot Test 1: Orbital altitude effects"""
    print("Generating Figure 1: Orbital Altitude Effects...")

    data = results['test_1']
    altitudes = data['altitudes']

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Test Suite 1: Orbital Altitude Effects on Lorentz Force Performance',
                 fontsize=14, fontweight='bold')

    # Plot 1: Magnetic Field vs Altitude
    ax = axes[0, 0]
    ax.plot(altitudes, data['b_field_magnitudes'], 'bo-', markersize=8, markerfacecolor='b')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Magnetic Field (μT)')
    ax.set_title('Earth\'s Magnetic Field Strength')
    ax.grid(True, alpha=0.3)

    # Plot 2: Orbital Velocity vs Altitude
    ax = axes[0, 1]
    ax.plot(altitudes, data['velocities'], 'go-', markersize=8, markerfacecolor='g')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Orbital Velocity (m/s)')
    ax.set_title('Circular Orbital Velocity')
    ax.grid(True, alpha=0.3)

    # Plot 3: Lorentz Force vs Altitude
    ax = axes[0, 2]
    ax.plot(altitudes, data['forces'], 'ro-', markersize=8, markerfacecolor='r')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Net Force (μN)')
    ax.set_title('Lorentz Force Magnitude (6 shells @ 1μC)')
    ax.grid(True, alpha=0.3)

    # Plot 4: Acceleration vs Altitude
    ax = axes[1, 0]
    ax.plot(altitudes, data['accelerations'], 'mo-', markersize=8, markerfacecolor='m')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Acceleration (nm/s²)')
    ax.set_title('Spacecraft Acceleration (m=1270kg)')
    ax.grid(True, alpha=0.3)

    # Plot 5: Torque vs Altitude
    ax = axes[1, 1]
    ax.plot(altitudes, data['torques'], 'co-', markersize=8, markerfacecolor='c')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Torque (μN·m)')
    ax.set_title('Attitude Control Torque (±1μC pair)')
    ax.grid(True, alpha=0.3)

    # Plot 6: Summary comparison
    ax = axes[1, 2]
    ax2 = ax.twinx()
    l1 = ax.plot(altitudes, data['forces'], 'r^-', markersize=8, label='Force (μN)')
    l2 = ax2.plot(altitudes, data['b_field_magnitudes'], 'bs-', markersize=8, label='B-field (μT)')
    ax.set_xlabel('Altitude (km)')
    ax.set_ylabel('Force (μN)', color='r')
    ax2.set_ylabel('Magnetic Field (μT)', color='b')
    ax.set_title('Force vs Magnetic Field')
    ax.tick_params(axis='y', labelcolor='r')
    ax2.tick_params(axis='y', labelcolor='b')
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'test1_altitude_effects.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: test1_altitude_effects.png")
    plt.close()

def plot_test2_charge_scaling(results):
    """Plot Test 2: Charge level scaling"""
    print("Generating Figure 2: Charge Level Scaling...")

    data = results['test_2']
    charges = data['charge_levels']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Test Suite 2: Charge Level Effects on Lorentz Force Performance',
                 fontsize=14, fontweight='bold')

    # Plot 1: Force vs Charge (linear scale)
    ax = axes[0]
    ax.plot(charges, data['forces'], 'bo-', markersize=8, markerfacecolor='b', linewidth=2)
    ax.set_xlabel('Shell Charge (μC)')
    ax.set_ylabel('Net Force (μN)')
    ax.set_title('Lorentz Force vs Charge (Linear)')
    ax.grid(True, alpha=0.3)

    # Add linear fit to verify F ∝ q
    coeffs = np.polyfit(charges, data['forces'], 1)
    fit_line = np.poly1d(coeffs)
    ax.plot(charges, fit_line(charges), 'r--', alpha=0.7, label=f'Linear fit: F = {coeffs[0]:.2f}q + {coeffs[1]:.2f}')
    ax.legend()

    # Plot 2: Torque vs Charge
    ax = axes[1]
    ax.plot(charges, data['torques'], 'go-', markersize=8, markerfacecolor='g', linewidth=2)
    ax.set_xlabel('Shell Charge (μC)')
    ax.set_ylabel('Torque (μN·m)')
    ax.set_title('Attitude Control Torque vs Charge')
    ax.grid(True, alpha=0.3)

    # Plot 3: Acceleration vs Charge
    ax = axes[2]
    ax.plot(charges, data['accelerations'], 'ro-', markersize=8, markerfacecolor='r', linewidth=2)
    ax.set_xlabel('Shell Charge (μC)')
    ax.set_ylabel('Acceleration (nm/s²)')
    ax.set_title('Spacecraft Acceleration vs Charge')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'test2_charge_scaling.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: test2_charge_scaling.png")
    plt.close()

def plot_test3_orbital_variation(results):
    """Plot Test 3: Force variation along orbit"""
    print("Generating Figure 3: Orbital Position Variation...")

    data = results['test_3']
    theta = np.array(data['theta_deg'])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Test Suite 3: Lorentz Force Variation Along Orbit',
                 fontsize=14, fontweight='bold')

    # Plot 1: Force magnitude vs orbital position (Cartesian)
    ax = axes[0]
    ax.plot(theta, data['forces'], 'b-', linewidth=2)
    ax.fill_between(theta, data['forces'], alpha=0.3)
    ax.set_xlabel('Orbital Position (degrees)')
    ax.set_ylabel('Force Magnitude (μN)')
    ax.set_title('Lorentz Force Around Complete Orbit')
    ax.set_xlim(0, 360)
    ax.set_xticks([0, 90, 180, 270, 360])
    ax.grid(True, alpha=0.3)

    # Add statistics
    avg_force = np.mean(data['forces'])
    std_force = np.std(data['forces'])
    ax.axhline(avg_force, color='r', linestyle='--', alpha=0.7, label=f'Mean: {avg_force:.2f} μN')
    ax.axhline(avg_force + std_force, color='g', linestyle=':', alpha=0.5)
    ax.axhline(avg_force - std_force, color='g', linestyle=':', alpha=0.5, label=f'±1σ: {std_force:.2f} μN')
    ax.legend()

    # Plot 2: Polar plot of force magnitude
    ax = plt.subplot(122, projection='polar')
    theta_rad = theta * np.pi / 180
    ax.plot(theta_rad, data['forces'], 'b-', linewidth=2)
    ax.fill(theta_rad, data['forces'], alpha=0.3)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title('Polar View: Force Around Orbit', pad=20)
    ax.set_ylabel('Force (μN)', labelpad=30)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'test3_orbital_variation.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: test3_orbital_variation.png")
    plt.close()

def plot_test4_delta_v_accumulation(results):
    """Plot Test 4: Delta-v accumulation over time"""
    print("Generating Figure 4: Delta-V Accumulation...")

    data = results['test_4']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Test Suite 4: Velocity Change (Δv) Accumulation Over Time',
                 fontsize=14, fontweight='bold')

    # Plot 1: Delta-v vs time (hours)
    ax = axes[0]
    ax.plot(data['durations_hours'], data['delta_v_mm_s'], 'bo-', markersize=10, markerfacecolor='b', linewidth=2)
    ax.set_xlabel('Mission Duration (hours)')
    ax.set_ylabel('Accumulated Δv (mm/s)')
    ax.set_title('Δv Accumulation (Short Duration)')
    ax.grid(True, alpha=0.3)

    # Add annotations
    for i, (hours, dv) in enumerate(zip(data['durations_hours'], data['delta_v_mm_s'])):
        ax.annotate(f'{dv:.1f} mm/s', xy=(hours, dv), xytext=(5, 5),
                   textcoords='offset points', fontsize=9)

    # Plot 2: Delta-v vs time (days, log scale)
    ax = axes[1]
    days = data['durations_days']
    dv_m_s = data['delta_v_m_s']
    ax.semilogy(days, dv_m_s, 'ro-', markersize=10, markerfacecolor='r', linewidth=2)
    ax.set_xlabel('Mission Duration (days)')
    ax.set_ylabel('Accumulated Δv (m/s) [log scale]')
    ax.set_title('Δv Accumulation (Extended Duration)')
    ax.grid(True, alpha=0.3, which='both')

    # Add annotations
    for i, (d, dv) in enumerate(zip(days, dv_m_s)):
        label = f'{dv:.3f} m/s' if dv < 1 else f'{dv:.2f} m/s'
        ax.annotate(label, xy=(d, dv), xytext=(5, 5),
                   textcoords='offset points', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'test4_delta_v_accumulation.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: test4_delta_v_accumulation.png")
    plt.close()

def plot_test5_energy_consumption(results):
    """Plot Test 5: Energy consumption analysis"""
    print("Generating Figure 5: Energy Consumption...")

    data = results['test_5']
    charges = data['charge_levels_uC']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Test Suite 5: Energy Requirements for Charging Coulomb Shells',
                 fontsize=14, fontweight='bold')

    # Plot 1: Energy vs charge (quadratic relationship)
    ax = axes[0]
    ax.plot(charges, data['total_energy_mJ'], 'go-', markersize=10, markerfacecolor='g', linewidth=2)
    ax.set_xlabel('Shell Charge (μC)')
    ax.set_ylabel('Total Energy (mJ)')
    ax.set_title('Charging Energy (6 shells)')
    ax.grid(True, alpha=0.3)

    # Add quadratic fit to verify E ∝ q²
    coeffs = np.polyfit(charges, data['total_energy_mJ'], 2)
    fit_line = np.poly1d(coeffs)
    charge_fit = np.linspace(min(charges), max(charges), 100)
    ax.plot(charge_fit, fit_line(charge_fit), 'r--', alpha=0.7, label='Quadratic fit: E ∝ q²')
    ax.legend()

    # Plot 2: Energy budget comparison
    ax = axes[1]
    available_energy_mJ = 500e6  # 500 MJ in mJ
    max_used_mJ = max(data['total_energy_mJ'])

    categories = ['Available\nEnergy', f'Max Used\n({max(charges):.1f} μC)', 'Margin']
    values = [available_energy_mJ, max_used_mJ, available_energy_mJ - max_used_mJ]
    colors = ['blue', 'red', 'green']

    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Energy (mJ) [log scale]')
    ax.set_yscale('log')
    ax.set_title('Energy Budget Analysis')
    ax.grid(True, alpha=0.3, which='both', axis='y')

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        if val > 1e6:
            label = f'{val/1e6:.0f} MJ'
        elif val > 1e3:
            label = f'{val/1e3:.1f} kJ'
        else:
            label = f'{val:.2f} mJ'
        ax.text(bar.get_x() + bar.get_width()/2., height,
               label, ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'test5_energy_consumption.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: test5_energy_consumption.png")
    plt.close()

def plot_summary_comparison(results):
    """Create summary comparison figure"""
    print("Generating Figure 6: Summary Comparison...")

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    fig.suptitle('Magneto-Coulombic Actuation System: Comprehensive Performance Summary',
                 fontsize=16, fontweight='bold')

    # Panel 1: Altitude effects
    ax1 = fig.add_subplot(gs[0, 0])
    data1 = results['test_1']
    ax1.plot(data1['altitudes'], data1['forces'], 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('Altitude (km)', fontsize=9)
    ax1.set_ylabel('Force (μN)', fontsize=9)
    ax1.set_title('Altitude Effects', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Panel 2: Charge scaling
    ax2 = fig.add_subplot(gs[0, 1])
    data2 = results['test_2']
    ax2.plot(data2['charge_levels'], data2['forces'], 'r-o', linewidth=2, markersize=6)
    ax2.set_xlabel('Charge (μC)', fontsize=9)
    ax2.set_ylabel('Force (μN)', fontsize=9)
    ax2.set_title('Charge Scaling (Linear)', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Panel 3: Orbital variation
    ax3 = fig.add_subplot(gs[0, 2])
    data3 = results['test_3']
    ax3.plot(data3['theta_deg'], data3['forces'], 'g-', linewidth=1.5)
    ax3.set_xlabel('Orbital Position (°)', fontsize=9)
    ax3.set_ylabel('Force (μN)', fontsize=9)
    ax3.set_title('Force Along Orbit', fontsize=10, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Panel 4: Delta-v accumulation
    ax4 = fig.add_subplot(gs[1, 0])
    data4 = results['test_4']
    ax4.plot(data4['durations_days'], data4['delta_v_m_s'], 'm-o', linewidth=2, markersize=6)
    ax4.set_xlabel('Time (days)', fontsize=9)
    ax4.set_ylabel('Δv (m/s)', fontsize=9)
    ax4.set_title('Velocity Accumulation', fontsize=10, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # Panel 5: Energy scaling
    ax5 = fig.add_subplot(gs[1, 1])
    data5 = results['test_5']
    ax5.plot(data5['charge_levels_uC'], data5['total_energy_mJ'], 'c-o', linewidth=2, markersize=6)
    ax5.set_xlabel('Charge (μC)', fontsize=9)
    ax5.set_ylabel('Energy (mJ)', fontsize=9)
    ax5.set_title('Energy Requirements (E ∝ q²)', fontsize=10, fontweight='bold')
    ax5.grid(True, alpha=0.3)

    # Panel 6: B-field vs altitude
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(data1['altitudes'], data1['b_field_magnitudes'], 'y-o', linewidth=2, markersize=6)
    ax6.set_xlabel('Altitude (km)', fontsize=9)
    ax6.set_ylabel('B-field (μT)', fontsize=9)
    ax6.set_title('Earth Magnetic Field', fontsize=10, fontweight='bold')
    ax6.grid(True, alpha=0.3)

    # Bottom row: Key metrics table
    ax7 = fig.add_subplot(gs[2, :])
    ax7.axis('off')

    # Create summary table
    table_data = [
        ['Parameter', 'Value', 'Unit', 'Notes'],
        ['Typical Force', f'{np.mean(data1["forces"]):.2f}', 'μN', 'At 600 km, 1 μC/shell'],
        ['Typical Acceleration', f'{np.mean(data1["accelerations"]):.2f}', 'nm/s²', 'Spacecraft mass 1270 kg'],
        ['Δv per Day', f'{data4["delta_v_m_s"][1]:.5f}', 'm/s', 'Continuous thrust'],
        ['Δv per Month', f'{data4["delta_v_m_s"][3]:.3f}', 'm/s', 'Continuous thrust'],
        ['Energy per Charge', f'{data5["total_energy_mJ"][2]:.2f}', 'mJ', '6 shells @ 1 μC'],
        ['Energy Margin', '>99.9999', '%', 'vs 500 MJ capacity'],
        ['Fuel Consumption', '0', 'kg', 'Propellantless!']
    ]

    table = ax7.table(cellText=table_data, cellLoc='left', loc='center',
                     colWidths=[0.25, 0.2, 0.15, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#4CAF50')
        cell.set_text_props(weight='bold', color='white')

    # Alternate row colors
    for i in range(1, len(table_data)):
        for j in range(4):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#f0f0f0')

    plt.savefig(os.path.join(FIGURES_DIR, 'summary_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"  Saved: summary_comparison.png")
    plt.close()

def generate_all_figures():
    """Generate all figures"""
    print("\n" + "=" * 70)
    print("GENERATING COMPREHENSIVE FIGURES")
    print("=" * 70 + "\n")

    # Load results
    results = load_results()

    # Generate all plots
    plot_test1_altitude_effects(results)
    plot_test2_charge_scaling(results)
    plot_test3_orbital_variation(results)
    plot_test4_delta_v_accumulation(results)
    plot_test5_energy_consumption(results)
    plot_summary_comparison(results)

    print("\n" + "=" * 70)
    print("ALL FIGURES GENERATED SUCCESSFULLY")
    print(f"Saved to: {FIGURES_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    generate_all_figures()
