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
    logging.info("data sent for evaluation {}".format(data))
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
    logging.info("result :{}".format(result))


    return jsonify(result)


def hedge_ratio(corelation, spot_vol, futures_vol):
    return corelation * spot_vol / futures_vol


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
    df["OptimalHedgeRatio"] = df["OptimalHedgeRatio"].round(3)

    df = df.sort_values(["OptimalHedgeRatio","FuturePrcVol","NumFuturesContract"])
    row = df.iloc[0]
    result = {
        "HedgePositionName": row["Name"],
        "OptimalHedgeRatio": row["OptimalHedgeRatio"],
        "NumFuturesContract": int(row["NumFuturesContract"])
    }
    return result

    # min_hedges = df[df["OptimalHedgeRatio"] == df["OptimalHedgeRatio"].min()].index
    # min_future_vols = df[df["FuturePrcVol"] == df["FuturePrcVol"].min()].index

    # # try to find intersection
    # intersection = min_hedges.intersection(min_future_vols)

    # if len(intersection) == 1:
    #     row = df.iloc[intersection[0]]
    #     result = {
    #         "HedgePositionName": row["Name"],
    #         "OptimalHedgeRatio": row["OptimalHedgeRatio"],
    #         "NumFuturesContract": int(row["NumFuturesContract"])
    #     }
    #     return result
        
    # elif len(intersection) > 1:
    #     df = df.iloc[intersection]
    #     min_num_futures = df[df["NumFuturesContract"] == df["NumFuturesContract"].min()]
    #     row = min_num_futures.iloc[0]
    #     result = {
    #         "HedgePositionName": row["Name"],
    #         "OptimalHedgeRatio": row["OptimalHedgeRatio"],
    #         "NumFuturesContract": int(row["NumFuturesContract"])
    #     }
    #     return result

    # else:
    #     total = min_hedges.union(min_future_vols)

    #     df = df.iloc[total]
    #     min_num_futures = df[df["NumFuturesContract"] == df["NumFuturesContract"].min()]
    #     row = min_num_futures.iloc[0]
    #     result = {
    #         "HedgePositionName": row["Name"],
    #         "OptimalHedgeRatio": row["OptimalHedgeRatio"],
    #         "NumFuturesContract": int(row["NumFuturesContract"])
    #     }
    #     return result