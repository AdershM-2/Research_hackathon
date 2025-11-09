% Comprehensive Test Suite: Orbital Conditions & Charge Levels
% IIT Kanpur Research Hackathon 2025
% Tests electrostatic tractor across varied mission scenarios

clear; clc; close all;

fprintf('========================================\n');
fprintf('COMPREHENSIVE TEST SUITE\n');
fprintf('Electrostatic Tractor Performance\n');
fprintf('IIT Kanpur Research Hackathon 2025\n');
fprintf('========================================\n\n');

% Create results directory
results_dir = '../Electrostatic_Test_Results';
if ~exist(results_dir, 'dir')
    mkdir(results_dir);
end

%% Load Base Configuration
config = config_electrostatic();

%% TEST SUITE 1: DIFFERENT ORBITAL ALTITUDES
fprintf('\n### TEST SUITE 1: ORBITAL ALTITUDE VARIATION ###\n');
fprintf('Testing debris at different orbital altitudes\n\n');

altitudes = [400, 500, 600, 800, 1000]; % km
results_altitudes = struct();

for i = 1:length(altitudes)
    fprintf('--- Test 1.%d: Debris altitude = %d km ---\n', i, altitudes(i));

    config_test = config;
    config_test.debris.altitude = altitudes(i);
    config_test.debris.orbit_radius = config.R_earth + altitudes(i);
    config_test.sim.verbose = false;

    % Adjust mission duration based on altitude difference
    alt_diff = abs(altitudes(i) - config.chaser.altitude);
    duration = 7200; % base 2 hours
    if alt_diff > 400
        duration = 14400; % 4 hours for large altitude difference
    end

    results = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        duration, config.phase2.dt);

    results_altitudes(i).altitude = altitudes(i);
    results_altitudes(i).success = results.success;
    results_altitudes(i).final_error = results.final_pos_error;
    results_altitudes(i).total_dv = results.total_dv;
    results_altitudes(i).energy_used = results.energy_used;
    results_altitudes(i).time = results.total_time;

    fprintf('  Success: %s | Error: %.2f m | Energy: %.2f MJ\n', ...
            mat2str(results.success), results.final_pos_error*1000, ...
            results.energy_used/1e6);
end

% Save results
save([results_dir '/test1_orbital_altitudes.mat'], 'results_altitudes', 'altitudes');

%% TEST SUITE 2: CHASER CHARGE CAPACITY VARIATION
fprintf('\n\n### TEST SUITE 2: CHASER CHARGE CAPACITY ###\n');
fprintf('Testing different maximum charge levels on chaser\n\n');

charge_levels = [0.1, 0.5, 1.0, 2.0, 5.0]; % Coulombs
results_charges = struct();

for i = 1:length(charge_levels)
    fprintf('--- Test 2.%d: Chaser max charge = %.1f C ---\n', i, charge_levels(i));

    config_test = config;
    config_test.chaser.charge_max = charge_levels(i);
    config_test.chaser.charge_min = -charge_levels(i);
    config_test.sim.verbose = false;

    results = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        config.phase2.duration, config.phase2.dt);

    results_charges(i).charge_max = charge_levels(i);
    results_charges(i).success = results.success;
    results_charges(i).final_error = results.final_pos_error;
    results_charges(i).total_dv = results.total_dv;
    results_charges(i).energy_used = results.energy_used;
    results_charges(i).max_force = max(results.forces);
    results_charges(i).avg_force = mean(results.forces);

    fprintf('  Success: %s | Error: %.2f m | Max Force: %.2e N\n', ...
            mat2str(results.success), results.final_pos_error*1000, ...
            results_charges(i).max_force);
end

% Save results
save([results_dir '/test2_charge_capacity.mat'], 'results_charges', 'charge_levels');

%% TEST SUITE 3: ORBITAL PLANE DIFFERENCES (Inclination)
fprintf('\n\n### TEST SUITE 3: ORBITAL INCLINATION ###\n');
fprintf('Testing different orbital inclinations\n\n');

inclinations = [0, 28.5, 51.6, 75, 98]; % degrees (Equatorial, Cape, ISS, Polar, SSO)
results_inclinations = struct();

