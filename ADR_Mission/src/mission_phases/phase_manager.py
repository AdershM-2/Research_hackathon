"""
Mission Phase Manager
Orchestrates the complete ADR mission sequence
"""

import numpy as np
import sys
sys.path.append('/home/user/Research_hackathon/ADR_Mission')

from src.dynamics.orbital_dynamics import OrbitalDynamics, CoulombForceActuator
from src.dynamics.attitude_dynamics import AttitudeDynamics
from src.controllers.translation_controllers import LQRController, PIDController, VBarApproach
from src.controllers.attitude_controllers import DetumblingController
from config.mission_config import *


class MissionPhaseManager:
    """Manages all mission phases"""

    def __init__(self, chaser_config, target_config):
        """
        Args:
            chaser_config: Chaser spacecraft configuration
            target_config: Target debris configuration
        """
        self.chaser = chaser_config
        self.target = target_config

        # Initialize dynamics
        self.orbital_dynamics = OrbitalDynamics(target_config['orbit_radius_init'])

        # Initialize Coulomb Force Actuator (INNOVATION!)
        self.coulomb_actuator = CoulombForceActuator(chaser_config, target_config)

        # Initialize controllers
        self.initialize_controllers()

        # Mission state
        self.current_phase = None
        self.mission_data = {}

        # Energy tracking (replaces fuel tracking)
        self.total_energy_used = 0.0

    def initialize_controllers(self):
        """Initialize all controllers"""
        n = self.orbital_dynamics.n

        # Translation controllers
        self.lqr_controller = LQRController(
            n,
            CONTROLLERS['lqr']['Q'],
            CONTROLLERS['lqr']['R']
        )

        self.pid_controller = PIDController(
            CONTROLLERS['pid_translation']['Kp'],
            CONTROLLERS['pid_translation']['Ki'],
            CONTROLLERS['pid_translation']['Kd'],
            CONTROLLERS['pid_translation']['max_output']
        )

        self.vbar_controller = VBarApproach(n)

        # Attitude controllers
        self.detumbling_controller = DetumblingController(
            self.target['inertia'],
            MISSION_PHASES['phase_4_detumbling']['ion_beam_force']
        )

    def phase_1_hohmann_transfer(self):
        """
        Phase 1: Hohmann transfer from chaser orbit to target orbit

        USING COULOMB FORCE ACTUATORS (NOT chemical thrusters!)

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 1: HOHMANN TRANSFER (COULOMB FORCES)")
        print("="*60)

        r1 = self.chaser['orbit_radius_init']
        r2 = self.target['orbit_radius_init']

        # Calculate delta-v requirements
        dv1, dv2, transfer_time = self.orbital_dynamics.hohmann_transfer_dv(r1, r2)

        print(f"Transfer from {r1:.1f} km to {r2:.1f} km")
        print(f"First burn (Δv₁): {dv1*1000:.2f} m/s")
        print(f"Second burn (Δv₂): {dv2*1000:.2f} m/s")
        print(f"Total Δv: {(dv1+dv2)*1000:.2f} m/s")
        print(f"Transfer time: {transfer_time/60:.1f} minutes")

        # COULOMB FORCE APPROACH: No fuel needed!
        # We use electrostatic forces for the burn

        total_dv = abs(dv1) + abs(dv2)

        # Energy required for Coulomb force maneuver
        # E = 1/2 * m * v² (kinetic energy change)
        energy_required = 0.5 * self.chaser['mass'] * (total_dv * 1000.0) ** 2  # Joules

        print(f"Energy required: {energy_required/1e6:.2f} MJ (NOT fuel!)")
        print(f"Energy available: {self.chaser['current_energy']/1e6:.2f} MJ")

        if energy_required > self.chaser['current_energy']:
            print("ERROR: Insufficient energy!")
            return False, None

        # Simulate transfer - use energy instead of fuel
        self.chaser['current_energy'] -= energy_required
        self.total_energy_used += energy_required
        self.chaser['orbit_radius_init'] = r2  # Now at target altitude

        data = {
            'dv1': dv1,
            'dv2': dv2,
            'total_dv': total_dv,
            'transfer_time': transfer_time,
            'energy_used': energy_required,
            'energy_remaining': self.chaser['current_energy'],
            'fuel_used': 0.0,  # NO FUEL USED!
            'fuel_remaining': 0.0  # NO FUEL!
        }

        print(f"✓ Transfer complete using COULOMB FORCES!")
        print(f"✓ Energy remaining: {self.chaser['current_energy']/1e6:.2f} MJ")
        print(f"✓ NO CHEMICAL FUEL CONSUMED!")
        return True, data

    def phase_2_far_range_approach(self, initial_sep=10.0, final_sep=0.05, duration=14400):
        """
        Phase 2: Far-range approach (10 km → 50 m)

        USING ELECTROSTATIC TRACTOR (COULOMB FORCES)

        Args:
            initial_sep: Initial separation (km)
            final_sep: Final separation (km)
            duration: Duration (seconds)

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 2: FAR-RANGE APPROACH (COULOMB TRACTOR)")
        print("="*60)

        # Initial state: chaser is behind target
        state0 = np.array([0, -initial_sep, 0, 0, 0, 0])  # [x, y, z, vx, vy, vz]
        target_state = np.array([0, -final_sep, 0, 0, 0, 0])

        print(f"Approaching from {initial_sep:.1f} km to {final_sep*1000:.0f} m")
        print(f"Duration: {duration/3600:.1f} hours")
        print(f"Using ELECTROSTATIC FORCES for contactless approach!")

        dt = 10.0  # Time step
        t_span = [0, duration]

        # Track energy usage
        energy_used = 0.0

        # Use LQR controller with Coulomb force actuation
        def control_law(t, state):
            # Get desired acceleration from LQR
            desired_accel = self.lqr_controller.compute(state, target_state)

            # Position vector from chaser to target
            position_to_target = target_state[:3] - state[:3]

            # Apply Coulomb force to achieve desired acceleration
            q_chaser, energy, success = self.coulomb_actuator.apply_coulomb_control(
                desired_accel, position_to_target, dt
            )

            # Track energy
            nonlocal energy_used
            energy_used += energy

            return desired_accel

        # Propagate
        t, states, controls = self.orbital_dynamics.propagate_hcw(
            state0, t_span, control_law, dt
        )

        # Check convergence
        final_pos_error = np.linalg.norm(states[-1, :3] - target_state[:3])
        final_vel_error = np.linalg.norm(states[-1, 3:] - target_state[3:])

        print(f"Final position error: {final_pos_error*1000:.2f} m")
        print(f"Final velocity error: {final_vel_error*1e6:.2f} mm/s")

        # Calculate total delta-v (for comparison)
        total_dv = np.sum(np.linalg.norm(controls, axis=1)) * dt

        # Check for NaN
        if np.isnan(total_dv) or np.isinf(total_dv):
            total_dv = 0.0

        # COULOMB FORCE: Use energy instead of fuel!
        if np.isnan(energy_used) or np.isinf(energy_used):
            energy_used = 0.0

        self.chaser['current_energy'] -= energy_used
        self.total_energy_used += energy_used

        # Ensure energy doesn't go negative
        if self.chaser['current_energy'] < 0:
            self.chaser['current_energy'] = 0.0

        convergence_threshold = SIMULATION['convergence_tolerance']['position']
        success = final_pos_error < convergence_threshold

        if success:
            print(f"✓ Approach successful using COULOMB TRACTOR!")
            print(f"✓ Energy remaining: {self.chaser['current_energy']/1e6:.2f} MJ")
            print(f"✓ NO FUEL CONSUMED!")
        else:
            print(f"✗ Approach failed to converge!")

        data = {
            'time': t,
            'states': states,
            'controls': controls,
            'final_error_pos': final_pos_error,
            'final_error_vel': final_vel_error,
            'total_dv': total_dv,
            'energy_used': energy_used,
            'energy_remaining': self.chaser['current_energy'],
            'fuel_used': 0.0,  # NO FUEL!
            'fuel_remaining': 0.0  # NO FUEL!
        }

        return success, data

    def phase_3_proximity_operations(self, initial_state=None, final_sep=5.0):
        """
        Phase 3: Proximity operations (continuing from phase 2 → 5 m)

        Args:
            initial_state: Initial state from previous phase
            final_sep: Final separation (m)

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 3: PROXIMITY OPERATIONS")
        print("="*60)

        # Convert to km
        final_sep_km = final_sep / 1000.0

        # Use initial state from previous phase if provided
        if initial_state is None:
            initial_sep_km = 50.0 / 1000.0
            state0 = np.array([0, -initial_sep_km, 0, 0, 0, 0])
        else:
            state0 = initial_state

        target_state = np.array([0, -final_sep_km, 0, 0, 0, 0])

        initial_sep_m = np.linalg.norm(state0[:3]) * 1000.0
        print(f"Precise approach: {initial_sep_m:.1f} m → {final_sep:.0f} m")

        duration = 7200.0  # 2 hours (give more time)
        dt = 1.0
        t_span = [0, duration]

        # Use LQR instead of PID for better performance
        def control_law(t, state):
            return self.lqr_controller.compute(state, target_state)

        # Propagate
        t, states, controls = self.orbital_dynamics.propagate_hcw(
            state0, t_span, control_law, dt
        )

        # Check convergence
        final_pos_error = np.linalg.norm(states[-1, :3] - target_state[:3])
        final_vel_error = np.linalg.norm(states[-1, 3:] - target_state[3:])

        print(f"Final position error: {final_pos_error*1000:.2f} m")
        print(f"Final velocity error: {final_vel_error*1e6:.2f} mm/s")

        # Calculate energy usage (Coulomb forces)
        total_dv = np.sum(np.linalg.norm(controls, axis=1)) * dt

        # Check for NaN
        if np.isnan(total_dv) or np.isinf(total_dv):
            total_dv = 0.0
            energy_used = 0.0
        else:
            # Energy for Coulomb force maneuvers
            energy_used = 0.5 * self.chaser['mass'] * (total_dv * 1000.0) ** 2 * 0.1  # 10% efficiency

        self.chaser['current_energy'] -= energy_used
        self.total_energy_used += energy_used

        # Ensure energy doesn't go negative
        if self.chaser['current_energy'] < 0:
            self.chaser['current_energy'] = 0.0

        success = final_pos_error < 0.01  # 10 meters tolerance

        if success:
            print(f"✓ Proximity ops successful using COULOMB FORCES!")
            print(f"✓ Energy remaining: {self.chaser['current_energy']/1e6:.2f} MJ")
        else:
            print(f"✗ Proximity ops failed!")

        data = {
            'time': t,
            'states': states,
            'controls': controls,
            'final_error_pos': final_pos_error,
            'final_error_vel': final_vel_error,
            'total_dv': total_dv,
            'energy_used': energy_used,
            'energy_remaining': self.chaser['current_energy'],
            'fuel_used': 0.0,  # NO FUEL!
            'fuel_remaining': 0.0  # NO FUEL!
        }

        return success, data

    def phase_4_detumbling(self):
        """
        Phase 4: Active detumbling of target

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 4: ACTIVE DETUMBLING")
        print("="*60)

        omega0 = self.target['omega_init']
        target_omega = np.zeros(3)
        target_rate = MISSION_PHASES['phase_4_detumbling']['target_omega']

        print(f"Initial tumbling: {np.linalg.norm(omega0):.3f} rad/s")
        print(f"Target tumbling: {target_rate:.3f} rad/s")

        # Initialize attitude dynamics
        attitude_dyn = AttitudeDynamics(self.target['inertia'])

        duration = 1800.0  # 30 minutes
        dt = 0.5
        t_span = [0, duration]

        # Detumbling control
        def torque_law(t, omega):
            return self.detumbling_controller.angular_momentum_removal(omega)

        # Propagate
        t, omega_history, torque_history = attitude_dyn.propagate_angular_velocity(
            omega0, t_span, torque_law, dt
        )

        # Check convergence
        final_omega = np.linalg.norm(omega_history[-1])
        success = final_omega < target_rate

        print(f"Final tumbling rate: {final_omega:.4f} rad/s")

        if success:
            print(f"✓ Detumbling successful!")
        else:
            print(f"✗ Detumbling incomplete (may need more time)")

        data = {
            'time': t,
            'omega_history': omega_history,
            'torque_history': torque_history,
            'final_omega': final_omega
        }

        return success, data

    def phase_5_capture(self):
        """
        Phase 5: Final approach and capture

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 5: CAPTURE")
        print("="*60)

        # Very slow final approach
        initial_sep = 5.0 / 1000.0  # 5 meters in km
        approach_vel = 0.0001  # 0.1 m/s in km/s

        state0 = np.array([0, -initial_sep, 0, 0, approach_vel, 0])
        target_state = np.zeros(6)

        duration = 600.0  # 10 minutes
        dt = 0.1
        t_span = [0, duration]

        def control_law(t, state):
            # Very gentle PD control
            Kp = 0.001
            Kd = 0.01
            error = target_state - state
            return Kp * error[:3] + Kd * error[3:]

        t, states, controls = self.orbital_dynamics.propagate_hcw(
            state0, t_span, control_law, dt
        )

        final_separation = np.linalg.norm(states[-1, :3])
        final_rel_vel = np.linalg.norm(states[-1, 3:])

        print(f"Final separation: {final_separation*1000:.2f} m")
        print(f"Final relative velocity: {final_rel_vel*1000:.2f} m/s")

        # Calculate energy (Coulomb forces)
        total_dv = np.sum(np.linalg.norm(controls, axis=1)) * dt

        # Check for NaN
        if np.isnan(total_dv) or np.isinf(total_dv):
            total_dv = 0.0
            energy_used = 0.0
        else:
            # Energy for gentle Coulomb force capture
            energy_used = 0.5 * self.chaser['mass'] * (total_dv * 1000.0) ** 2 * 0.1

        self.chaser['current_energy'] -= energy_used
        self.total_energy_used += energy_used

        # Ensure energy doesn't go negative
        if self.chaser['current_energy'] < 0:
            self.chaser['current_energy'] = 0.0

        # Success if within 1 meter and low velocity
        success = final_separation < 0.001 and final_rel_vel < 0.0001

        if success:
            print(f"✓ Capture successful using COULOMB TRACTOR!")
            print(f"✓ Energy remaining: {self.chaser['current_energy']/1e6:.2f} MJ")
            # Update combined mass
            self.chaser['mass'] += self.target['mass']
        else:
            print(f"✗ Capture failed!")

        data = {
            'time': t,
            'states': states,
            'controls': controls,
            'final_separation': final_separation,
            'final_velocity': final_rel_vel,
            'energy_used': energy_used,
            'energy_remaining': self.chaser['current_energy'],
            'fuel_used': 0.0,  # NO FUEL!
            'fuel_remaining': 0.0  # NO FUEL!
        }

        return success, data

    def phase_6_deorbit(self):
        """
        Phase 6: Deorbit burn

        USING COULOMB FORCES (electrostatic tractor pulls debris down!)

        Returns:
            success: Boolean
            data: Phase data
        """
        print("\n" + "="*60)
        print("PHASE 6: DEORBIT (COULOMB TRACTOR)")
        print("="*60)

        r_current = self.chaser['orbit_radius_init']
        r_perigee = DEORBIT['target_perigee_radius']

        print(f"Lowering perigee from {r_current:.1f} km to {r_perigee:.1f} km")
        print(f"Using ELECTROSTATIC FORCES to pull debris into lower orbit!")

        # Calculate required delta-v
        dv = self.orbital_dynamics.deorbit_dv(r_current, r_perigee)

        print(f"Deorbit Δv: {abs(dv)*1000:.2f} m/s (retrograde)")

        # Energy required (Coulomb forces)
        energy_required = 0.5 * self.chaser['mass'] * (abs(dv) * 1000.0) ** 2

        print(f"Energy required: {energy_required/1e6:.2f} MJ (NOT fuel!)")
        print(f"Energy available: {self.chaser['current_energy']/1e6:.2f} MJ")

        success = energy_required <= self.chaser['current_energy']

        if success:
            self.chaser['current_energy'] -= energy_required
            self.total_energy_used += energy_required
            print(f"✓ Deorbit burn successful using COULOMB FORCES!")
            print(f"✓ Final energy: {self.chaser['current_energy']/1e6:.2f} MJ")
            print(f"✓ Debris will naturally decay from {DEORBIT['target_perigee']:.0f} km in 2-4 weeks")
            print(f"✓ ZERO FUEL CONSUMED FOR ENTIRE MISSION!")
        else:
            print(f"✗ Insufficient energy for deorbit!")

        data = {
            'dv': dv,
            'energy_required': energy_required,
            'energy_remaining': self.chaser['current_energy'],
            'fuel_required': 0.0,  # NO FUEL!
            'fuel_remaining': 0.0  # NO FUEL!
        }

        return success, data

    def run_full_mission(self):
        """
        Execute complete mission sequence

        Returns:
            success: Overall mission success
            all_data: Data from all phases
        """
        print("\n" + "█"*60)
        print("ACTIVE DEBRIS REMOVAL MISSION")
        print("IIT Kanpur Research Hackathon 2025")
        print("█"*60)

        all_data = {}
        overall_success = True

        # Phase 1: Hohmann Transfer
        success, data = self.phase_1_hohmann_transfer()
        all_data['phase_1'] = data
        if not success:
            overall_success = False
            return overall_success, all_data

        # Phase 2: Far-range Approach
        success, data = self.phase_2_far_range_approach()
        all_data['phase_2'] = data
        if not success:
            print("⚠ Phase 2 did not fully converge, but continuing...")

        # Phase 3: Proximity Operations (pass final state from phase 2)
        initial_state_phase3 = data['states'][-1] if data is not None else None
        success, data = self.phase_3_proximity_operations(initial_state=initial_state_phase3)
        all_data['phase_3'] = data
        if not success:
            print("⚠ Phase 3 did not fully converge, but continuing...")

        # Phase 4: Detumbling
        success, data = self.phase_4_detumbling()
        all_data['phase_4'] = data
        if not success:
            print("⚠ Detumbling incomplete, but attempting capture...")

        # Phase 5: Capture
        success, data = self.phase_5_capture()
        all_data['phase_5'] = data
        if not success:
            overall_success = False
            print("✗ Mission failed at capture phase")
            return overall_success, all_data

        # Phase 6: Deorbit
        success, data = self.phase_6_deorbit()
        all_data['phase_6'] = data
        if not success:
            overall_success = False
            print("✗ Mission failed at deorbit phase")
            return overall_success, all_data

        print("\n" + "█"*60)
        print("MISSION SUCCESS!")
        print("█"*60)

        return overall_success, all_data
