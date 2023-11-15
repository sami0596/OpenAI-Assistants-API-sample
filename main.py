import openai
import asyncio
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI()

async def main(initial_delay=1, max_delay=5):
    
    # Step 1: Create an Assistant
    assistant = client.beta.assistants.create(
            name="Sami's Assistant",
            instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
            tools=[{"type": "retrieval"}]
            model="gpt-3.5-turbo-1106",
            file_ids=["file-1oRbQgN2BbDNyHWFDSG8O3a"]
        )

    # Step 2: Create a Thread
    thread = client.beta.threads.create()


    # Step 3: Add a Message to a Thread
    user_question="Hvad hvis de har en grund til at beholde dem?"
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_question
        )


    # Step 4: Run the Assistant
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions="Please address the user as a customer. The user has a premium account."
    )


    # Step 5: Wait until proceed
    wait_time = initial_delay
    while True:

        # Step 5.1: Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(
                                                        thread_id=thread.id,
                                                        run_id=run.id
                                                    )
        
        if run_status.status == "completed":
            break

        elif run_status.status in ["in_progress", "queued"]:
            print(f"Run status: {run_status.status}. Checking again in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            wait_time = min(wait_time * 2, max_delay)  # Exponential backoff with a cap

        else:
            print(f"Unexpected run status: {run_status.status}")
            break
    
    # Step 6: Get messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for msg in messages.data:
        role = msg.role
        content = msg.content[0].text.value
        print(f"{role.capitalize()}: {content}")

    # print("###############")
    # print(messages.data)

asyncio.run(main())
