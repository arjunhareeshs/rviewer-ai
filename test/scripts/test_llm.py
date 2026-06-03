import asyncio
import sys

sys.path.append(r"c:\SSG projects\Rviewer - ai\server")
from app.core.rag.synthesizer import synthesizer

async def main():
    try:
        print("Testing fallback synthesizer...")
        prompt_text = "Here is a resume: John Doe. He is a Software Engineer with 5 years of experience."
        res = await synthesizer._fallback_synthesize(prompt_text)
        print("Success!")
        print(res)
    except Exception as e:
        print("Error during synthesis:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
