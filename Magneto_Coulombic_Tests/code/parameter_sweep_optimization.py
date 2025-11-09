#!/usr/bin/env python3
"""
Parameter Sweep Optimization for Magneto-Coulombic ADR Mission
Tests various parameter combinations to reduce mission time
"""

import numpy as np
import json
from pathlib import Path
from lorentz_force_physics import LorentzForceActuator, EarthMagneticField, orbital_velocity, R_EARTH

class ParameterSweepOptimizer:
    def __init__(self):
        self.actuator = LorentzForceActuator()
        self.earth_field = EarthMagneticField()

    def calculate_mission_time(self, force_N, mass_kg, delta_v_ms):
        """
        Calculate mission time given force, mass, and required delta-v

        Using: a = F/m, Δv = a·t → t = Δv/a = Δv·m/F

        Returns time in days
        """
        if force_N <= 0:
            return np.inf

        acceleration = force_N / mass_kg  # m/s²
        time_seconds = delta_v_ms / acceleration
        time_days = time_seconds / (24 * 3600)

        return time_days

    def calculate_energy_requirement(self, charge_C, n_shells, voltage_V=50000, capacitance_F=1e-6):
        """
        Calculate energy required to charge all shells
        E = Q²/(2C) per shell
        """
        energy_per_shell = (charge_C ** 2) / (2 * capacitance_F)
        total_energy = energy_per_shell * n_shells
        return total_energy

    def calculate_force_at_altitude(self, altitude_km, charge_C, n_shells):
        """Calculate total Lorentz force at given altitude with given charge"""
        # Position and velocity
        position_km = np.array([R_EARTH + altitude_km, 0, 0])
        v_mag = orbital_velocity(altitude_km)  # km/s
        velocity_km_s = np.array([0, v_mag, 0])  # circular orbit

        # Create actuator with specified shells
        actuator = LorentzForceActuator(num_shells=n_shells, max_charge=charge_C)

        # Charge all shells identically for net force
        shell_charges = np.ones(n_shells) * charge_C

        # Compute net force
        F_net, F_mag = actuator.compute_net_force(shell_charges, velocity_km_s, position_km)

        return F_mag

    def sweep_charge_levels(self):
        """Test 1: High charge levels (10-1000 μC)"""
        print("\n" + "="*80)
        print("TEST 1: HIGH CHARGE LEVEL SWEEP")
        print("="*80)

        altitude_km = 400  # Use optimal altitude
        mass_kg = 1270  # Current baseline
        n_shells = 6

        charge_levels_uC = [10, 50, 100, 500, 1000]
        results = []

        for charge_uC in charge_levels_uC:
            charge_C = charge_uC * 1e-6

            # Total force from all shells
            total_force = self.calculate_force_at_altitude(altitude_km, charge_C, n_shells)

            # Calculate mission times
            approach_time = self.calculate_mission_time(total_force, mass_kg, 0.004)  # 4 mm/s
            rendezvous_time = self.calculate_mission_time(total_force, mass_kg, 1.0)  # 1 m/s
            deorbit_time = self.calculate_mission_time(total_force, mass_kg, 100.0)  # 100 m/s
            total_mission_time = approach_time + rendezvous_time + deorbit_time

            # Energy requirement
            energy_J = self.calculate_energy_requirement(charge_C, n_shells)

            result = {
                'charge_uC': charge_uC,
                'n_shells': n_shells,
                'mass_kg': mass_kg,
                'altitude_km': altitude_km,
                'force_uN': total_force * 1e6,
                'acceleration_nm_s2': (total_force / mass_kg) * 1e9,
                'approach_days': approach_time,
                'rendezvous_days': rendezvous_time,
                'deorbit_days': deorbit_time,
                'total_mission_days': total_mission_time,
                'total_mission_years': total_mission_time / 365.25,
                'energy_J': energy_J,
                'energy_margin': (500e6 - energy_J) / 500e6 * 100  # % of 500 MJ budget
            }
            results.append(result)

            print(f"\nCharge: {charge_uC} μC")
            print(f"  Force: {result['force_uN']:.2f} μN")
            print(f"  Acceleration: {result['acceleration_nm_s2']:.2f} nm/s²")
            print(f"  Approach: {approach_time:.2f} days")
            print(f"  Rendezvous: {rendezvous_time:.2f} days ({rendezvous_time/365.25:.2f} years)")
            print(f"  Deorbit: {deorbit_time:.2f} days ({deorbit_time/365.25:.2f} years)")
            print(f"  TOTAL: {total_mission_time/365.25:.2f} years")
            print(f"  Energy: {energy_J:.3f} J (margin: {result['energy_margin']:.6f}%)")

        return results

    def sweep_shell_configurations(self):
        """Test 2: Multiple shell configurations (12-100 shells)"""
        print("\n" + "="*80)
        print("TEST 2: MULTI-SHELL CONFIGURATION SWEEP")
        print("="*80)

        altitude_km = 400
        mass_kg = 1270
        charge_uC = 100  # Moderate charge
        charge_C = charge_uC * 1e-6

        n_shells_list = [12, 24, 48, 100]
        results = []

        for n_shells in n_shells_list:
            total_force = self.calculate_force_at_altitude(altitude_km, charge_C, n_shells)

            approach_time = self.calculate_mission_time(total_force, mass_kg, 0.004)
            rendezvous_time = self.calculate_mission_time(total_force, mass_kg, 1.0)
            deorbit_time = self.calculate_mission_time(total_force, mass_kg, 100.0)
            total_mission_time = approach_time + rendezvous_time + deorbit_time

            energy_J = self.calculate_energy_requirement(charge_C, n_shells)

            result = {
                'charge_uC': charge_uC,
                'n_shells': n_shells,
                'mass_kg': mass_kg,
                'altitude_km': altitude_km,
                'force_uN': total_force * 1e6,
                'acceleration_nm_s2': (total_force / mass_kg) * 1e9,
                'approach_days': approach_time,
                'rendezvous_days': rendezvous_time,
                'deorbit_days': deorbit_time,
                'total_mission_days': total_mission_time,
                'total_mission_years': total_mission_time / 365.25,
                'energy_J': energy_J,
                'energy_margin': (500e6 - energy_J) / 500e6 * 100
            }
            results.append(result)

            print(f"\nShells: {n_shells}")
            print(f"  Force: {result['force_uN']:.2f} μN")
            print(f"  Acceleration: {result['acceleration_nm_s2']:.2f} nm/s²")
            print(f"  TOTAL: {total_mission_time/365.25:.2f} years")
            print(f"  Energy: {energy_J:.3f} J (margin: {result['energy_margin']:.6f}%)")

        return results

    def sweep_lightweight_spacecraft(self):
        """Test 3: Very lightweight spacecraft (10-100 kg)"""
        print("\n" + "="*80)
        print("TEST 3: VERY LIGHTWEIGHT SPACECRAFT SWEEP (10-100 kg)")
        print("="*80)

        altitude_km = 400
        charge_uC = 100
        charge_C = charge_uC * 1e-6
        n_shells = 24  # More shells for lightweight design

        mass_list_kg = [10, 25, 50, 75, 100]
        results = []

        for mass_kg in mass_list_kg:
            total_force = self.calculate_force_at_altitude(altitude_km, charge_C, n_shells)

            approach_time = self.calculate_mission_time(total_force, mass_kg, 0.004)
            rendezvous_time = self.calculate_mission_time(total_force, mass_kg, 1.0)
            deorbit_time = self.calculate_mission_time(total_force, mass_kg, 100.0)
            total_mission_time = approach_time + rendezvous_time + deorbit_time

            energy_J = self.calculate_energy_requirement(charge_C, n_shells)

            result = {
                'charge_uC': charge_uC,
                'n_shells': n_shells,
                'mass_kg': mass_kg,
                'altitude_km': altitude_km,
                'force_uN': total_force * 1e6,
                'acceleration_nm_s2': (total_force / mass_kg) * 1e9,
                'approach_days': approach_time,
                'rendezvous_days': rendezvous_time,
                'deorbit_days': deorbit_time,
                'total_mission_days': total_mission_time,
                'total_mission_years': total_mission_time / 365.25,
                'energy_J': energy_J,
                'energy_margin': (500e6 - energy_J) / 500e6 * 100
            }
            results.append(result)

            print(f"\nMass: {mass_kg} kg")
            print(f"  Force: {result['force_uN']:.2f} μN")
            print(f"  Acceleration: {result['acceleration_nm_s2']:.2f} nm/s²")
            print(f"  Approach: {approach_time:.2f} days")
            print(f"  Rendezvous: {rendezvous_time:.2f} days ({rendezvous_time/365.25:.2f} years)")
            print(f"  Deorbit: {deorbit_time:.2f} days ({deorbit_time/365.25:.2f} years)")
            print(f"  TOTAL: {total_mission_time/365.25:.2f} years")
            print(f"  Energy: {energy_J:.3f} J")

        return results

    def sweep_low_altitudes(self):
        """Test 4: Low altitude operations (200-350 km)"""
        print("\n" + "="*80)
        print("TEST 4: LOW ALTITUDE SWEEP (200-350 km)")
        print("="*80)

        mass_kg = 50  # Lightweight design
        charge_uC = 100
        charge_C = charge_uC * 1e-6
        n_shells = 24

        altitude_list_km = [200, 250, 300, 350, 400]
        results = []

        for altitude_km in altitude_list_km:
            total_force = self.calculate_force_at_altitude(altitude_km, charge_C, n_shells)

            approach_time = self.calculate_mission_time(total_force, mass_kg, 0.004)
            rendezvous_time = self.calculate_mission_time(total_force, mass_kg, 1.0)
            deorbit_time = self.calculate_mission_time(total_force, mass_kg, 100.0)
            total_mission_time = approach_time + rendezvous_time + deorbit_time

            # Get B-field strength
            position = np.array([altitude_km + 6371, 0, 0])
            b_field = self.earth_field.get_field(position)
            b_magnitude = np.linalg.norm(b_field) * 1e6  # Convert to μT

            energy_J = self.calculate_energy_requirement(charge_C, n_shells)

            result = {
                'charge_uC': charge_uC,
                'n_shells': n_shells,
                'mass_kg': mass_kg,
                'altitude_km': altitude_km,
                'b_field_uT': b_magnitude,
                'force_uN': total_force * 1e6,
                'acceleration_nm_s2': (total_force / mass_kg) * 1e9,
                'approach_days': approach_time,
                'rendezvous_days': rendezvous_time,
                'deorbit_days': deorbit_time,
                'total_mission_days': total_mission_time,
                'total_mission_years': total_mission_time / 365.25,
                'energy_J': energy_J,
                'energy_margin': (500e6 - energy_J) / 500e6 * 100
            }
            results.append(result)

            print(f"\nAltitude: {altitude_km} km")
            print(f"  B-field: {b_magnitude:.2f} μT")
            print(f"  Force: {result['force_uN']:.2f} μN")
            print(f"  Acceleration: {result['acceleration_nm_s2']:.2f} nm/s²")
            print(f"  TOTAL: {total_mission_time/365.25:.2f} years")

        return results

    def find_optimal_configuration(self):
        """Test 5: Optimal combined configuration"""
        print("\n" + "="*80)
        print("TEST 5: OPTIMAL COMBINED CONFIGURATION SEARCH")
        print("="*80)

        best_result = None
        best_time = np.inf

        # Parameter ranges
        charge_levels = [100, 500, 1000]  # μC
        n_shells_list = [24, 48, 100]
        mass_list = [10, 25, 50]  # kg
        altitude_list = [200, 250, 300]  # km

        all_results = []

        for charge_uC in charge_levels:
            charge_C = charge_uC * 1e-6
            for n_shells in n_shells_list:
                for mass_kg in mass_list:
                    for altitude_km in altitude_list:
                        total_force = self.calculate_force_at_altitude(altitude_km, charge_C, n_shells)

                        approach_time = self.calculate_mission_time(total_force, mass_kg, 0.004)
                        rendezvous_time = self.calculate_mission_time(total_force, mass_kg, 1.0)
                        deorbit_time = self.calculate_mission_time(total_force, mass_kg, 100.0)
                        total_mission_time = approach_time + rendezvous_time + deorbit_time

                        energy_J = self.calculate_energy_requirement(charge_C, n_shells)

                        # Check energy constraint
                        if energy_J > 500e6:
                            continue  # Skip if exceeds energy budget

                        result = {
                            'charge_uC': charge_uC,
                            'n_shells': n_shells,
                            'mass_kg': mass_kg,
                            'altitude_km': altitude_km,
                            'force_uN': total_force * 1e6,
                            'acceleration_nm_s2': (total_force / mass_kg) * 1e9,
                            'approach_days': approach_time,
                            'rendezvous_days': rendezvous_time,
                            'deorbit_days': deorbit_time,
                            'total_mission_days': total_mission_time,
                            'total_mission_years': total_mission_time / 365.25,
                            'energy_J': energy_J,
                            'energy_margin': (500e6 - energy_J) / 500e6 * 100
                        }

                        all_results.append(result)

                        if total_mission_time < best_time:
                            best_time = total_mission_time
                            best_result = result

        print(f"\n{'='*80}")
        print("OPTIMAL CONFIGURATION FOUND:")
        print(f"{'='*80}")
        print(f"  Charge: {best_result['charge_uC']} μC per shell")
        print(f"  Number of shells: {best_result['n_shells']}")
        print(f"  Spacecraft mass: {best_result['mass_kg']} kg")
        print(f"  Altitude: {best_result['altitude_km']} km")
        print(f"  Total force: {best_result['force_uN']:.2f} μN")
        print(f"  Acceleration: {best_result['acceleration_nm_s2']:.2f} nm/s²")
        print(f"  Approach: {best_result['approach_days']:.2f} days")
        print(f"  Rendezvous: {best_result['rendezvous_days']:.2f} days ({best_result['rendezvous_days']/365.25:.2f} years)")
        print(f"  Deorbit: {best_result['deorbit_days']:.2f} days ({best_result['deorbit_days']/365.25:.2f} years)")
        print(f"  TOTAL MISSION: {best_result['total_mission_years']:.2f} years")
        print(f"  Energy: {best_result['energy_J']:.3f} J (margin: {best_result['energy_margin']:.6f}%)")

        # Sort all results by mission time
        all_results.sort(key=lambda x: x['total_mission_days'])

        print(f"\nTop 10 configurations:")
        print("-" * 120)
        print(f"{'Rank':<6} {'Charge':<10} {'Shells':<8} {'Mass':<8} {'Alt':<8} {'Force':<12} {'Accel':<15} {'Mission Time':<15}")
        print(f"{'':>6} {'(μC)':<10} {'(#)':<8} {'(kg)':<8} {'(km)':<8} {'(μN)':<12} {'(nm/s²)':<15} {'(years)':<15}")
        print("-" * 120)
        for i, res in enumerate(all_results[:10], 1):
            print(f"{i:<6} {res['charge_uC']:<10.0f} {res['n_shells']:<8} {res['mass_kg']:<8} {res['altitude_km']:<8} "
                  f"{res['force_uN']:<12.2f} {res['acceleration_nm_s2']:<15.2f} {res['total_mission_years']:<15.2f}")

        return best_result, all_results


