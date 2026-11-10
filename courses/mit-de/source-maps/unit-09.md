# Unit 9 source map (source-reader, Sonnet; verify)

Frames read: v48 0690, 1110, 1230; v49 0450, 0510, 0690. Book 7.2 PDF 408-416 (printed = PDF - 12).

- v48 00:00 y'' + Sy = 0, e^{iωt}x, λ = ω² needs λ ≥ 0. Positive definite: symmetric, all λ>0; semidefinite λ ≥ 0.
- v48 01:30 S = A^T A; x^T A^T A x = ||Ax||^2 = λ||x||^2 => λ ≥ 0.
- v48 04:30 five tests on S = [[4,6],[6,10]] (frame 0690): eigenvalues > 0; pivots 4, 1; upper-left determinants 4, 4; S = A^T A with independent columns; energy x^T S x > 0.
- v48 12:00 energy 4x1^2 + 12 x1 x2 + 10 x2^2; x=(1,1) gives 26 (4+12+10, checked); x=(1,-1) gives 2.
- v48 15:30 bowl picture, minimum at origin; second-derivative test.
- v48 17:00 correlation matrix [[1,a,b],[a,1,c],[b,c,1]]: 1-a^2>0, det = 1 + 2abc - a^2 - b^2 - c^2 > 0 (full formula not on board).
- v49 00:00 A = U Σ V^T (rotate, stretch, rotate); U m×m, Σ m×n, V n×n.
- v49 03:00 A^T A = V Σ^T Σ V^T, A A^T = U Σ Σ^T U^T; σ² = eigenvalues.
- v49 06:30 example (frames 0450, 0510): agent read A = [[2,2],[-1,1]] with board σ = √10, 0 and U = (1/√5)[[2,1],[-1,2]]. That A is invertible (σ = 2√2, √2), so the board is probably A = [[2,2],[1,1]] (rank 1, σ = √10, 0). VERIFY ON THE FRAME before authoring.
- v49 09:00 gene-expression matrix (people × genes); u1 σ1 v1^T is the most important rank-1 piece (PCA).
- Book only: square root of S, Cholesky, norm = σ1, data matrices.
- Animation ideas: energy bowl and level ellipses; unit circle -> rotate -> stretch -> rotate -> ellipse; rank-1 pieces adding to A.
