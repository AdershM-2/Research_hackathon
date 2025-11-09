%% COULOMB TRACTOR COMPREHENSIVE TEST SUITE
% Test electrostatic approach with varied parameters
clear; clc; close all;

fprintf('========================================\n');
fprintf('COULOMB TRACTOR TEST SUITE\n');
fprintf('========================================\n\n');

%% TEST CASES
test_cases = struct();

% Case 1: Nominal
test_cases(1).name = 'Nominal';
test_cases(1).altitude = 500;
test_cases(1).initial_dist = 10;
test_cases(1).debris_mass = 10;
test_cases(1).debris_charge = 6e-3;
test_cases(1).max_chaser_charge = 0.01;

% Case 2: Low debris charge
test_cases(2).name = 'Low Debris Charge';
test_cases(2).altitude = 500;
test_cases(2).initial_dist = 10;
test_cases(2).debris_mass = 10;
test_cases(2).debris_charge = 1e-3;  % Much lower
test_cases(2).max_chaser_charge = 0.01;

% Case 3: High debris charge
test_cases(3).name = 'High Debris Charge';
test_cases(3).altitude = 500;
test_cases(3).initial_dist = 10;
test_cases(3).debris_mass = 10;
test_cases(3).debris_charge = 15e-3;  % Higher
test_cases(3).max_chaser_charge = 0.02;  % Need more capacity

% Case 4: Close start
test_cases(4).name = 'Close Start (5km)';
test_cases(4).altitude = 500;
test_cases(4).initial_dist = 5;
test_cases(4).debris_mass = 10;
test_cases(4).debris_charge = 6e-3;
test_cases(4).max_chaser_charge = 0.01;

% Case 5: Far start
test_cases(5).name = 'Far Start (20km)';
test_cases(5).altitude = 500;
test_cases(5).initial_dist = 20;
test_cases(5).debris_mass = 10;
test_cases(5).debris_charge = 10e-3;  % Need higher charge for far distance
test_cases(5).max_chaser_charge = 0.02;

% Case 6: Heavy debris
test_cases(6).name = 'Heavy Debris (20kg)';
test_cases(6).altitude = 500;
test_cases(6).initial_dist = 10;
test_cases(6).debris_mass = 20;
test_cases(6).debris_charge = 6e-3;
test_cases(6).max_chaser_charge = 0.01;

% Case 7: Light debris
test_cases(7).name = 'Light Debris (5kg)';
test_cases(7).altitude = 500;
test_cases(7).initial_dist = 10;
test_cases(7).debris_mass = 5;
test_cases(7).debris_charge = 6e-3;
test_cases(7).max_chaser_charge = 0.01;

% Case 8: Low altitude
test_cases(8).name = 'Low Altitude (400km)';
test_cases(8).altitude = 400;
test_cases(8).initial_dist = 10;
test_cases(8).debris_mass = 10;
test_cases(8).debris_charge = 6e-3;
test_cases(8).max_chaser_charge = 0.01;

% Case 9: High altitude
test_cases(9).name = 'High Altitude (600km)';
test_cases(9).altitude = 600;
test_cases(9).initial_dist = 10;
test_cases(9).debris_mass = 10;
test_cases(9).debris_charge = 6e-3;
test_cases(9).max_chaser_charge = 0.01;

% Case 10: Worst case
test_cases(10).name = 'Worst Case';
test_cases(10).altitude = 600;
test_cases(10).initial_dist = 20;
test_cases(10).debris_mass = 20;
test_cases(10).debris_charge = 3e-3;  % Low charge
test_cases(10).max_chaser_charge = 0.02;

n_cases = length(test_cases);

%% RUN ALL TEST CASES
results = struct();
mu = 398600;
R_earth = 6371;
k_e = 8.99e9;
m_chaser = 100;

fprintf('Running %d test cases...\n\n', n_cases);

