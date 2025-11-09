function [u_desired, K] = lqr_controller(state, target_state, n, Q, R)
    % LQR controller for HCW dynamics
    %
    % Inputs:
    %   state - Current state [x; y; z; vx; vy; vz] (km, km/s)
    %   target_state - Target state [x; y; z; vx; vy; vz] (km, km/s)
    %   n - Mean motion (rad/s)
    %   Q - State cost matrix (6x6)
    %   R - Control cost matrix (3x3)
    %
    % Outputs:
    %   u_desired - Desired control acceleration [ax; ay; az] (km/s^2)
    %   K - LQR gain matrix (3x6)

    % HCW state-space matrices
    % dx/dt = A*x + B*u
    A = [0,    0,    0,     1,    0,    0;
         0,    0,    0,     0,    1,    0;
         0,    0,    0,     0,    0,    1;
         3*n^2, 0,   0,     0,    2*n,  0;
         0,    0,    0,    -2*n,  0,    0;
         0,    0,   -n^2,   0,    0,    0];

    B = [0, 0, 0;
         0, 0, 0;
         0, 0, 0;
         1, 0, 0;
         0, 1, 0;
         0, 0, 1];

    % Compute LQR gain
    [K, ~, ~] = lqr(A, B, Q, R);

    % Error state
    error_state = state - target_state;

    % Control law: u = -K*(x - x_target)
    u_desired = -K * error_state;
end