for i = 1:length(inclinations)
    fprintf('--- Test 3.%d: Inclination = %.1f deg ---\n', i, inclinations(i));

    config_test = config;
    config_test.chaser.inclination = inclinations(i);
    config_test.debris.inclination = inclinations(i);
    config_test.sim.verbose = false;

    results = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        config.phase2.duration, config.phase2.dt);

    results_inclinations(i).inclination = inclinations(i);
    results_inclinations(i).success = results.success;
    results_inclinations(i).final_error = results.final_pos_error;
    results_inclinations(i).total_dv = results.total_dv;
    results_inclinations(i).energy_used = results.energy_used;

    fprintf('  Success: %s | Error: %.2f m | Δv: %.2f m/s\n', ...
            mat2str(results.success), results.final_pos_error*1000, ...
            results.total_dv*1000);
end

% Save results
save([results_dir '/test3_inclinations.mat'], 'results_inclinations', 'inclinations');

%% TEST SUITE 4: DEBRIS CHARGE VARIATION (Extended Range)
fprintf('\n\n### TEST SUITE 4: DEBRIS CHARGE VARIATION ###\n');
fprintf('Testing wide range of debris charge levels\n\n');

debris_charges = [-1.0, -0.1, -0.01, -0.001, 0.001, 0.01, 0.1, 1.0]; % Coulombs
results_debris_charges = struct();

for i = 1:length(debris_charges)
    fprintf('--- Test 4.%d: Debris charge = %.3f C ---\n', i, debris_charges(i));

    config_test = config;
    config_test.debris.charge = debris_charges(i);
    config_test.sim.verbose = false;

    results = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        config.phase2.duration, config.phase2.dt);

    results_debris_charges(i).debris_charge = debris_charges(i);
    results_debris_charges(i).success = results.success;
    results_debris_charges(i).final_error = results.final_pos_error;
    results_debris_charges(i).total_dv = results.total_dv;
    results_debris_charges(i).energy_used = results.energy_used;
    results_debris_charges(i).max_force = max(results.forces);

    fprintf('  Success: %s | Error: %.2f m | Energy: %.2f MJ\n', ...
            mat2str(results.success), results.final_pos_error*1000, ...
            results.energy_used/1e6);
end

% Save results
save([results_dir '/test4_debris_charges.mat'], 'results_debris_charges', 'debris_charges');

%% TEST SUITE 5: COMBINED STRESS TEST
fprintf('\n\n### TEST SUITE 5: COMBINED STRESS TEST ###\n');
fprintf('Testing extreme combinations\n\n');

stress_tests = {
    % [altitude, chaser_charge, debris_charge, duration, name]
    [400, 0.5, -0.001, 7200, 'Low altitude, low charge'];
    [1000, 1.0, -0.01, 14400, 'High altitude, nominal'];
    [600, 5.0, -0.1, 7200, 'Nominal altitude, high charge'];
    [800, 0.1, -0.0001, 10800, 'High altitude, very low charge'];
    [500, 2.0, -0.05, 7200, 'Mid altitude, high charge'];
};

results_stress = struct();

for i = 1:size(stress_tests, 1)
    test = stress_tests{i, :};
    fprintf('--- Test 5.%d: %s ---\n', i, test{5});
    fprintf('    Alt=%d km, q_chaser=%.1f C, q_debris=%.4f C\n', ...
            test{1}, test{2}, test{3});

    config_test = config;
    config_test.debris.altitude = test{1};
    config_test.debris.orbit_radius = config.R_earth + test{1};
    config_test.chaser.charge_max = test{2};
    config_test.chaser.charge_min = -test{2};
    config_test.debris.charge = test{3};
    config_test.sim.verbose = false;

    results = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        test{4}, config.phase2.dt);

    results_stress(i).name = test{5};
    results_stress(i).altitude = test{1};
    results_stress(i).chaser_charge = test{2};
    results_stress(i).debris_charge = test{3};
    results_stress(i).success = results.success;
    results_stress(i).final_error = results.final_pos_error;
    results_stress(i).total_dv = results.total_dv;
    results_stress(i).energy_used = results.energy_used;
    results_stress(i).time = results.total_time;

    fprintf('  Success: %s | Error: %.2f m | Time: %.1f min\n', ...
            mat2str(results.success), results.final_pos_error*1000, ...
            results.total_time/60);
end

% Save results
save([results_dir '/test5_stress_tests.mat'], 'results_stress', 'stress_tests');

