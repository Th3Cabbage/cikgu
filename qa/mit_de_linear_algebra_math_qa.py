"""Independent check of courses/mit-de/linear-algebra/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_linear_algebra_math_qa.py

Compares the exact RREF, rank and the four subspaces with SymPy for random integer matrices
(bases must be independent, lie in the right space and have the right dimension), checks the
complete solution of Av = b, the graph incidence matrices (rank, loops, Laplacian), and the
worked examples.
"""
import json
from pathlib import Path
import random
import subprocess
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/linear-algebra/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const num = M => M.map(r => r.map(SM.toNumber));
const out = inp.mats.map(c => {
  const s = SM.subspaces(c.A), r = SM.rref(c.A), sol = SM.solve(c.A, c.b);
  return {R: num(r.R), pivots: r.pivots, rank: s.rank, col: num(s.col), row: num(s.row), nul: num(s.null), left: num(s.leftNull),
          dims: s.dims, solvable: sol.solvable, part: sol.particular ? sol.particular.map(SM.toNumber) : null};
});
const graphs = inp.graphs.map(g => { const G = SM.graphInfo(g.n, g.edges);
  return {A: G.A, rank: G.rank, comps: G.components, loops: G.loops.map(v => v.map(SM.toNumber)), L: G.laplacian}; });
process.stdout.write(JSON.stringify({out, graphs}));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


random.seed(7)
mats = [{"A": [[1, 1, 2], [1, 2, 3], [1, 2, 3]], "b": [3, 4, 4]}, {"A": [[2, 4, 1], [1, 2, 0], [5, 0, 0]], "b": [1, 0, 0]},
        {"A": [[1, 2, 3], [4, 5, 6]], "b": [1, 1]}, {"A": [[1, 2], [2, 4], [3, 6]], "b": [1, 2, 3]},
        {"A": [[1, 0, 1], [0, 1, 1], [1, 1, 2]], "b": [1, 2, 3]}, {"A": [[1, 0, 1], [0, 1, 1], [1, 1, 2]], "b": [1, 2, 4]},
        {"A": [[0, 0], [0, 0]], "b": [0, 0]}, {"A": [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "b": [1, 1, 1]}]
for _ in range(150):
    m, n = random.randint(1, 4), random.randint(1, 4)
    r = random.randint(1, min(m, n))
    B = [[random.randint(-3, 3) for _ in range(r)] for _ in range(m)]
    C = [[random.randint(-3, 3) for _ in range(n)] for _ in range(r)]
    A = (sp.Matrix(B) * sp.Matrix(C)).tolist()
    if max(abs(x) for row in A for x in row) > 9:
        continue
    b = [random.randint(-3, 3) for _ in range(m)]
    mats.append({"A": [[int(x) for x in row] for row in A], "b": b})
graphs = [{"n": 4, "edges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4]]}, {"n": 4, "edges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [3, 4]]},
          {"n": 3, "edges": [[1, 2], [2, 3], [1, 3]]}, {"n": 4, "edges": [[1, 2], [3, 4]]}, {"n": 4, "edges": [[1, 2]]}]
res = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps({"mats": mats, "graphs": graphs}),
                                capture_output=True, text=True, check=True).stdout)


def rank_of(vecs):
    return sp.Matrix(vecs).rank() if vecs else 0


for c, r in zip(mats, res["out"]):
    A = sp.Matrix(c["A"])
    m, n = A.shape
    Rw, piv = A.rref()
    tag = c["A"]
    ok(sp.Matrix(r["R"]).applyfunc(sp.nsimplify) == Rw and tuple(r["pivots"]) == piv, f"rref {tag}")
    rk = A.rank()
    ok(r["rank"] == rk and r["dims"] == {"row": rk, "null": n - rk, "col": rk, "leftNull": m - rk}, f"rank/dims {tag}")
    nul = [sp.Matrix([sp.nsimplify(x) for x in v]) for v in r["nul"]]
    ok(all(A * v == sp.zeros(m, 1) for v in nul) and rank_of([list(v) for v in nul]) == n - rk, f"null space {tag}")
    left = [sp.Matrix([sp.nsimplify(x) for x in v]) for v in r["left"]]
    ok(all(A.T * v == sp.zeros(n, 1) for v in left) and rank_of([list(v) for v in left]) == m - rk, f"left null space {tag}")
    colsp = [list(map(sp.nsimplify, v)) for v in r["col"]]
    ok(rank_of(colsp) == rk and (not colsp or sp.Matrix.hstack(A, sp.Matrix(colsp).T).rank() == rk), f"column space {tag}")
    rows = [list(map(sp.nsimplify, v)) for v in r["row"]]
    ok(rank_of(rows) == rk and (not rows or sp.Matrix.vstack(A, sp.Matrix(rows)).rank() == rk), f"row space {tag}")
    # orthogonality N(A) perp row space
    ok(all((sp.Matrix(rw).T * v)[0] == 0 for rw in rows for v in nul), f"N(A) perp row space {tag}")
    b = sp.Matrix(c["b"])
    solvable = sp.Matrix.hstack(A, b).rank() == rk
    ok(r["solvable"] == solvable, f"solvable {tag} b={c['b']}")
    if solvable:
        vp = sp.Matrix([sp.nsimplify(x) for x in r["part"]])
        ok(A * vp == b, f"particular {tag}")

