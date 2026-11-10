# Unit 12 source map (source-reader; verify).
- v66 tumbling box x'=yz, y'=-2xz, z'=xy (frames 0030, 0090), ode23, start near (1,0,0) normalised; middle axis y unstable; unit sphere conserved. Book PDF 188-189; general a yz, b xz, c xy with moments.
- v67 Lotka-Volterra y1'=y1(1-y2/mu2), y2'=-y2(1-y1/mu1) (frames 0030/0150); critical (mu1,mu2); Jacobian ±i, period ~2pi locally; ode45 [0,25], mu=(300,200), eta=(400,100); period ~6.5; pitstop event. Book PDF 185-186.
- v68 Lorenz x'=sigma(y-x), y'=rho x - y - xz, z'=xy-beta z, sigma=10, rho=28, beta=8/3 (frame 0090). Matrix A(y): [-beta 0 eta; 0 -sigma sigma; -eta rho -1], critical eta=±sqrt(beta(rho-1)), (rho-1, eta, eta). y0 = critical + [3 2 -4]', [0,30]. rho menu 28, 99.65, 100.5, 160, 350; rho=160 periodic.