%% TEST SUITE 6: ENERGY EFFICIENCY AT DIFFERENT RANGES
fprintf('\n\n### TEST SUITE 6: APPROACH DISTANCE VARIATION ###\n');
fprintf('Testing energy efficiency at different starting distances\n\n');

approach_distances = [1, 3, 5, 10, 20, 50]; % km
results_distances = struct();

for i = 1:length(approach_distances)
    fprintf('--- Test 6.%d: Initial distance = %.1f km ---\n', i, approach_distances(i));

    config_test = config;
    config_test.sim.verbose = false;

    % Adjust duration based on distance
    duration = 7200 * (approach_distances(i) / 10); % Scale with distance

    results = simulate_approach(config_test, ...
        approach_distances(i), ...
        config.phase2.final_separation, ...
        duration, config.phase2.dt);

    results_distances(i).distance = approach_distances(i);
    results_distances(i).success = results.success;
    results_distances(i).final_error = results.final_pos_error;
    results_distances(i).total_dv = results.total_dv;
    results_distances(i).energy_used = results.energy_used;
    results_distances(i).time = results.total_time;
    results_distances(i).efficiency = results.total_dv / (results.energy_used/1e6); % m/s per MJ

    fprintf('  Success: %s | Δv: %.2f m/s | Efficiency: %.1f m/s/MJ\n', ...
            mat2str(results.success), results.total_dv*1000, ...
            results_distances(i).efficiency);
end

% Save results
save([results_dir '/test6_approach_distances.mat'], 'results_distances', 'approach_distances');

%% GENERATE SUMMARY REPORT
fprintf('\n\n========================================\n');
fprintf('COMPREHENSIVE TEST SUITE SUMMARY\n');
fprintf('========================================\n\n');

fprintf('TEST SUITE 1 - ORBITAL ALTITUDES:\n');
success_rate = sum([results_altitudes.success]) / length(results_altitudes) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_altitudes.success]), length(results_altitudes));
fprintf('  Altitude range: %d - %d km\n', min(altitudes), max(altitudes));
energy_range = [min([results_altitudes.energy_used]), max([results_altitudes.energy_used])];
fprintf('  Energy range: %.2f - %.2f MJ\n', energy_range(1)/1e6, energy_range(2)/1e6);

fprintf('\nTEST SUITE 2 - CHASER CHARGE CAPACITY:\n');
success_rate = sum([results_charges.success]) / length(results_charges) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_charges.success]), length(results_charges));
fprintf('  Charge range: %.1f - %.1f C\n', min(charge_levels), max(charge_levels));
force_range = [min([results_charges.max_force]), max([results_charges.max_force])];
fprintf('  Force range: %.2e - %.2e N\n', force_range(1), force_range(2));

fprintf('\nTEST SUITE 3 - ORBITAL INCLINATIONS:\n');
success_rate = sum([results_inclinations.success]) / length(results_inclinations) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_inclinations.success]), length(results_inclinations));
fprintf('  Inclination range: %.1f - %.1f deg\n', min(inclinations), max(inclinations));

fprintf('\nTEST SUITE 4 - DEBRIS CHARGE VARIATION:\n');
success_rate = sum([results_debris_charges.success]) / length(results_debris_charges) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_debris_charges.success]), length(results_debris_charges));
fprintf('  Charge range: %.3f - %.3f C\n', min(debris_charges), max(debris_charges));

fprintf('\nTEST SUITE 5 - STRESS TESTS:\n');
success_rate = sum([results_stress.success]) / length(results_stress) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_stress.success]), length(results_stress));

fprintf('\nTEST SUITE 6 - APPROACH DISTANCES:\n');
success_rate = sum([results_distances.success]) / length(results_distances) * 100;
fprintf('  Success rate: %.0f%% (%d/%d)\n', success_rate, sum([results_distances.success]), length(results_distances));
fprintf('  Distance range: %.1f - %.1f km\n', min(approach_distances), max(approach_distances));

fprintf('\n========================================\n');
fprintf('ALL TESTS COMPLETE\n');
fprintf('Results saved to: %s\n', results_dir);
fprintf('========================================\n');

%% Save comprehensive summary
save([results_dir '/comprehensive_test_summary.mat'], ...
     'results_altitudes', 'results_charges', 'results_inclinations', ...
     'results_debris_charges', 'results_stress', 'results_distances');

fprintf('\nComprehensive summary saved to: comprehensive_test_summary.mat\n');
