import pandas as pred_df
import mylib as my

df = my.db_to_df_random(db_name='steel.db', table_name='test')

print({"data": df.to_dict("records")})