for idx = 1:n_cases
    fprintf('========================================\n');
    fprintf('TEST CASE %d: %s\n', idx, test_cases(idx).name);
    fprintf('========================================\n');

    % Extract parameters
    altitude = test_cases(idx).altitude;
    r = R_earth + altitude;
    n = sqrt(mu/r^3);

    initial_dist = test_cases(idx).initial_dist;
    m_debris = test_cases(idx).debris_mass;
    Q_debris = test_cases(idx).debris_charge;
    Q_max = test_cases(idx).max_chaser_charge;

    fprintf('  Altitude: %.0f km\n', altitude);
    fprintf('  Initial distance: %.0f km\n', initial_dist);
    fprintf('  Debris mass: %.0f kg\n', m_debris);
    fprintf('  Debris charge: %.1e C\n', Q_debris);
    fprintf('  Max chaser charge: %.1e C\n\n', Q_max);

    % Initial conditions
    x0 = 0;
    y0 = -initial_dist;
    z0 = 0.1;
    vx0 = 0; vy0 = 0; vz0 = 0;

    % Approach target
    xd = 0; yd = -0.5; zd = 0;  % 500m target

    % Time parameters
    dt = 1;
    t_max = 8000;  % Longer for difficult cases
    N = floor(t_max/dt);

    % Storage
    dist_hist = zeros(1, N);
    vel_hist = zeros(1, N);
    time_hist = (0:N-1)*dt;
    force_hist = zeros(1, N);
    charge_hist = zeros(1, N);

    % State
    x = x0; y = y0; z = z0;
    vx = vx0; vy = vy0; vz = vz0;

    % Control gains
    k_app = 8*n;
    lambda_app = 4*n;

    converged = false;
    conv_time = nan;

    fprintf('  Simulating...\n');

    for i = 1:N
        % Position error
        ex = x - xd;
        ey = y - yd;
        ez = z - zd;
        r_rel = sqrt(ex^2 + ey^2 + ez^2);

        dist_hist(i) = r_rel;
        vel_mag = sqrt(vx^2 + vy^2 + vz^2);
        vel_hist(i) = vel_mag;

        % Desired acceleration
        ax_des = -lambda_app*(vx + k_app*ex);
        ay_des = -lambda_app*(vy + k_app*ey);
        az_des = -lambda_app*(vz + k_app*ez);

        a_des_mag = sqrt(ax_des^2 + ay_des^2 + az_des^2);

        % Required Coulomb force
        if r_rel > 0.001
            F_required = a_des_mag * m_chaser * 1e6;  % Convert to N
            Q_chaser_required = -F_required * (r_rel*1000)^2 / (k_e * Q_debris);
            Q_chaser = max(-Q_max, min(Q_max, Q_chaser_required));
        else
            Q_chaser = 0;
        end

        charge_hist(i) = Q_chaser;

        % Actual Coulomb acceleration
        if r_rel > 0.001
            F_coulomb = k_e * abs(Q_chaser * Q_debris) / (r_rel*1000)^2;
            force_hist(i) = F_coulomb;

            a_coulomb_mag = F_coulomb / (m_chaser*1e3) / 1000;  % km/s²

            if Q_chaser * Q_debris < 0
                % Attraction
                a_coulomb_x = -a_coulomb_mag * ex / r_rel;
                a_coulomb_y = -a_coulomb_mag * ey / r_rel;
                a_coulomb_z = -a_coulomb_mag * ez / r_rel;
            else
                % Repulsion
                a_coulomb_x = a_coulomb_mag * ex / r_rel;
                a_coulomb_y = a_coulomb_mag * ey / r_rel;
                a_coulomb_z = a_coulomb_mag * ez / r_rel;
            end
        else
            F_coulomb = 0;
            force_hist(i) = 0;
            a_coulomb_x = 0; a_coulomb_y = 0; a_coulomb_z = 0;
        end

        % HCW dynamics
        ax = 3*n^2*x + 2*n*vy + a_coulomb_x;
        ay = -2*n*vx + a_coulomb_y;
        az = -n^2*z + a_coulomb_z;

        % Simple Euler integration (faster for testing)
        vx = vx + dt*ax;
        vy = vy + dt*ay;
        vz = vz + dt*az;

        x = x + dt*vx;
        y = y + dt*vy;
        z = z + dt*vz;

        % Check convergence
        if r_rel*1000 < 600 && vel_mag*1000 < 1.0
            if ~converged
                converged = true;
                conv_time = time_hist(i);
                fprintf('  ✓ Converged at t = %.1f min\n', conv_time/60);
            end
        end

        % Check if diverging badly
        if r_rel > initial_dist*2
            fprintf('  ✗ Diverging - stopping\n');
            break;
        end
    end

    % Trim histories
    dist_hist = dist_hist(1:i);
    vel_hist = vel_hist(1:i);
    time_hist = time_hist(1:i);
    force_hist = force_hist(1:i);
    charge_hist = charge_hist(1:i);

    % Store results
    results(idx).name = test_cases(idx).name;
    results(idx).converged = converged;
    results(idx).final_dist = dist_hist(end);  % km
    results(idx).final_vel = vel_hist(end);   % km/s
    results(idx).time_to_conv = conv_time;
    results(idx).mean_force = mean(force_hist);
    results(idx).mean_charge = mean(abs(charge_hist));
    results(idx).dist_hist = dist_hist;
    results(idx).vel_hist = vel_hist;
    results(idx).time_hist = time_hist;

    fprintf('  Final distance: %.1f m\n', dist_hist(end)*1000);
    fprintf('  Final velocity: %.3f m/s\n', vel_hist(end)*1000);
    fprintf('  Mean force: %.2e N\n', results(idx).mean_force);
    fprintf('  Mean charge: %.2e C\n\n', results(idx).mean_charge);
end

%% SUMMARY
fprintf('========================================\n');
fprintf('TEST SUITE SUMMARY\n');
fprintf('========================================\n\n');

success_count = sum([results.converged]);
fprintf('Success rate: %d/%d (%.1f%%)\n\n', success_count, n_cases, ...
        100*success_count/n_cases);

fprintf('%-25s %12s %12s %12s %10s\n', 'Test Case', 'Final Dist', 'Final Vel', 'Conv Time', 'Status');
fprintf('%s\n', repmat('-', 1, 85));

