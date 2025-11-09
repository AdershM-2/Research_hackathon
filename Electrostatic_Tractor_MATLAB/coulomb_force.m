function [F_vec, F_mag, acceleration] = coulomb_force(q_chaser, q_debris, position_vector, mass_chaser, k_coulomb)
    % Calculate Coulomb electrostatic force between chaser and debris
    %
    % Inputs:
    %   q_chaser - Charge on chaser spacecraft (C)
    %   q_debris - Charge on debris (C)
    %   position_vector - Vector from chaser to debris [x; y; z] (km)
    %   mass_chaser - Mass of chaser (kg)
    %   k_coulomb - Coulomb's constant (N*m^2/C^2)
    %
    % Outputs:
    %   F_vec - Force vector (N) in [x; y; z]
    %   F_mag - Force magnitude (N)
    %   acceleration - Acceleration of chaser (km/s^2)

    % Distance in meters
    distance_m = norm(position_vector) * 1000; % Convert km to m

    % Safety check: minimum distance
    if distance_m < 0.001  % 1 mm minimum
        distance_m = 0.001;
    end

    % Unit vector from chaser to debris
    r_hat = position_vector / norm(position_vector);

    % Coulomb force magnitude (N)
    % F = k * |q1 * q2| / r^2
    F_mag = k_coulomb * abs(q_chaser * q_debris) / (distance_m^2);

    % Force direction
    % If q1*q2 < 0 (opposite charges): attractive force (towards debris)
    % If q1*q2 > 0 (same charges): repulsive force (away from debris)
    if q_chaser * q_debris < 0
        % Attractive - force points toward debris
        F_vec_N = F_mag * r_hat;
    else
        % Repulsive - force points away from debris
        F_vec_N = -F_mag * r_hat;
    end

    % Convert force from Newtons to km/s^2 acceleration
    % F (N) = m (kg) * a (m/s^2)
    % a (km/s^2) = F (N) / m (kg) / 1000
    acceleration = F_vec_N / mass_chaser / 1000; % km/s^2

    % Force vector in Newtons
    F_vec = F_vec_N;
end
