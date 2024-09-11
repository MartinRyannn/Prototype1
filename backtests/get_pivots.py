import pandas as pd

hist_data = pd.read_csv("historical.csv")

pivot_data = []

for i in range(1, len(hist_data)):
    prev_day = hist_data.iloc[i - 1]
    high = prev_day['h']
    low = prev_day['l']
    open = prev_day['o']
    close = prev_day['c']

    pivot_point = (high + low + close) / 3
    s1 = (pivot_point * 2) - high
    s2 = pivot_point - (high - low)
    r1 = (pivot_point * 2) - low
    r2 = pivot_point + (high - low)

    current_day = hist_data.iloc[i]
    current_date = current_day['time']

    pivot_data.append({
        'date': current_date,
        'pivot_point': round(pivot_point, 2),
        's1': round(s1, 2),
        's2': round(s2, 2),
        'r1': round(r1, 2),
        'r2': round(r2, 2)
    })

    pivot_df = pd.DataFrame(pivot_data)

    pivot_df.to_csv("pivot_points.csv", index=False)

    