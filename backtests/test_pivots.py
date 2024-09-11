import pandas as pd

pivot_points = pd.read_csv("pivot_points.csv")

def check_bounce_breakout(day_data, pivot, s1, s2, r1, r2):
    bounces = 0
    fakeouts = 0
    successful_fakeouts = 0
    successful_fakeout_times = []
    tolerance = 0.01

    for i, row in day_data.iterrows():
        high = row['h']
        low = row['l']
        close = row['c']
        candle_time = row['time']


        #check for bounce or fakeout
        for level, level_type in [(pivot, "pivot"), (s1, "support"), (s2, "support"), (r1, "resistance"), (r2, "resistance")]:
            if low <= level <= high:

                if close > level and low < level: #fakout at resistance
                    fakeouts +=1
                    if level_type == "resistance":
                        if check_fakeout_success(day_data, i, "down"):
                            successful_fakeouts += 1
                            successful_fakeout_times.append(candle_time)

                elif close < level and high > level: #fakeout at support
                    fakeouts += 1
                    if level_type == "support":
                        if check_fakeout_success(day_data, i, "up"):
                            successful_fakeouts += 1
                            successful_fakeout_times.append(candle_time)
                elif (abs(close - level) <= tolerance or
                      abs(low - level) <= tolerance or
                      abs(high - level) <= tolerance):
                    bounces += 1

    return bounces, fakeouts, successful_fakeouts, successful_fakeout_times

def check_fakeout_success(day_data, current_index, expected_direction, candle_count=4):
    for j in range(current_index + 1, min(current_index + 1 + candle_count, len(day_data))):
        next_candle_close = day_data.iloc[j]['c']
        prev_candle_close = day_data.iloc[current_index]['c']

        if expected_direction == "up" and next_candle_close > prev_candle_close:
            return True
        elif expected_direction == " down" and next_candle_close < prev_candle_close:
            return True
    return False


results = []

for _, row in pivot_points.iterrows():
    date = row['date']
    pivot = row['pivot_point']
    s1 = row['s1']
    s2 = row['s2']
    r1 = row['r1']
    r2 = row['r2']

    try:
        day_data = pd.read_csv(f"15min_data_{date.split()[0]}.csv")
        
        bounces, fakeouts, successful_fakeouts, successful_fakeout_times = check_bounce_breakout(day_data, pivot, s1, s2, r1, r2)
        
        print(f"Date: {date}")
        print(f"Pivot Point: {pivot:.2f}, S1: {s1:.2f}, S2: {s2:.2f}, R1: {r1:.2f}, R2: {r2:.2f}")
        print(f"Bounces: {bounces}")
        print(f"Fakeouts: {fakeouts}")
        print(f"Successful Fakeouts: {successful_fakeouts}")

        if successful_fakeouts > 0:
            print("Successful fakeout times: ")
            for time in successful_fakeout_times:
                print(f"- {time}")
        print("-" * 40)
        
        results.append({
            'date': date,
            'pivot_point': pivot,
            's1': s1,
            's2': s2,
            'r1': r1,
            'r2': r2,
            'bounces': bounces,
            'fakeouts': fakeouts,
            'successful_fakeouts': successful_fakeouts,
            'successful_fakeout_times': successful_fakeout_times
        })
    
    except FileNotFoundError:
        print(f"15-minute data for {date} not found.")
        continue

results_df = pd.DataFrame(results)
results_df.to_csv("pivot_backtest_results.csv", index=False)

                        

