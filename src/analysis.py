
import pandas as pd
def load(path):
 d=pd.read_csv(path);d["Data"]=pd.to_datetime(d["Data"]);d["Faturamento"]=d["Quantidade"]*d["Preco"];return d
