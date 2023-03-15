import os
from dotenv import load_dotenv
import math
import time
import random
import numpy as np
from time import sleep
from datetime import datetime, timezone, timedelta
import pymongo
import statistics
import plot

monthMap = {
    "01": "31",
    "02": "28",
    "03": "31",
    "04": "30",
    "05": "31",
    "06": "30",
    "07": "31",
    "08": "31",
    "09": "30",
    "10": "31",
    "11": "30",
    "12": "31",
}

def copySimulate(traderId, margin = 10, lossPerPosition = 100, month = "2023-02"):
    load_dotenv()
    client = pymongo.MongoClient(os.getenv('MONGODB'))
    drawdownDB = client.TraderDrawdown.traderDrawdown
    lastday = monthMap[month.split('-')[1]]

    traderData = drawdownDB.find({"traderId": traderId})
    traderData = (list(traderData)[0])
    # print(traderData)
    if len(traderData) == 0 :
        hasDrawdownData = False
        # print('Cannot find trader data in DB.')
        return False
    else:
        positionCount = 0
        suggestCapital = 0.00
        # margin = 10
        pnlInDays = np.zeros(int(lastday), dtype=float)
        startTimestamp = int(time.mktime(time.strptime(f"{month}-01 00:00:00", "%Y-%m-%d %H:%M:%S"))) - 3600*8
        endTimestamp = int(time.mktime(time.strptime(f"{month}-{lastday} 23:59:59", "%Y-%m-%d %H:%M:%S"))) - 3600*8
        traderShareRatio = 0.1
        totalTraderShare = 0.00
        copyProfit = 0.00
        hasDrawdownData = True
        history = traderData["history"]
        traderName = traderData["traderName"]
        countSL = 0

        for each in history:
            openTimestamp = int(time.mktime(time.strptime(each["openDate"], "%Y-%m-%d %H:%M:%S")))
            closeTimestamp = int(time.mktime(time.strptime(each["closeDate"], "%Y-%m-%d %H:%M:%S")))
            leverage = each["leverage"]
            drawdown = each["drawdown"]
            if startTimestamp <= openTimestamp and closeTimestamp <= endTimestamp:
                positionCount += 1
                day = int((closeTimestamp-startTimestamp)/86400)
                # 手續費6%, 開倉平倉各付一次
                fee = 0.0006 * margin * leverage * 2
                if drawdown >= lossPerPosition :
                    pnl = (-1 * lossPerPosition / 100) * margin
                    countSL += 1
                else:
                    pnl = (margin * float(each["revenue"])/100) - fee

                if pnl > 0:
                    pnlInDays[day] += pnl * (1 - traderShareRatio)
                    totalTraderShare += pnl * traderShareRatio
                    copyProfit += pnl * (1 - traderShareRatio)
                else:
                    pnlInDays[day] += pnl
                    copyProfit += pnl
        # PLOT -------------------------------------
        x = []
        y = []
        y.append(pnlInDays[0])
        for i in range(int(lastday)):
            x.append(i + 1)
            if i == 0:
                pass
            else:
                y.append(pnlInDays[i] + y[i - 1])
        filename = plot.plotLine(x, y, month.split('-')[1])
        # ------------------------------------------

        return {
            "traderName": traderName,               # 交易員名稱
            "positionCount": positionCount,         # 總計開倉數
            "pnlInDays": pnlInDays,                 # 每日收益
            "totalTraderShare": totalTraderShare,   # 帶單員分潤收益
            "copyProfit": round(copyProfit, 2),     # 跟單收益
            "suggestCapital": suggestCapital,       # 建議本金
            "countSL": countSL,                     # 共計止損？次
            "filename": filename,                   # 圖表檔案名稱
        }
    

def potentialExtremeMaxDrawdown(drawdownData, turns):
    drawdownList = []
    roundList = []
    potentialMaxDrawdown = 0

    for r in range(len(turns)):
        roundList.append(turns[r][0])

    for row in drawdownData:
        drawdownList.append(round(float(row["drawdown"]) / 100, 2))

    while (len(drawdownList) < sum(roundList)):
        drawdownList.append(
            drawdownList[random.randint(0, len(drawdownList) - 1)])

    maxPosition = max(roundList)
    drawdownList.sort(reverse=True)
    for i in range(maxPosition):
        potentialMaxDrawdown = potentialMaxDrawdown + drawdownList[i]

    return potentialMaxDrawdown


