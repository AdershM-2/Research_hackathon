"""
Attitude Controllers for Detumbling and Attitude Control
"""

import numpy as np


class AttitudePIDController:
    """PID controller for attitude control"""

    def __init__(self, Kp, Ki, Kd, max_torque=None):
        """
        Args:
            Kp: Proportional gain
            Ki: Integral gain
            Kd: Derivative gain
            max_torque: Maximum torque output
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_torque = max_torque

        self.integral = np.zeros(3)
        self.previous_error = np.zeros(3)

    def reset(self):
        """Reset integral term"""
        self.integral = np.zeros(3)
        self.previous_error = np.zeros(3)

    def compute(self, omega_current, omega_target, dt):
        """
        Compute PID torque control

        Args:
            omega_current: Current angular velocity
            omega_target: Target angular velocity
            dt: Time step

        Returns:
            torque: Control torque
        """
        error = omega_target - omega_current

        # Update integral
        self.integral += error * dt

        # Compute derivative
        derivative = (error - self.previous_error) / dt

        # PID output
        torque = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Saturate
        if self.max_torque is not None:
            torque_mag = np.linalg.norm(torque)
            if torque_mag > self.max_torque:
                torque = torque * (self.max_torque / torque_mag)
                # Anti-windup
                self.integral -= error * dt

        self.previous_error = error.copy()

        return torque


class DetumblingController:
    """Specialized controller for detumbling non-cooperative targets"""

    def __init__(self, inertia_tensor, max_torque=0.001):
        """
        Args:
            inertia_tensor: Target's inertia (estimated)
            max_torque: Maximum torque available (N·m)
        """
        self.I = np.array(inertia_tensor)
        self.max_torque = max_torque

    def angular_momentum_removal(self, omega):
        """
        Compute torque to remove angular momentum

        Strategy: Apply torque opposite to angular momentum vector

        Args:
            omega: Current angular velocity

        Returns:
            torque: Detumbling torque
        """
        # Angular momentum
        L = self.I @ omega

        # Torque opposite to angular momentum
        L_mag = np.linalg.norm(L)
        if L_mag > 1e-6:
            torque_direction = -L / L_mag
            torque = torque_direction * self.max_torque
        else:
            torque = np.zeros(3)

        return torque

    def energy_dissipation(self, omega, damping_ratio=0.1):
        """
        Energy dissipation control (like magnetic damping)

        Args:
            omega: Current angular velocity
            damping_ratio: Damping coefficient

        Returns:
            torque: Damping torque
        """
        # Damping torque proportional to angular velocity
        torque = -damping_ratio * self.I @ omega

        # Saturate
        torque_mag = np.linalg.norm(torque)
        if torque_mag > self.max_torque:
            torque = torque * (self.max_torque / torque_mag)

        return torque

    def optimal_detumbling(self, omega, target_omega=None, strategy='momentum'):
        """
        Optimal detumbling strategy

        Args:
            omega: Current angular velocity
            target_omega: Target angular velocity (default: zero)
            strategy: 'momentum' or 'energy'

        Returns:
            torque: Optimal detumbling torque
        """
        if target_omega is None:
            target_omega = np.zeros(3)

        if strategy == 'momentum':
            return self.angular_momentum_removal(omega)
        elif strategy == 'energy':
            return self.energy_dissipation(omega)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


class IonBeamController:
    """Ion beam shepherd controller (contactless)"""

    def __init__(self, beam_force_max=0.001, standoff_distance=5.0):
        """
        Args:
            beam_force_max: Maximum force from ion beam (N)
            standoff_distance: Safe standoff distance (m)
        """
        self.F_max = beam_force_max
        self.d_standoff = standoff_distance

    def compute_beam_torque(self, omega_target, r_contact_point, normal_direction):
        """
        Compute torque from ion beam

        Args:
            omega_target: Target angular velocity
            r_contact_point: Contact point on target (body frame)
            normal_direction: Direction of ion beam force

        Returns:
            torque: Torque from ion beam
        """
        # Force applied by ion beam
        F = self.F_max * normal_direction

        # Torque = r × F
        torque = np.cross(r_contact_point, F)

        return torque

    def station_keeping_control(self, position_error, velocity_error):
        """
        Station-keeping control for chaser during detumbling

        Args:
            position_error: Position error from desired standoff
            velocity_error: Velocity error

        Returns:
            control_accel: Station-keeping acceleration
        """
        # PD control
        Kp = 0.01
        Kd = 0.05

        control = -Kp * position_error - Kd * velocity_error

        return control


class AdaptiveDetumbling:
    """Adaptive controller for unknown inertia"""

    def __init__(self, I_nominal, max_torque=0.001):
        """
        Args:
            I_nominal: Nominal (estimated) inertia
            max_torque: Maximum torque
        """
        self.I_est = np.array(I_nominal)
        self.max_torque = max_torque

        # Adaptation gains
        self.gamma = 0.01  # Learning rate

    def update_inertia_estimate(self, omega, omega_dot, torque_applied, dt):
        """
        Update inertia estimate using adaptive law

        Based on: I·ω_dot + ω × (I·ω) = τ

        Args:
            omega: Measured angular velocity
            omega_dot: Measured angular acceleration
            torque_applied: Applied torque
            dt: Time step

        Returns:
            I_est: Updated inertia estimate
        """
        # Simplified adaptive law
        # In practice, this requires persistent excitation

        # Prediction error
        omega_cross_Iomega = np.cross(omega, self.I_est @ omega)
        predicted_omega_dot = np.linalg.inv(self.I_est) @ (torque_applied - omega_cross_Iomega)
        error = omega_dot - predicted_omega_dot

        # Update diagonal elements only (simplified)
        # Full version would estimate all inertia parameters
        for i in range(3):
            self.I_est[i, i] += self.gamma * error[i] * omega[i] * dt

        # Ensure positive definiteness
        self.I_est = np.clip(self.I_est, 0.1, 100.0)

        return self.I_est

    def compute_adaptive_control(self, omega, target_omega=None):
        """
        Compute adaptive detumbling control

        Args:
            omega: Current angular velocity
            target_omega: Target angular velocity

        Returns:
            torque: Control torque
        """
        if target_omega is None:
            target_omega = np.zeros(3)

        # Error
        e = omega - target_omega

        # Control law with estimated inertia
        L_est = self.I_est @ omega
        L_mag = np.linalg.norm(L_est)

        if L_mag > 1e-6:
            torque_direction = -L_est / L_mag
            torque = torque_direction * self.max_torque
        else:
            torque = np.zeros(3)

        # Saturate
        torque_mag = np.linalg.norm(torque)
        if torque_mag > self.max_torque:
            torque = torque * (self.max_torque / torque_mag)

        return torque
