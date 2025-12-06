#!/usr/bin/env python3
"""
High-Charge Magneto-Coulombic Test Suite with Variable Shell Separation
Tests 10kg and 25kg chasers with 1-5 Coulombs per shell and variable separations
IIT Kanpur Research Hackathon 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from lorentz_force_physics import EarthMagneticField, orbital_velocity, MU_EARTH, R_EARTH
import json
import os

# Set output directories
RESULTS_DIR = '../results'
FIGURES_DIR = '../figures'

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


class VariableSeparationLorentzActuator:
    """Lorentz force actuator with variable shell separation"""

    def __init__(self, num_shells=6, max_charge=5.0, shell_separation=1.0):
        """
        Args:
            num_shells: Number of charged shells (default 6: ±x, ±y, ±z)
            max_charge: Maximum charge per shell in Coulombs
            shell_separation: Distance from center to each shell in meters
        """
        self.num_shells = num_shells
        self.max_charge = max_charge
        self.shell_separation = shell_separation  # meters

        # Shell positions in body frame (meters)
        # 6 shells: ±x, ±y, ±z directions
        self.shell_positions = np.array([
            [shell_separation, 0, 0],   # +x
            [-shell_separation, 0, 0],  # -x
            [0, shell_separation, 0],   # +y
            [0, -shell_separation, 0],  # -y
            [0, 0, shell_separation],   # +z
            [0, 0, -shell_separation]   # -z
        ])

    def compute_net_force(self, shell_charges, velocity, position):
        """
        Compute net Lorentz force on spacecraft
        F = q(v × B) for each charged shell

        Args:
            shell_charges: Array of charges on each shell (Coulombs)
            velocity: Velocity vector in km/s
            position: Position vector in km

        Returns:
            F_net: Net force vector (N)
            F_mag: Force magnitude (N)
        """
        b_field_model = EarthMagneticField()
        B_field = b_field_model.get_field(position)  # Tesla

        # Convert velocity to m/s
        v_ms = velocity * 1000.0  # m/s

        # Compute Lorentz force for each shell
        F_net = np.zeros(3)
        for i in range(self.num_shells):
            q = shell_charges[i]
            # F = q(v × B)
            F_shell = q * np.cross(v_ms, B_field)
            F_net += F_shell

        F_mag = np.linalg.norm(F_net)
        return F_net, F_mag

    def compute_torque(self, shell_charges, velocity, position):
        """
        Compute net torque on spacecraft from Lorentz forces
        τ = r × F for each shell

        Args:
            shell_charges: Array of charges on each shell (Coulombs)
            velocity: Velocity vector in km/s
            position: Position vector in km

        Returns:
            tau_net: Net torque vector (N·m)
            tau_mag: Torque magnitude (N·m)
        """
        b_field_model = EarthMagneticField()
        B_field = b_field_model.get_field(position)  # Tesla

        # Convert velocity to m/s
        v_ms = velocity * 1000.0  # m/s

        # Compute torque for each shell
        tau_net = np.zeros(3)
        for i in range(self.num_shells):
            q = shell_charges[i]
            r = self.shell_positions[i]  # meters

            # F = q(v × B)
            F_shell = q * np.cross(v_ms, B_field)

            # τ = r × F
            tau_shell = np.cross(r, F_shell)
            tau_net += tau_shell

        tau_mag = np.linalg.norm(tau_net)
        return tau_net, tau_mag


class HighChargeTestSuite:
    """Test suite for high-charge (1-5 C) systems with variable separation"""

    def __init__(self):
        self.b_field_model = EarthMagneticField()
        self.results = {}

    def test_1_force_vs_charge(self):
        """Test Case 1: Force variation with charge level (1-5 C)"""
        print("\n" + "=" * 80)
        print("TEST CASE 1: FORCE VS CHARGE LEVEL (1-5 COULOMBS)")
        print("=" * 80)

        charge_levels = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Coulombs
        chaser_masses = [10.0, 25.0]  # kg
        altitude = 600  # km
        shell_separation = 1.0  # meters

        results = {
            'charge_levels': charge_levels.tolist(),
            'chaser_10kg': {'forces': [], 'accelerations': []},
            'chaser_25kg': {'forces': [], 'accelerations': []}
        }

        # Fixed orbital parameters
        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])

        actuator = VariableSeparationLorentzActuator(num_shells=6, shell_separation=shell_separation)

        for mass in chaser_masses:
            key = f'chaser_{int(mass)}kg'
            print(f"\n--- Chaser Mass: {mass} kg ---")

            for q in charge_levels:
                # All 6 shells at same charge level
                shell_charges = np.ones(6) * q

                F_net, F_mag = actuator.compute_net_force(shell_charges, velocity, position)
                acceleration = F_mag / mass  # m/s²

                results[key]['forces'].append(F_mag)
                results[key]['accelerations'].append(acceleration)

                print(f"  Charge: {q:.1f} C -> Force: {F_mag:.4f} N, Accel: {acceleration:.6f} m/s²")

        self.results['test_1'] = results
        return results

    def test_2_torque_vs_separation(self):
        """Test Case 2: Torque variation with shell separation"""
        print("\n" + "=" * 80)
        print("TEST CASE 2: TORQUE VS SHELL SEPARATION")
        print("=" * 80)

        separations = np.array([0.5, 1.0, 2.0, 3.0, 5.0])  # meters
        charge_levels = [1.0, 3.0, 5.0]  # Coulombs
        altitude = 600  # km

        results = {
            'separations': separations.tolist(),
            'charge_1C': [],
            'charge_3C': [],
            'charge_5C': []
        }

        # Fixed orbital parameters
        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])

        for q in charge_levels:
            key = f'charge_{int(q)}C'
            print(f"\n--- Charge Level: {q} C ---")

            for sep in separations:
                actuator = VariableSeparationLorentzActuator(num_shells=6, shell_separation=sep)

                # Use opposing charges to create torque (e.g., +x and -x shells)
                shell_charges = np.array([q, -q, 0, 0, 0, 0])

                tau_net, tau_mag = actuator.compute_torque(shell_charges, velocity, position)

                results[key].append(tau_mag)

                print(f"  Separation: {sep:.1f} m -> Torque: {tau_mag:.6f} N·m")

        self.results['test_2'] = results
        return results

    def test_3_acceleration_comparison(self):
        """Test Case 3: Detailed acceleration comparison (10kg vs 25kg)"""
        print("\n" + "=" * 80)
        print("TEST CASE 3: ACCELERATION COMPARISON (10kg vs 25kg)")
        print("=" * 80)

        charge_levels = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Coulombs
        altitudes = [400, 600, 800]  # km
        shell_separation = 2.0  # meters (larger for more torque)

        results = {
            'charge_levels': charge_levels.tolist(),
            'altitudes': altitudes,
            'data': {}
        }

        actuator = VariableSeparationLorentzActuator(num_shells=6, shell_separation=shell_separation)

        for alt in altitudes:
            position = np.array([R_EARTH + alt, 0, 0])
            v_mag = orbital_velocity(alt)
            velocity = np.array([0, v_mag, 0])

            results['data'][f'{alt}km'] = {
                '10kg': {'forces': [], 'accelerations': []},
                '25kg': {'forces': [], 'accelerations': []}
            }

            print(f"\n--- Altitude: {alt} km ---")

            for q in charge_levels:
                shell_charges = np.ones(6) * q
                F_net, F_mag = actuator.compute_net_force(shell_charges, velocity, position)

                acc_10kg = F_mag / 10.0
                acc_25kg = F_mag / 25.0

                results['data'][f'{alt}km']['10kg']['forces'].append(F_mag)
                results['data'][f'{alt}km']['10kg']['accelerations'].append(acc_10kg)
                results['data'][f'{alt}km']['25kg']['forces'].append(F_mag)
                results['data'][f'{alt}km']['25kg']['accelerations'].append(acc_25kg)

                print(f"  Q={q}C: F={F_mag:.4f}N | 10kg: {acc_10kg:.6f} m/s² | 25kg: {acc_25kg:.6f} m/s²")

        self.results['test_3'] = results
        return results

    def test_4_delta_v_accumulation(self):
        """Test Case 4: Delta-v accumulation over mission duration"""
        print("\n" + "=" * 80)
        print("TEST CASE 4: DELTA-V ACCUMULATION OVER TIME")
        print("=" * 80)

        durations = {
            '1 hour': 3600,
            '6 hours': 6 * 3600,
            '1 day': 24 * 3600,
            '3 days': 3 * 24 * 3600,
            '1 week': 7 * 24 * 3600,
            '2 weeks': 14 * 24 * 3600
        }

        charge_levels = [1.0, 3.0, 5.0]  # Coulombs
        chaser_masses = [10.0, 25.0]  # kg
        altitude = 600  # km
        shell_separation = 2.0  # meters

        results = {
            'durations': list(durations.keys()),
            'duration_seconds': list(durations.values()),
            'data': {}
        }

        # Calculate force at nominal conditions
        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])

        actuator = VariableSeparationLorentzActuator(num_shells=6, shell_separation=shell_separation)

        for mass in chaser_masses:
            for q in charge_levels:
                key = f'{int(mass)}kg_{int(q)}C'

                shell_charges = np.ones(6) * q
                F_net, F_mag = actuator.compute_net_force(shell_charges, velocity, position)
                acceleration = F_mag / mass  # m/s²

                results['data'][key] = {
                    'force': F_mag,
                    'acceleration': acceleration,
                    'delta_v_m_s': [],
                    'delta_v_km_s': []
                }

                print(f"\n--- {mass} kg chaser, {q} C per shell ---")
                print(f"  Constant force: {F_mag:.4f} N")
                print(f"  Constant acceleration: {acceleration:.6f} m/s²")

                for duration_name, duration_s in durations.items():
                    delta_v = acceleration * duration_s  # m/s

                    results['data'][key]['delta_v_m_s'].append(delta_v)
                    results['data'][key]['delta_v_km_s'].append(delta_v / 1000.0)

                    print(f"  After {duration_name:10s}: Δv = {delta_v:8.2f} m/s = {delta_v/1000:.4f} km/s")

        self.results['test_4'] = results
        return results

    def test_5_optimal_configuration(self):
        """Test Case 5: Find optimal configuration for maximum performance"""
        print("\n" + "=" * 80)
        print("TEST CASE 5: OPTIMAL CONFIGURATION FINDER")
        print("=" * 80)

        separations = np.array([0.5, 1.0, 2.0, 3.0, 5.0])  # meters
        charge_levels = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Coulombs
        altitude = 600  # km

        position = np.array([R_EARTH + altitude, 0, 0])
        v_mag = orbital_velocity(altitude)
        velocity = np.array([0, v_mag, 0])

        results = {
            'separations': separations.tolist(),
            'charges': charge_levels.tolist(),
            'max_force_config': {},
            'max_torque_config': {},
            'force_matrix': [],
            'torque_matrix': []
        }

        max_force = 0
        max_force_config = {}
        max_torque = 0
        max_torque_config = {}

        print("\nSearching for optimal configuration...")
        print("(Separation x Charge grid search)\n")

        force_matrix = np.zeros((len(separations), len(charge_levels)))
        torque_matrix = np.zeros((len(separations), len(charge_levels)))

        for i, sep in enumerate(separations):
            actuator = VariableSeparationLorentzActuator(num_shells=6, shell_separation=sep)

            for j, q in enumerate(charge_levels):
                # Force test (all shells same charge)
                shell_charges_force = np.ones(6) * q
                F_net, F_mag = actuator.compute_net_force(shell_charges_force, velocity, position)

                # Torque test (opposing charges)
                shell_charges_torque = np.array([q, -q, 0, 0, 0, 0])
                tau_net, tau_mag = actuator.compute_torque(shell_charges_torque, velocity, position)

                force_matrix[i, j] = F_mag
                torque_matrix[i, j] = tau_mag

                if F_mag > max_force:
                    max_force = F_mag
                    max_force_config = {
                        'separation': sep,
                        'charge': q,
                        'force': F_mag,
                        'accel_10kg': F_mag / 10.0,
                        'accel_25kg': F_mag / 25.0
                    }

                if tau_mag > max_torque:
                    max_torque = tau_mag
                    max_torque_config = {
                        'separation': sep,
                        'charge': q,
                        'torque': tau_mag
                    }

        results['force_matrix'] = force_matrix.tolist()
        results['torque_matrix'] = torque_matrix.tolist()
        results['max_force_config'] = max_force_config
        results['max_torque_config'] = max_torque_config

        print("OPTIMAL FORCE CONFIGURATION:")
        print(f"  Separation: {max_force_config['separation']} m")
        print(f"  Charge: {max_force_config['charge']} C")
        print(f"  Max Force: {max_force_config['force']:.4f} N")
        print(f"  Acceleration (10kg): {max_force_config['accel_10kg']:.6f} m/s²")
        print(f"  Acceleration (25kg): {max_force_config['accel_25kg']:.6f} m/s²")

        print("\nOPTIMAL TORQUE CONFIGURATION:")
        print(f"  Separation: {max_torque_config['separation']} m")
        print(f"  Charge: {max_torque_config['charge']} C")
        print(f"  Max Torque: {max_torque_config['torque']:.6f} N·m")

        self.results['test_5'] = results
        return results

    def test_6_energy_requirements(self):
        """Test Case 6: Energy requirements for high-charge system"""
        print("\n" + "=" * 80)
        print("TEST CASE 6: ENERGY REQUIREMENTS")
        print("=" * 80)

        charge_levels = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Coulombs
        capacitance = 1e-3  # 1 mF (millifarad) - realistic for high-charge systems
        voltage_levels = []

        results = {
            'charge_levels': charge_levels.tolist(),
            'capacitance': capacitance,
            'voltages': [],
            'energy_per_shell': [],
            'total_energy_6_shells': [],
            'power_for_1hr_charge': []
        }

        print(f"Capacitance: {capacitance*1000:.1f} mF\n")

        for q in charge_levels:
            # V = Q/C
            voltage = q / capacitance  # Volts

            # E = Q²/(2C) = ½CV²
            energy_per_shell = (q**2) / (2 * capacitance)  # Joules
            total_energy = energy_per_shell * 6  # 6 shells

            # Power to charge in 1 hour
            charge_time = 3600  # seconds (1 hour)
            power = total_energy / charge_time  # Watts

            results['voltages'].append(voltage)
            results['energy_per_shell'].append(energy_per_shell)
            results['total_energy_6_shells'].append(total_energy)
            results['power_for_1hr_charge'].append(power)

            print(f"Charge: {q:.1f} C")
            print(f"  Voltage: {voltage:.0f} V = {voltage/1000:.1f} kV")
            print(f"  Energy per shell: {energy_per_shell:.2f} J")
            print(f"  Total energy (6 shells): {total_energy:.2f} J = {total_energy/1000:.3f} kJ")
            print(f"  Power (1hr charge): {power:.2f} W")
            print()

        # Compare to available energy budget
        available_energy = 500e6  # 500 MJ from config
        max_energy = max(results['total_energy_6_shells'])

        print(f"Available energy budget: {available_energy/1e6:.0f} MJ")
        print(f"Maximum energy used: {max_energy:.2f} J = {max_energy/1e6:.6f} MJ")
        print(f"Energy margin: {(available_energy - max_energy)/available_energy * 100:.6f}%")
        print(f"Number of charge cycles possible: {int(available_energy / max_energy):,}")

        self.results['test_6'] = results
        return results

    def save_results(self, filename='high_charge_variable_separation_results.json'):
        """Save all test results to JSON file"""
        filepath = os.path.join(RESULTS_DIR, filename)

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{'='*80}")
        print(f"Results saved to: {filepath}")
        print(f"{'='*80}")

    def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "█" * 80)
        print(" " * 20 + "HIGH-CHARGE MAGNETO-COULOMBIC ANALYSIS")
        print(" " * 15 + "10kg & 25kg Chasers | 1-5 C/shell | Variable Separation")
        print(" " * 25 + "IIT Kanpur Research Hackathon 2025")
        print("█" * 80)

        self.test_1_force_vs_charge()
        self.test_2_torque_vs_separation()
        self.test_3_acceleration_comparison()
        self.test_4_delta_v_accumulation()
        self.test_5_optimal_configuration()
        self.test_6_energy_requirements()

        print("\n" + "=" * 80)
        print("ALL TEST CASES COMPLETE")
        print("=" * 80)

        self.save_results()


if __name__ == "__main__":
    suite = HighChargeTestSuite()
    suite.run_all_tests()
