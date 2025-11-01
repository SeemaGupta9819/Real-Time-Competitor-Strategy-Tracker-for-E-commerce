import pandas as pd
from datetime import datetime

def save_to_excel(final_data, query):
    df = pd.DataFrame(final_data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"amazon_{query.replace('+','_')}_{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"\n✅ Completed! Total rows: {len(df)}, Saved to: {filename}")
