import asyncio
import edge_tts
async def edgetts(text, output_file) -> None:
    print(f"Starting TTS for: {text}")
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_file)
    print(f"Audio saved to: {output_file}")

text = 'hi, what can i do for you?'
output_file = 'test.wav'
asyncio.run(edgetts(text, output_file))