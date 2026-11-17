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
    def differ(self, var_name: str = 'x') -> 'Telement': pass

    def set_var(self, name: str, val: float):
        if self.left:
            self.left.set_var(name, val)
        if self.right:
            self.right.set_var(name, val)


class Real(Telement):
    def __init__(self, f: float):
        super().__init__(None, None)
        self.f = float(f)

    def rezult(self) -> float: return self.f
    def copy(self) -> 'Telement': return Real(self.f)
    def differ(self, var_name: str = 'x') -> 'Telement': return Real(0.0)


class Var(Telement):
    def __init__(self, name: str, val: float = 0.0):
        super().__init__(None, None)
        self.name = name
        self.val = float(val)

    def rezult(self) -> float: return self.val
    def copy(self) -> 'Telement': return Var(self.name, self.val)

    def differ(self, var_name: str = 'x') -> 'Telement':
        return Real(1.0 if self.name == var_name else 0.0)

    def set_var(self, name: str, val: float):
        if self.name == name:
            self.val = float(val)


class Plus(Telement):
    def rezult(self) -> float: return self.left.rezult() + self.right.rezult()
    def copy(self) -> 'Telement': return Plus(self.left.copy(), self.right.copy())
    def differ(self, var_name: str = 'x') -> 'Telement':
        return Plus(self.left.differ(var_name), self.right.differ(var_name))


class Minus(Telement):
    def rezult(self) -> float: return self.left.rezult() - self.right.rezult()
    def copy(self) -> 'Telement': return Minus(self.left.copy(), self.right.copy())
    def differ(self, var_name: str = 'x') -> 'Telement':
        return Minus(self.left.differ(var_name), self.right.differ(var_name))


class Mult(Telement):
    def rezult(self) -> float: return self.left.rezult() * self.right.rezult()
    def copy(self) -> 'Telement': return Mult(self.left.copy(), self.right.copy())
    def differ(self, var_name: str = 'x') -> 'Telement':
        return Plus(
            Mult(self.left.differ(var_name), self.right.copy()),
            Mult(self.left.copy(), self.right.differ(var_name))
        )


class Div(Telement):
    def rezult(self) -> float:
        denom = self.right.rezult()
        if denom == 0:
            raise ZeroDivisionError("Помилка: ділення на нуль у виразі!")
        return self.left.rezult() / denom

    def copy(self) -> 'Telement': return Div(self.left.copy(), self.right.copy())
    def differ(self, var_name: str = 'x') -> 'Telement':
        return Div(
            Minus(
                Mult(self.left.differ(var_name), self.right.copy()),
                Mult(self.left.copy(), self.right.differ(var_name))
            ),
            Mult(self.right.copy(), self.right.copy())
        )


def form(s: str) -> Telement:
    s = s.replace(" ", "").replace(",", ".")
    if not s:
        raise ValueError("Введено порожній рядок!")

    for op, cls in [('+', Plus), ('-', Minus), ('*', Mult), ('/', Div)]:
        p = s.rfind(op)
        if p > 0:
            return cls(form(s[:p]), form(s[p + 1:]))

    if s == "x":
        return Var('x')
    if s == "h":
        return Var('h')

    return Real(float(s))


if __name__ == "__main__":
    print("=== Політ ракети: модель S(x, h) з двома змінними ===")
    print("Допустимі операції: +, -, *, /; змінні: x (час), h (відстань до Землі)\n")

    try:
        expr_x = input("Введіть вираз або значення для часу x (напр. 10 або 5+2*2.5): ")
        expr_h = input("Введіть вираз або значення для відстані до Землі h (напр. 250): ")
        expr_s = input("Введіть вираз для шляху S(x, h) (напр. h + 12.5*x*x - 500/h): ")
        digits = int(input("Введіть точність (кількість знаків після коми, напр. 4): "))

        tree_x = form(expr_x)
        tree_h = form(expr_h)
        f = form(expr_s)

        f1 = f.differ('x')
        f2 = f1.differ('x')

        t_val = tree_x.rezult()
        dist_val = tree_h.rezult()

        for tree in (f, f1, f2):
            tree.set_var('x', t_val)
            tree.set_var('h', dist_val)

        print("\n--- Результати обчислень ---")
        print(f"Час (x):                 {t_val:.{digits}f}")
        print(f"Відстань до Землі (h):   {dist_val:.{digits}f}")
        print(f"Шлях S(x, h):            {f.rezult():.{digits}f}")
        print(f"Швидкість S'(x):         {f1.rezult():.{digits}f}")
        print(f"Прискорення S''(x):      {f2.rezult():.{digits}f}")

    except ZeroDivisionError as e:
        print(f"\n{e}")
    except ValueError as e:
        print(f"\nПомилка введення даних: {e}")