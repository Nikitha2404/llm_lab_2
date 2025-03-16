from pydantic import BaseModel
from src.utils.azure_client import client,logging,azure_openai_model

class Step(BaseModel):
    explanation: str
    ouput: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

completion = client.beta.chat.completions.parse(
    model = azure_openai_model,
    messages=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "How can I solve 8x + 7 = -23?"}
    ],
    response_format=MathReasoning,
)

math_reasoning = completion.choices[0].message.parsed

print("steps:",math_reasoning.steps)
print("final_answer:",math_reasoning.final_answer)
