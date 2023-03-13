const { REST, Routes, Client, GatewayIntentBits } = require('discord.js');
require("dotenv").config();
const { commands } = require('./commands');

const token = process.env.TOKEN;
const clientId = process.env.CLIENT_ID;


const rest = new REST({ version: '10' }).setToken(token);

// INITIALIZATION---------------------------------------------------------------------------
(async () => {
    try {
        console.log('Started refreshing application (/) commands.');
        // await rest.put(Routes.applicationCommands(clientId), { body: commands });
        await rest.delete(Routes.applicationCommand(clientId, '1084846454004252814'))
        // console.log(await rest.get(Routes.applicationCommands(clientId)))
        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
})();
// -----------------------------------------------------------------------------------------


const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.on('ready', () => {
	console.log(`Logged in as ${client.user.tag}!`);
});

client.on('interactionCreate', async (interaction) => {
	if (!interaction.isChatInputCommand()) return;

	if (interaction.commandName === 'GG') {
		await interaction.reply('Pong!');
	}
});

client.login(token);