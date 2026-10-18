import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    targets = ['hi-IN', 'te-IN', 'ta-IN', 'kn-IN', 'ml-IN', 'en-IN']
    for v in voices:
        if any(t in v['Locale'] for t in targets):
            print(f"{v['ShortName']} | {v['Locale']} | {v['Gender']}")

if __name__ == '__main__':
    asyncio.run(main())
