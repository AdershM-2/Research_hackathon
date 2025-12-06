"""
Attitude Dynamics for Tumbling Debris
Implements Euler's rotational equations
"""

import numpy as np
from scipy.integrate import odeint
from scipy.spatial.transform import Rotation


class AttitudeDynamics:
    """Handles rotational dynamics of rigid bodies"""

    def __init__(self, inertia_tensor):
        """
        Args:
            inertia_tensor: 3x3 inertia matrix (kg·m^2)
        """
        self.I = np.array(inertia_tensor)
        self.I_inv = np.linalg.inv(self.I)

    def euler_equations(self, state, t, torque):
        """
        Euler's rotational equations

        State: [omega_x, omega_y, omega_z] - angular velocities in body frame
        Torque: [tau_x, tau_y, tau_z] - applied torques in body frame

        Returns:
            domega_dt: Angular acceleration
        """
        omega = state
        tau = torque

        # Euler's equation: I·ω_dot + ω × (I·ω) = τ
        omega_cross_Iomega = np.cross(omega, self.I @ omega)
        omega_dot = self.I_inv @ (tau - omega_cross_Iomega)

        return omega_dot

    def propagate_angular_velocity(self, omega0, t_span, torque_func, dt=0.1):
        """
        Propagate angular velocity

        Args:
            omega0: Initial angular velocity [wx, wy, wz]
            t_span: [t_start, t_end]
            torque_func: Function that returns torque given (t, omega)
            dt: Time step

        Returns:
            t: Time array
            omega_history: Angular velocity history
            torque_history: Applied torque history
        """
        t = np.arange(t_span[0], t_span[1], dt)
        omega_history = np.zeros((len(t), 3))
        torque_history = np.zeros((len(t), 3))

        omega_history[0] = omega0

        for i in range(len(t)-1):
            # Get torque at current time
            tau = torque_func(t[i], omega_history[i])
            torque_history[i] = tau

            # Propagate one step
            omega_next = odeint(self.euler_equations, omega_history[i],
                              [t[i], t[i+1]], args=(tau,))[-1]
            omega_history[i+1] = omega_next

        # Last torque
        torque_history[-1] = torque_func(t[-1], omega_history[-1])

        return t, omega_history, torque_history

    def rotational_kinetic_energy(self, omega):
        """Calculate rotational kinetic energy"""
        return 0.5 * omega @ self.I @ omega

    def angular_momentum(self, omega):
        """Calculate angular momentum in body frame"""
        return self.I @ omega

    def torque_free_motion(self, omega0, t):
        """
        Analytical solution for torque-free motion (only for principal axes)

        For a symmetric body with I1 = I2 ≠ I3, the motion is periodic
        """
        # This is a simplified version - real solution involves elliptic integrals
        # For now, use numerical integration
        result = odeint(self.euler_equations, omega0, t, args=(np.zeros(3),))
        return result

    def detumbling_torque(self, omega_current, omega_target=None):
        """
        Calculate optimal detumbling torque (opposite to angular momentum)

        Args:
            omega_current: Current angular velocity
            omega_target: Target angular velocity (default: zero)

        Returns:
            torque: Optimal detumbling torque
        """
        if omega_target is None:
            omega_target = np.zeros(3)

        # Current angular momentum
        L_current = self.angular_momentum(omega_current)

        # Simple proportional control: τ = -k * L
        # This removes angular momentum
        k_detumble = 0.1
        torque = -k_detumble * L_current

        return torque


class QuaternionDynamics:
    """Quaternion-based attitude representation (no singularities)"""

    @staticmethod
    def quaternion_derivative(q, omega):
        """
        Quaternion kinematic equation: q_dot = 0.5 * Ω(ω) * q

        Args:
            q: Quaternion [q0, q1, q2, q3] (scalar-first convention)
            omega: Angular velocity [wx, wy, wz]

        Returns:
            q_dot: Time derivative of quaternion
        """
        q0, q1, q2, q3 = q
        wx, wy, wz = omega

        # Omega matrix
        Omega = np.array([
            [0,   -wx,  -wy,  -wz],
            [wx,   0,    wz,  -wy],
            [wy,  -wz,   0,    wx],
            [wz,   wy,  -wx,   0]
        ])

        q_dot = 0.5 * Omega @ q

        return q_dot

    @staticmethod
    def normalize_quaternion(q):
        """Ensure quaternion has unit norm"""
        return q / np.linalg.norm(q)

    @staticmethod
    def quaternion_to_rotation_matrix(q):
        """Convert quaternion to rotation matrix"""
        return Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()

    @staticmethod
    def rotation_matrix_to_quaternion(R):
        """Convert rotation matrix to quaternion"""
        r = Rotation.from_matrix(R)
        q_scipy = r.as_quat()  # [x, y, z, w]
        return np.array([q_scipy[3], q_scipy[0], q_scipy[1], q_scipy[2]])  # [w, x, y, z]

    def propagate_attitude(self, q0, omega0, t_span, inertia, torque_func, dt=0.1):
        """
        Propagate full attitude (quaternion + angular velocity)

        Args:
            q0: Initial quaternion
            omega0: Initial angular velocity
            t_span: [t_start, t_end]
            inertia: Inertia tensor
            torque_func: Function returning torque(t, q, omega)
            dt: Time step

        Returns:
            t, q_history, omega_history
        """
        t = np.arange(t_span[0], t_span[1], dt)
        q_history = np.zeros((len(t), 4))
        omega_history = np.zeros((len(t), 3))

        q_history[0] = q0
        omega_history[0] = omega0

        I = np.array(inertia)
        I_inv = np.linalg.inv(I)

        for i in range(len(t)-1):
            q_current = q_history[i]
            omega_current = omega_history[i]

            # Get applied torque
            tau = torque_func(t[i], q_current, omega_current)

            # Update quaternion (kinematic equation)
            q_dot = self.quaternion_derivative(q_current, omega_current)
            q_next = q_current + q_dot * dt
            q_next = self.normalize_quaternion(q_next)

            # Update angular velocity (Euler's equation)
            omega_cross_Iomega = np.cross(omega_current, I @ omega_current)
            omega_dot = I_inv @ (tau - omega_cross_Iomega)
            omega_next = omega_current + omega_dot * dt

            q_history[i+1] = q_next
            omega_history[i+1] = omega_next

        return t, q_history, omega_history
