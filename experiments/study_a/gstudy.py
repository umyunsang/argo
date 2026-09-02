"""G-study and D-study for the verified-endpoint design.

Object of measurement: the condition. Facets: scoring method and anchor element,
both fully crossed with the condition within a task. Elements are task specific, so
one study is run per task rather than pooling across tasks.

Design is condition x method x element with one observation per cell. The three-way
interaction is confounded with error and is reported as the residual.

Variance components are ANOVA estimates. Negative estimates are reported as
estimated and also clamped at zero for use, and the clamping is recorded rather
than hidden, because a negative estimate is evidence that a component is small
relative to its sampling error, not evidence that it is zero.
"""
from __future__ import annotations
import itertools
from dataclasses import dataclass, field, asdict


class DesignError(ValueError):
    pass


def _mean(xs):
    xs = list(xs)
    if not xs:
        raise DesignError("mean of an empty set is undefined")
    return sum(xs) / len(xs)


def check_rectangular(obs: dict, conditions, methods, elements) -> None:
    """Every cell of the crossed design must be present exactly once."""
    if len(conditions) < 2:
        raise DesignError(
            f"a variance component for the condition needs at least 2 conditions, got {len(conditions)}"
        )
    if len(methods) < 2:
        raise DesignError(
            f"a method facet needs at least 2 methods, got {len(methods)}"
        )
    if len(elements) < 2:
        raise DesignError(
            f"an element facet needs at least 2 elements, got {len(elements)}"
        )
    want = set(itertools.product(conditions, methods, elements))
    have = set(obs)
    missing = want - have
    extra = have - want
    if missing:
        raise DesignError(
            f"design is not rectangular: {len(missing)} of {len(want)} cells are missing, "
            f"first missing {sorted(missing)[0]}"
        )
    if extra:
        raise DesignError(
            f"design has {len(extra)} observations outside the declared levels, "
            f"first extra {sorted(extra)[0]}"
        )
    for k, v in obs.items():
        if v not in (0, 1):
            raise DesignError(f"observation at {k} is {v!r}; scores must be 0 or 1")


def degrees_of_freedom(n_conditions: int, n_methods: int, n_elements: int) -> dict:
    """Degrees of freedom for a fully crossed design with one observation per cell.

    The three-way interaction is the residual, so it carries the product of the
    three main-effect degrees of freedom and nothing is left over for pure error.
    """
    a, b, c = n_conditions - 1, n_methods - 1, n_elements - 1
    if min(a, b, c) < 1:
        raise DesignError(
            f"every facet needs at least two levels; got {n_conditions} conditions, "
            f"{n_methods} methods, {n_elements} elements"
        )
    return {"condition": a, "method": b, "element": c,
            "condition_method": a * b, "condition_element": a * c,
            "method_element": b * c, "residual": a * b * c}


@dataclass
class Components:
    condition: float
    method: float
    element: float
    condition_method: float
    condition_element: float
    method_element: float
    residual: float

    def clamped(self) -> "Components":
        return Components(**{k: max(0.0, v) for k, v in asdict(self).items()})

    def negatives(self) -> list[str]:
        return sorted(k for k, v in asdict(self).items() if v < 0)

    def total(self) -> float:
        return sum(asdict(self).values())


def g_study(obs: dict, conditions, methods, elements) -> Components:
    """ANOVA variance components for a fully crossed p x m x e design, n = 1."""
    check_rectangular(obs, conditions, methods, elements)
    np_, nm, ne = len(conditions), len(methods), len(elements)
    grand = _mean(obs.values())

    mp = {p: _mean(obs[(p, m, e)] for m in methods for e in elements) for p in conditions}
    mm = {m: _mean(obs[(p, m, e)] for p in conditions for e in elements) for m in methods}
    me_ = {e: _mean(obs[(p, m, e)] for p in conditions for m in methods) for e in elements}
    mpm = {(p, m): _mean(obs[(p, m, e)] for e in elements) for p in conditions for m in methods}
    mpe = {(p, e): _mean(obs[(p, m, e)] for m in methods) for p in conditions for e in elements}
    mme = {(m, e): _mean(obs[(p, m, e)] for p in conditions) for m in methods for e in elements}

    ss_p = nm * ne * sum((mp[p] - grand) ** 2 for p in conditions)
    ss_m = np_ * ne * sum((mm[m] - grand) ** 2 for m in methods)
    ss_e = np_ * nm * sum((me_[e] - grand) ** 2 for e in elements)
    ss_pm = ne * sum((mpm[(p, m)] - mp[p] - mm[m] + grand) ** 2 for p in conditions for m in methods)
    ss_pe = nm * sum((mpe[(p, e)] - mp[p] - me_[e] + grand) ** 2 for p in conditions for e in elements)
    ss_me = np_ * sum((mme[(m, e)] - mm[m] - me_[e] + grand) ** 2 for m in methods for e in elements)
    ss_t = sum((v - grand) ** 2 for v in obs.values())
    ss_res = ss_t - ss_p - ss_m - ss_e - ss_pm - ss_pe - ss_me

    df = degrees_of_freedom(np_, nm, ne)
    df_p, df_m, df_e = df["condition"], df["method"], df["element"]
    df_pm, df_pe, df_me = df["condition_method"], df["condition_element"], df["method_element"]
    df_res = df["residual"]

    ms_p, ms_m, ms_e = ss_p / df_p, ss_m / df_m, ss_e / df_e
    ms_pm, ms_pe, ms_me = ss_pm / df_pm, ss_pe / df_pe, ss_me / df_me
    ms_res = ss_res / df_res

    v_res = ms_res
    v_pm = (ms_pm - ms_res) / ne
    v_pe = (ms_pe - ms_res) / nm
    v_me = (ms_me - ms_res) / np_
    v_p = (ms_p - ms_pm - ms_pe + ms_res) / (nm * ne)
    v_m = (ms_m - ms_pm - ms_me + ms_res) / (np_ * ne)
    v_e = (ms_e - ms_pe - ms_me + ms_res) / (np_ * nm)
    return Components(v_p, v_m, v_e, v_pm, v_pe, v_me, v_res)


def d_study(c: Components, n_methods: int, n_elements: int) -> dict:
    """Error variances and coefficients for a chosen number of methods and elements."""
    if n_methods < 1 or n_elements < 1:
        raise DesignError(
            f"a decision study needs at least one method and one element, got "
            f"{n_methods} methods and {n_elements} elements"
        )
    k = c.clamped()
    rel = k.condition_method / n_methods + k.condition_element / n_elements + \
        k.residual / (n_methods * n_elements)
    absol = rel + k.method / n_methods + k.element / n_elements + \
        k.method_element / (n_methods * n_elements)
    g = k.condition / (k.condition + rel) if (k.condition + rel) > 0 else 0.0
    phi = k.condition / (k.condition + absol) if (k.condition + absol) > 0 else 0.0
    return {
        "n_methods": n_methods,
        "n_elements": n_elements,
        "relative_error_variance": rel,
        "absolute_error_variance": absol,
        "generalizability_coefficient": g,
        "dependability_index": phi,
    }


def elements_needed(c: Components, target: float, n_methods: int, cap: int = 400) -> int | None:
    """Smallest element count reaching a dependability target, or None within the cap."""
    if not 0 < target < 1:
        raise DesignError(f"dependability target must lie strictly between 0 and 1, got {target}")
    for n in range(1, cap + 1):
        if d_study(c, n_methods, n)["dependability_index"] >= target:
            return n
    return None
