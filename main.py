
from src.analysis import load
import matplotlib.pyplot as plt, os
d=load("data/vendas.csv")
os.makedirs("images",exist_ok=True)
print(d.describe(include="all"))
m=d.groupby(d["Data"].dt.to_period("M"))["Faturamento"].sum()
m.plot(kind="bar");plt.tight_layout();plt.savefig("images/faturamento.png")
