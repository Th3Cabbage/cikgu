# Control Bootcamp

All Control Bootcamp packages are together here, in lecture order:

| Lecture folder | Content | Standalone command (repository root) |
|---|---|---|
| [overview/](overview/README.md) | State space, feedback and why control matters | `.\launch_control.ps1` |
| [linear-systems/](linear-systems/README.md) | Eigenvector coordinates and the matrix exponential | `.\launch_linear_systems.ps1` |
| [stability-eigenvalues/](stability-eigenvalues/README.md) | Continuous/discrete stability and eigenvalues | `.\launch_stability_eigenvalues.ps1` |
| [linearization/](linearization/README.md) | Jacobians, local validity and a nonlinear/linear pendulum comparison | `.\launch_linearization.ps1` |
| [controllability/](controllability/README.md) | Actuators, coupling, the controllability matrix and reachable directions | `.\launch_controllability.ps1` |

For one browser containing the whole course and the separate ODE course, run `.\launch_study.ps1`.
The public course URL stays `/controls/`; browser progress keys are unchanged.

Each lecture owns its `dist/` viewing files, `animation/` sources, optional Python server and
README/review notes. Environments, QA, source caches and `databook.pdf` are shared at the root.
Run maintenance commands from the repository root unless stated otherwise.

New control lectures are created here by default:

```powershell
python tools/scaffold_study.py --slug next-lecture --title 'Next Lecture' --port 8810
```

This creates `courses/controls/next-lecture/` and a root launcher, refusing existing targets.
Then author/review the lesson and add it to `site/catalog.json`; see
[the workflow](../../tools/README.md) and [website documentation](../../site/README.md).
