"""
This is not OCR implementation yet. This part of code is only a demo that using provided data.
The OCR implementation will be added later.
"""

import pandas as pd

def get_fin_data(): 
    data = {
        'Company': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E'],
        'Price': [100, 200, 150, 300, 250],
        'Revenue': [1000, 2000, 1500, 3000, 2500],
        'Profit': [100, 200, 150, 300, 250]
    }
    df = pd.DataFrame(data)
    return df   