#!/usr/bin/env python3
"""
Test Coulomb Force Mission with Various Parameters
Tests different initial charges, separations, and tumbling rates
"""

import numpy as np
import sys
sys.path.append('/home/user/Research_hackathon/ADR_Mission')

from config.mission_config import CHASER, TARGET, MISSION_PHASES
from src.mission_phases.phase_manager import MissionPhaseManager


def test_different_charges():
    """Test with different debris charge levels"""
    print("\n" + "="*80)
    print("TEST 1: DIFFERENT DEBRIS CHARGE LEVELS")
    print("="*80)

    charges = [-0.01, -0.001, -0.0001, 0.0001, 0.001, 0.01]

    for charge in charges:
        print(f"\n--- Testing with debris charge: {charge:.5f} C ---")

        chaser = CHASER.copy()
        target = TARGET.copy()
        target['charge'] = charge

        mission = MissionPhaseManager(chaser, target)

        # Test just Phase 1
        success, data = mission.phase_1_hohmann_transfer()

        if success:
            print(f"✓ Success! Energy used: {data['energy_used']/1e6:.2f} MJ")
        else:
            print(f"✗ Failed!")


def test_different_separations():
    """Test with different initial separations"""
    print("\n" + "="*80)
    print("TEST 2: DIFFERENT INITIAL SEPARATIONS")
    print("="*80)

    separations = [1.0, 5.0, 10.0, 20.0, 50.0]  # km

    for sep in separations:
        print(f"\n--- Testing with separation: {sep:.1f} km ---")

        chaser = CHASER.copy()
        target = TARGET.copy()

        mission = MissionPhaseManager(chaser, target)

        # Test Phase 2 with different separations
        success, data = mission.phase_2_far_range_approach(
            initial_sep=sep,
            final_sep=0.05,
            duration=7200  # 2 hours
        )

        if success:
            print(f"✓ Converged! Energy used: {data.get('energy_used', 0)/1e6:.2f} MJ")
        else:
            print(f"⚠ Did not fully converge. Final error: {data['final_error_pos']*1000:.2f} m")


def test_different_tumbling():
    """Test with different tumbling rates"""
    print("\n" + "="*80)
    print("TEST 3: DIFFERENT TUMBLING RATES")
    print("="*80)

    tumbling_rates = [
        np.array([0.01, 0.01, 0.01]),
        np.array([0.1, 0.05, 0.15]),
        np.array([0.5, 0.3, 0.4]),
        np.array([1.0, 0.8, 1.2])
    ]

    for omega in tumbling_rates:
        omega_mag = np.linalg.norm(omega)
        print(f"\n--- Testing with tumbling: {omega_mag:.3f} rad/s ---")

        chaser = CHASER.copy()
        target = TARGET.copy()
        target['omega_init'] = omega

        mission = MissionPhaseManager(chaser, target)

        # Test Phase 4
        success, data = mission.phase_4_detumbling()

        if success:
            print(f"✓ Detumbled! Final rate: {data['final_omega']:.4f} rad/s")
        else:
            print(f"⚠ Not fully detumbled. Final rate: {data['final_omega']:.4f} rad/s")


def test_different_orbital_altitudes():
    """Test with different orbital altitudes"""
    print("\n" + "="*80)
    print("TEST 4: DIFFERENT TARGET ORBITAL ALTITUDES")
    print("="*80)

    altitudes = [400, 600, 800, 1000]  # km

    for alt in altitudes:
        print(f"\n--- Testing transfer to {alt} km altitude ---")

        chaser = CHASER.copy()
        target = TARGET.copy()
        target['altitude_init'] = alt
        target['orbit_radius_init'] = 6371.0 + alt

        mission = MissionPhaseManager(chaser, target)

        # Test Phase 1
        success, data = mission.phase_1_hohmann_transfer()

        if success:
            print(f"✓ Transfer successful!")
            print(f"  Total Δv: {data['total_dv']*1000:.2f} m/s")
            print(f"  Energy used: {data['energy_used']/1e6:.2f} MJ")
            print(f"  Energy remaining: {data['energy_remaining']/1e6:.2f} MJ")
        else:
            print(f"✗ Failed!")


def test_energy_limited_scenarios():
    """Test with limited energy capacity"""
    print("\n" + "="*80)
    print("TEST 5: ENERGY-LIMITED SCENARIOS")
    print("="*80)

    energy_levels = [10e6, 50e6, 100e6, 500e6, 1e9]  # Joules

    for energy in energy_levels:
        print(f"\n--- Testing with {energy/1e6:.0f} MJ energy ---")

        chaser = CHASER.copy()
        chaser['current_energy'] = energy
        chaser['capacitor_energy'] = energy
        target = TARGET.copy()

        mission = MissionPhaseManager(chaser, target)

        # Run full mission
        success, data = mission.run_full_mission()

        if success:
            final_energy = data['phase_6']['energy_remaining'] if 'phase_6' in data else 0
            print(f"✓ MISSION SUCCESS! Final energy: {final_energy/1e6:.2f} MJ")
        else:
            print(f"✗ Mission incomplete")


def main():
    """Run all tests"""
    print("\n" + "█"*80)
    print(" "*15 + "COULOMB FORCE ACTUATOR - PARAMETER VARIATION TESTS")
    print(" "*20 + "IIT Kanpur Research Hackathon 2025")
    print("█"*80)

    test_different_charges()
    test_different_separations()
    test_different_tumbling()
    test_different_orbital_altitudes()
    test_energy_limited_scenarios()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
