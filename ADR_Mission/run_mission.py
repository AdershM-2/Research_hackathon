#!/usr/bin/env python3
"""
Active Debris Removal Mission Simulator
IIT Kanpur Research Hackathon 2025

Complete mission simulation from launch to deorbit
"""

import numpy as np
import sys
import os
import json
from datetime import datetime

# Add project to path
sys.path.append('/home/user/Research_hackathon/ADR_Mission')

from config.mission_config import CHASER, TARGET, MISSION_PHASES
from src.mission_phases.phase_manager import MissionPhaseManager
from src.utils.visualization import (
    plot_trajectory_3d,
    plot_state_history,
    plot_control_history,
    plot_angular_velocity,
    plot_mission_summary
)


def save_mission_report(mission_data, output_file):
    """
    Generate and save mission report

    Args:
        mission_data: Mission data dictionary
        output_file: Output file path
    """
    report = []
    report.append("="*80)
    report.append("ACTIVE DEBRIS REMOVAL MISSION REPORT")
    report.append("IIT Kanpur Research Hackathon 2025")
    report.append("="*80)
    report.append("")

    report.append(f"Mission Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Phase 1
    if 'phase_1' in mission_data and mission_data['phase_1'] is not None:
        report.append("-" * 80)
        report.append("PHASE 1: HOHMANN TRANSFER (COULOMB FORCES)")
        report.append("-" * 80)
        data = mission_data['phase_1']
        report.append(f"  First burn (Δv₁):      {data['dv1']*1000:8.2f} m/s")
        report.append(f"  Second burn (Δv₂):     {data['dv2']*1000:8.2f} m/s")
        report.append(f"  Total Δv:              {data['total_dv']*1000:8.2f} m/s")
        report.append(f"  Transfer time:         {data['transfer_time']/60:8.1f} minutes")
        report.append(f"  Energy used:           {data.get('energy_used', 0)/1e6:8.2f} MJ")
        report.append(f"  Energy remaining:      {data.get('energy_remaining', 0)/1e6:8.2f} MJ")
        report.append("")

    # Phase 2
    if 'phase_2' in mission_data and mission_data['phase_2'] is not None:
        report.append("-" * 80)
        report.append("PHASE 2: FAR-RANGE APPROACH (COULOMB TRACTOR)")
        report.append("-" * 80)
        data = mission_data['phase_2']
        report.append(f"  Final position error:  {data['final_error_pos']*1000:8.2f} m")
        report.append(f"  Final velocity error:  {data['final_error_vel']*1e6:8.2f} mm/s")
        report.append(f"  Total Δv:              {data['total_dv']*1000:8.2f} m/s")
        report.append(f"  Energy used:           {data.get('energy_used', 0)/1e6:8.2f} MJ")
        report.append(f"  Energy remaining:      {data.get('energy_remaining', 0)/1e6:8.2f} MJ")
        report.append("")

    # Phase 3
    if 'phase_3' in mission_data and mission_data['phase_3'] is not None:
        report.append("-" * 80)
        report.append("PHASE 3: PROXIMITY OPERATIONS (COULOMB FORCES)")
        report.append("-" * 80)
        data = mission_data['phase_3']
        report.append(f"  Final position error:  {data['final_error_pos']*1000:8.2f} m")
        report.append(f"  Final velocity error:  {data['final_error_vel']*1e6:8.2f} mm/s")
        report.append(f"  Total Δv:              {data['total_dv']*1000:8.2f} m/s")
        report.append(f"  Energy used:           {data.get('energy_used', 0)/1e6:8.2f} MJ")
        report.append(f"  Energy remaining:      {data.get('energy_remaining', 0)/1e6:8.2f} MJ")
        report.append("")

    # Phase 4
    if 'phase_4' in mission_data and mission_data['phase_4'] is not None:
        report.append("-" * 80)
        report.append("PHASE 4: ACTIVE DETUMBLING")
        report.append("-" * 80)
        data = mission_data['phase_4']
        report.append(f"  Initial tumbling:      {np.linalg.norm(TARGET['omega_init']):8.4f} rad/s")
        report.append(f"  Final tumbling:        {data['final_omega']:8.4f} rad/s")
        report.append(f"  Target tumbling:       {MISSION_PHASES['phase_4_detumbling']['target_omega']:8.4f} rad/s")
        report.append("")

    # Phase 5
    if 'phase_5' in mission_data and mission_data['phase_5'] is not None:
        report.append("-" * 80)
        report.append("PHASE 5: CAPTURE (COULOMB TRACTOR)")
        report.append("-" * 80)
        data = mission_data['phase_5']
        report.append(f"  Final separation:      {data['final_separation']*1000:8.2f} m")
        report.append(f"  Final velocity:        {data['final_velocity']*1000:8.2f} m/s")
        report.append(f"  Energy used:           {data.get('energy_used', 0)/1e6:8.2f} MJ")
        report.append(f"  Energy remaining:      {data.get('energy_remaining', 0)/1e6:8.2f} MJ")
        report.append("")

    # Phase 6
    if 'phase_6' in mission_data and mission_data['phase_6'] is not None:
        report.append("-" * 80)
        report.append("PHASE 6: DEORBIT (COULOMB TRACTOR)")
        report.append("-" * 80)
        data = mission_data['phase_6']
        report.append(f"  Deorbit Δv:            {abs(data['dv'])*1000:8.2f} m/s")
        report.append(f"  Energy required:       {data.get('energy_required', 0)/1e6:8.2f} MJ")
        report.append(f"  Energy remaining:      {data.get('energy_remaining', 0)/1e6:8.2f} MJ")
        report.append("")

    # Summary
    report.append("="*80)
    report.append("MISSION SUMMARY")
    report.append("="*80)

    total_dv = 0
    total_fuel = 0

    for phase in ['phase_1', 'phase_2', 'phase_3', 'phase_5', 'phase_6']:
        if phase in mission_data and mission_data[phase] is not None:
            data = mission_data[phase]
            if 'total_dv' in data:
                total_dv += data['total_dv']
            if 'dv' in data:
                total_dv += abs(data['dv'])
            if 'energy_used' in data:
                total_fuel += data['energy_used']
            if 'energy_required' in data:
                total_fuel += data['energy_required']

    report.append(f"  Total Δv:              {total_dv*1000:8.2f} m/s")
    report.append(f"  Total energy consumed: {total_fuel/1e6:8.2f} MJ")
    report.append(f"  Initial energy:        {CHASER['current_energy']/1e6:8.2f} MJ")
    report.append(f"  Energy margin:         {(CHASER['current_energy']-total_fuel)/CHASER['current_energy']*100:8.1f}%")
    report.append("")
    report.append("  🚀 COULOMB FORCE PROPULSION - ZERO CHEMICAL FUEL USED!")
    report.append("")
    report.append("="*80)

    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nMission report saved to: {output_file}")

    # Also print to console
    print('\n'.join(report))


def main():
    """Main simulation runner"""
    print("\n" + "█"*80)
    print(" "*20 + "ACTIVE DEBRIS REMOVAL MISSION SIMULATOR")
    print(" "*20 + "IIT Kanpur Research Hackathon 2025")
    print("█"*80 + "\n")

    # Create output directories
    os.makedirs('/home/user/Research_hackathon/ADR_Mission/results/plots', exist_ok=True)
    os.makedirs('/home/user/Research_hackathon/ADR_Mission/results/data', exist_ok=True)
    os.makedirs('/home/user/Research_hackathon/ADR_Mission/results/reports', exist_ok=True)

    # Initialize mission
    mission = MissionPhaseManager(CHASER.copy(), TARGET.copy())

    # Run full mission
    success, mission_data = mission.run_full_mission()

    if success:
        print("\n🎉 MISSION ACCOMPLISHED! 🎉\n")
    else:
        print("\n⚠ MISSION INCOMPLETE ⚠\n")

    # Generate visualizations
    print("\nGenerating visualizations...")

    results_dir = '/home/user/Research_hackathon/ADR_Mission/results/plots'

    # Phase 2: Far-range approach
    if 'phase_2' in mission_data and mission_data['phase_2'] is not None:
        data = mission_data['phase_2']
        plot_trajectory_3d(
            data['states'],
            "Phase 2: Far-Range Approach (10 km → 50 m)",
            f"{results_dir}/phase2_trajectory.png"
        )
        plot_state_history(
            data['time'],
            data['states'],
            f"{results_dir}/phase2_states.png"
        )
        plot_control_history(
            data['time'],
            data['controls'],
            f"{results_dir}/phase2_controls.png"
        )

    # Phase 3: Proximity operations
    if 'phase_3' in mission_data and mission_data['phase_3'] is not None:
        data = mission_data['phase_3']
        plot_trajectory_3d(
            data['states'],
            "Phase 3: Proximity Operations (50 m → 5 m)",
            f"{results_dir}/phase3_trajectory.png"
        )
        plot_state_history(
            data['time'],
            data['states'],
            f"{results_dir}/phase3_states.png"
        )

    # Phase 4: Detumbling
    if 'phase_4' in mission_data and mission_data['phase_4'] is not None:
        data = mission_data['phase_4']
        plot_angular_velocity(
            data['time'],
            data['omega_history'],
            MISSION_PHASES['phase_4_detumbling']['target_omega'],
            f"{results_dir}/phase4_detumbling.png"
        )

    # Mission summary
    plot_mission_summary(
        mission_data,
        f"{results_dir}/mission_summary.png"
    )

    # Generate report
    print("\nGenerating mission report...")
    save_mission_report(
        mission_data,
        '/home/user/Research_hackathon/ADR_Mission/results/reports/mission_report.txt'
    )

    # Save data as JSON
    print("\nSaving mission data...")
    # Convert numpy arrays to lists for JSON serialization
    json_data = {}
    for phase, data in mission_data.items():
        if data is not None:
            json_data[phase] = {}
            for key, value in data.items():
                if isinstance(value, np.ndarray):
                    json_data[phase][key] = value.tolist()
                elif isinstance(value, (np.float64, np.float32)):
                    json_data[phase][key] = float(value)
                else:
                    json_data[phase][key] = value

    with open('/home/user/Research_hackathon/ADR_Mission/results/data/mission_data.json', 'w') as f:
        json.dump(json_data, f, indent=2)

    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)
    print(f"Results saved in: /home/user/Research_hackathon/ADR_Mission/results/")
    print("  - plots/         : Trajectory and performance plots")
    print("  - reports/       : Mission report (text)")
    print("  - data/          : Mission data (JSON)")
    print("="*80 + "\n")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