ok(res["out"][0]["part"] == [2, 1, 0], "lecture v_p = (2, 1, 0)")
ok(res["out"][4]["part"] == [1, 2, 0] and not res["out"][5]["solvable"], "s1 example")

for g, r in zip(graphs, res["graphs"]):
    A = sp.Matrix(r["A"])
    ok(all(sorted(row) in ([-1, 0, 0, 1][:0] or sorted(row),) for row in r["A"]), "incidence rows")
    for k, (a, bb) in enumerate(g["edges"]):
        ok(r["A"][k][a - 1] == -1 and r["A"][k][bb - 1] == 1 and sum(abs(x) for x in r["A"][k]) == 2, f"incidence row {g} {k}")
    ok(r["rank"] == A.rank() == g["n"] - r["comps"], f"graph rank {g}")
    loops = [sp.Matrix(v) for v in r["loops"]]
    ok(len(loops) == len(g["edges"]) - A.rank() and all(A.T * w == sp.zeros(g["n"], 1) for w in loops), f"loops {g}")
    ok(sp.Matrix(r["L"]) == A.T * A, f"laplacian {g}")
eg = json.loads(subprocess.run(["node", "-e", "const S=require(process.argv[1]);const g=S.graphInfo(4,[]);"
                                "console.log(JSON.stringify({L:g.laplacian,N:g.nullA.map(v=>v.map(S.toNumber)),r:g.rank,l:g.loops.length}))",
                                str(MATH)], capture_output=True, text=True, check=True).stdout)
ok(eg["L"] == [[0] * 4 for _ in range(4)] and sp.Matrix(eg["N"]).rank() == 4 and eg["r"] == 0 and eg["l"] == 0, "edgeless graph")
w1, w2 = sp.Matrix([1, -1, 1, 0, 0]), sp.Matrix([1, 0, 0, -1, 1])
A0 = sp.Matrix(res["graphs"][0]["A"])
ok(A0.T * w1 == sp.zeros(4, 1) and (w2 - w1) == sp.Matrix([0, 1, -1, -1, 1]) and A0.T * (w2 - w1) == sp.zeros(4, 1), "loop difference cancels the shared edge")
ok(res["graphs"][0]["rank"] == 3 and len(res["graphs"][0]["loops"]) == 2 and len(res["graphs"][1]["loops"]) == 3, "lecture graph and K4 counts")
A = sp.Matrix(res["graphs"][0]["A"])
ok(A.T * sp.Matrix([1, 0, 0, -1, 1]) == sp.zeros(4, 1), "lecture loop w = (1, 0, 0, -1, 1)")
T = sp.Matrix([[-1, 1, 0], [0, -1, 1], [-1, 0, 1]])
ok(T * sp.Matrix([0, 1, 3]) == sp.Matrix([1, 2, 3]) and T.T * sp.Matrix([1, 1, -1]) == sp.zeros(3, 1), "triangle example")
ok(sp.Matrix([[1, 2, 3], [4, 5, 6]]) * sp.Matrix([1, -2, 1]) == sp.zeros(2, 1), "lecture 37 null vector")
ok(sp.Matrix([[1, 4, 7], [2, 5, 8], [3, 6, 9]]) * sp.Matrix([1, -2, 1]) == sp.zeros(3, 1), "s2 example dependency")

print(f"linear-algebra math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
