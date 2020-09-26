import json
import logging
import time

import numpy as np
import pandas as pd
from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/optimizedportfolio', methods=['POST'])
def evaluate_optimized_portfolio():
    data = request.get_json()["inputs"]
    # logger.info(request.get_json())
    outputs = []

    for d in data:
        portfolio_value = d["Portfolio"]["Value"]
        spot_volatility = d["Portfolio"]["SpotPrcVol"]
        df = pd.DataFrame(d["IndexFutures"])
        outputs.append(optimized_portfolio(portfolio_value, spot_volatility, df))

    result = {
        "outputs": outputs
    }

    return jsonify(result)


def hedge_ratio(corelation, spot_vol, futures_vol):
    return np.round(corelation * spot_vol / futures_vol, 3)


def num_futures_contract(hedge_ratio, portfolio_val, futures_price, notional_val):
    return np.round(hedge_ratio * portfolio_val / (futures_price * notional_val))    

def min_max_scaler(val, maximum, minimum):
    return (val-minimum)/(maximum-minimum)

def optimized_portfolio(portfolio_value, spot_volatility, df):
    df["OptimalHedgeRatio"] = hedge_ratio(df["CoRelationCoefficient"].values, spot_volatility,
                                          df["FuturePrcVol"].values)
    df["NumFuturesContract"] = num_futures_contract(df["OptimalHedgeRatio"].values, portfolio_value,
                                                    df["IndexFuturePrice"].values,
                                                    df["Notional"].values)
    # max_vol = df['FuturePrcVol'].max()
    # min_vol = df['FuturePrcVol'].min()
    # df['FuturePrcVolScaled'] = df['FuturePrcVol'].apply(lambda x: min_max_scaler(x, max_vol, min_vol))
    df['HRVolCombined'] = df['OptimalHedgeRatio'] + df['FuturePrcVol']
    min_hr_vols = df[df["HRVolCombined"] == df["HRVolCombined"].min()].index
    if len(min_hr_vols) == 1:
        row = df.iloc[min_hr_vols[0]]
        result = {
            "HedgePositionName": row["Name"],
            "OptimalHedgeRatio": row["OptimalHedgeRatio"],
            "NumFuturesContract": int(row["NumFuturesContract"])
        }
        return result
    
    if len(min_hr_vols) > 1:
        df = df.iloc[min_hr_vols]
        min_num_futures = df[df["NumFuturesContract"] == df["NumFuturesContract"].min()]
        row = df.iloc[min_num_futures[0]]
        result = {
            "HedgePositionName": row["Name"],
            "OptimalHedgeRatio": row["OptimalHedgeRatio"],
            "NumFuturesContract": int(row["NumFuturesContract"])
        }
        return result
    # min_hedges = df[df["OptimalHedgeRatio"] == df["OptimalHedgeRatio"].min()].index
    # min_future_vols = df[df["FuturePrcVol"] == df["FuturePrcVol"].min()].index

    # total = min_hedges.union(min_future_vols)
    # if len(total) == 1:
    #     row = df.iloc[total[0]]
    #     num = num_futures_contract(row["OptimalHedgeRatio"], portfolio_value, row["IndexFuturePrice"], row["Notional"])
    #     result = {
    #         "HedgePositionName": row["Name"],
    #         "OptimalHedgeRatio": row["OptimalHedgeRatio"],
    #         "NumFuturesContract": int(num)
    #     }
    #     return result

    # df = df.iloc[total]

    # min_num_futures = df[df["NumFuturesContract"] == df["NumFuturesContract"].min()]
    # row = min_num_futures.iloc[0]
    # if len(min_num_futures.index) > 1:
    #     logger.error("unable to decide by num_futures")

    # hedge_result = {
    #     "HedgePositionName": row["Name"],
    #     "OptimalHedgeRatio": row["OptimalHedgeRatio"],
    #     "NumFuturesContract": int(row["NumFuturesContract"])
    # }

    # return hedge_result
