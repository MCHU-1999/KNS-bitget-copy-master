import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import traceback
import util
import keep_alive

load_dotenv() 
token = os.getenv('TOKEN')
app_id = os.getenv('APP_ID')
guild_id = os.getenv('GUILD_ID')
KNS = discord.Object(id=guild_id)


class menuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='跟單收益試算', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(simulate())

    @discord.ui.button(label='跟單風險試算', style=discord.ButtonStyle.red, custom_id='persistent_view:red')
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(analyze())

    @discord.ui.button(label='連線狀態測試', style=discord.ButtonStyle.grey, custom_id='persistent_view:grey')
    async def grey(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("I'm ready!", ephemeral=True)


class simulate(discord.ui.Modal, title='交易員實盤績效查詢&試算'):
    traderLink = discord.ui.TextInput(
        label = 'bitget交易員連結',
        placeholder = '輸入網址（或ID）'
    )
    margin = discord.ui.TextInput(
        label = '開倉大小',
        placeholder = '每倉保證金（USDT）ex:10'
    )
    lossPerPos = discord.ui.TextInput(
        label = '倉位止損',
        placeholder = '自訂倉位止損（％）ex:100'
    )
    month = discord.ui.TextInput(
        label = '試算時間段',
        placeholder = '輸入『西元年-月份』ex:2022-09'
    )

    async def on_submit(self, interaction: discord.Interaction):
        # print(self.traderLink)
        resData = util.copySimulate(str(self.traderLink).split('?id=')[1], int(str(self.margin)), int(str(self.lossPerPos)), str(self.month))
        # print(resData)
        # print("交易員：" + resData["traderName"])
        file = discord.File(f'./{ resData["filename"] }', filename="image.png")
        embed = discord.Embed(
            title = str(self.month) + "月收益試算",
            type = "rich",
            description = f'交易員: {resData["traderName"]}'
        )\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="本金（每倉）", value=f'{ str(self.margin) }USDT')\
        .add_field(name="倉位", value=f'共{ resData["positionCount"] }倉')\
        .add_field(name=f"{ str(self.lossPerPos) }％止損", value=f'共觸發{ resData["countSL"] }次')\
        .add_field(name="總收益（無爆倉）", value=f'{ resData["copyProfit"] }USDT', inline=False)\
        .set_image(url="attachment://image.png")
        await interaction.response.send_message(file = file, embed = embed, ephemeral = True)
        os.remove(f'{ resData["filename"] }')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral = True)
        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class analyze(discord.ui.Modal, title='交易員風險與回撤試算'):
    traderLink = discord.ui.TextInput(
        label = 'bitget交易員連結',
        placeholder = '輸入網址（或ID）'
    )
    initialCapital = discord.ui.TextInput(
        label = '本金',
        placeholder = '總資金（USDT）ex:10000'
    )
    maxLossPercent = discord.ui.TextInput(
        label = '最大回撤',
        placeholder = '可承受之最大回撤（％）ex:20'
    )
    month = discord.ui.TextInput(
        label = '試算時間段',
        placeholder = '輸入『西元年-月份』ex:2022-09'
    )

    async def on_submit(self, interaction: discord.Interaction):
        # print(self.traderLink)
        resData = util.analyzeTraderMDD(str(self.traderLink).split('?id=')[1], int(str(self.initialCapital)), int(str(self.maxLossPercent)), str(self.month))
        # print(resData)
        # print("交易員：" + resData["traderName"])
        embed = discord.Embed(
            title = str(self.month) + "月風險試算",
            type = "rich",
            description = f'交易員: {resData["traderName"]}'
        )\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="本金", value=f'{ str(self.initialCapital) }USDT')\
        .add_field(name="設定最大回撤", value=f'{ str(self.maxLossPercent) }％')\
        .add_field(name="試算時間段", value=f'{ str(self.month) }月')\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="最大回合持倉數", value=f'{ resData["maxPosition"] }')\
        .add_field(name="最大浮動虧損 (倉)", value=f'{ resData["drawdownHighest"] }倍倉')\
        .add_field(name="最大浮動虧損 (％)", value=f'{ resData["drawdownHighestPercent"] }％')\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="發生最大浮動虧損時持倉數", value=f'{ resData["drawdownHighestPosition"] }')\
        .add_field(name="潛在極端浮動虧損 (倉)", value=f'{ resData["potentialMDD"] }倍倉')\
        .add_field(name="潛在極端浮動虧損 (％)", value=f'{ resData["potentialMDDPercent"] }％')\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="風報比平均值", value=f'{ resData["RDMean"] }')\
        .add_field(name="風報比標準差", value=f'{ resData["RDDev"] }')\
        .add_field(name="風報比中位數", value=f'{ resData["RDMid"] }')\
        .add_field(name=" ", value=" ", inline=False)\
        .add_field(name="建議安全保證金", value=f'{ resData["safeMargin"] }')\
        .add_field(name="建議安全倉數上限", value=f'{ resData["positionEstimate"] }')\
        .add_field(name=" ", value=" ")\
        .add_field(name="※潛在極端", value="將前 N 大單筆保證金浮動虧損組合進最大回合持倉內計算", inline=False)\
        .add_field(name="※建議安全保證金", value="(最大可接受虧損金額 ÷ 最大保證金浮動虧損 (％)) ÷ 最大保證金浮動虧損時持倉數", inline=False)\
        .add_field(name="※建議安全總倉數", value="持倉數平均值 + 2 × 持倉數標準差 (包含 95% 事件)", inline=False)\
        .add_field(name="※風報比", value="收益 ÷ 最大浮動虧損", inline=False)
        await interaction.response.send_message(embed = embed, ephemeral = True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral = True)
        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class CopyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix=commands.when_mentioned_or('/'), intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync(guild = KNS)
        self.add_view(menuView())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        mainChannel = self.get_channel(914526949630693458)
        botLogChannel = self.get_channel(944846007051620404)
        msg = await mainChannel.fetch_message(1085534223387078670)
        await msg.edit(content="Bitget 交易員分析 & 試算工具", view=menuView())
        # await mainChannel.send("Bitget 交易員分析 & 試算工具", view=menuView())
        await botLogChannel.send("I'm ready!")
        print('ready------')

bot = CopyBot()


@bot.tree.command(name = "ping", description = "pong!", guild = KNS)
async def ping(ctx):
    await ctx.response.send_message("pong!")

keep_alive.keep_alive()
bot.run(token)