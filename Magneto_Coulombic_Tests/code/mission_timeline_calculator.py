#!/usr/bin/env python3
"""
Mission Timeline Calculator for ADR with High-Charge Magneto-Coulombic System
Calculates rendezvous and deorbit times for different configurations
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import json
import os

# Physical constants
MU_EARTH = 398600.0  # km^3/s^2
R_EARTH = 6371.0  # km

def orbital_velocity(altitude_km):
    """Calculate circular orbital velocity"""
    r = R_EARTH + altitude_km
    return np.sqrt(MU_EARTH / r)  # km/s

def hohmann_transfer_time(r1, r2):
    """Calculate Hohmann transfer time between two circular orbits"""
    a_transfer = (r1 + r2) / 2.0
    period_transfer = 2 * np.pi * np.sqrt(a_transfer**3 / MU_EARTH)
    return period_transfer / 2.0  # seconds (half orbit)

def hohmann_delta_v(alt1_km, alt2_km):
    """Calculate delta-v required for Hohmann transfer"""
    r1 = R_EARTH + alt1_km
    r2 = R_EARTH + alt2_km

    v1 = np.sqrt(MU_EARTH / r1)
    v2 = np.sqrt(MU_EARTH / r2)

    # Delta-v at periapsis (burn 1)
    v_transfer_peri = np.sqrt(MU_EARTH * (2/r1 - 1/((r1+r2)/2)))
    dv1 = abs(v_transfer_peri - v1)

    # Delta-v at apoapsis (burn 2)
    v_transfer_apo = np.sqrt(MU_EARTH * (2/r2 - 1/((r1+r2)/2)))
    dv2 = abs(v2 - v_transfer_apo)

    return dv1, dv2, dv1 + dv2

class MissionTimelineCalculator:
    """Calculate mission timelines for ADR"""

    def __init__(self, chaser_mass_kg, charge_per_shell_C, acceleration_ms2):
        self.chaser_mass = chaser_mass_kg
        self.charge = charge_per_shell_C
        self.acceleration = acceleration_ms2  # m/s²

    def calculate_burn_time(self, delta_v_km_s):
        """Calculate time needed to achieve delta-v with constant acceleration"""
        delta_v_ms = delta_v_km_s * 1000  # Convert to m/s
        burn_time = delta_v_ms / self.acceleration  # seconds
        return burn_time

    def calculate_approach_time(self, distance_km, final_velocity_m_s=1.0):
        """
        Calculate time for approach phase using constant acceleration
        Assumes: accelerate to midpoint, decelerate to final velocity
        """
        distance_m = distance_km * 1000

        # For constant acceleration approach with final velocity constraint
        # Using kinematic equation: d = v_f*t - 0.5*a*t^2
        # Simplified: assume symmetric acceleration/deceleration

        # Accelerate to midpoint, decelerate to final velocity
        half_distance = distance_m / 2.0

        # Max velocity at midpoint (starting from low velocity)
        # v^2 = v0^2 + 2*a*d, assume v0 ≈ 0
        v_max = np.sqrt(2 * self.acceleration * half_distance)

        # Time to accelerate
        t_accel = v_max / self.acceleration

        # Time to decelerate from v_max to v_final
        t_decel = (v_max - final_velocity_m_s) / self.acceleration

        total_time = t_accel + t_decel
        return total_time

    def calculate_full_mission(self):
        """Calculate complete mission timeline"""

        print("\n" + "="*80)
        print(f"MISSION TIMELINE: {self.chaser_mass}kg chaser, {self.charge}C/shell")
        print(f"Acceleration: {self.acceleration:.6f} m/s²")
        print("="*80)

        # Mission phases
        chaser_alt = 400  # km
        target_alt = 600  # km

        timeline = {}

        # ====================================================================
        # PHASE 1: HOHMANN TRANSFER (400 km → 600 km)
        # ====================================================================
        print("\n--- PHASE 1: HOHMANN TRANSFER (400 km → 600 km) ---")

        r1 = R_EARTH + chaser_alt
        r2 = R_EARTH + target_alt

        dv1, dv2, total_dv = hohmann_delta_v(chaser_alt, target_alt)
        transfer_time = hohmann_transfer_time(r1, r2)

        # Burn times
        burn1_time = self.calculate_burn_time(dv1)
        burn2_time = self.calculate_burn_time(dv2)

        # Coast time (transfer orbit)
        coast_time = transfer_time - burn1_time - burn2_time

        phase1_total = burn1_time + coast_time + burn2_time

        print(f"  Burn 1 delta-v: {dv1:.6f} km/s ({dv1*1000:.2f} m/s)")
        print(f"  Burn 1 time: {burn1_time:.1f} seconds = {burn1_time/60:.2f} minutes")
        print(f"  Coast time: {coast_time:.1f} seconds = {coast_time/60:.2f} minutes")
        print(f"  Burn 2 delta-v: {dv2:.6f} km/s ({dv2*1000:.2f} m/s)")
        print(f"  Burn 2 time: {burn2_time:.1f} seconds = {burn2_time/60:.2f} minutes")
        print(f"  TOTAL PHASE 1: {phase1_total:.1f} seconds = {phase1_total/60:.2f} minutes = {phase1_total/3600:.2f} hours")

        timeline['phase1_transfer'] = {
            'burn1_dv': dv1,
            'burn1_time': burn1_time,
            'coast_time': coast_time,
            'burn2_dv': dv2,
            'burn2_time': burn2_time,
            'total_time': phase1_total
        }

        # ====================================================================
        # PHASE 2: FAR-RANGE APPROACH (10 km → 50 m)
        # ====================================================================
        print("\n--- PHASE 2: FAR-RANGE APPROACH (10 km → 50 m) ---")

        approach_distance = 10.0  # km
        final_velocity = 1.0  # m/s (safe approach velocity)

        approach_time = self.calculate_approach_time(approach_distance, final_velocity)

        print(f"  Distance: {approach_distance} km")
        print(f"  Final approach velocity: {final_velocity} m/s")
        print(f"  Approach time: {approach_time:.1f} seconds = {approach_time/60:.2f} minutes = {approach_time/3600:.2f} hours")

        timeline['phase2_approach'] = {
            'distance': approach_distance,
            'final_velocity': final_velocity,
            'time': approach_time
        }

        # ====================================================================
        # PHASE 3: PROXIMITY OPERATIONS (50 m → 5 m)
        # ====================================================================
        print("\n--- PHASE 3: PROXIMITY OPERATIONS (50 m → 5 m) ---")

        proximity_distance = 0.045  # km (45 meters)
        final_velocity_prox = 0.1  # m/s (very slow)

        proximity_time = self.calculate_approach_time(proximity_distance, final_velocity_prox)

        print(f"  Distance: {proximity_distance*1000:.1f} m")
        print(f"  Final velocity: {final_velocity_prox} m/s")
        print(f"  Proximity time: {proximity_time:.1f} seconds = {proximity_time/60:.2f} minutes")

        timeline['phase3_proximity'] = {
            'distance': proximity_distance,
            'final_velocity': final_velocity_prox,
            'time': proximity_time
        }

        # ====================================================================
        # PHASE 4: DETUMBLING
        # ====================================================================
        print("\n--- PHASE 4: DETUMBLING (Active Stabilization) ---")

        # Assume debris tumbling at ~0.15 rad/s, need to reduce to < 0.01 rad/s
        # Using Magneto-Coulombic torques (when available)
        # Conservative estimate: 30 minutes

        detumble_time = 30 * 60  # 30 minutes in seconds

        print(f"  Estimated detumbling time: {detumble_time/60:.1f} minutes")
        print(f"  (Depends on torque capability - needs optimization)")

        timeline['phase4_detumble'] = {
            'time': detumble_time,
            'note': 'Conservative estimate - depends on torque optimization'
        }

        # ====================================================================
        # PHASE 5: CAPTURE
        # ====================================================================
        print("\n--- PHASE 5: FINAL APPROACH & CAPTURE (5 m → contact) ---")

        capture_distance = 0.005  # km (5 meters)
        final_velocity_capture = 0.01  # m/s (very slow contact)

        capture_time = self.calculate_approach_time(capture_distance, final_velocity_capture)

        print(f"  Distance: {capture_distance*1000:.1f} m")
        print(f"  Contact velocity: {final_velocity_capture} m/s")
        print(f"  Capture time: {capture_time:.1f} seconds = {capture_time/60:.2f} minutes")

        timeline['phase5_capture'] = {
            'distance': capture_distance,
            'final_velocity': final_velocity_capture,
            'time': capture_time
        }

        # ====================================================================
        # TOTAL RENDEZVOUS TIME
        # ====================================================================
        total_rendezvous = (phase1_total + approach_time + proximity_time +
                           detumble_time + capture_time)

        print("\n" + "="*80)
        print("RENDEZVOUS SUMMARY")
        print("="*80)
        print(f"  Phase 1 (Transfer):    {phase1_total/3600:.2f} hours")
        print(f"  Phase 2 (Approach):    {approach_time/3600:.2f} hours")
        print(f"  Phase 3 (Proximity):   {proximity_time/60:.2f} minutes")
        print(f"  Phase 4 (Detumble):    {detumble_time/60:.2f} minutes")
        print(f"  Phase 5 (Capture):     {capture_time/60:.2f} minutes")
        print(f"  ---")
        print(f"  TOTAL RENDEZVOUS:      {total_rendezvous/3600:.2f} hours = {total_rendezvous/86400:.2f} days")

        timeline['total_rendezvous'] = {
            'seconds': total_rendezvous,
            'hours': total_rendezvous/3600,
            'days': total_rendezvous/86400
        }

        # ====================================================================
        # PHASE 6: DEORBIT (600 km → 250 km perigee)
        # ====================================================================
        print("\n" + "="*80)
        print("DEORBIT PHASE")
        print("="*80)

        # Combined mass after capture
        combined_mass = self.chaser_mass + 50  # 50 kg debris
        combined_acceleration = (self.acceleration * self.chaser_mass) / combined_mass

        print(f"\n  Combined mass: {combined_mass} kg")
        print(f"  Combined acceleration: {combined_acceleration:.6f} m/s²")

        # Deorbit: lower perigee from 600 km to 250 km
        current_alt = 600  # km
        target_perigee = 250  # km

        # For deorbit, we need to lower perigee while at apogee
        # This is a tangential retrograde burn at current altitude

        r_current = R_EARTH + current_alt
        r_perigee = R_EARTH + target_perigee

        # Current circular velocity
        v_circular = np.sqrt(MU_EARTH / r_current)

        # Velocity needed for elliptical orbit with perigee at target
        # At apogee: v = sqrt(mu * (2/r_apo - 1/a))
        # where a = (r_apo + r_peri) / 2
        a_ellipse = (r_current + r_perigee) / 2
        v_ellipse = np.sqrt(MU_EARTH * (2/r_current - 1/a_ellipse))

        deorbit_dv = v_circular - v_ellipse  # km/s

        # Burn time with combined mass
        deorbit_burn_time = self.calculate_burn_time(deorbit_dv) * (combined_mass / self.chaser_mass)

        # Time to decay from 250 km perigee to reentry (~100 km)
        # This is atmospheric drag-dominated
        # Rough estimate: 1-3 days depending on solar activity
        decay_time_days = 2.0  # Conservative estimate
        decay_time = decay_time_days * 86400  # seconds

        print(f"\n--- PHASE 6a: DEORBIT BURN ---")
        print(f"  Current altitude: {current_alt} km (circular)")
        print(f"  Target perigee: {target_perigee} km")
        print(f"  Required delta-v: {deorbit_dv:.6f} km/s ({deorbit_dv*1000:.2f} m/s)")
        print(f"  Burn time: {deorbit_burn_time:.1f} seconds = {deorbit_burn_time/60:.2f} minutes = {deorbit_burn_time/3600:.2f} hours")

        print(f"\n--- PHASE 6b: ATMOSPHERIC DECAY ---")
        print(f"  From {target_perigee} km perigee to reentry")
        print(f"  Estimated decay time: {decay_time_days:.1f} days (drag-dependent)")

        total_deorbit = deorbit_burn_time + decay_time

        print(f"\n  TOTAL DEORBIT TIME: {total_deorbit/86400:.2f} days")
        print(f"    (Burn: {deorbit_burn_time/3600:.2f} hours + Decay: {decay_time_days:.1f} days)")

        timeline['phase6_deorbit'] = {
            'burn_dv': deorbit_dv,
            'burn_time': deorbit_burn_time,
            'decay_time': decay_time,
            'total_time': total_deorbit,
            'combined_mass': combined_mass,
            'combined_acceleration': combined_acceleration
        }

        # ====================================================================
        # TOTAL MISSION TIME
        # ====================================================================
        total_mission = total_rendezvous + total_deorbit

        print("\n" + "="*80)
        print("COMPLETE MISSION TIMELINE")
        print("="*80)
        print(f"  Rendezvous:  {total_rendezvous/86400:.2f} days")
        print(f"  Deorbit:     {total_deorbit/86400:.2f} days")
        print(f"  ---")
        print(f"  TOTAL:       {total_mission/86400:.2f} days")
        print("="*80)

        timeline['total_mission'] = {
            'seconds': total_mission,
            'hours': total_mission/3600,
            'days': total_mission/86400
        }

        return timeline


if __name__ == "__main__":

    # Load performance data from high-charge tests
    results_file = '../results/high_charge_variable_separation_results.json'
    with open(results_file, 'r') as f:
        results = json.load(f)

    print("\n" + "█"*80)
    print(" "*25 + "ADR MISSION TIMELINE ANALYSIS")
    print(" "*20 + "High-Charge Magneto-Coulombic System")
    print(" "*25 + "IIT Kanpur Research Hackathon 2025")
    print("█"*80)

    # Test configurations
    configurations = [
        # (mass_kg, charge_C, acceleration_m_s2)
        (10, 1, results['test_1']['chaser_10kg']['accelerations'][0]),
        (10, 3, results['test_1']['chaser_10kg']['accelerations'][2]),
        (10, 5, results['test_1']['chaser_10kg']['accelerations'][4]),
        (25, 1, results['test_1']['chaser_25kg']['accelerations'][0]),
        (25, 3, results['test_1']['chaser_25kg']['accelerations'][2]),
        (25, 5, results['test_1']['chaser_25kg']['accelerations'][4]),
    ]

    all_timelines = {}

    for mass, charge, accel in configurations:
        calc = MissionTimelineCalculator(mass, charge, accel)
        timeline = calc.calculate_full_mission()

        key = f"{mass}kg_{charge}C"
        all_timelines[key] = timeline

    # Save results
    output_file = '../results/mission_timelines.json'
    with open(output_file, 'w') as f:
        json.dump(all_timelines, f, indent=2)

    print(f"\n\nTimeline results saved to: {output_file}")

    # Summary comparison
    print("\n\n" + "="*80)
    print("MISSION TIMELINE COMPARISON")
    print("="*80)
    print(f"{'Configuration':<15} {'Rendezvous':<15} {'Deorbit':<15} {'Total Mission':<15}")
    print("-"*80)

    for key, timeline in all_timelines.items():
        rendezvous_days = timeline['total_rendezvous']['days']
        deorbit_days = timeline['phase6_deorbit']['total_time'] / 86400
        total_days = timeline['total_mission']['days']

        print(f"{key:<15} {rendezvous_days:>7.2f} days   {deorbit_days:>7.2f} days   {total_days:>7.2f} days")

    print("="*80)