def analyzeTraderMDD(traderId, initialCapital = 10000, maxLossPercent = 20, month = "2023-02"):
    # Initialize
    load_dotenv()
    client = pymongo.MongoClient(os.getenv('MONGODB'))
    drawdownDB = client.TraderDrawdown.traderDrawdown
    lastday = monthMap[month.split('-')[1]]

    hasDrawdownData = False

    # Query in drawdown DB
    traderData = drawdownDB.find({"traderId": traderId})
    traderData = (list(traderData)[0])
    # print(traderData)
    if len(traderData) == 0 :
        hasDrawdownData = False
        # print('Cannot find trader data in DB.')
        return False
    else:
        hasDrawdownData = True
        startTimestamp = int(time.mktime(time.strptime(f"{month}-01 00:00:00", "%Y-%m-%d %H:%M:%S"))) - 3600*8
        endTimestamp = int(time.mktime(time.strptime(f"{month}-{lastday} 23:59:59", "%Y-%m-%d %H:%M:%S"))) - 3600*8
        history = traderData["history"]
        traderName = traderData["traderName"]
        drawdownData = []
        for each in history:
            openTimestamp = int(time.mktime(time.strptime(each["openDate"], "%Y-%m-%d %H:%M:%S")))
            closeTimestamp = int(time.mktime(time.strptime(each["closeDate"], "%Y-%m-%d %H:%M:%S")))
            if startTimestamp <= openTimestamp and closeTimestamp <= endTimestamp:
                drawdownData.append(each)

        # Round
        turns = []
        operating = []
        RevenueVSDrawback = []
        if hasDrawdownData == True:
            for row in drawdownData:
                remove = []  # 存放要刪除的筆數
                # ---more data--
                if row["drawdown"] <= 0: # 無回撤通常伴隨小收益，負回撤也歸類到1
                    RevenueVSDrawback.append(1)
                else:
                    RevenueVSDrawback.append(row["revenue"] / row["drawdown"])
                # --------------

                for trade in operating:
                    # 新 trade 與在場上的 trade 時間不重疊
                    if time.mktime(time.strptime(row["closeDate"], "%Y-%m-%d %H:%M:%S")) < time.mktime(time.strptime(trade["openDate"], "%Y-%m-%d %H:%M:%S")):
                        remove.append(trade)
                if len(remove) != 0:
                    draw = 0.0
                    num = 0
                    for trade in operating:
                        num = num + 1
                        draw = draw + trade["drawdown"]
                    turns.append([num, round(draw / 100, 2)])
                    for re in remove:
                        operating.remove(re)
                operating.append(row)
            # 最後一筆資料
            draw = 0.0
            num = 0
            for trade in operating:
                num = num + 1
                draw = draw + trade["drawdown"]
            turns.append([num, round(draw / 100, 2)])

            # Result
            # print(turns)
            if len(turns) != 0:
                # 最大回撤保證金(倉數) 回撤保證金倉數平均、 標準差
                maxPosition = max([(a[0]) for a in turns])
                drawdownHighestPosition = int(turns[np.argmax(turns, axis=0)[1]][0])
                drawdownHighest = np.max(np.array(turns), axis=0)[1]
                drawdownMean = statistics.mean((a[1]) for a in turns)
                drawdownDev = statistics.pstdev((a[1]) for a in turns)
                drawdownEstimate = drawdownMean + (3 * drawdownDev)
                positionMean = statistics.mean((a[0]) for a in turns)
                positionDev = statistics.pstdev((a[0]) for a in turns)
                positionEstimate = str(round(positionMean + (2 * positionDev), 0)).split(".")[0]

                # 收益/最大浮動虧損
                #RD = statistics.NormalDist.from_samples(RevenueVSDrawback)
                RDMean = statistics.mean(RevenueVSDrawback)
                RDDev = statistics.pstdev(RevenueVSDrawback)
                # RDmax = max(RevenueVSDrawback)
                RDQuantiles = []
                RevenueVSDrawback.sort()
                for i in range(len(RevenueVSDrawback)):
                    for a in range(0, 11):
                        if i == int((len(RevenueVSDrawback) - 1) * a / 10):
                            RDQuantiles.append(round(RevenueVSDrawback[i], 2))

                # Monte Carlo simulation
                # monteCarloMaxDrawdown, monteCarloPosition = monteCarloSimulation(
                #     drawdownData, turns)

                # Potential extreme maximum drawdown
                potentialMaxDrawdown = potentialExtremeMaxDrawdown(drawdownData, turns)

                # Position strategy
                maxLoss = initialCapital * (maxLossPercent / 100)
                strategyMaxDrawdown = max(drawdownHighest, drawdownEstimate)
                safeTotalMargin = maxLoss / (strategyMaxDrawdown / drawdownHighestPosition)
                safeMargin = round(safeTotalMargin / drawdownHighestPosition, 2)


                # print(f"※常態分佈 = 保證金浮動虧損平均值 + 3 × 保證金浮動虧損標準差 (包含 99.73% 事件)")
                # print(f"※潛在極端 = 將前 N 大單筆保證金浮動虧損組合進最大回合持倉內計算")
                # print(f"※建議安全保證金 = (最大可接受虧損金額 ÷ 最大保證金浮動虧損 (％)) ÷ 最大保證金浮動虧損時持倉數")
                # print(f"※建議安全總倉數 = 持倉數平均值 + 2 × 持倉數標準差 (包含 95% 事件)\n\n\n")
                # print(f"※風報比 = 收益 ÷ 最大浮動虧損")
                
                return {
                    "traderName": traderName,
                    "traderId": traderId,
                    "maxPosition": maxPosition,             # 最大回合持倉數
                    "drawdownHighest": drawdownHighest,     # 最大保證金浮動虧損 (倉)
                    "drawdownHighestPercent": round((drawdownHighest / drawdownHighestPosition) * 100, 2),  # 最大保證金浮動虧損 (％)
                    "drawdownHighestPosition": drawdownHighestPosition,     # 發生最大保證金浮動虧損時持倉數
                    "potentialMDD": round(potentialMaxDrawdown, 2),         # 潛在極端最大保證金浮動虧損 (倉)
                    "potentialMDDPercent": round((potentialMaxDrawdown / maxPosition) * 100, 2),    # 潛在極端最大保證金浮動虧損 (％)
                    "RDMean": round(RDMean, 2),             # 風報比平均值
                    "RDDev": round(RDDev, 2),               # 風報比標準差
                    "RDMid": RDQuantiles[5],                # 風報比中位數
                    "initialCapital": initialCapital,       # 初始資金（使用者設定）
                    "maxLossPercent": maxLossPercent,       # 最大風險（使用者設定）
                    "safeMargin": safeMargin,               # 建議安全保證金
                    "positionEstimate": positionEstimate,   # 建議安全倉數上限
                }


