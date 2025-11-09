#!/usr/bin/env python3
"""
Comprehensive Test Suite for Magneto-Coulombic Actuation System
Tests Lorentz force performance across varied conditions
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from lorentz_force_physics import (
    LorentzForceActuator, EarthMagneticField,
    orbital_velocity, MU_EARTH, R_EARTH
)
import json
import os

# Set output directories
RESULTS_DIR = '../results'
FIGURES_DIR = '../figures'

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

class MagnetoCoulombicTestSuite:
    """Comprehensive test suite for Magneto-Coulombic system"""

    def __init__(self):
        self.actuator = LorentzForceActuator(num_shells=6, max_charge=1e-6)
        self.b_field_model = EarthMagneticField()
        self.results = {}

    def test_1_orbital_altitude_variation(self):
        """Test Suite 1: Performance vs orbital altitude"""
        print("\n" + "=" * 70)
        print("TEST SUITE 1: ORBITAL ALTITUDE VARIATION")
        print("=" * 70)

        altitudes = [400, 500, 600, 800, 1000]  # km
        results = {
            'altitudes': altitudes,
            'velocities': [],
            'b_field_magnitudes': [],
            'forces': [],
            'torques': [],
            'accelerations': []
        }

        spacecraft_mass = 1270  # kg

        for alt in altitudes:
            print(f"\n--- Testing altitude: {alt} km ---")

            # Position and velocity
            position = np.array([R_EARTH + alt, 0, 0])
            v_mag = orbital_velocity(alt)
            velocity = np.array([0, v_mag, 0])

            # Magnetic field
            B_field = self.b_field_model.get_field(position)
            B_mag = np.linalg.norm(B_field)

            # Net force (all shells at +1 μC)
            shell_charges = np.ones(6) * 1e-6
            F_net, F_mag = self.actuator.compute_net_force(shell_charges, velocity, position)
            acceleration = F_mag / spacecraft_mass  # m/s^2

            # Torque (±x pair at ±1 μC)
            shell_charges_torque = np.array([1e-6, -1e-6, 0, 0, 0, 0])
            torque, tau_mag = self.actuator.compute_torque(shell_charges_torque, velocity, position)

            # Store results
            results['velocities'].append(v_mag * 1000)  # m/s
            results['b_field_magnitudes'].append(B_mag * 1e6)  # μT
            results['forces'].append(F_mag * 1e6)  # μN
            results['torques'].append(tau_mag * 1e6)  # μN·m
            results['accelerations'].append(acceleration * 1e9)  # nm/s^2

            print(f"  Orbital velocity: {v_mag*1000:.1f} m/s")
            print(f"  Magnetic field: {B_mag*1e6:.2f} μT")
            print(f"  Net force: {F_mag*1e6:.2f} μN")
            print(f"  Acceleration: {acceleration*1e9:.2f} nm/s²")
            print(f"  Torque: {tau_mag*1e6:.2f} μN·m")

        self.results['test_1'] = results
        return results

    def test_2_charge_level_variation(self):
        """Test Suite 2: Performance vs charge magnitude"""
        print("\n" + "=" * 70)
        print("TEST SUITE 2: CHARGE LEVEL VARIATION")
        print("=" * 70)

        charge_levels = [0.1e-6, 0.5e-6, 1.0e-6, 2.0e-6, 5.0e-6]  # Coulombs
        results = {
            'charge_levels': [q * 1e6 for q in charge_levels],  # μC
            'forces': [],
            'torques': [],
            'accelerations': []
        }

        # Fixed altitude: 600 km
        altitude = 600
        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])
        spacecraft_mass = 1270  # kg

        for q in charge_levels:
            print(f"\n--- Testing charge level: {q*1e6:.2f} μC ---")

            # Net force
            shell_charges = np.ones(6) * q
            F_net, F_mag = self.actuator.compute_net_force(shell_charges, velocity, position)
            acceleration = F_mag / spacecraft_mass

            # Torque
            shell_charges_torque = np.array([q, -q, 0, 0, 0, 0])
            torque, tau_mag = self.actuator.compute_torque(shell_charges_torque, velocity, position)

            results['forces'].append(F_mag * 1e6)  # μN
            results['torques'].append(tau_mag * 1e6)  # μN·m
            results['accelerations'].append(acceleration * 1e9)  # nm/s^2

            print(f"  Net force: {F_mag*1e6:.2f} μN")
            print(f"  Acceleration: {acceleration*1e9:.2f} nm/s²")
            print(f"  Torque: {tau_mag*1e6:.2f} μN·m")

        self.results['test_2'] = results
        return results

    def test_3_orbital_position_variation(self):
        """Test Suite 3: Force variation along orbit"""
        print("\n" + "=" * 70)
        print("TEST SUITE 3: ORBITAL POSITION VARIATION")
        print("=" * 70)

        num_points = 36  # Every 10 degrees
        theta_values = np.linspace(0, 2*np.pi, num_points)
        altitude = 600  # km
        r = R_EARTH + altitude

        results = {
            'theta_deg': (theta_values * 180 / np.pi).tolist(),
            'forces': [],
            'force_directions': [],
            'b_field_magnitudes': []
        }

        shell_charges = np.ones(6) * 1e-6  # 1 μC each

        print(f"\nCircular orbit at {altitude} km altitude")
        print("Testing force variation around complete orbit...")

        for theta in theta_values:
            # Position in orbit
            position = np.array([r * np.cos(theta), r * np.sin(theta), 0])

            # Velocity (perpendicular to radius)
            v_mag = orbital_velocity(altitude)
            velocity = np.array([-v_mag * np.sin(theta), v_mag * np.cos(theta), 0])

            # Magnetic field
            B_field = self.b_field_model.get_field(position)
            B_mag = np.linalg.norm(B_field)

            # Net force
            F_net, F_mag = self.actuator.compute_net_force(shell_charges, velocity, position)

            results['forces'].append(F_mag * 1e6)  # μN
            results['force_directions'].append(F_net.tolist())
            results['b_field_magnitudes'].append(B_mag * 1e6)  # μT

        avg_force = np.mean(results['forces'])
        print(f"  Average force: {avg_force:.2f} μN")
        print(f"  Force variation: {np.std(results['forces']):.2f} μN (std dev)")

        self.results['test_3'] = results
        return results

    def test_4_delta_v_accumulation(self):
        """Test Suite 4: Delta-v accumulation over time"""
        print("\n" + "=" * 70)
        print("TEST SUITE 4: DELTA-V ACCUMULATION")
        print("=" * 70)

        durations = [3600, 86400, 7*86400, 30*86400]  # 1hr, 1day, 1week, 1month (seconds)
        altitude = 600  # km
        spacecraft_mass = 1270  # kg
        shell_charges = np.ones(6) * 1e-6  # 1 μC each

        # Calculate typical force
        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])
        F_net, F_mag = self.actuator.compute_net_force(shell_charges, velocity, position)
        acceleration = F_mag / spacecraft_mass  # m/s^2

        results = {
            'durations_hours': [d/3600 for d in durations],
            'durations_days': [d/86400 for d in durations],
            'delta_v_mm_s': [],
            'delta_v_m_s': []
        }

        print(f"\nConstant acceleration: {acceleration*1e9:.2f} nm/s²")
        print(f"At {altitude} km altitude with {shell_charges[0]*1e6} μC per shell\n")

        for duration in durations:
            delta_v = acceleration * duration  # m/s
            results['delta_v_mm_s'].append(delta_v * 1000)  # mm/s
            results['delta_v_m_s'].append(delta_v)  # m/s

            duration_str = f"{duration/86400:.1f} days" if duration >= 86400 else f"{duration/3600:.1f} hours"
            print(f"  After {duration_str:15s}: Δv = {delta_v*1000:8.2f} mm/s = {delta_v:8.5f} m/s")

        self.results['test_4'] = results
        return results

    def test_5_energy_consumption(self):
        """Test Suite 5: Energy requirements for charging"""
        print("\n" + "=" * 70)
        print("TEST SUITE 5: ENERGY CONSUMPTION")
        print("=" * 70)

        charge_levels = [0.1e-6, 0.5e-6, 1.0e-6, 2.0e-6, 5.0e-6]  # Coulombs
        voltage = 50000  # 50 kV
        num_shells = 6
        capacitance = 1e-6  # 1 μF (assumed)

        results = {
            'charge_levels_uC': [q * 1e6 for q in charge_levels],
            'energy_per_shell_mJ': [],
            'total_energy_mJ': [],
            'total_energy_J': []
        }

        print(f"Voltage: {voltage/1000:.0f} kV")
        print(f"Capacitance (assumed): {capacitance*1e6:.1f} μF")
        print(f"Number of shells: {num_shells}\n")

        for q in charge_levels:
            # Energy: E = Q²/(2C)
            energy_per_shell = (q**2) / (2 * capacitance)  # Joules
            total_energy = energy_per_shell * num_shells

            results['energy_per_shell_mJ'].append(energy_per_shell * 1000)  # mJ
            results['total_energy_mJ'].append(total_energy * 1000)  # mJ
            results['total_energy_J'].append(total_energy)  # J

            print(f"  Charge {q*1e6:.1f} μC: E_shell = {energy_per_shell*1000:.2f} mJ, " +
                  f"E_total = {total_energy*1000:.2f} mJ = {total_energy:.4f} J")

        # Compare to available energy (500 MJ)
        available_energy = 500e6  # Joules
        max_energy_used = max(results['total_energy_J'])
        margin = (available_energy - max_energy_used) / available_energy * 100

        print(f"\n  Available energy: {available_energy/1e6:.0f} MJ")
        print(f"  Maximum used: {max_energy_used:.4f} J = {max_energy_used*1e6:.4f} μJ")
        print(f"  Energy margin: {margin:.8f}%")

        self.results['test_5'] = results
        return results

    def save_results(self, filename='test_results.json'):
        """Save all test results to JSON file"""
        filepath = os.path.join(RESULTS_DIR, filename)

        # Convert numpy arrays to lists for JSON serialization
        json_results = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                json_results[key] = {k: v for k, v in value.items()}
            else:
                json_results[key] = value

        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2)

        print(f"\nResults saved to: {filepath}")

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "█" * 70)
        print(" " * 15 + "MAGNETO-COULOMBIC ACTUATION")
        print(" " * 18 + "COMPREHENSIVE TEST SUITE")
        print(" " * 15 + "IIT Kanpur Research Hackathon 2025")
        print("█" * 70)

        self.test_1_orbital_altitude_variation()
        self.test_2_charge_level_variation()
        self.test_3_orbital_position_variation()
        self.test_4_delta_v_accumulation()
        self.test_5_energy_consumption()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETE")
        print("=" * 70)

        self.save_results()


if __name__ == "__main__":
    suite = MagnetoCoulombicTestSuite()
    suite.run_all_tests()
