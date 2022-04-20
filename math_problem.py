#%%

def f(x: int) -> int:
    while x > 0 and x != 1:
        yield x
        x = 3*x+1 if x % 2 == 1 else x // 2
    yield 1

print([y for y in f(10)])


# %%
for e in range(2,43, 2):
    i = pow(2, e)
    if (i - 1) % 3 == 0:
        print(e, i)


# %%
!conda install -q -y sympy

# %%
from sympy import symbols, Equality
from sympy.solvers import solve, solveset
from sympy.plotting import plot

x, l, w, p = symbols('x l w p')

# %%
plot(3*(x-4)**2+2, xlim=(-5.0, 15))