% Test Electrostatic Tractor with Various Parameters
% IIT Kanpur Research Hackathon 2025

clear; clc; close all;

fprintf('========================================\n');
fprintf('ELECTROSTATIC TRACTOR TESTING\n');
fprintf('IIT Kanpur Research Hackathon 2025\n');
fprintf('========================================\n\n');

%% Load Configuration
config = config_electrostatic();

%% Test 1: Baseline Case (Default Parameters)
fprintf('\n### TEST 1: BASELINE CASE ###\n');
results_baseline = simulate_approach(config, ...
    config.phase2.initial_separation, ...
    config.phase2.final_separation, ...
    config.phase2.duration, ...
    config.phase2.dt);

%% Test 2: Different Debris Charges
fprintf('\n\n### TEST 2: DIFFERENT DEBRIS CHARGES ###\n');
charges = [-0.01, -0.001, -0.0001, 0.0001, 0.001, 0.01];
results_charges = cell(length(charges), 1);

for i = 1:length(charges)
    fprintf('\n--- Testing debris charge: %.5f C ---\n', charges(i));
    config_test = config;
    config_test.debris.charge = charges(i);
    config_test.sim.verbose = false;

    results_charges{i} = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        config.phase2.duration, ...
        config.phase2.dt);

    if results_charges{i}.success
        fprintf('✓ Success! Energy used: %.2f MJ\n', results_charges{i}.energy_used/1e6);
    else
        fprintf('✗ Did not converge. Final error: %.3f km\n', results_charges{i}.final_pos_error);
    end
end

%% Test 3: Different Initial Separations
fprintf('\n\n### TEST 3: DIFFERENT INITIAL SEPARATIONS ###\n');
separations = [1.0, 5.0, 10.0, 20.0, 50.0]; % km
results_separations = cell(length(separations), 1);

for i = 1:length(separations)
    fprintf('\n--- Testing initial separation: %.1f km ---\n', separations(i));
    config_test = config;
    config_test.sim.verbose = false;

    results_separations{i} = simulate_approach(config_test, ...
        separations(i), ...
        config.phase2.final_separation, ...
        config.phase2.duration, ...
        config.phase2.dt);

    if results_separations{i}.success
        fprintf('✓ Converged! Time: %.1f s\n', results_separations{i}.total_time);
    else
        fprintf('⚠ Partial convergence. Final error: %.3f km\n', results_separations{i}.final_pos_error);
    end
end

%% Test 4: Different Durations (Mission Time Sensitivity)
fprintf('\n\n### TEST 4: DIFFERENT MISSION DURATIONS ###\n');
durations = [1800, 3600, 7200, 14400]; % seconds
results_durations = cell(length(durations), 1);

for i = 1:length(durations)
    fprintf('\n--- Testing duration: %.1f min ---\n', durations(i)/60);
    config_test = config;
    config_test.sim.verbose = false;

    results_durations{i} = simulate_approach(config_test, ...
        config.phase2.initial_separation, ...
        config.phase2.final_separation, ...
        durations(i), ...
        config.phase2.dt);

    if results_durations{i}.success
        fprintf('✓ Converged! Δv used: %.2f m/s\n', results_durations{i}.total_dv*1000);
    else
        fprintf('⚠ Did not converge. Final error: %.3f km\n', results_durations{i}.final_pos_error);
    end
end

%% Test 5: Proximity Operations (Close Range)
fprintf('\n\n### TEST 5: PROXIMITY OPERATIONS (50m → 5m) ###\n');
config_prox = config;
config_prox.sim.verbose = true;
results_proximity = simulate_approach(config_prox, ...
    config.phase3.initial_separation / 1000, ... % Convert m to km
    config.phase3.final_separation / 1000, ...   % Convert m to km
    config.phase3.duration, ...
    config.phase3.dt);

%% Summary Report
fprintf('\n\n========================================\n');
fprintf('SUMMARY REPORT\n');
fprintf('========================================\n\n');

fprintf('TEST 1 - BASELINE:\n');
fprintf('  Convergence: %s\n', mat2str(results_baseline.success));
fprintf('  Final error: %.3f m\n', results_baseline.final_pos_error*1000);
fprintf('  Energy used: %.2f MJ\n', results_baseline.energy_used/1e6);

fprintf('\nTEST 2 - DEBRIS CHARGES:\n');
success_count = sum(cellfun(@(x) x.success, results_charges));
fprintf('  Success rate: %d/%d\n', success_count, length(charges));
fprintf('  Charge range tested: [%.4f, %.4f] C\n', min(charges), max(charges));

fprintf('\nTEST 3 - INITIAL SEPARATIONS:\n');
success_count = sum(cellfun(@(x) x.success, results_separations));
fprintf('  Success rate: %d/%d\n', success_count, length(separations));
fprintf('  Separation range: [%.1f, %.1f] km\n', min(separations), max(separations));

fprintf('\nTEST 4 - MISSION DURATIONS:\n');
success_count = sum(cellfun(@(x) x.success, results_durations));
fprintf('  Success rate: %d/%d\n', success_count, length(durations));
fprintf('  Duration range: [%.1f, %.1f] min\n', min(durations)/60, max(durations)/60);

fprintf('\nTEST 5 - PROXIMITY OPERATIONS:\n');
fprintf('  Convergence: %s\n', mat2str(results_proximity.success));
fprintf('  Final error: %.3f m\n', results_proximity.final_pos_error*1000);

fprintf('\n========================================\n');
fprintf('ALL TESTS COMPLETE\n');
fprintf('========================================\n');

%% Save Results
save('electrostatic_tractor_test_results.mat', ...
     'results_baseline', 'results_charges', 'results_separations', ...
     'results_durations', 'results_proximity');

fprintf('\nResults saved to: electrostatic_tractor_test_results.mat\n');
