import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import numpy as np

def getTime():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    return dt2.strftime("%Y-%m-%d-%H-%M-%S")

def plotLine(x, y, month:str):
    try:
        timeNow = getTime()
        date = [month + '/' + str(each) for each in x]
        yLast = [y[-1] for each in y]
        plt.plot(x, y, linewidth=2, solid_capstyle='round', c='YellowGreen')  # Plot some data on the axes.
        plt.plot(x, yLast, linestyle='--', linewidth=1, solid_capstyle='round', c='grey')  # final funds
        plt.plot(x[-1], y[-1], marker='o', c='YellowGreen')
        plt.text(x[-1]+0.5, y[-1], f'{ round(y[-1],2) }\nUSDT', c='black')
        plt.xticks(
            ticks = x,
            labels = date,
            color = 'grey',
            fontsize = 8,
            rotation = 45
        )
        plt.grid(color='silver', linestyle='--', linewidth=0.5)
        plt.xlabel('Date',{'fontsize':12,'color':'black'})
        plt.ylabel('Fund (USDT)',{'fontsize':12,'color':'black'})
        # plt.show()
        plt.savefig(f'./{ timeNow }.png')
        plt.close('all')
        return f'{ timeNow }.png'

    except Exception as e:
        print(e)



if __name__ == "__main__":
    # print(getTime())
    pass