# My handmade function: FAILED
# def calcMaxMDD(traderId):
#     load_dotenv()
#     client = pymongo.MongoClient(os.getenv('MONGODB'))
#     drawdownDB = client.TraderDrawdown.traderDrawdown

#     traderData = drawdownDB.find({"traderId": traderId})
#     traderData = (list(traderData)[0])
#     # print(traderData)
#     if len(traderData) == 0 :
#         hasDrawdownData = False
#         # print('Cannot find trader data in DB.')
#         return False
#     else:
#         positionCount = 0
#         positions = []
#         suggestCapital = 0.00
#         startTimestamp = int(time.mktime(time.strptime(f"2023-02-20 00:00:00", "%Y-%m-%d %H:%M:%S"))) + 3600*8
#         endTimestamp = int(time.mktime(time.strptime(f"2023-03-10 23:59:59", "%Y-%m-%d %H:%M:%S"))) + 3600*8
#         hasDrawdownData = True
#         history = traderData["history"]

#         for each in history:
#             openTimestamp = int(time.mktime(time.strptime(each["openDate"], "%Y-%m-%d %H:%M:%S")))
#             closeTimestamp = int(time.mktime(time.strptime(each["closeDate"], "%Y-%m-%d %H:%M:%S")))
#             leverage = each["leverage"]
#             drawdown = each["drawdown"]
#             if startTimestamp <= openTimestamp and closeTimestamp <= endTimestamp:
#                 # print(f'{openTimestamp}, {closeTimestamp}')
#                 positions.append({
#                     "openTimestamp": openTimestamp,
#                     "closeTimestamp": closeTimestamp,
#                     "drawdown": drawdown,
#                     "overlapPos": []
#                 })

#         overlap = np.zeros((len(positions), len(positions)), dtype="int_")
#         for i in range(len(positions)):
#             for j in range(len(positions)):
#                 if positions[i]["openTimestamp"] < positions[j]["closeTimestamp"] :
#                     overlap[i][j] = 1
#                 else :
#                     overlap[i][j] = 0

#         for i in range(len(positions)):
#             for j in range(len(positions)):
#                 if overlap[i][j] != overlap[j][i]:
#                     overlap[i][j] = 0
#                     overlap[j][i] = 0
#                 elif overlap[i][j] == 1 and overlap[j][i] == 1:
#                     positions[i]["overlapPos"].append(j)
#                     pass

#         print(positions[64])
#         # print(overlap)
#         print(positions[256])

#         MDD = 0
#         for eachPos in positions :
#             for eachOverlap in eachPos["overlapPos"]:
#                 MDD += positions[eachOverlap]["drawdown"]
#             eachPos["overlapMDD"] = MDD
#             MDD = 0

#         return 0


if __name__ == "__main__":
    response = copySimulate("4876423973")
    # print(response["pnlInDays"])
    # print(response["copyProfit"])
    x = []
    y = []
    y.append(response["pnlInDays"][0])
    for i in range(len(response["pnlInDays"])):
        x.append(i + 1)
        if i == 0:
            pass
        else:
            y.append(response["pnlInDays"][i] + y[i - 1])

    # print(analyzeTraderMDD("4876423973", 10000, 10, "2023-02"))