for idx = 1:n_cases
    status_str = 'PASS';
    if ~results(idx).converged
        status_str = 'FAIL';
    end

    if isnan(results(idx).time_to_conv)
        time_str = 'N/A';
    else
        time_str = sprintf('%.1f min', results(idx).time_to_conv/60);
    end

    fprintf('%-25s %10.2f m %10.4f m/s %12s %10s\n', ...
            results(idx).name, ...
            results(idx).final_dist*1000, ...
            results(idx).final_vel*1000, ...
            time_str, ...
            status_str);
end

fprintf('\n');

%% VISUALIZATION
fprintf('Generating plots...\n');

% Create test results folder
test_results_folder = 'coulomb_test_results';
if ~exist(test_results_folder, 'dir')
    mkdir(test_results_folder);
end

figure('Position', [50 50 1600 1000], 'Color', 'w');

% Distance convergence for all cases
subplot(2,2,1)
colors = lines(n_cases);
hold on
for idx = 1:n_cases
    if results(idx).converged
        plot(results(idx).time_hist/60, results(idx).dist_hist*1000, ...
             'LineWidth', 2, 'Color', colors(idx,:));
    else
        plot(results(idx).time_hist/60, results(idx).dist_hist*1000, ...
             '--', 'LineWidth', 1.5, 'Color', colors(idx,:));
    end
end
grid on
xlabel('Time (min)', 'FontWeight', 'bold')
ylabel('Distance (m)', 'FontWeight', 'bold')
title('Distance Convergence - All Cases', 'FontWeight', 'bold')
set(gca, 'YScale', 'log')

% Velocity convergence
subplot(2,2,2)
hold on
for idx = 1:n_cases
    if results(idx).converged
        plot(results(idx).time_hist/60, results(idx).vel_hist*1000, ...
             'LineWidth', 2, 'Color', colors(idx,:));
    else
        plot(results(idx).time_hist/60, results(idx).vel_hist*1000, ...
             '--', 'LineWidth', 1.5, 'Color', colors(idx,:));
    end
end
grid on
xlabel('Time (min)', 'FontWeight', 'bold')
ylabel('Velocity (m/s)', 'FontWeight', 'bold')
title('Velocity Convergence - All Cases', 'FontWeight', 'bold')
set(gca, 'YScale', 'log')

% Final distance comparison
subplot(2,2,3)
final_dists = [results.final_dist]*1000;  % Convert to meters
bar(1:n_cases, final_dists, 'FaceColor', [0.2 0.6 0.8])
hold on
plot([0, n_cases+1], [600, 600], 'r--', 'LineWidth', 2)
grid on
xlabel('Test Case', 'FontWeight', 'bold')
ylabel('Final Distance (m)', 'FontWeight', 'bold')
title('Final Distance Accuracy', 'FontWeight', 'bold')
set(gca, 'XTick', 1:n_cases, 'XTickLabel', 1:n_cases)
xlim([0, n_cases+1])

% Mean Coulomb force
subplot(2,2,4)
mean_forces = [results.mean_force]*1e3;  % Convert to mN
bar(1:n_cases, mean_forces, 'FaceColor', [0.8 0.4 0.2])
grid on
xlabel('Test Case', 'FontWeight', 'bold')
ylabel('Mean Coulomb Force (mN)', 'FontWeight', 'bold')
title('Electrostatic Control Force', 'FontWeight', 'bold')
set(gca, 'XTick', 1:n_cases, 'XTickLabel', 1:n_cases)
xlim([0, n_cases+1])

saveas(gcf, fullfile(test_results_folder, 'coulomb_test_results.png'));
saveas(gcf, fullfile(test_results_folder, 'coulomb_test_results.fig'));
print(gcf, fullfile(test_results_folder, 'coulomb_test_results_highres.png'), '-dpng', '-r300');

fprintf('\n');
fprintf('Results saved to: %s/\n', test_results_folder);

%% EXPORT CSV
csv_file = fullfile(test_results_folder, 'coulomb_test_summary.csv');
fid = fopen(csv_file, 'w');
fprintf(fid, 'Test Case,Final Distance (m),Final Velocity (m/s),Convergence Time (min),Mean Force (mN),Status\n');
for idx = 1:n_cases
    status_str = 'PASS';
    if ~results(idx).converged
        status_str = 'FAIL';
    end

    if isnan(results(idx).time_to_conv)
        time_val = -1;
    else
        time_val = results(idx).time_to_conv/60;
    end

    fprintf(fid, '%s,%.2f,%.4f,%.1f,%.2f,%s\n', ...
            results(idx).name, ...
            results(idx).final_dist*1000, ...
            results(idx).final_vel*1000, ...
            time_val, ...
            results(idx).mean_force*1e3, ...
            status_str);
end
fclose(fid);

fprintf('CSV exported: %s\n\n', csv_file);

fprintf('========================================\n');
fprintf('COULOMB TRACTOR TEST SUITE COMPLETE\n');
fprintf('========================================\n');
