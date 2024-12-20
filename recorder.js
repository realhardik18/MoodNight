import dotenv from "dotenv";
dotenv.config();

import { GatewayIntentBits } from "discord-api-types/v10";
import { Events, Client } from "discord.js";
import {
  joinVoiceChannel,
  VoiceConnectionStatus,
  EndBehaviorType,
  createAudioPlayer,
  createAudioResource,
  AudioPlayerStatus,
  StreamType,
} from "@discordjs/voice";
import fs from "fs";
import prism from "prism-media";
import { spawn } from "child_process";
import play from "play-dl";

const client = new Client({
  intents: [
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.Guilds,
  ],
});
var file = 0;
// Ensure the audio folder exists
if (!fs.existsSync("./audio")) {
  fs.mkdirSync("./audio");
}

function getCurrentTimestamp() {
  const now = new Date();
  return now.toISOString().replace(/[:.-]/g, "_");
}

async function startContinuousRecording(receiver, userId, guildId) {
  let isRecording = true;

  const recordChunk = async () => {
    if (!isRecording) return;

    const opusDecoder = new prism.opus.Decoder({
      rate: 48000, // Sample rate in Hz
      channels: 2, // Stereo audio
      frameSize: 960,
    });

    const audioStream = receiver.subscribe(userId, {
      end: { behavior: EndBehaviorType.AfterSilence, duration: 1000 },
    });

    const timestamp = getCurrentTimestamp();
    const pcmFilePath = `./audio/${timestamp}.pcm`;
    const wavFilePath = pcmFilePath.replace(".pcm", ".wav");
    const writeStream = fs.createWriteStream(pcmFilePath);

    console.log(`Recording audio to ${pcmFilePath}`);
    audioStream.pipe(opusDecoder).pipe(writeStream);

    // Stop recording after 30 seconds
    setTimeout(() => {
      audioStream.unpipe(opusDecoder);
      opusDecoder.unpipe(writeStream);
      writeStream.end();

      console.log(`Saved PCM file: ${pcmFilePath}`);

      // Convert PCM to WAV using ffmpeg with high-quality settings
      const ffmpeg = spawn("ffmpeg", [
        "-f", "s16le", // Input format: PCM 16-bit little-endian
        "-ar", "48000", // Input sample rate (48 kHz)
        "-ac", "2", // Input channels (stereo)
        "-i", pcmFilePath, // Input file
        "-vn", // No video
        "-ar", "48000", // Output sample rate (48 kHz)
        "-ac", "2", // Output channels (stereo)
        "-b:a", "192k", // Audio bitrate (192 kbps)
        wavFilePath, // Output file
      ]);

      ffmpeg.on("close", (code) => {
        if (code === 0) {
          console.log(`Converted to high-quality WAV: ${wavFilePath}`);
          fs.unlinkSync(pcmFilePath); // Delete the PCM file
        } else {
          console.error(`ffmpeg process failed with code ${code}`);
        }
      });

      // Start a new recording chunk
      recordChunk();
    }, 30 * 1000); // 30 seconds

    // Handle stream errors
    audioStream.on("error", (error) => {
      console.error("Audio stream error:", error);
      isRecording = false;
    });
  };

  // Start the first recording chunk
  recordChunk();

  return () => {
    isRecording = false;
    console.log("Stopped recording.");
  };
}

client.on(Events.ClientReady, () => console.log("Bot is ready!"));

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
          startContinuousRecording(receiver, member.id, channel.guild.id);
        }
      });
    });

    connection.on(VoiceConnectionStatus.Disconnected, () => {
      console.log("Disconnected from the voice channel.");
    });
  }

  if (message.content.startsWith("!play ")) {
    const args = message.content.split(" ");
    if (args.length < 2) {
      return message.reply("Please provide a valid song URL!");
    }

    const url = args[1];
    const channel = message.member?.voice?.channel;

    if (!channel) {
      return message.reply("You need to join a voice channel first!");
    }

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: channel.guild.id,
      adapterCreator: channel.guild.voiceAdapterCreator,
    });

    connection.on(VoiceConnectionStatus.Ready, async () => {
      try {
        const stream = await play.stream(url);
        const resource = createAudioResource(stream.stream, {
          inputType: StreamType.Arbitrary,
        });

        const player = createAudioPlayer();
        connection.subscribe(player);

        player.play(resource);

        player.on(AudioPlayerStatus.Playing, () => {
          console.log("Playing audio");
        });

        player.on(AudioPlayerStatus.Idle, () => {
          console.log("Audio playback finished");
          connection.destroy();
        });

        player.on("error", (error) => {
          console.error("Error with audio playback:", error);
          connection.destroy();
        });

        message.reply(`Now playing: ${url}`);
      } catch (error) {
        console.error("Error playing audio:", error);
        message.reply("Could not play the song. Make sure the URL is valid!");
      }
    });

    connection.on(VoiceConnectionStatus.Disconnected, () => {
      console.log("Disconnected from the voice channel.");
    });
  }
});

void client.login(process.env.BOT_TOKEN);