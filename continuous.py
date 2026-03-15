import asyncio
import json
import os
import sounddevice as sd
import websockets
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY=os.getenv("DEEPGRAM_API_KEY")

sample_rate=16000
channels=1

DG_URL=(
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&language=en"
    "&encoding=linear16"
    "&sample_rate=16000"
    "&endpointing=2000"
)

async def microphone_stream(websocket):
    
    loop=asyncio.get_event_loop()

    def callback(indata, frames, time, status):
        audio_bytes=indata.tobytes()
        loop.call_soon_threadsafe(
            asyncio.create_task,
            websocket.send(audio_bytes)
        )
    
    with sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype="int16",
        callback=callback,
    ):
        print(" Microphone streaming...")
        await asyncio.Future()

async def receive_transcripts(websocket):

    async for message in websocket:
        data = json.loads(message)

        if "channel" in data:
            transcript = data["channel"]["alternatives"][0]["transcript"]

            if transcript:
                print("Transcript:", transcript)

async def main():
    
    async with websockets.connect(
        DG_URL,
        additional_headers={"Authorization":f"Token {DEEPGRAM_API_KEY}"},
    ) as websocket:

        print("Connected to Deepgram")
        await asyncio.gather(
            microphone_stream(websocket),
            receive_transcripts(websocket),
        )

asyncio.run(main())