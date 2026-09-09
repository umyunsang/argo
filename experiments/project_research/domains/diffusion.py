"""Known-solution algebraic anisotropic diffusion development experiments."""
from __future__ import annotations

import io
import math
import random
import statistics
import time
import warnings
from pathlib import Path

import numpy as np
from pyamg import smoothed_aggregation_solver
from pyamg.gallery import diffusion_stencil_2d, stencil_grid
from scipy.sparse import csr_array
from scipy.sparse.linalg import LinearOperator, cg, splu
from threadpoolctl import threadpool_limits

from .common import DomainError, EventSink, emit, file_digest, write_new

METHODS = ("sparse_direct", "jacobi_cg", "amg_cg")
RESIDUAL_LIMIT = 1e-9
SOLUTION_ERROR_LIMIT = 1e-7
CG_RTOL = 1e-10
CG_MAXITER = 5000


def apply_stencil(stencil: np.ndarray, vector: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
    """Independent zero-boundary application, without the generated sparse matrix."""
    if stencil.shape != (3, 3) or vector.shape != (grid[0] * grid[1],):
        raise DomainError("independent stencil dimensions mismatch")
    padded = np.pad(vector.reshape(grid), 1)
    result = np.zeros(grid)
    for x in range(3):
        for y in range(3):
            result += stencil[x, y] * padded[x:x + grid[0], y:y + grid[1]]
    return result.ravel()


def check_solution(stencil: np.ndarray, grid: tuple[int, int], rhs: np.ndarray,
                   truth: np.ndarray, solution: np.ndarray) -> dict[str, object]:
    if solution.shape != truth.shape or rhs.shape != truth.shape or not np.isfinite(solution).all():
        return {"passed": False, "error": "shape_or_nonfinite_solution"}
    rhs_norm = float(np.linalg.norm(rhs))
    truth_norm = float(np.linalg.norm(truth))
    if rhs_norm == 0 or truth_norm == 0:
        raise DomainError("known-solution fixture requires nonzero vectors")
    residual = float(np.linalg.norm(apply_stencil(stencil, solution, grid) - rhs) / rhs_norm)
    error = float(np.linalg.norm(solution - truth) / truth_norm)
    return {"relative_residual": residual, "relative_solution_error": error,
            "residual_limit": RESIDUAL_LIMIT, "solution_error_limit": SOLUTION_ERROR_LIMIT,
            "passed": residual <= RESIDUAL_LIMIT and error <= SOLUTION_ERROR_LIMIT}


def make_problem(n: int, epsilon: float, angle: float, rhs_count: int,
                 seed: int) -> tuple[csr_array, np.ndarray, np.ndarray, np.ndarray]:
    if not 8 <= n <= 256 or not 0 < epsilon <= 1 or not math.isfinite(angle):
        raise DomainError("diffusion parameters outside validated development bounds")
    if not 1 <= rhs_count <= 8:
        raise DomainError("right-hand-side count must be in [1, 8]")
    stencil = diffusion_stencil_2d(epsilon=epsilon, theta=angle, type="FE")
    matrix = csr_array(stencil_grid(stencil, (n, n), format="csr"))
    skew = matrix - matrix.T
    if skew.nnz and np.max(np.abs(skew.data)) > 1e-13:
        raise DomainError("generated diffusion matrix is not symmetric")
    coordinates = np.arange(1, n + 1) / (n + 1)
    x, y = np.meshgrid(coordinates, coordinates, indexing="ij")
    rng = np.random.default_rng(seed)
    truths = []
    for index in range(rhs_count):
        truth = (np.sin((index + 1) * np.pi * x) * np.sin(2 * np.pi * y)
                 + 0.15 * np.sin(3 * np.pi * x) * np.sin(np.pi * y)
                 + 0.03 * rng.standard_normal((n, n)))
        truths.append(truth.ravel())
    truth_matrix = np.column_stack(truths)
    rhs = np.column_stack([apply_stencil(stencil, truth, (n, n)) for truth in truths])
    if not np.allclose(matrix @ truth_matrix, rhs, rtol=1e-12, atol=1e-12):
        raise DomainError("sparse generator and independent stencil application disagree")
    return matrix, stencil, truth_matrix, rhs


def solve_method(matrix: csr_array, rhs: np.ndarray, method: str, seed: int) -> tuple[np.ndarray, dict[str, object]]:
    # PyAMG spectral-radius estimates use NumPy's legacy random state.
    np.random.seed(seed)
    started = time.perf_counter()
    preconditioner: LinearOperator | None = None
    setup_detail: dict[str, object] = {}
    direct = None
    with warnings.catch_warnings(record=True) as warning_records:
        warnings.simplefilter("always")
        if method == "sparse_direct":
            direct = splu(matrix.tocsc(), permc_spec="COLAMD")
            setup_detail = {"solver": "SuperLU", "ordering": "COLAMD", "factor_nnz": direct.L.nnz + direct.U.nnz}
        elif method == "jacobi_cg":
            diagonal = matrix.diagonal()
            preconditioner = LinearOperator(matrix.shape, matvec=lambda vector: vector / diagonal,
                                            dtype=matrix.dtype)
            setup_detail = {"preconditioner": "inverse diagonal"}
        elif method == "amg_cg":
            hierarchy = smoothed_aggregation_solver(matrix, symmetry="hermitian",
                strength="symmetric", presmoother=("gauss_seidel", {"sweep": "symmetric"}),
                postsmoother=("gauss_seidel", {"sweep": "symmetric"}),
                max_levels=10, max_coarse=10, coarse_solver="pinv")
            preconditioner = hierarchy.aspreconditioner(cycle="V")
            setup_detail = {"preconditioner": "smoothed aggregation V cycle",
                            "levels": len(hierarchy.levels), "operator_complexity": float(hierarchy.operator_complexity()),
                            "strength": "symmetric", "smoother": "symmetric Gauss-Seidel", "coarse_solver": "pinv"}
        else:
            raise DomainError("unknown diffusion method")
        setup_done = time.perf_counter()
        solutions: list[np.ndarray] = []
        observations: list[dict[str, object]] = []
        for index in range(rhs.shape[1]):
            counter = [0]

            def count_iteration(_iterate: np.ndarray) -> None:
                counter[0] += 1

            solve_started = time.perf_counter()
            if direct is not None:
                solution = direct.solve(rhs[:, index])
                info = 0
            else:
                solution, info = cg(matrix, rhs[:, index], x0=np.zeros(matrix.shape[0]),
                                    rtol=CG_RTOL, atol=0.0, maxiter=CG_MAXITER,
                                    M=preconditioner, callback=count_iteration)
            observations.append({"rhs_index": index, "solve_seconds": time.perf_counter() - solve_started,
                                 "solver_info": int(info), "iterations": counter[0] if direct is None else None})
            solutions.append(solution)
        finished = time.perf_counter()
    return np.column_stack(solutions), {
        "method": method, "setup_seconds": setup_done - started,
        "solve_seconds": finished - setup_done, "total_seconds": finished - started,
        "setup_detail": setup_detail, "right_hand_sides": observations,
        "warnings": [str(item.message) for item in warning_records],
        "solver_success": all(item["solver_info"] == 0 for item in observations),
    }


def verify_artifact(path: Path) -> dict[str, object]:
    checks: dict[str, object] = {}
    with np.load(path, allow_pickle=False) as arrays:
        grid = tuple(int(value) for value in arrays["grid"])
        for method in METHODS:
            key = f"solution_{method}"
            if key not in arrays:
                continue
            checks[method] = [check_solution(arrays["stencil"], grid, arrays["rhs"][:, index],
                                            arrays["truth"][:, index], arrays[key][:, index])
                              for index in range(arrays["rhs"].shape[1])]
    return {"artifact_sha256": file_digest(path), "checks": checks,
            "passed": bool(checks) and all(item["passed"] for entries in checks.values() for item in entries)}


def run_diffusion(artifact_root: Path, seed: int, grids: tuple[int, ...] = (48, 80),
                  epsilons: tuple[float, ...] = (0.1, 0.01), angles: tuple[float, ...] = (0.0, math.pi / 6),
                  repeats: int = 3, rhs_count: int = 3,
                  sink: EventSink | None = None) -> dict[str, object]:
    if not 1 <= repeats <= 7 or not 1 <= len(grids) * len(epsilons) * len(angles) <= 24:
        raise DomainError("diffusion design exceeds bounded development run size")
    artifact_root.mkdir(mode=0o700)
    cases: list[dict[str, object]] = []
    order_rng = random.Random(seed)
    with threadpool_limits(limits=1):
        for n in grids:
            for epsilon in epsilons:
                for angle in angles:
                    case_index = len(cases)
                    case_seed = seed + case_index
                    generation_started = time.perf_counter()
                    matrix, stencil, truth, rhs = make_problem(n, epsilon, angle, rhs_count, case_seed)
                    generation_seconds = time.perf_counter() - generation_started
                    trials: list[dict[str, object]] = []
                    for repeat in range(repeats):
                        order = list(METHODS)
                        order_rng.shuffle(order)
                        stored = {"grid": np.asarray((n, n)), "stencil": stencil, "truth": truth, "rhs": rhs,
                                  "matrix_data": matrix.data, "matrix_indices": matrix.indices,
                                  "matrix_indptr": matrix.indptr}
                        methods: dict[str, object] = {}
                        for method in order:
                            started = time.perf_counter()
                            try:
                                solution, observation = solve_method(matrix, rhs, method, case_seed)
                                checks = [check_solution(stencil, (n, n), rhs[:, index], truth[:, index], solution[:, index])
                                          for index in range(rhs_count)]
                                observation["independent_checks"] = checks
                                observation["correct"] = observation["solver_success"] and all(check["passed"] for check in checks)
                                stored[f"solution_{method}"] = solution
                                methods[method] = observation
                            except Exception as error:
                                methods[method] = {"method": method, "correct": False, "status": "FAILED",
                                                   "error_type": type(error).__name__, "error": str(error),
                                                   "elapsed_seconds": time.perf_counter() - started}
                            emit(sink, "hypothesis_observation" if method == "amg_cg" else "baseline_observation",
                                 domain="diffusion", case=case_index, repeat=repeat, method=method,
                                 observation=methods[method])
                        artifact = artifact_root / f"case-{case_index:02d}-repeat-{repeat:02d}.npz"
                        output = io.BytesIO()
                        np.savez_compressed(output, **stored)
                        write_new(artifact, output.getvalue())
                        trials.append({"repeat": repeat, "order": order, "methods": methods,
                                       "artifact": artifact.name, "artifact_sha256": file_digest(artifact)})
                    summaries: dict[str, object] = {}
                    for method in METHODS:
                        successful = all(trial["methods"][method]["correct"] for trial in trials)
                        summaries[method] = {"all_trials_correct": successful,
                            "mean_total_seconds": statistics.mean(trial["methods"][method]["total_seconds"] for trial in trials) if successful else None,
                            "median_setup_seconds": statistics.median(trial["methods"][method]["setup_seconds"] for trial in trials) if successful else None,
                            "median_solve_seconds": statistics.median(trial["methods"][method]["solve_seconds"] for trial in trials) if successful else None}
                    valid_baselines = [method for method in METHODS[:2] if summaries[method]["all_trials_correct"]]
                    baseline = min(valid_baselines, key=lambda method: summaries[method]["mean_total_seconds"]) if valid_baselines else None
                    reduction = None
                    if baseline is not None and summaries["amg_cg"]["all_trials_correct"]:
                        reduction = 1 - summaries["amg_cg"]["mean_total_seconds"] / summaries[baseline]["mean_total_seconds"]
                    cases.append({"case": case_index, "grid": [n, n], "epsilon": epsilon, "angle_radians": angle,
                                  "seed": case_seed, "right_hand_sides": rhs_count, "matrix_nnz": matrix.nnz,
                                  "common_problem_generation_seconds": generation_seconds, "trials": trials,
                                  "summary": summaries, "fastest_correct_baseline": baseline,
                                  "candidate_total_reduction_against_fastest_baseline": reduction})
    all_correct = all(observation["correct"] for case in cases for trial in case["trials"] for observation in trial["methods"].values())
    return {
        "research_question": "Where does AMG-preconditioned CG reduce setup plus solve costs for rotated anisotropic diffusion systems at verified accuracy?",
        "hypothesis": "Smoothed aggregation setup amortizes at favorable sizes and anisotropy over multiple right-hand sides.",
        "source": {"generator_url": "https://pyamg.readthedocs.io/en/latest/generated/pyamg.gallery.html",
                   "generator": "diffusion_stencil_2d(type='FE') + stencil_grid(format='csr')",
                   "solver_url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.cg.html",
                   "amg_url": "https://pyamg.readthedocs.io/en/latest/generated/pyamg.aggregation.html"},
        "comparison": {"baselines": list(METHODS[:2]), "candidate": METHODS[-1],
                       "cg_rtol": CG_RTOL, "cg_atol": 0.0, "maxiter": CG_MAXITER,
                       "setup_reused_for_rhs_count": rhs_count, "repeats": repeats},
        "known_solution": "Fixed nodal sine components plus seeded random perturbation; rhs formed by independent local stencil application.",
        "cases": cases, "verification": {"all_methods_all_trials_correct": all_correct,
            "residual_computation": "Separate padded-array stencil application, no solver residual estimate",
            "relative_residual_limit": RESIDUAL_LIMIT, "relative_solution_error_limit": SOLUTION_ERROR_LIMIT,
            "independent_reexecution": "REQUIRED_SEPARATE_EXECUTION", "hidden_parameters_read": False},
        "limitations": ["Algebraic solver experiment, not evidence of PDE discretization accuracy or a physical discovery.",
                        "Public development sizes and coefficients only; final and future configurations remain unevaluated.",
                        "Few timing repetitions support exploratory choices; performance measurement isolation is owned by the controller.",
                        "Incorrect or failed methods are retained and cannot support a speed claim."],
    }