def main():
    optimizer = ParameterSweepOptimizer()

    # Run all parameter sweeps
    results_charge = optimizer.sweep_charge_levels()
    results_shells = optimizer.sweep_shell_configurations()
    results_mass = optimizer.sweep_lightweight_spacecraft()
    results_altitude = optimizer.sweep_low_altitudes()
    best_config, all_configs = optimizer.find_optimal_configuration()

    # Save all results
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)

    results_summary = {
        'charge_sweep': results_charge,
        'shell_sweep': results_shells,
        'mass_sweep': results_mass,
        'altitude_sweep': results_altitude,
        'optimal_configuration': best_config,
        'all_configurations': all_configs
    }

    output_file = output_dir / "parameter_sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")

    # Summary comparison: baseline vs optimal
    print(f"\n{'='*80}")
    print("BASELINE vs OPTIMAL COMPARISON")
    print(f"{'='*80}")

    baseline_force = 1.07e-6 * 6  # 6 shells, 1 μC each, 600 km
    baseline_mass = 1270
    baseline_accel = baseline_force / baseline_mass
    baseline_mission_time = 113223  # years (from previous results)

    optimal_force = best_config['force_uN'] * 1e-6
    optimal_mass = best_config['mass_kg']
    optimal_accel = optimal_force / optimal_mass
    optimal_mission_time = best_config['total_mission_years']

    improvement_factor = baseline_mission_time / optimal_mission_time

    print(f"\nBASELINE (1270 kg, 6 shells, 1 μC, 600 km):")
    print(f"  Force: {baseline_force*1e6:.2f} μN")
    print(f"  Acceleration: {baseline_accel*1e9:.2f} nm/s²")
    print(f"  Mission time: {baseline_mission_time:.0f} years")

    print(f"\nOPTIMAL ({best_config['mass_kg']} kg, {best_config['n_shells']} shells, "
          f"{best_config['charge_uC']} μC, {best_config['altitude_km']} km):")
    print(f"  Force: {optimal_force*1e6:.2f} μN")
    print(f"  Acceleration: {optimal_accel*1e9:.2f} nm/s²")
    print(f"  Mission time: {optimal_mission_time:.2f} years")

    print(f"\nIMPROVEMENT:")
    print(f"  Force increase: {(optimal_force/baseline_force):.1f}x")
    print(f"  Acceleration increase: {(optimal_accel/baseline_accel):.1f}x")
    print(f"  Mission time reduction: {improvement_factor:.1f}x faster")
    print(f"  Time saved: {baseline_mission_time - optimal_mission_time:.0f} years")

    # Feasibility assessment
    print(f"\n{'='*80}")
    print("FEASIBILITY ASSESSMENT")
    print(f"{'='*80}")

    if optimal_mission_time > 10:
        print(f"❌ Still INFEASIBLE: {optimal_mission_time:.2f} years is too long")
        print(f"   Target: ~0.1 years (1-2 months)")
        print(f"   Gap: {optimal_mission_time/0.1:.0f}x too slow")
    elif optimal_mission_time > 1:
        print(f"⚠️  MARGINAL: {optimal_mission_time:.2f} years (~{optimal_mission_time*12:.0f} months)")
        print(f"   May be viable for non-critical missions")
    else:
        print(f"✓ FEASIBLE: {optimal_mission_time:.2f} years (~{optimal_mission_time*12:.0f} months)")
        print(f"   Within reasonable mission duration")


if __name__ == "__main__":
    main()
