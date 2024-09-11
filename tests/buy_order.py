import pandas as pd
import tpqoa

api = tpqoa.tpqoa("oanda.cfg")

#order = api.create_order('XAU_USD', units=0.1, sl_distance=8, tp_price=2500.000)
order = api.create_order('XAU_USD', price=2490, units=1, sl_distance=2485, tp_price=2500)


print(order)