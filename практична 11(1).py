import tkinter as tk
from tkinter import ttk, messagebox
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
        if self.left: self.left.set_var(X)
        if self.right: self.right.set_var(X)


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
    def rezult(self) -> float: return self.left.rezult() / self.right.rezult()
    def copy(self) -> 'Telement': return Div(self.left.copy(), self.right.copy())
    def differ(self) -> 'Telement':
        return Div(
            Minus(
                Mult(self.left.differ(), self.right.copy()),
                Mult(self.left.copy(), self.right.differ())
            ),
            Mult(self.right.copy(), self.right.copy())
        )


def pos_from_end(s: str, sub: str) -> int:
    idx = s.rfind(sub)
    return idx if idx > 0 else -1


def form(s: str) -> Telement:
    s = s.replace(" ", "").replace(",", ".")
    for op, cls in [('+', Plus), ('-', Minus), ('*', Mult), ('/', Div)]:
        p = pos_from_end(s, op)
        if p > 0:
            return cls(form(s[:p]), form(s[p + 1:]))
    if s == "x":
        return Var()
    return Real(float(s))


class AppEx1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вправа 1: Третя похідна (ривок ракети)")
        self.geometry("460x360")

        tk.Label(self, text="Час (Edit1):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.edit1 = tk.Entry(self, width=30)
        self.edit1.insert(0, "5,88+1,25/0,13698*3")
        self.edit1.grid(row=0, column=1, pady=5)

        tk.Label(self, text="Шлях (Edit2):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.edit2 = tk.Entry(self, width=30)
        self.edit2.insert(0, "8,3*x*x*x-12/x/x+0,13")
        self.edit2.grid(row=1, column=1, pady=5)

        fields = [
            "Час (Edit3):",
            "Шлях (Edit4):",
            "Швидкість S'(x) (Edit5):",
            "Прискорення S''(x) (Edit6):",
            "3-тя похідна S'''(x) (Edit7):"
        ]
        self.outputs = []
        for i, label in enumerate(fields, start=2):
            tk.Label(self, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=4)
            ent = tk.Entry(self, width=25)
            ent.grid(row=i, column=1, sticky="w", pady=4)
            self.outputs.append(ent)

        tk.Label(self, text="Точність:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.combo = ttk.Combobox(self, values=["2", "3", "4", "5", "6"], width=5, state="readonly")
        self.combo.set("4")
        self.combo.grid(row=7, column=1, sticky="w", pady=5)

        tk.Button(self, text="Обчислити", command=self.button1_click, width=15).grid(row=8, column=1, sticky="w", pady=10)

    def button1_click(self):
        try:
            x = form(self.edit1.get())
            f = form(self.edit2.get())
            f1 = f.differ()
            f2 = f1.differ()
            f3 = f2.differ()

            X = x.rezult()
            for tree in (f, f1, f2, f3):
                tree.set_var(X)

            digits = int(self.combo.get())
            vals = [X, f.rezult(), f1.rezult(), f2.rezult(), f3.rezult()]
            for ent, v in zip(self.outputs, vals):
                ent.delete(0, tk.END)
                ent.insert(0, f"{v:.{digits}f}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))


if __name__ == "__main__":
    AppEx1().mainloop()