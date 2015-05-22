import pandas as pd
import numpy as np

o = ['O']
d = ['D']
p = ['p']


df = pd.concat([pd.DataFrame(data = o), pd.DataFrame(data = d), pd.DataFrame(data = p)], axis = 1)

print(df)
