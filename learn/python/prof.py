#%%
import pandas as pd

#%%
def read_cars():
    ans = pd.read_csv("./USA_cars_datasets.csv")
    print(ans)

if __name__ == '__main__' :
    df = read_cars()



# %%
