#!/usr/bin/env python3
"""
Lorentz Force Physics for Magneto-Coulombic Actuation
F = q(v × B) - Force on charged particle in magnetic field
IIT Kanpur Research Hackathon 2025
"""

import numpy as np

# Physical constants
MU_EARTH = 398600.0  # km^3/s^2
R_EARTH = 6371.0  # km
EARTH_MAGNETIC_MOMENT = 8.0e22  # A·m^2
MU_0 = 4 * np.pi * 1e-7  # T·m/A (permeability of free space)

class EarthMagneticField:
    """Earth's magnetic field model (dipole approximation)"""

    def __init__(self):
        self.M = EARTH_MAGNETIC_MOMENT  # Magnetic moment
        self.mu_0 = MU_0

    def get_field(self, position_km, latitude_deg=0):
        """
        Calculate Earth's magnetic field at given position

        Args:
            position_km: Position vector [x, y, z] in km (ECI frame)
            latitude_deg: Magnetic latitude in degrees (simplified)

        Returns:
            B_field: Magnetic field vector [Bx, By, Bz] in Tesla
        """
        # Convert to meters
        r_vec = np.array(position_km) * 1000.0
        r_mag = np.linalg.norm(r_vec)

        # Dipole field approximation
        # B(r) = (μ₀M)/(4πr³) * [2cosθ r̂ + sinθ θ̂]
        # Simplified: assume dipole aligned with z-axis

        theta = np.arctan2(np.sqrt(r_vec[0]**2 + r_vec[1]**2), r_vec[2])

        # Radial and tangential components
        B_r = (self.mu_0 * self.M) / (2 * np.pi * r_mag**3) * np.cos(theta)
        B_theta = (self.mu_0 * self.M) / (4 * np.pi * r_mag**3) * np.sin(theta)

        # Convert to Cartesian coordinates
        r_hat = r_vec / r_mag

        # Approximate theta_hat (perpendicular to r in meridional plane)
        z_axis = np.array([0, 0, 1])
        theta_hat = np.cross(np.cross(z_axis, r_hat), r_hat)
        if np.linalg.norm(theta_hat) > 1e-10:
            theta_hat = theta_hat / np.linalg.norm(theta_hat)

        B_field = B_r * r_hat + B_theta * theta_hat

        return B_field  # Tesla

    def get_field_magnitude(self, altitude_km):
        """
        Get approximate field magnitude at given altitude

        Args:
            altitude_km: Altitude above Earth surface in km

        Returns:
            B_mag: Field magnitude in Tesla
        """
        r = (R_EARTH + altitude_km) * 1000  # meters
        # Approximate: B ~ M/(r^3)
        B_mag = (self.mu_0 * self.M) / (4 * np.pi * r**3)
        return B_mag


