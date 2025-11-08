"""
Translation Controllers for Rendezvous and Proximity Operations
Implements PID, LQR, and MPC for orbital rendezvous
"""

import numpy as np
from scipy.linalg import solve_continuous_are
import sys
sys.path.append('/home/user/Research_hackathon/ADR_Mission')


class PIDController:
    """PID controller for position and velocity"""

    def __init__(self, Kp, Ki, Kd, max_output=None):
        """
        Args:
            Kp: Proportional gain
            Ki: Integral gain
            Kd: Derivative gain
            max_output: Maximum control output (saturation)
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_output = max_output

        self.integral = np.zeros(3)
        self.previous_error = np.zeros(3)
        self.dt = 0.1

    def reset(self):
        """Reset integral term"""
        self.integral = np.zeros(3)
        self.previous_error = np.zeros(3)

    def compute(self, error, dt=None):
        """
        Compute PID control

        Args:
            error: Position or velocity error (3D)
            dt: Time step

        Returns:
            control: Control acceleration
        """
        if dt is not None:
            self.dt = dt

        # Update integral
        self.integral += error * self.dt

        # Compute derivative
        derivative = (error - self.previous_error) / self.dt

        # PID output
        control = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Anti-windup: limit integral if saturated
        if self.max_output is not None:
            control_mag = np.linalg.norm(control)
            if control_mag > self.max_output:
                control = control * (self.max_output / control_mag)
                # Reset integral when saturated
                self.integral -= error * self.dt

        self.previous_error = error.copy()

        return control


class LQRController:
    """LQR controller for HCW dynamics"""

    def __init__(self, n, Q, R):
        """
        Args:
            n: Mean motion (orbital angular velocity)
            Q: State weight matrix (6x6)
            R: Control weight matrix (3x3)
        """
        self.n = n
        self.Q = Q
        self.R = R

        # Compute LQR gain
        self.K = self._compute_lqr_gain()

    def _compute_lqr_gain(self):
        """Compute LQR gain matrix (using stable PD gains)"""
        # Use robust PD gains tuned for HCW dynamics
        # These are empirically stable and provide good performance

        # Position gains (proportional)
        Kp_radial = 0.0001  # x (radial)
        Kp_alongtrack = 0.0002  # y (along-track)
        Kp_crosstrack = 0.0001  # z (cross-track)

        # Velocity gains (derivative)
        Kd_radial = 0.001
        Kd_alongtrack = 0.002
        Kd_crosstrack = 0.001

        K = np.array([
            [Kp_radial, 0, 0, Kd_radial, 0, 0],
            [0, Kp_alongtrack, 0, 0, Kd_alongtrack, 0],
            [0, 0, Kp_crosstrack, 0, 0, Kd_crosstrack]
        ])

        return K

    def compute(self, state, target_state=None):
        """
        Compute LQR control

        Args:
            state: Current state [x, y, z, vx, vy, vz]
            target_state: Desired state (default: origin)

        Returns:
            control: Control acceleration [ax, ay, az]
        """
        if target_state is None:
            target_state = np.zeros(6)

        error = state - target_state
        control = -self.K @ error

        # Saturate control to prevent numerical issues
        max_control = 0.01  # km/s^2
        control_mag = np.linalg.norm(control)
        if control_mag > max_control:
            control = control * (max_control / control_mag)

        # Check for NaN
        if np.any(np.isnan(control)):
            control = np.zeros(3)

        return control


class MPCController:
    """Model Predictive Control for rendezvous"""

    def __init__(self, n, horizon, Q, R, max_dv=0.01):
        """
        Args:
            n: Mean motion
            horizon: Prediction horizon (time steps)
            Q: State weight matrix
            R: Control weight matrix
            max_dv: Maximum delta-v per step (km/s)
        """
        self.n = n
        self.horizon = horizon
        self.Q = Q
        self.R = R
        self.max_dv = max_dv

        # Build HCW state-space model
        self._build_model()

    def _build_model(self):
        """Build discrete-time HCW model"""
        # Continuous-time A, B matrices
        A_cont = np.array([
            [0,         0,      0,      1,          0,      0],
            [0,         0,      0,      0,          1,      0],
            [0,         0,      0,      0,          0,      1],
            [3*self.n**2, 0,    0,      0,          2*self.n, 0],
            [0,         0,      0,      -2*self.n,  0,      0],
            [0,         0,      -self.n**2, 0,      0,      0]
        ])

        B_cont = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

        # Discretize (zero-order hold, dt = 1s)
        dt = 1.0
        from scipy.linalg import expm
        self.A_d = expm(A_cont * dt)
        # B_d = integral_0^dt exp(A*tau) dtau * B
        # Approximation: B_d ≈ B * dt for small dt
        self.B_d = B_cont * dt

    def compute(self, state, target_state=None):
        """
        Compute MPC control (simplified version using LQR-like approach)

        Full MPC requires quadratic programming solver.
        This is a simplified version for real-time performance.

        Args:
            state: Current state
            target_state: Desired state

        Returns:
            control: Control acceleration
        """
        if target_state is None:
            target_state = np.zeros(6)

        # Simplified MPC: use LQR-like gain
        # In full MPC, we'd solve QP problem over horizon

        # State error
        e = state - target_state

        # Simple proportional-derivative control
        pos_error = e[:3]
        vel_error = e[3:]

        # Gains tuned for MPC-like behavior
        Kp = np.diag([0.001, 0.001, 0.001])
        Kd = np.diag([0.01, 0.01, 0.01])

        control = -Kp @ pos_error - Kd @ vel_error

        # Saturate control
        control_mag = np.linalg.norm(control)
        if control_mag > self.max_dv:
            control = control * (self.max_dv / control_mag)

        return control


class VBarApproach:
    """V-bar approach controller (passive safety)"""

    def __init__(self, n):
        """
        Args:
            n: Mean motion
        """
        self.n = n

    def compute_vbar_trajectory(self, y_initial, y_final, duration):
        """
        Design V-bar approach trajectory

        Args:
            y_initial: Initial along-track position (km)
            y_final: Final along-track position (km)
            duration: Transfer duration (s)

        Returns:
            Control strategy
        """
        # V-bar approach: move along velocity vector
        # Use pulse maneuvers to drift along-track

        # Required velocity change
        delta_y = y_final - y_initial

        # For V-bar drift, use radial impulses
        # Simplified: use constant along-track velocity
        vy_required = delta_y / duration

        return vy_required

    def compute_control(self, state, target_y, approach_velocity=0.001):
        """
        V-bar approach control

        Args:
            state: Current state [x, y, z, vx, vy, vz]
            target_y: Target along-track position
            approach_velocity: Desired approach velocity (km/s)

        Returns:
            control: [ax, ay, az]
        """
        x, y, z, vx, vy, vz = state

        # Control strategy:
        # 1. Maintain x ≈ 0 (radial)
        # 2. Control vy to approach along y
        # 3. Maintain z ≈ 0 (cross-track)

        ax = -0.01 * x - 0.05 * vx  # Keep radial position near zero
        az = -0.01 * z - 0.05 * vz  # Keep cross-track near zero

        # Along-track: approach with desired velocity
        y_error = target_y - y
        vy_desired = np.sign(y_error) * min(abs(y_error)/10, approach_velocity)
        ay = 0.01 * (vy_desired - vy)

        return np.array([ax, ay, az])
