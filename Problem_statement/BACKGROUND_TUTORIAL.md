# Space Debris Removal - Background for Robotics & Controls Engineers

## Table of Contents
1. [Space Debris Problem Overview](#1-space-debris-problem-overview)
2. [Orbital Mechanics Fundamentals](#2-orbital-mechanics-fundamentals)
3. [The Kessler Syndrome](#3-the-kessler-syndrome)
4. [Spacecraft Dynamics & Control in Space](#4-spacecraft-dynamics--control-in-space)
5. [Rendezvous and Proximity Operations (RPO)](#5-rendezvous-and-proximity-operations-rpo)
6. [Capture Mechanisms](#6-capture-mechanisms)
7. [Control Challenges for Non-Cooperative Targets](#7-control-challenges-for-non-cooperative-targets)
8. [Deorbiting Techniques](#8-deorbiting-techniques)
9. [Key Differences from Terrestrial Robotics](#9-key-differences-from-terrestrial-robotics)

---

## 1. Space Debris Problem Overview

### What is Space Debris?
- **Defunct satellites**: No longer operational spacecraft
- **Rocket bodies**: Upper stages left in orbit
- **Fragmentation debris**: Pieces from collisions and explosions
- **Mission-related objects**: Lens caps, separation mechanisms, etc.

### LEO Characteristics
- **Altitude**: 200-2000 km above Earth
- **Orbital velocity**: ~7.8 km/s (28,000 km/h!)
- **Orbital period**: ~90-120 minutes
- **Atmospheric drag**: Still present, causes gradual decay

### Why It Matters
- Over 34,000 tracked objects >10 cm
- ~1 million objects between 1-10 cm
- Collision at orbital speeds can destroy spacecraft
- Even small debris (1 cm) can be catastrophic

---

## 2. Orbital Mechanics Fundamentals

### Kepler's Laws
As a controls engineer, you need to understand that satellites follow predictable paths:

**1. Elliptical Orbits**
- Orbits are ellipses with Earth at one focus
- Described by semi-major axis (a) and eccentricity (e)

**2. Orbital Parameters (State Vector)**
```
Position: [x, y, z]
Velocity: [vx, vy, vz]
```

Or using **Keplerian Elements**:
- **a**: Semi-major axis (orbit size)
- **e**: Eccentricity (orbit shape: 0 = circular, <1 = ellipse)
- **i**: Inclination (tilt relative to equator)
- **Ω**: Right Ascension of Ascending Node (RAAN)
- **ω**: Argument of Periapsis
- **ν**: True Anomaly (position in orbit)

### Two-Body Problem
The fundamental equation of orbital motion:

```
r̈ = -μ/r³ · r
```

Where:
- μ = GM (gravitational parameter of Earth = 398,600 km³/s²)
- r = position vector
- r̈ = acceleration

**Key Insight for Controls:** In orbit, there's no friction! Any velocity change is permanent unless you apply another force.

### Hohmann Transfer
To change orbits efficiently:
1. Apply Δv at periapsis to raise apoapsis
2. Coast to new apoapsis
3. Apply Δv to circularize

**Critical for your problem:** Rendezvous requires matching both position AND velocity!

---

## 3. The Kessler Syndrome

### The Cascading Collision Problem

Named after NASA scientist Donald Kessler (1978), this is the critical threat:

1. Two objects collide at ~15 km/s relative velocity
2. Collision creates thousands of new debris fragments
3. Each fragment can cause more collisions
4. **Exponential growth** of debris population
5. Eventually, LEO becomes unusable (chain reaction)

### Current Risk Level
- We're approaching the critical density threshold
- Some orbits (800-1000 km) are already at risk
- Mega-constellations (Starlink: 42,000 satellites planned) increase risk

### Why Active Removal is Needed
- Natural decay takes decades-to-centuries in LEO
- Atmospheric drag only significant below ~600 km
- We need to remove ~5-10 large objects per year to stabilize

---

## 4. Spacecraft Dynamics & Control in Space

### Attitude Dynamics (Rotation)

**Euler's Rotational Equation:**
```
I·ω̇ + ω × (I·ω) = τ
```

Where:
- I = Moment of inertia tensor (3×3 matrix)
- ω = Angular velocity vector
- τ = Applied torque

**Attitude Representation:**
- Euler angles (intuitive but have singularities)
- Quaternions (4 parameters, no singularities - preferred!)
- Rotation matrices (9 parameters, redundant)

### Actuators in Space

**For Translation (Δv):**
1. **Thrusters**: Chemical or electric propulsion
   - Impulse: Δv = ve · ln(m₀/mf) - Tsiolkovsky equation
   - Fuel limited!

**For Rotation (torque):**
1. **Reaction Wheels**: Spin internal mass, conserve angular momentum
   - Fast, precise, can saturate (need desaturation)
2. **Control Moment Gyroscopes (CMGs)**: Gimbaled spinning wheels
   - Higher torque than reaction wheels
3. **Magnetic Torquers**: Interact with Earth's magnetic field
   - Slow, only certain directions, free propellant
4. **Thrusters**: Fast but uses fuel

### Key Control Challenges
- **Underactuated system**: Limited fuel, must be efficient
- **Coupled dynamics**: Translation-rotation coupling during capture
- **Long time delays**: Ground communication ~1 second delay
- **Sensor noise**: Star trackers, gyros, GPS in space

---

## 5. Rendezvous and Proximity Operations (RPO)

### The Four Phases of Rendezvous

**Phase 1: Phasing (Far Range, >100 km)**
- Match orbital plane (inclination)
- Adjust orbit to approach target
- Use ground-based tracking

**Phase 2: Approach (10-100 km)**
- Refine trajectory
- Begin autonomous sensing
- Switch to relative navigation

**Phase 3: Proximity Operations (100 m - 10 km)**
- **Critical phase for your problem!**
- Careful trajectory planning
- Collision avoidance
- Continuous target tracking

**Phase 4: Close Proximity & Capture (<100 m)**
- Final approach corridor
- Synchronize rotation rates
- Execute capture

### Hill-Clohessy-Wiltshire (HCW) Equations

**Relative motion in orbit** (linearized):

```
ẍ - 2nẏ - 3n²x = fx/m
ÿ + 2nẋ = fy/m
z̈ + n²z = fz/m
```

Where:
- (x, y, z): Local orbital frame (radial, along-track, cross-track)
- n: Mean motion (orbital angular velocity) = √(μ/a³)
- f: Control forces

**Key Insight:**
- Radial (x) and along-track (y) are **coupled** via Coriolis terms (2nẏ, 2nẋ)
- Cross-track (z) is **decoupled**
- Natural motion creates elliptical relative trajectories

### V-bar and R-bar Approaches

**R-bar (Radial approach):**
- Approach from above/below
- Naturally stable against along-track drift
- Requires active station-keeping

**V-bar (Velocity vector approach):**
- Approach from behind/front
- Passive safety (natural separation if engines fail)
- Preferred for ISS

---

## 6. Capture Mechanisms

### Contact-Based Methods

**1. Robotic Arm**
- Example: Canadarm2 on ISS, SSRMS
- **Pros**: Precise, proven technology
- **Cons**: Requires close proximity, complex dynamics
- **Control Challenge**: Free-floating base problem!

**Free-Floating Dynamics:**
```
When arm moves → spacecraft base reacts (Newton's 3rd law)
```

You need **Generalized Jacobian** that accounts for base motion:
- Position of end-effector depends on both joint angles AND base motion
- Captures induce momentum transfer → spacecraft tumbles

**2. Harpoon**
- Fire penetrating spike into target
- Tether connects chaser to target
- **Pros**: Works for non-cooperative targets
- **Cons**: Can fragment target, tether dynamics complex

**3. Net**
- Deploy net to envelop target
- **Pros**: Gentle, encapsulates fragments
- **Cons**: Deployment dynamics, tangling risk

**4. Gripper/Grapple**
- Mechanical jaws grip target
- Requires attachment point (cooperative targets)

### Contactless Methods

**1. Electrostatic Tractor**
- Charge spacecraft oppositely → Coulomb attraction
- **Pros**: No contact, scalable force
- **Cons**: Requires charge management, works at close range

**2. Laser Ablation**
- Vaporize surface material → creates thrust on target
- **Pros**: Standoff distance, no rendezvous needed
- **Cons**: Debris from ablation, power requirements

**3. Ion Beam Shepherd**
- Plasma thruster creates force on target
- **Pros**: Gentle, continuous force
- **Cons**: Very slow, complex plasma dynamics

**4. Magnetic Tractor**
- Use magnetic fields (for ferromagnetic debris)
- **Pros**: No contact
- **Cons**: Only works for magnetic materials

---

## 7. Control Challenges for Non-Cooperative Targets

### What Makes a Target "Non-Cooperative"?

1. **Unknown dynamics**: Tumbling rate unknown
2. **No communication**: Can't command it
3. **Unknown mass properties**: Center of mass, inertia tensor unknown
4. **Unknown shape/structure**: Visual only
5. **Unpredictable**: Solar radiation pressure, atmospheric drag variations

### State Estimation Problem

You need to estimate:
- **Position & velocity** (6 DOF translation)
- **Orientation & angular velocity** (6 DOF rotation)
- **Total: 12-state estimation problem**

**Sensors:**
- **LIDAR**: Range and range-rate
- **Cameras**: Visual tracking, structure from motion
- **Radar**: All-weather tracking

**Estimation Algorithms:**
- Extended Kalman Filter (EKF)
- Unscented Kalman Filter (UKF) - better for nonlinear
- Particle Filters - for highly nonlinear/multimodal

### Tumbling Dynamics

Debris often tumbles due to:
- Collision-induced rotation
- Gravity gradient torque
- Solar radiation pressure
- Magnetic field interaction

**Euler's Equation** (torque-free motion):
```
I₁ω̇₁ = (I₂ - I₃)ω₂ω₃
I₂ω̇₂ = (I₃ - I₁)ω₃ω₁
I₃ω̇₃ = (I₁ - I₂)ω₁ω₂
```

**Result:** Complex 3D tumbling, periodic for rigid bodies

### Detumbling Strategies

**Option 1: Match Rotation**
- Estimate target angular velocity
- Synchronize chaser rotation
- Capture in rotating frame
- **Challenge**: High-rate tumbling → high control effort

**Option 2: Active Detumbling Before Capture**
- Apply external torque (contactless methods)
- Slow down tumbling gradually
- Then capture
- **Challenge**: Takes time, requires precise torque control

**Option 3: Capture While Tumbling**
- Fast capture mechanism
- Accept the momentum transfer
- Detumble combined system afterward
- **Challenge**: Huge impact forces, risk of damage

---

## 8. Deorbiting Techniques

### Natural Decay
- Atmospheric drag gradually lowers orbit
- Decay time = f(altitude, area-to-mass ratio, solar activity)
- **Problem:** Can take decades above 600 km

### Active Deorbiting

**1. Direct Re-entry**
- Use propulsion to lower periapsis below ~80 km
- Atmospheric drag increases exponentially
- Object burns up
- **Δv required:** ~100-200 m/s from LEO

**2. Drag Augmentation**

**a) Drag Sail**
- Deploy large surface area (sail)
- Increases drag force: F_drag = 0.5 ρ v² C_D A
- Accelerates natural decay
- **Pros:** Passive, no propellant
- **Cons:** Attitude stabilization needed

**b) Inflatable Structures**
- Similar to drag sail but lighter
- Can increase area by 10-100×

**c) Electrodynamic Tether**
- Long conducting wire in Earth's magnetic field
- Generates current → Lorentz force → drag
- **Pros:** No propellant, can generate power
- **Cons:** Complex deployment, tether dynamics

**3. Graveyard Orbit**
- Boost to higher orbit (>2000 km)
- Out of useful LEO region
- **Problem:** Doesn't solve long-term issue

### Controlled Re-entry
For large objects (>1 ton):
- Target specific ocean areas (South Pacific)
- Prevent casualty on ground
- Requires precise trajectory control

---

## 9. Key Differences from Terrestrial Robotics

### 1. No Fixed Base
- Manipulator motion → base reaction
- Need **Generalized Jacobian** and **Dynamic Singularities**
- Momentum conservation critical

### 2. No Gravity (Microgravity)
- Objects don't "fall"
- Small forces persist
- Contact forces dominate

### 3. Orbital Dynamics
- Reference frame accelerates (centripetal)
- Coriolis effects in relative motion
- Tidal forces (gravity gradient)

### 4. Propellant Constraints
- Every maneuver costs fuel
- Fuel mass = mission lifetime
- Optimization critical

### 5. Extreme Environment
- Temperature extremes: -150°C to +150°C
- Radiation damages electronics
- Vacuum → no convective cooling
- Atomic oxygen erodes materials

### 6. Communication Delays
- Ground stations: ~1 sec delay
- Requires autonomy
- Can't teleoperate fast maneuvers

### 7. Sensing Challenges
- GPS limited to LEO
- Visual tracking affected by lighting (sun/eclipse)
- No tactile feedback before contact

---

## Control Architecture for ADR Mission

### Typical System Layers

```
┌─────────────────────────────────────┐
│  Mission Planning (Ground/Onboard)  │
│  - Target selection                 │
│  - Trajectory optimization          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Guidance (Path Planning)           │
│  - Collision avoidance              │
│  - Approach corridors               │
│  - Fuel optimization                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Navigation (State Estimation)      │
│  - Sensor fusion (LIDAR, camera)    │
│  - Target pose estimation           │
│  - Relative state (position, vel)   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Control (Low-Level)                │
│  - Attitude control (PD, MPC)       │
│  - Thruster firing logic            │
│  - Manipulator control              │
└───────────────────────────────────────┘
```

### Control Algorithms Relevant for This Problem

**1. PID Control**
- Simple, robust
- Works for attitude stabilization
- May struggle with coupled dynamics

**2. Model Predictive Control (MPC)**
- Optimal for constrained systems
- Handles thruster saturation
- Fuel optimization
- Collision avoidance constraints
- **Highly recommended for proximity ops!**

**3. Sliding Mode Control**
- Robust to uncertainties
- Good for non-cooperative targets
- Chattering can waste fuel

**4. Adaptive Control**
- Estimate unknown target parameters online
- Adjust control gains
- Useful for tumbling targets

**5. Optimal Control (LQR/LQG)**
- Minimize fuel + time
- Well-suited for rendezvous

---

## Recommended Focus Areas for Your Solution

### As a Robotics/Controls Engineer, You Can Contribute:

1. **Robust State Estimation**
   - Develop filters for tumbling target tracking
   - Sensor fusion (vision + LIDAR)
   - Handle occlusions, lighting changes

2. **Trajectory Planning**
   - Fuel-optimal approach trajectories
   - Collision avoidance
   - Reachability analysis

3. **Capture Control**
   - Free-floating base control
   - Impact minimization
   - Post-capture stabilization

4. **Detumbling Strategies**
   - Contactless detumbling (if using ion beam, etc.)
   - Momentum management
   - Combined system control after capture

5. **Fault Tolerance**
   - Thruster failures
   - Sensor degradation
   - Safe-mode behaviors

---

## Key Equations Cheat Sheet

### Orbital Mechanics
```
Orbital velocity:     v = √(μ/r)
Orbital period:       T = 2π√(a³/μ)
Vis-viva equation:    v² = μ(2/r - 1/a)
Hohmann Δv:           Δv₁ = √(μ/r₁)(√(2r₂/(r₁+r₂)) - 1)
```

### Relative Motion (HCW)
```
ẍ - 2nẏ - 3n²x = fx/m
ÿ + 2nẋ = fy/m
z̈ + n²z = fz/m
where n = √(μ/a³)
```

### Attitude Dynamics
```
I·ω̇ + ω × (I·ω) = τ
Quaternion kinematics: q̇ = 0.5 Ω(ω)q
```

### Drag Force
```
F_drag = 0.5 ρ v² C_D A
where ρ = atmospheric density
```

### Tsiolkovsky Rocket Equation
```
Δv = ve ln(m₀/mf)
where ve = exhaust velocity
```

---

## Resources for Further Learning

### Papers (from problem statement)
1. A. Ledkov, V. Aslanov, "Review of contact and contactless active space debris removal approaches", Prog. Aerosp. Sci. 134 (2022) 100858
2. M. Shan, J. Guo, E. Gill, "Review and comparison of active space debris capture and removal methods", Prog. Aero. Sci. 80 (2016) 18-32

### Recommended Textbooks
- **Orbital Mechanics**: "Orbital Mechanics for Engineering Students" by Howard Curtis
- **Spacecraft Dynamics**: "Spacecraft Dynamics and Control" by Marcel Sidi
- **Space Robotics**: "Robotics and Automation in Space" - Yoshida/Umetani

### Online Resources
- ESA Space Debris Office: https://www.esa.int/Space_Safety/Space_Debris
- NASA Orbital Debris Program: https://orbitaldebris.jsc.nasa.gov/

### Software Tools
- **GMAT** (General Mission Analysis Tool): Free trajectory design
- **STK** (Systems Tool Kit): Commercial, orbit visualization
- **Orekit**: Open-source orbital mechanics library (Python/Java)

---

## Summary: Your Robotics Skills Applied to Space

| Terrestrial Robotics | Space Robotics (ADR) |
|----------------------|----------------------|
| Fixed base manipulator | Free-floating base |
| Cooperative targets | Non-cooperative, tumbling |
| Gravity assists | Orbital dynamics dominate |
| Unlimited power | Solar/battery constrained |
| Rich sensing | Limited, delayed sensing |
| Ground-based testing | Simulation + limited space testing |
| Reaction forces to ground | Momentum conservation |

**Your advantage:** Control theory, state estimation, path planning, and optimization translate directly! The physics is different but the mathematical frameworks are similar.

Good luck with your hackathon! 🚀
