"""
Orbital Dynamics for Active Debris Removal Mission
Implements Hill-Clohessy-Wiltshire equations for relative motion
"""

import numpy as np
from scipy.integrate import odeint
import sys
sys.path.append('/home/user/Research_hackathon/ADR_Mission')
from config.mission_config import MU_EARTH


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
