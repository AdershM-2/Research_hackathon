"""
Orbital Dynamics for Active Debris Removal Mission
Implements Hill-Clohessy-Wiltshire equations for relative motion
"""

import numpy as np
from scipy.integrate import odeint
import sys
sys.path.append('/home/user/Research_hackathon/ADR_Mission')
from config.mission_config import MU_EARTH, COULOMB_K


class OrbitalDynamics:
    """Handles orbital mechanics and relative motion dynamics"""

    def __init__(self, reference_radius):
        """
        Args:
            reference_radius: Orbital radius of reference (target) orbit in km
        """
        self.r_ref = reference_radius
        self.n = np.sqrt(MU_EARTH / reference_radius**3)  # Mean motion (rad/s)

    def orbital_velocity(self, radius):
        """Calculate circular orbital velocity"""
        return np.sqrt(MU_EARTH / radius)

    def orbital_period(self, radius):
        """Calculate orbital period in seconds"""
        return 2 * np.pi * np.sqrt(radius**3 / MU_EARTH)

    def hcw_dynamics(self, state, t, control):
        """
        Hill-Clohessy-Wiltshire equations for relative motion

        State: [x, y, z, vx, vy, vz]
        - x: radial (toward/away from Earth)
        - y: along-track (in direction of motion)
        - z: cross-track (perpendicular to orbital plane)

        Control: [fx, fy, fz] - accelerations in km/s^2
        """
        x, y, z, vx, vy, vz = state
        fx, fy, fz = control

        # HCW equations with control
        dx_dt = vx
        dy_dt = vy
        dz_dt = vz

        dvx_dt = 2*self.n*vy + 3*self.n**2*x + fx
        dvy_dt = -2*self.n*vx + fy
        dvz_dt = -self.n**2*z + fz

        return [dx_dt, dy_dt, dz_dt, dvx_dt, dvy_dt, dvz_dt]

    def propagate_hcw(self, state0, t_span, control_func, dt=1.0):
        """
        Propagate HCW dynamics with time-varying control

        Args:
            state0: Initial state [x, y, z, vx, vy, vz]
            t_span: [t_start, t_end]
            control_func: Function that returns control given (t, state)
            dt: Time step

        Returns:
            t: Time array
            states: State history
            controls: Control history
        """
        t = np.arange(t_span[0], t_span[1], dt)
        states = np.zeros((len(t), 6))
        controls = np.zeros((len(t), 3))

        states[0] = state0

        for i in range(len(t)-1):
            # Get control at current time
            u = control_func(t[i], states[i])
            controls[i] = u

            # Propagate one step
            state_next = odeint(self.hcw_dynamics, states[i],
                              [t[i], t[i+1]], args=(u,))[-1]
            states[i+1] = state_next

        # Last control
        controls[-1] = control_func(t[-1], states[-1])

        return t, states, controls

    def hohmann_transfer_dv(self, r1, r2):
        """
        Calculate delta-v for Hohmann transfer

        Returns:
            dv1: First burn (at r1)
            dv2: Second burn (at r2)
            transfer_time: Time for transfer
        """
        # Semi-major axis of transfer orbit
        a_transfer = (r1 + r2) / 2

        # Velocities in circular orbits
        v1 = np.sqrt(MU_EARTH / r1)
        v2 = np.sqrt(MU_EARTH / r2)

        # Velocities on transfer ellipse
        vt1 = np.sqrt(MU_EARTH * (2/r1 - 1/a_transfer))
        vt2 = np.sqrt(MU_EARTH * (2/r2 - 1/a_transfer))

        # Delta-v's
        dv1 = vt1 - v1
        dv2 = v2 - vt2

        # Transfer time (half period of transfer ellipse)
        transfer_time = np.pi * np.sqrt(a_transfer**3 / MU_EARTH)

        return dv1, dv2, transfer_time

    def deorbit_dv(self, r_current, r_perigee):
        """
        Calculate delta-v needed to lower perigee to r_perigee

        Args:
            r_current: Current circular orbit radius
            r_perigee: Target perigee radius

        Returns:
            dv: Delta-v required (negative = retrograde burn)
        """
        # Current circular velocity
        v_circular = np.sqrt(MU_EARTH / r_current)

        # Semi-major axis of deorbit ellipse
        a_deorbit = (r_current + r_perigee) / 2

        # Velocity at apogee of deorbit ellipse
        v_deorbit = np.sqrt(MU_EARTH * (2/r_current - 1/a_deorbit))

        # Delta-v (negative for retrograde)
        dv = v_deorbit - v_circular

        return dv

    def natural_motion_solution(self, state0, t):
        """
        Analytical solution for HCW equations (no control)
        Useful for validation and initial trajectory design

        Args:
            state0: Initial state [x0, y0, z0, vx0, vy0, vz0]
            t: Time (can be scalar or array)

        Returns:
            state(t): State at time t
        """
        x0, y0, z0, vx0, vy0, vz0 = state0
        n = self.n

        # Convert to array if scalar
        t_scalar = np.isscalar(t)
        t = np.atleast_1d(t)

        # In-plane motion (x, y)
        x = (4*x0 + 2*vy0/n) + (vx0/n)*np.sin(n*t) - (3*x0 + 2*vy0/n)*np.cos(n*t)
        y = y0 + (2*vx0/n) - (2*vx0/n)*np.cos(n*t) - (6*x0 + 4*vy0/n)*n*t + (6*x0 + 4*vy0/n - 2*vy0/(n))*np.sin(n*t)

        vx = vx0*np.cos(n*t) + (3*x0*n + 2*vy0)*np.sin(n*t)
        vy = vy0 - 2*vx0*np.sin(n*t) - (6*x0*n + 4*vy0)*np.cos(n*t) + (6*x0*n + 4*vy0)

        # Out-of-plane motion (z) - simple harmonic
        z = z0*np.cos(n*t) + (vz0/n)*np.sin(n*t)
        vz = -z0*n*np.sin(n*t) + vz0*np.cos(n*t)

        if t_scalar:
            return np.array([x[0], y[0], z[0], vx[0], vy[0], vz[0]])
        else:
            return np.column_stack([x, y, z, vx, vy, vz])

    def energy(self, state):
        """Calculate specific orbital energy (per unit mass)"""
        r = np.linalg.norm(state[:3])
        v = np.linalg.norm(state[3:])
        return v**2/2 - MU_EARTH/r

    def angular_momentum(self, state):
        """Calculate specific angular momentum vector"""
        r = state[:3]
        v = state[3:]
        return np.cross(r, v)


