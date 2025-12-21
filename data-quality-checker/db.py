from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_a4SOHZlRD1th@ep-winter-breeze-a1003u3y-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)

def load_table(table_name):
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)
