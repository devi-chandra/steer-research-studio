import asyncio
import edge_tts

async def test_sub_stream():
    comm = edge_tts.Communicate("Walking for just 10 minutes right after eating reduces your glucose spike by 34 percent.", "en-IN-NeerjaNeural")
    words = []
    async for chunk in comm.stream():
        if chunk["type"] == "WordBoundary":
            words.append((chunk["text"], chunk["offset"] / 10_000_000, chunk["duration"] / 10_000_000))
    print(f"Captured {len(words)} word boundaries:")
    for w in words[:5]:
        print(w)

if __name__ == '__main__':
    asyncio.run(test_sub_stream())
