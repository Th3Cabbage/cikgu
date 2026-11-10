# Unit 4 source map (source-reader; verify). Printed = PDF - 12 (header 118 at PDF 130).
- v20 [00:00] RLC loop, source V e^{iwt}. [02:00] L I' + R I + (1/C) int I = V e^{iwt} (frame 0450). [05:00] L,R,1/C ~ m,b,k. [06:30] I=W e^{iwt}: (iwL + R + 1/(iwC))W=V, Z=R+i(wL-1/(wC)) (frame 0690). [11:30] |Z|^2=R^2+(wL-1/(wC))^2. [13:30] KCL/KVL, incidence matrix later. Book PDF 130-136 (Ex: R=10, L=0.1, C=1e-4; tuning wL=1/(wC)).
- v21 [00:00] y''+y'+y=f. [01:00] e^{st}: Y=1/(s^2+s+1). [02:30] f=t: yp=t-1 (frames 0570/0870). [05:30] sin t: C1 cos + C2 sin. [07:30] t sin t: (a+bt)cos+(c+dt)sin. [12:00] resonance y''-y=e^t, try Y t e^t.
- v22 [01:00] y''-3y'+2y=4t, null e^t, e^{2t} (frame 0210), yp=3+2t. [04:00] 4t^2: a+bt+ct^2. [04:30] Y=1/(s^2-3s+2). [07:30] s=1,2 resonance -> t e^{st}. [12:30] t cos wt: 4 coefficients.
- v23 [04:00] y=c1(t)y1+c2(t)y2, c1'y1+c2'y2=0, c1'y1'+c2'y2'=f (frame 0450). [05:00] y = -y1 int y2 f/W + y2 int y1 f/W, W=y1y2'-y2y1'. [08:30] y=e^{s1 t},e^{s2 t}: W=(s2-s1)e^{(s1+s2)t} (frame 1050). [12:00] y = int_0^t g(t-T) f(T) dT, g=(e^{s2 t}-e^{s1 t})/(s2-s1).
- Book: PDF 143 y''+4y'+3y=e^{-t}+t -> yp=(1/2)t e^{-t}+t/3-4/9; PDF 146 y''+y=t by VP gives t.
- ASR: "runski"=Wronskian, "Mohler"=Moler, "oil's"=Euler's.
