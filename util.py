import os
from dotenv import load_dotenv
import config
import math
import time
import random
import numpy as np
from time import sleep
from datetime import datetime, timezone, timedelta
import pymongo
import statistics


def get_trader_drawdown(traderId):
    load_dotenv()
    client = pymongo.MongoClient(os.getenv('MONGODB'))
    drawdownDB = client.TraderDrawdown.traderDrawdown

    # traderDrawdown Schema EXAMPLE:
    # _id: 639e8524dbfdd377db639603
    # traderId: "5938058384"
    # state: "active"
    # updateDate: "2023-01-12 04:09:48"
    # traderName: "紫渝"
    # ROI: -32.46
    # totalTrade: 271
    # winTrade: 188
    # loseTrade: 83
    # totalFollower: 205
    # totalRevenue: 176.58
    # history: [   
        # side: "short"
        # leverage: 50
        # symbol: "ETHUSDT"
        # marginType: "cross"
        # openDate: "2023-01-07 12:16:37"
        # openPrice: 1265.63
        # closeDate: "2023-01-11 23:13:28"
        # closePrice: 1333.2
        # revenue: -266.94
        # orderId: "995472239410921475"
        # drawdown: 324.19
    # ]
    # follower: 125

    traderData = drawdownDB.find({"traderId": traderId})
    traderData = (list(traderData)[0])
    # print(traderData)
    if len(traderData) == 0 :
        hasDrawdownData = False
        print('Cannot find trader data in DB.')
    else:
        dayCount = 28
        margin = 10
        pnlInDays = np.zeros(dayCount, dtype=float)
        startTimestamp = int(time.mktime(time.strptime("2023-02-01 00:00:00", "%Y-%m-%d %H:%M:%S")))
        endTimestamp = int(time.mktime(time.strptime("2023-02-28 23:59:59", "%Y-%m-%d %H:%M:%S")))
        traderShareRatio = 0.1
        totalTraderShare = 0.0
        hasDrawdownData = True
        history = traderData["history"]
        traderName = traderData["traderName"]
        for each in history:
            openTimestamp = int(time.mktime(time.strptime(each["openDate"], "%Y-%m-%d %H:%M:%S")))
            closeTimestamp = int(time.mktime(time.strptime(each["closeDate"], "%Y-%m-%d %H:%M:%S")))
            leverage = each["leverage"]
            if startTimestamp <= openTimestamp and closeTimestamp <= endTimestamp:
                day = int((closeTimestamp-startTimestamp)/86400)
                # 手續費6%, 開倉平倉各付一次
                fee = 0.0006 * margin * leverage * 2
                pnl = (margin * float(each["revenue"])/100) - fee

                if pnl > 0:
                    pnlInDays[day] += pnl * (1 - traderShareRatio)
                    totalTraderShare += pnl * traderShareRatio
                else:
                    pnlInDays[day] += pnl

        return {
            "traderName": traderName,
            "pnlInDays": pnlInDays,
            "totalTraderShare": totalTraderShare
        }


if __name__ == "__main__":
    get_trader_drawdown("2442813206")
