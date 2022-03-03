import mido
import mido.backends.rtmidi
import asyncio

def make_stream():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)
    async def stream():
        while True:
            yield await queue.get()
    return callback, stream()

async def print_messages():
    # create a callback/stream pair and pass callback to mido
    cb, stream = make_stream()
    inputs = mido.get_input_names()

    print(inputs)
    mido.open_input(inputs[1],callback=cb)

    # print messages as they come just by reading from stream
    async for message in stream:
        print(message)

async def main():
    await asyncio.gather(print_messages())

if __name__ == "__main__":

    asyncio.run(main())
