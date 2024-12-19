import dotenv from "dotenv";
dotenv.config();

import { GatewayIntentBits } from "discord-api-types/v10";
import { Events, Client } from "discord.js";
import {
  joinVoiceChannel,
  VoiceConnectionStatus,
  EndBehaviorType,
} from "@discordjs/voice";
import fs from "fs";
import prism from "prism-media";

const client = new Client({
  intents: [
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.Guilds,
  ],
});

// Ensure the audio folder exists
if (!fs.existsSync("./audio")) {
  fs.mkdirSync("./audio");
}

async function recordAudio(receiver, userId, guildId) {
  const audioStream = receiver.subscribe(userId, {
    end: { behavior: EndBehaviorType.AfterSilence, duration: 1000 },
  });

  const opusDecoder = new prism.opus.Decoder({
    rate: 48000,
    channels: 2,
    frameSize: 960,
  });

  const filePath = `./audio/${guildId}-${userId}-${Date.now()}.pcm`;
  const writeStream = fs.createWriteStream(filePath);

  console.log(`Recording audio to ${filePath}`);
  audioStream.pipe(opusDecoder).pipe(writeStream);

  // Close the stream after 10 seconds
  setTimeout(() => {
    audioStream.unpipe(opusDecoder);
    opusDecoder.unpipe(writeStream);
    writeStream.end();
    console.log(`Saved audio file: ${filePath}`);
  }, 10 * 1000);
}

client.on(Events.ClientReady, () => console.log("Ready!"));

client.on(Events.MessageCreate, async (message) => {
  if (message.content.toLowerCase() === "!join") {
    const channel = message.member?.voice?.channel;

    if (!channel) {
      return message.reply("You need to join a voice channel first!");
    }

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: channel.guild.id,
      adapterCreator: channel.guild.voiceAdapterCreator,
    });

    connection.on(VoiceConnectionStatus.Ready, () => {
      message.reply(`Joined voice channel: ${channel.name}`);
      const receiver = connection.receiver;

      // Start recording audio for each user in the channel
      channel.members.forEach((member) => {
        if (!member.user.bot) {
          recordAudio(receiver, member.id, channel.guild.id);
        }
      });
    });

    connection.on(VoiceConnectionStatus.Disconnected, () => {
      console.log("Disconnected from the voice channel.");
    });
  }
});

void client.login(process.env.BOT_TOKEN);
