# Unit 2 source map (source-reader, Sonnet; to be verified by the architect)

Frames read: v11 0330, 0390; v12 1230; v13 0270, 0750. Book offset here: printed = PDF - 12 (PDF 65 = p.53).

- v11 00:00 y' = ay - by^2 (competition y*y). Book PDF 65.
- v11 01:30 z = 1/y gives z' = -az + b (linear). PDF 66.
- v11 03:30 y(t) = a / (d e^{-at} + b), d from y(0) (d = a/y(0) - b). PDF 66.
- v11 05:30 S-curve; t->inf gives a/b, t->-inf gives 0. Book Fig 1.9 (a=b=1, d=3, inflection y=a/2b).
- v11 08:30 steady states Y=0 (unstable), Y=a/b (stable, 11:30). v11 12:00 preview y'=f(y).
- Book only: y' = ay(1-y/K); partial fractions PDF 68-69; harvesting y'=4y-y^2-3 (steady 1, 3; critical h=4 double root 2) PDF 71-72.
- v12 00:00 y'=f(y), f(Y)=0, stable definition. 02:00 examples y'=ay; y-y^2 (0,1); y-y^3 (0,±1) (board 1230).
- v12 04:00 linear: stable iff a<0. 05:30 test df/dy<0 at Y: y-y^2 f'=1-2y (+1 at 0, -1 at 1); y-y^3 f'=1-3y^2 (+1 at 0, -2 at ±1). PDF 70.
- v12 09:30 linear approximation f(y)-f(Y) ≈ f'(Y)(y-Y), y-Y ~ e^{ct}; c=0 undecided (13:00).
- v12 14:00 tumbling book (from Prof. Tokieda): thin and widest axes stable, middle unstable; returns in 3D. Not in book pages.
- v12 16:30 stability line (board "Stability line"), arrows to ±1, away from 0.
- v13 00:00 separable y' = g(t)/f(y): ∫f(y)dy = ∫g dt. y'=y+t is not separable. PDF 77 (p.65).
- v13 03:00 y'=t/y: y = sqrt(y(0)^2 + t^2). Book Ex. 1 PDF 77.
- v13 05:30 y(0)=0: y=t and y=-t both solve it (non-unique) (board).
- v13 07:30 logistic by separation, partial fractions A/y + B/(1-y) (board 0750); z=1/y faster (11:30).
- Book only: Ex 2 y'=2ty => y(0)e^{t^2}; Ex 3 y'=ay+q by separation; exact equations PDF 79-83.
- Caption fixes: "12 t^2" = (1/2)t^2; "capital y equal z" = Y=0; "y = y cubed" = y - y^3 = 0.
- Animation ideas: S-curves between 0 and a/b; stability line with sign of f' on parabola f(y); branching y=±t; tumbling book.
