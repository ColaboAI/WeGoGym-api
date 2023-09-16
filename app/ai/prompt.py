from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.ai.schema import ai_coaching_parser


def get_zero_shot_prompt(text: str):
    prompt = f"""Our mission is to provide professional feedback to a user seeking advice related to weight training. 
    Use the following step-by-step instructions to respond to user inputs.

    1. Summarize main idea of the user's text, separated by ''' ''', in maximum 3 sentences of Korean.
    2. Analyze the text and provide a comprehensive answer from the perspective of a healthcare expert. You must provide specific answers in Korean to the questions user asked.
    3. Add positive encouragement in Korean that can help with exercise motivation at the end.

    
    '''{text}'''

    DO NOT RETURN ANY TEXT OTHER THAN INSTRUCTED FORMAT BELOW."""

    return prompt + ai_coaching_parser.get_format_instructions()


def make_chat_user_input(t: str):
    return f"'''\n{t}\n'''"


system_prompt = "You are health care expert. You are helping a user who is seeking advice related to weight training."

format_restriction = "DO NOT RETURN ANY TEXT OTHER THAN INSTRUCTED FORMAT BELOW."

combine_system_prompt_with_format_instructions = """You will be given a list of summaries of user question.

1. Take these and distill it into a final, consolidated summary into maximum 3 sentences of Korean.
2. Analyze the summary and provide a comprehensive answer from the perspective of a healthcare expert. You must provide specific answers in Korean to the questions user asked.
3. Add positive encouragement in Korean that can help with exercise motivation at the end."""


map_template = """Summarize the user's text, separated by ''' ''' in 3 bullet points.
'''{text}'''"""

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
