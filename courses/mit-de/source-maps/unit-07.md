# Unit 7 source map (source-reader, Sonnet; verify)

Frames spot-checked: v35 0150; v36 0390; v37 0810; v38 0570; v39 0870. Book: 5.1 PDF 263-272; 5.4 PDF 297-311; 5.5 PDF ~311-324; 5.6 PDF 325-336. Printed = PDF - 12 (the agent used -11; recompute its printed numbers).

- v35 00:00 Av = combination of columns. A = [[1,1,2],[1,2,3],[1,2,3]] (frame 0150). 03:00 col3 = col1+col2 => C(A) is a plane; changing to 11 gives R^3 (caption, unverified). 04:30 Av=b solvable iff b in C(A). 06:30 N(A) line through (-1,-1,1); dims 2+1=3. 10:00 complete solution v = v_p + v_n (b values unverified; v_p=(2,1,0)?).
- v36 00:00 a1=(2,1,5), a2=(4,2,0) (top entries cut off on frame 0390; captions "215", "420"). 02:30 a3=a1+a2=(6,3,5) dependent. 04:00 a3=(1,0,0) independent => basis. 05:30 A=[[2,4,1],[1,2,0],[5,0,0]], Av=0 only v=0. 08:00 subspaces of R^3 dims 0-3. 09:30 every basis same size = dimension.
- v37 A=[[1,2,3],[4,5,6]] (frame 0810). 00:30 row space plane in R^3. 02:30 N(A) line (1,-2,1), check 05:30; perpendicular to row space. 06:30 C(A)=R^2. 08:30 row space = C(A^T). 09:30 N(A^T)={0}. 12:30 big picture; 13:30 dims r, n-r, r, m-r.
- v38 graph 4 nodes 5 edges: edges 1->2, 1->3, 2->3, 1->4, 2->4; A = [[-1,1,0,0],[-1,0,1,0],[0,-1,1,0],[-1,0,0,1],[0,-1,0,1]]. 06:00 Av = potential differences. 09:30 KCL A^T w = 0. 12:00 Ohm. 14:30 A^T A graph Laplacian.
- v39 01:30 Av=0 for (1,1,1,1). 03:30 ground V4=0 -> 5x3. 06:30 A^T (frame 0870). 08:00 node 1: -(w1+w2+w4)=0. 11:00 loop flow w=(1,0,0,-1,1); second small loop. 14:00 big loop = sum of small loops. 16:30 m - n + 1 = 2 independent loops.
- Caption fixes: "V is C C C C" = v = c(1,1,1,1); incidence A is 5x4; "A one, a two and a four" = edges 1, 2, 4.
- Animation ideas: plane spanned by a1,a2 with a3 in/out; row space plane ⟂ null line; graph with node potentials and loop flows; small loops adding to big loop.
