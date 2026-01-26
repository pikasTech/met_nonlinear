import sympy as sp
from typing import Tuple, Union
from .utilities import stringfy


def convert_capacitance(value: float) -> Tuple[float, str]:
    if value >= 1e-6:
        return value * 1e6, "µF"
    elif value >= 1e-9:
        return value * 1e9, "nF"
    elif value >= 1e-12:
        return value * 1e12, "pF"
    else:
        return value * 1e15, "fF"


class ComponentValues:
    def __init__(self, R_39: float, R_42: float, R_43: float, C_14: float, C_15: float, C_16: float):
        self.R_39 = R_39
        self.R_42 = R_42
        self.R_43 = R_43
        self.C_14 = C_14
        self.C_15 = C_15
        self.C_16 = C_16


def process_exam(A_val: float,
                 B_val: float,
                 C_val: float,
                 R_39_val: float = 10000,
                 R_42_val: float = 10000,
                 R_43_val: float = 10000) -> ComponentValues:
    A, B, C = sp.symbols("A B C")
    R_39, R_42, R_43, C_14, C_15, C_16 = sp.symbols(
        "R_39 R_42 R_43 C_14 C_15 C_16")

    # Define the equations
    eq1 = sp.Eq(A, (R_39 * C_14) / (R_42 * R_43 * C_16 * C_15))
    eq2 = sp.Eq(B, 1 / (R_42 * R_43 * C_16 * C_15))
    eq3 = sp.Eq(C, (R_42 + R_43) / (R_42 * R_43 * C_16))

    # Solve the system of equations
    solutions = sp.solve((eq1, eq2, eq3), (R_39, R_42, R_43, C_14, C_15, C_16))

    # Get the first solution tuple
    solution = solutions[0]

    # Substitute the values of R_39, R_42, R_43, A, B, and C, and evaluate the expressions
    C_14_val = float(solution[3].subs(
        {R_39: R_39_val, A: A_val, B: B_val}).evalf())
    C_15_val = float(solution[4].subs(
        {R_42: R_42_val, R_43: R_43_val, B: B_val, C: C_val}).evalf())
    C_16_val = float(solution[5].subs(
        {R_42: R_42_val, R_43: R_43_val, C: C_val}).evalf())

    # Return the computed values as an instance of ComponentValues
    return ComponentValues(R_39_val, R_42_val, R_43_val, C_14_val, C_15_val, C_16_val)


class CFun:
    A: float
    B: float
    C: float
    simu_R_39: float
    simu_R_42: float
    simu_R_43: float
    simu_C_14: float
    simu_C_15: float
    simu_C_16: float

    def __init__(self,
                 A: float,
                 B: float,
                 C: float,
                 R_39_val: float = 10000,
                 R_42_val: float = 10000,
                 R_43_val: float = 10000):
        self.A = A
        self.B = B
        self.C = C
        component_values = process_exam(A, B, C, R_39_val, R_42_val, R_43_val)
        self.simu_R_39 = component_values.R_39
        self.simu_R_42 = component_values.R_42
        self.simu_R_43 = component_values.R_43
        self.simu_C_14 = component_values.C_14
        self.simu_C_15 = component_values.C_15
        self.simu_C_16 = component_values.C_16

    def clone(self) -> 'CFun':
        return CFun(self.A, self.B, self.C)

    def todict(self):
        return {
            'A': self.A,
            'B': self.B,
            'C': self.C,
            'simu_R_39': self.simu_R_39,
            'simu_R_42': self.simu_R_42,
            'simu_R_43': self.simu_R_43,
            'simu_C_14': self.simu_C_14,
            'simu_C_15': self.simu_C_15,
            'simu_C_16': self.simu_C_16
        }

    def __str__(self) -> str:
        return stringfy(self)
