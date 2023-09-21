from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.ai.schema import ai_coaching_parser


def get_zero_shot_prompt(text: str):
    return system_prompt + make_chat_user_input(text)


def get_gpt4_system_prompt_with_format_instructions():
    return system_prompt


def make_chat_user_input(t: str):
    return f"\n###{t}###\n" + ai_coaching_parser.get_format_instructions()


def get_gpt_messages(model_name: str, user_input: str):
    if model_name == "gpt-4":
        return [
            {"role": "system", "content": get_gpt4_system_prompt_with_format_instructions()},
            {"role": "user", "content": make_chat_user_input(user_input)},
        ]
    else:
        return [
            {"role": "user", "content": get_zero_shot_prompt(user_input)},
        ]


system_prompt = """You are health care expert. You are helping a user who is seeking advice related to weight training.
    Use the following step-by-step instructions to respond to user inputs.

    1. Summarize the key points of the text, separated by six sharp(### ###), into maximum of 3 sentences in Korean.
    2. Analyze the text, separated by three sharp(### ###), and provide a comprehensive answer in Korean. If user asked multiple questions, answer all of them.
    3. Add positive encouragement based on the text in Korean that can help with exercise motivation at the end."""


format_restriction = "DO NOT RETURN ANY TEXT OTHER THAN INSTRUCTED FORMAT BELOW."

combine_system_prompt_with_format_instructions = """You will be given a list of summaries of user question.

1. Take these summaries and distill it into a final, consolidated summary into maximum of 3 sentences in Korean.
2. Analyze the summary and provide a comprehensive answer in Korean from the perspective of a healthcare expert. If user asked multiple questions, answer all of them.
3. Add positive encouragement in Korean that can help with exercise motivation at the end."""


map_template = """Summarize the user's text, separated by three sharp(###), in 3 bullet points.
###{text}###"""

combine_template = """{text}

{format_instructions}"""

map_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template(map_template),
    ],
    input_variables=["text"],
)
combine_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(combine_system_prompt_with_format_instructions),
        HumanMessagePromptTemplate.from_template(combine_template),
    ],
    input_variables=["text"],
    partial_variables={"format_instructions": ai_coaching_parser.get_format_instructions()},
)
