import math
from abc import ABC, abstractmethod


class Telement(ABC):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    @abstractmethod
    def rezult(self) -> float: pass

    @abstractmethod
    def copy(self) -> 'Telement': pass

    @abstractmethod
    def differ(self) -> 'Telement': pass

    def set_var(self, X: float):
        if self.left:
            self.left.set_var(X)
        if self.right:
            self.right.set_var(X)


class Real(Telement):
    def __init__(self, f: float):
        super().__init__(None, None)
        self.f = float(f)

    def rezult(self) -> float: return self.f
    def copy(self) -> 'Telement': return Real(self.f)
    def differ(self) -> 'Telement': return Real(0.0)


class Var(Telement):
    def __init__(self, x: float = 0.0):
        super().__init__(None, None)
        self.x = float(x)

    def rezult(self) -> float: return self.x
    def copy(self) -> 'Telement': return Var(self.x)
    def differ(self) -> 'Telement': return Real(1.0)
    def set_var(self, X: float): self.x = float(X)


class Plus(Telement):
    def rezult(self) -> float: return self.left.rezult() + self.right.rezult()
    def copy(self) -> 'Telement': return Plus(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement': return Plus(self.left.differ(), self.right.differ())


class Minus(Telement):
    def rezult(self) -> float: return self.left.rezult() - self.right.rezult()
    def copy(self) -> 'Telement': return Minus(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement': return Minus(self.left.differ(), self.right.differ())


class Mult(Telement):
    def rezult(self) -> float: return self.left.rezult() * self.right.rezult()
    def copy(self) -> 'Telement': return Mult(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement':
        return Plus(
            Mult(self.left.differ(), self.right.copy()),
            Mult(self.left.copy(), self.right.differ())
        )


class Div(Telement):
    def rezult(self) -> float:
        denom = self.right.rezult()
        if denom == 0:
            raise ZeroDivisionError("Помилка: ділення на нуль у виразі!")
        return self.left.rezult() / denom

    def copy(self) -> 'Telement': return Div(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement':
        return Div(
            Minus(
                Mult(self.left.differ(), self.right.copy()),
                Mult(self.left.copy(), self.right.differ())
            ),
            Mult(self.right.copy(), self.right.copy())
        )



class Sin(Telement):
    def __init__(self, arg: Telement):
        super().__init__(arg, None)

    def rezult(self) -> float:
        return math.sin(self.left.rezult())

    def copy(self) -> 'Telement':
        return Sin(self.left.copy())

    def differ(self) -> 'Telement':

        return Mult(Cos(self.left.copy()), self.left.differ())


class Cos(Telement):
    def __init__(self, arg: Telement):
        super().__init__(arg, None)

    def rezult(self) -> float:
        return math.cos(self.left.rezult())

    def copy(self) -> 'Telement':
        return Cos(self.left.copy())

    def differ(self) -> 'Telement':

        return Mult(Minus(Real(0.0), Sin(self.left.copy())), self.left.differ())


def find_op_outside_parens(s: str, ops: str) -> int:
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        if s[i] == ')':
            depth += 1
        elif s[i] == '(':
            depth -= 1
        elif depth == 0 and s[i] in ops:
            if s[i] == '-' and (i == 0 or s[i - 1] in '+-*/('):
                continue
            return i
    return -1


def strip_outer_parens(s: str) -> str:
    while s.startswith('(') and s.endswith(')'):
        depth = 0
        valid = True
        for i, ch in enumerate(s):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if depth == 0 and i < len(s) - 1:
                valid = False
                break
        if valid:
            s = s[1:-1]
        else:
            break
    return s


def form(s: str) -> Telement:
    s = strip_outer_parens(s.replace(" ", "").replace(",", "."))
    if not s:
        raise ValueError("Введено порожній вираз!")

    p = find_op_outside_parens(s, "+-")
    if p > 0:
        return Plus(form(s[:p]), form(s[p + 1:])) if s[p] == '+' else Minus(form(s[:p]), form(s[p + 1:]))

    p = find_op_outside_parens(s, "*/")
    if p > 0:
        return Mult(form(s[:p]), form(s[p + 1:])) if s[p] == '*' else Div(form(s[:p]), form(s[p + 1:]))

    if s.startswith('-'):
        return Minus(Real(0.0), form(s[1:]))

    if s.startswith("sin(") and s.endswith(")"):
        return Sin(form(s[4:-1]))
    if s.startswith("cos(") and s.endswith(")"):
        return Cos(form(s[4:-1]))

    if s == "x":
        return Var()

    return Real(float(s))


if __name__ == "__main__":
    print("=== Політ ракети: тригонометричні функції sin() та cos() ===")
    print("Допустимі операції: +, -, *, /, sin(...), cos(...); змінна: x (у радіанах)\n")

    try:

        expr_x = input("Введіть значення або вираз для часу x (напр. 0.5 або 3.14159/6): ")
        expr_f = input("Введіть вираз для шляху S(x) (напр. 10*sin(2*x) + 5*cos(x)): ")
        digits = int(input("Введіть точність (кількість знаків після коми, напр. 6): "))


        tree_x = form(expr_x)
        f = form(expr_f)
        f1 = f.differ()
        f2 = f1.differ()


        X = tree_x.rezult()
        for tree in (f, f1, f2):
            tree.set_var(X)


        print("\n--- Результати обчислень ---")
        print(f"Час (x):             {X:.{digits}f}")
        print(f"Шлях S(x):           {f.rezult():.{digits}f}")
        print(f"Швидкість S'(x):     {f1.rezult():.{digits}f}")
        print(f"Прискорення S''(x):  {f2.rezult():.{digits}f}")

    except ZeroDivisionError as e:
        print(f"\n{e}")
    except ValueError as e:
        print(f"\nПомилка введення даних: {e}")