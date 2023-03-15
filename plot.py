import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

def plotLine(x, y, month:str):
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
    plt.xlabel('Date',{'fontsize':12,'color':'black'})          # 設定 x 軸標籤
    plt.ylabel('Fund',{'fontsize':12,'color':'black'})       # 設定 y 軸標籤
    # plt.show()
    plt.savefig("./oneAndOnly.png")
    plt.close('all')
