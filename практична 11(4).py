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

    @abstractmethod
    def to_string(self) -> str:

        pass

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
    def to_string(self) -> str: return f"{self.f:g}"


class Var(Telement):
    def __init__(self, x: float = 0.0):
        super().__init__(None, None)
        self.x = float(x)

    def rezult(self) -> float: return self.x
    def copy(self) -> 'Telement': return Var(self.x)
    def differ(self) -> 'Telement': return Real(1.0)
    def set_var(self, X: float): self.x = float(X)
    def to_string(self) -> str: return "x"


class Plus(Telement):
    def rezult(self) -> float: return self.left.rezult() + self.right.rezult()
    def copy(self) -> 'Telement': return Plus(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement': return Plus(self.left.differ(), self.right.differ())

    def to_string(self) -> str:
        l, r = self.left.to_string(), self.right.to_string()
        if l == "0": return r
        if r == "0": return l
        return f"({l} + {r})"


class Minus(Telement):
    def rezult(self) -> float: return self.left.rezult() - self.right.rezult()
    def copy(self) -> 'Telement': return Minus(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement': return Minus(self.left.differ(), self.right.differ())

    def to_string(self) -> str:
        l, r = self.left.to_string(), self.right.to_string()
        if r == "0": return l
        return f"({l} - {r})"


class Mult(Telement):
    def rezult(self) -> float: return self.left.rezult() * self.right.rezult()
    def copy(self) -> 'Telement': return Mult(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement':
        return Plus(
            Mult(self.left.differ(), self.right.copy()),
            Mult(self.left.copy(), self.right.differ())
        )

    def to_string(self) -> str:
        l, r = self.left.to_string(), self.right.to_string()
        if l == "0" or r == "0": return "0"
        if l == "1": return r
        if r == "1": return l
        return f"({l} * {r})"


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

    def to_string(self) -> str:
        l, r = self.left.to_string(), self.right.to_string()
        if l == "0": return "0"
        if r == "1": return l
        return f"({l} / {r})"


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

    if s == "x":
        return Var()

    return Real(float(s))


if __name__ == "__main__":
    print("=== Аналітичне диференціювання виразу довільного порядку ===")
    print("Допустимі операції: +, -, *, /; змінна: x\n")

    try:
        # 1. Введення даних з клавіатури
        expr_str = input("Введіть математичний вираз f(x) (напр. 8.3*x*x*x - 12/x + 5): ")
        max_order = int(input("Введіть максимальний порядок похідної n (напр. 3): "))
        if max_order < 1:
            raise ValueError("Порядок похідної має бути цілим числом >= 1.")

        x_input = input("Введіть значення x для числової перевірки (або натисніть Enter, щоб пропустити): ").strip()


        tree = form(expr_str)
        print("\n--- Аналітичні результати (функція to_string) ---")
        print(f"Початковий вираз f(x): {tree.to_string()}")


        current_tree = tree
        for order in range(1, max_order + 1):
            current_tree = current_tree.differ()
            analytic_view = current_tree.to_string()

            if x_input:
                x_val = form(x_input).rezult()
                current_tree.set_var(x_val)
                num_val = current_tree.rezult()
                print(f"Похідна {order}-го порядку:  f^({order})(x) = {analytic_view}  |  при x={x_val:g} -> {num_val:.4f}")
            else:
                print(f"Похідна {order}-го порядку:  f^({order})(x) = {analytic_view}")

    except ZeroDivisionError as e:
        print(f"\n{e}")
    except ValueError as e:
        print(f"\nПомилка введення даних: {e}")