class LorentzForceActuator:
    """
    Magneto-Coulombic Actuation System
    Uses Lorentz force: F = q(v × B)
    """

    def __init__(self, num_shells=6, max_charge=1e-6):
        """
        Initialize Lorentz force actuator

        Args:
            num_shells: Number of Coulomb shells (default 6)
            max_charge: Maximum charge per shell in Coulombs (default 1 μC)
        """
        self.num_shells = num_shells
        self.max_charge = max_charge
        self.b_field_model = EarthMagneticField()

        # Shell positions relative to spacecraft center (meters)
        # Assume 1m spacing at extremities
        self.shell_positions = np.array([
            [1.0, 0, 0],    # +x
            [-1.0, 0, 0],   # -x
            [0, 1.0, 0],    # +y
            [0, -1.0, 0],   # -y
            [0, 0, 1.0],    # +z
            [0, 0, -1.0]    # -z
        ])

    def lorentz_force(self, charge, velocity_vec, b_field_vec):
        """
        Calculate Lorentz force on charged particle
        F = q(v × B)

        Args:
            charge: Charge in Coulombs
            velocity_vec: Velocity vector [vx, vy, vz] in m/s
            b_field_vec: Magnetic field vector [Bx, By, Bz] in Tesla

        Returns:
            force_vec: Force vector [Fx, Fy, Fz] in Newtons
        """
        # F = q(v × B)
        force_vec = charge * np.cross(velocity_vec, b_field_vec)
        return force_vec

    def compute_net_force(self, shell_charges, velocity_km_s, position_km):
        """
        Compute net force from all charged shells

        Args:
            shell_charges: Array of charges for each shell (Coulombs)
            velocity_km_s: Orbital velocity vector [vx, vy, vz] in km/s
            position_km: Position vector [x, y, z] in km

        Returns:
            F_net: Net force vector [Fx, Fy, Fz] in Newtons
            F_mag: Force magnitude in Newtons
        """
        # Get Earth's magnetic field at this position
        B_field = self.b_field_model.get_field(position_km)

        # Convert velocity to m/s
        velocity_m_s = np.array(velocity_km_s) * 1000.0

        # Compute force from each shell
        F_net = np.zeros(3)
        for i in range(self.num_shells):
            q = shell_charges[i]
            # Note: shells move with spacecraft, so same velocity
            F_i = self.lorentz_force(q, velocity_m_s, B_field)
            F_net += F_i

        F_mag = np.linalg.norm(F_net)
        return F_net, F_mag

    def compute_torque(self, shell_charges, velocity_km_s, position_km):
        """
        Compute torque from distributed shell charges
        τ = Σ r_i × F_i

        Args:
            shell_charges: Array of charges for each shell (Coulombs)
            velocity_km_s: Orbital velocity vector in km/s
            position_km: Position vector in km

        Returns:
            torque_vec: Torque vector [τx, τy, τz] in N·m
            torque_mag: Torque magnitude in N·m
        """
        # Get Earth's magnetic field
        B_field = self.b_field_model.get_field(position_km)
        velocity_m_s = np.array(velocity_km_s) * 1000.0

        # Compute torque from each shell
        torque_vec = np.zeros(3)
        for i in range(self.num_shells):
            q = shell_charges[i]
            r_i = self.shell_positions[i]
            F_i = self.lorentz_force(q, velocity_m_s, B_field)
            torque_i = np.cross(r_i, F_i)
            torque_vec += torque_i

        torque_mag = np.linalg.norm(torque_vec)
        return torque_vec, torque_mag

    def design_charge_config_for_force(self, desired_force_direction, magnitude=None):
        """
        Design charge configuration for desired net force direction
        All shells charged identically for translational force

        Args:
            desired_force_direction: Desired force direction (unit vector)
            magnitude: Desired charge magnitude (Coulombs), default max_charge

        Returns:
            shell_charges: Array of charges for each shell
        """
        if magnitude is None:
            magnitude = self.max_charge

        # For net force: charge all shells identically
        # Sign determines force direction (depends on v × B orientation)
        shell_charges = np.ones(self.num_shells) * magnitude

        return shell_charges

    def design_charge_config_for_torque(self, desired_torque_axis):
        """
        Design charge configuration for desired torque about axis
        Opposite shells charged with opposite signs

        Args:
            desired_torque_axis: Desired torque axis (unit vector)

        Returns:
            shell_charges: Array of charges for each shell
        """
        # For torque: charge opposite pairs with opposite signs
        # Example: for z-axis torque, charge +x/-x pair oppositely
        shell_charges = np.zeros(self.num_shells)

        # Simplified: charge pairs along torque axis
        if abs(desired_torque_axis[2]) > 0.7:  # z-axis dominant
            shell_charges[0] = self.max_charge   # +x
            shell_charges[1] = -self.max_charge  # -x
        elif abs(desired_torque_axis[1]) > 0.7:  # y-axis dominant
            shell_charges[4] = self.max_charge   # +z
            shell_charges[5] = -self.max_charge  # -z
        else:  # x-axis dominant
            shell_charges[2] = self.max_charge   # +y
            shell_charges[3] = -self.max_charge  # -y

        return shell_charges


def orbital_velocity(altitude_km):
    """
    Calculate circular orbital velocity at given altitude

    Args:
        altitude_km: Altitude above Earth in km

    Returns:
        v: Orbital velocity in km/s
    """
    r = R_EARTH + altitude_km
    v = np.sqrt(MU_EARTH / r)
    return v


if __name__ == "__main__":
    # Example usage
    print("Lorentz Force Physics for Magneto-Coulombic Actuation")
    print("=" * 60)

    # Initialize system
    actuator = LorentzForceActuator(num_shells=6, max_charge=1e-6)

    # Test at ISS altitude
    altitude = 400  # km
    position = np.array([R_EARTH + altitude, 0, 0])  # km
    velocity_mag = orbital_velocity(altitude)  # km/s
    velocity = np.array([0, velocity_mag, 0])  # circular orbit in y-direction

    print(f"\nTest Configuration:")
    print(f"  Altitude: {altitude} km")
    print(f"  Orbital velocity: {velocity_mag*1000:.1f} m/s")

    # Get magnetic field
    B_field = actuator.b_field_model.get_field(position)
    B_mag = np.linalg.norm(B_field)
    print(f"  Magnetic field magnitude: {B_mag*1e6:.2f} μT")

    # Test 1: Net force (all shells charged identically)
    print("\nTest 1: Net Force (Orbital Maneuver)")
    shell_charges = np.ones(6) * 1e-6  # 1 μC each
    F_net, F_mag = actuator.compute_net_force(shell_charges, velocity, position)
    print(f"  Total charge: {np.sum(shell_charges)*1e6:.1f} μC")
    print(f"  Net force: {F_mag:.2e} N")
    print(f"  Force vector: [{F_net[0]:.2e}, {F_net[1]:.2e}, {F_net[2]:.2e}] N")

    # Test 2: Torque (opposite shells charged)
    print("\nTest 2: Torque (Attitude Control)")
    shell_charges_torque = np.array([1e-6, -1e-6, 0, 0, 0, 0])  # ±x pair
    torque, tau_mag = actuator.compute_torque(shell_charges_torque, velocity, position)
    print(f"  Charge config: ±1 μC on ±x shells")
    print(f"  Torque magnitude: {tau_mag:.2e} N·m")
    print(f"  Torque vector: [{torque[0]:.2e}, {torque[1]:.2e}, {torque[2]:.2e}] N·m")

    print("\n" + "=" * 60)
