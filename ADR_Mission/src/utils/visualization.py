"""
Visualization utilities for mission data
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_trajectory_3d(states, title="Trajectory", save_path=None):
    """
    Plot 3D trajectory

    Args:
        states: State history (N x 6) - [x, y, z, vx, vy, vz]
        title: Plot title
        save_path: Path to save figure
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = states[:, 0] * 1000  # Convert to meters
    y = states[:, 1] * 1000
    z = states[:, 2] * 1000

    ax.plot(x, y, z, 'b-', linewidth=2, label='Chaser trajectory')
    ax.scatter([0], [0], [0], color='red', s=200, marker='*', label='Target')
    ax.scatter([x[0]], [y[0]], [z[0]], color='green', s=100, marker='o', label='Start')
    ax.scatter([x[-1]], [y[-1]], [z[-1]], color='orange', s=100, marker='s', label='End')

    ax.set_xlabel('Radial (m)')
    ax.set_ylabel('Along-track (m)')
    ax.set_zlabel('Cross-track (m)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.close()


def plot_state_history(t, states, save_path=None):
    """
    Plot position and velocity vs time

    Args:
        t: Time array
        states: State history
        save_path: Path to save
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Position
    axes[0].plot(t/3600, states[:, 0]*1000, label='Radial (x)', linewidth=2)
    axes[0].plot(t/3600, states[:, 1]*1000, label='Along-track (y)', linewidth=2)
    axes[0].plot(t/3600, states[:, 2]*1000, label='Cross-track (z)', linewidth=2)
    axes[0].set_ylabel('Position (m)')
    axes[0].set_title('Relative Position')
    axes[0].legend()
    axes[0].grid(True)

    # Velocity
    axes[1].plot(t/3600, states[:, 3]*1000, label='Radial (vx)', linewidth=2)
    axes[1].plot(t/3600, states[:, 4]*1000, label='Along-track (vy)', linewidth=2)
    axes[1].plot(t/3600, states[:, 5]*1000, label='Cross-track (vz)', linewidth=2)
    axes[1].set_ylabel('Velocity (m/s)')
    axes[1].set_xlabel('Time (hours)')
    axes[1].set_title('Relative Velocity')
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.close()


def plot_control_history(t, controls, save_path=None):
    """
    Plot control inputs

    Args:
        t: Time array
        controls: Control history (N x 3)
        save_path: Path to save
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(t/3600, controls[:, 0]*1e6, label='Radial (ax)', linewidth=2)
    ax.plot(t/3600, controls[:, 1]*1e6, label='Along-track (ay)', linewidth=2)
    ax.plot(t/3600, controls[:, 2]*1e6, label='Cross-track (az)', linewidth=2)

    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Acceleration (mm/s²)')
    ax.set_title('Control Accelerations')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.close()


def plot_angular_velocity(t, omega_history, target_omega=0.01, save_path=None):
    """
    Plot angular velocity during detumbling

    Args:
        t: Time array
        omega_history: Angular velocity history (N x 3)
        target_omega: Target angular velocity magnitude
        save_path: Path to save
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Components
    axes[0].plot(t/60, omega_history[:, 0], label='ωx', linewidth=2)
    axes[0].plot(t/60, omega_history[:, 1], label='ωy', linewidth=2)
    axes[0].plot(t/60, omega_history[:, 2], label='ωz', linewidth=2)
    axes[0].set_ylabel('Angular Velocity (rad/s)')
    axes[0].set_title('Angular Velocity Components')
    axes[0].legend()
    axes[0].grid(True)

    # Magnitude
    omega_mag = np.linalg.norm(omega_history, axis=1)
    axes[1].plot(t/60, omega_mag, 'b-', linewidth=2, label='|ω|')
    axes[1].axhline(target_omega, color='r', linestyle='--', label=f'Target ({target_omega} rad/s)')
    axes[1].set_ylabel('Angular Velocity Magnitude (rad/s)')
    axes[1].set_xlabel('Time (minutes)')
    axes[1].set_title('Detumbling Progress')
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.close()


def plot_mission_summary(mission_data, save_path=None):
    """
    Create comprehensive mission summary plot

    Args:
        mission_data: Dictionary with all phase data
        save_path: Path to save
    """
    fig = plt.figure(figsize=(16, 12))

    # Create grid
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Plot 1: Phase 2 trajectory
    ax1 = fig.add_subplot(gs[0, 0], projection='3d')
    if 'phase_2' in mission_data and mission_data['phase_2'] is not None:
        states = mission_data['phase_2']['states']
        x, y, z = states[:, 0]*1000, states[:, 1]*1000, states[:, 2]*1000
        ax1.plot(x, y, z, 'b-', linewidth=2)
        ax1.scatter([0], [0], [0], color='red', s=100, marker='*')
        ax1.set_title('Phase 2: Far-Range Approach')
        ax1.set_xlabel('x (m)')
        ax1.set_ylabel('y (m)')
        ax1.set_zlabel('z (m)')

    # Plot 2: Phase 3 trajectory
    ax2 = fig.add_subplot(gs[0, 1], projection='3d')
    if 'phase_3' in mission_data and mission_data['phase_3'] is not None:
        states = mission_data['phase_3']['states']
        x, y, z = states[:, 0]*1000, states[:, 1]*1000, states[:, 2]*1000
        ax2.plot(x, y, z, 'g-', linewidth=2)
        ax2.scatter([0], [0], [0], color='red', s=100, marker='*')
        ax2.set_title('Phase 3: Proximity Ops')
        ax2.set_xlabel('x (m)')
        ax2.set_ylabel('y (m)')
        ax2.set_zlabel('z (m)')

    # Plot 3: Detumbling
    ax3 = fig.add_subplot(gs[1, :])
    if 'phase_4' in mission_data and mission_data['phase_4'] is not None:
        t = mission_data['phase_4']['time']
        omega = mission_data['phase_4']['omega_history']
        omega_mag = np.linalg.norm(omega, axis=1)
        ax3.plot(t/60, omega_mag, 'r-', linewidth=2)
        ax3.axhline(0.01, color='g', linestyle='--', label='Target')
        ax3.set_xlabel('Time (min)')
        ax3.set_ylabel('|ω| (rad/s)')
        ax3.set_title('Phase 4: Detumbling')
        ax3.legend()
        ax3.grid(True)

    # Plot 4: Fuel usage
    ax4 = fig.add_subplot(gs[2, 0])
    phases = []
    fuel_used = []
    fuel_remaining = []

    for phase_name in ['phase_1', 'phase_2', 'phase_3', 'phase_5', 'phase_6']:
        if phase_name in mission_data and mission_data[phase_name] is not None:
            data = mission_data[phase_name]
            if 'fuel_used' in data:
                phases.append(phase_name.replace('phase_', 'P'))
                fuel_used.append(data['fuel_used'])
                fuel_remaining.append(data['fuel_remaining'])

    if phases:
        x = np.arange(len(phases))
        ax4.bar(x - 0.2, fuel_used, 0.4, label='Fuel Used', color='red')
        ax4.bar(x + 0.2, fuel_remaining, 0.4, label='Fuel Remaining', color='green')
        ax4.set_xticks(x)
        ax4.set_xticklabels(phases)
        ax4.set_ylabel('Fuel (kg)')
        ax4.set_title('Fuel Budget')
        ax4.legend()
        ax4.grid(True, axis='y')

    # Plot 5: Delta-V summary
    ax5 = fig.add_subplot(gs[2, 1])
    dv_data = []
    dv_labels = []

    if 'phase_1' in mission_data and mission_data['phase_1'] is not None:
        dv_data.append(mission_data['phase_1']['total_dv'] * 1000)
        dv_labels.append('Transfer')

    if 'phase_2' in mission_data and mission_data['phase_2'] is not None:
        dv_data.append(mission_data['phase_2']['total_dv'] * 1000)
        dv_labels.append('Approach')

    if 'phase_3' in mission_data and mission_data['phase_3'] is not None:
        dv_data.append(mission_data['phase_3']['total_dv'] * 1000)
        dv_labels.append('Proximity')

    if 'phase_6' in mission_data and mission_data['phase_6'] is not None:
        dv_data.append(abs(mission_data['phase_6']['dv']) * 1000)
        dv_labels.append('Deorbit')

    if dv_data:
        ax5.bar(dv_labels, dv_data, color='blue')
        ax5.set_ylabel('Δv (m/s)')
        ax5.set_title('Delta-V Budget')
        ax5.grid(True, axis='y')

    plt.suptitle('Active Debris Removal Mission Summary', fontsize=16, fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.close()


def create_animation_frames(states, output_dir, prefix='frame'):
    """
    Create animation frames for trajectory

    Args:
        states: State history
        output_dir: Output directory
        prefix: Frame file prefix
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    n_frames = min(100, len(states))
    indices = np.linspace(0, len(states)-1, n_frames, dtype=int)

    for i, idx in enumerate(indices):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot trajectory up to current point
        x = states[:idx+1, 0] * 1000
        y = states[:idx+1, 1] * 1000
        z = states[:idx+1, 2] * 1000

        ax.plot(x, y, z, 'b-', linewidth=2, alpha=0.6)
        ax.scatter([0], [0], [0], color='red', s=200, marker='*', label='Target')
        ax.scatter([x[-1]], [y[-1]], [z[-1]], color='green', s=150, marker='o', label='Chaser')

        # Set consistent axis limits
        max_range = max(np.max(np.abs(states[:, :3]))) * 1000
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])

        ax.set_xlabel('Radial (m)')
        ax.set_ylabel('Along-track (m)')
        ax.set_zlabel('Cross-track (m)')
        ax.set_title(f'Rendezvous Progress (Frame {i+1}/{n_frames})')
        ax.legend()

        filename = os.path.join(output_dir, f'{prefix}_{i:03d}.png')
        plt.savefig(filename, dpi=150)
        plt.close()

    print(f"Created {n_frames} animation frames in {output_dir}")