class CoulombForceActuator:
    """
    Coulomb Electrostatic Tractor System

    Uses electrostatic forces between charged spacecraft and debris
    for contactless orbital maneuvering and debris removal.

    Innovation: No chemical fuel needed!
    """

    def __init__(self, chaser_config, target_config):
        """
        Args:
            chaser_config: Chaser spacecraft configuration
            target_config: Target debris configuration
        """
        self.chaser = chaser_config
        self.target = target_config
        self.k = COULOMB_K  # Coulomb's constant

    def coulomb_force(self, q1, q2, distance):
        """
        Calculate Coulomb force between two charged objects

        F = k * |q1 * q2| / r²

        Args:
            q1: Charge of object 1 (Coulombs)
            q2: Charge of object 2 (Coulombs)
            distance: Separation distance (meters)

        Returns:
            force_magnitude: Force magnitude in Newtons
        """
        # Prevent division by zero
        if distance < 0.001:  # 1 mm minimum
            distance = 0.001

        # Coulomb's law: F = k * q1 * q2 / r²
        force = self.k * abs(q1 * q2) / (distance ** 2)

        return force

    def coulomb_force_vector(self, q1, q2, position_vector):
        """
        Calculate Coulomb force vector

        Args:
            q1: Charge of chaser (Coulombs)
            q2: Charge of target (Coulombs)
            position_vector: Position vector from chaser to target (meters)

        Returns:
            force_vector: Force vector in Newtons (3D)
        """
        # Distance
        r = np.linalg.norm(position_vector)

        if r < 0.001:  # Minimum distance
            r = 0.001

        # Force magnitude
        F_mag = self.coulomb_force(q1, q2, r)

        # Direction: attractive if q1*q2 < 0, repulsive if q1*q2 > 0
        direction = position_vector / r

        # Sign convention: positive force = attraction (toward target)
        if q1 * q2 < 0:
            # Opposite charges attract
            force_vector = F_mag * direction
        else:
            # Same charges repel
            force_vector = -F_mag * direction

        return force_vector

    def acceleration_from_coulomb_force(self, q_chaser, q_target, position_vector_km):
        """
        Calculate acceleration of chaser from Coulomb force

        Args:
            q_chaser: Chaser charge (Coulombs)
            q_target: Target charge (Coulombs)
            position_vector_km: Position vector chaser→target (km)

        Returns:
            acceleration: Acceleration vector (km/s²)
        """
        # Convert position to meters
        position_m = position_vector_km * 1000.0

        # Calculate force vector (Newtons)
        F = self.coulomb_force_vector(q_chaser, q_target, position_m)

        # Acceleration: a = F/m (m/s²)
        a_ms2 = F / self.chaser['mass']

        # Convert to km/s²
        a_kms2 = a_ms2 / 1000.0

        return a_kms2

    def energy_cost(self, q_change, dt):
        """
        Calculate energy cost of changing charge

        Energy stored in capacitor: E = 1/2 * C * V²
        For charge transfer: ΔE = work done

        Args:
            q_change: Change in charge (Coulombs)
            dt: Time interval (seconds)

        Returns:
            energy_used: Energy consumed (Joules)
        """
        # Simplified model: energy proportional to charge change squared
        # This accounts for capacitor charging/discharging
        C = self.chaser.get('capacitor_energy', 1e6) / (self.chaser.get('max_voltage', 1e5) ** 2)

        # Energy for charge change
        V = abs(q_change) / C if C > 0 else 0
        energy = 0.5 * C * V ** 2

        return energy / self.chaser.get('charging_efficiency', 0.95)

    def apply_coulomb_control(self, control_acceleration, position_vector_km, dt):
        """
        Determine required charge state to produce desired acceleration

        Args:
            control_acceleration: Desired acceleration (km/s²)
            position_vector_km: Position vector chaser→target (km)
            dt: Time step (seconds)

        Returns:
            q_chaser: Required chaser charge (Coulombs)
            energy_used: Energy consumed (Joules)
            success: Whether control is feasible
        """
        # Get target charge (including induced charge)
        q_target = self.target['charge'] + self.target.get('induced_charge', 0.0)

        # If target has zero charge, we need to induce charge first
        if abs(q_target) < 1e-9:
            # Induce small charge on target using electron beam
            q_target = -0.001  # 1 mC
            self.target['induced_charge'] = q_target

        # Convert desired acceleration to m/s²
        a_desired_ms2 = control_acceleration * 1000.0

        # Required force: F = m * a
        F_required = np.linalg.norm(a_desired_ms2) * self.chaser['mass']

        # Distance to target
        r_m = np.linalg.norm(position_vector_km) * 1000.0

        if r_m < 0.001:
            r_m = 0.001

        # From Coulomb's law: F = k * |q1 * q2| / r²
        # Solve for q_chaser: q_chaser = F * r² / (k * |q_target|)

        if abs(q_target) < 1e-9:
            return 0.0, 0.0, False

        q_chaser_required = F_required * (r_m ** 2) / (self.k * abs(q_target))

        # Determine sign based on desired direction
        if np.dot(control_acceleration, position_vector_km) > 0:
            # Want to accelerate toward target (attraction)
            # Need opposite sign charges
            q_chaser_required *= -np.sign(q_target)
        else:
            # Want to accelerate away from target (repulsion)
            # Need same sign charges
            q_chaser_required *= np.sign(q_target)

        # Check charge limits
        q_max = self.chaser.get('max_charge', 1.0)
        q_min = self.chaser.get('min_charge', -1.0)

        if q_chaser_required > q_max:
            q_chaser_required = q_max
            success = False
        elif q_chaser_required < q_min:
            q_chaser_required = q_min
            success = False
        else:
            success = True

        # Calculate energy cost
        q_change = abs(q_chaser_required - self.chaser.get('current_charge', 0.0))
        energy_used = self.energy_cost(q_change, dt)

        # Update chaser charge
        self.chaser['current_charge'] = q_chaser_required

        return q_chaser_required, energy_used, success
