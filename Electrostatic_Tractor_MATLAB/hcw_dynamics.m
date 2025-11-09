function dxdt = hcw_dynamics(t, x, acceleration, n)
    % Hill-Clohessy-Wiltshire equations for relative orbital motion
    %
    % Inputs:
    %   t - Time (not used, but required for ode45)
    %   x - State vector [x; y; z; vx; vy; vz] (km, km/s)
    %   acceleration - Control acceleration [ax; ay; az] (km/s^2)
    %   n - Mean motion (rad/s)
    %
    % Outputs:
    %   dxdt - State derivatives
    %
    % HCW Equations:
    %   dx/dt = vx
    %   dy/dt = vy
    %   dz/dt = vz
    %   dvx/dt = 2*n*vy + 3*n^2*x + ax
    %   dvy/dt = -2*n*vx + ay
    %   dvz/dt = -n^2*z + az

    % Extract state
    vx = x(4);
    vy = x(5);
    vz = x(6);

    % Position derivatives (velocity)
    dxdt = zeros(6, 1);
    dxdt(1) = vx;
    dxdt(2) = vy;
    dxdt(3) = vz;

    % Velocity derivatives (HCW dynamics + control)
    dxdt(4) = 2*n*vy + 3*n^2*x(1) + acceleration(1);
    dxdt(5) = -2*n*vx + acceleration(2);
    dxdt(6) = -n^2*x(3) + acceleration(3);
end
