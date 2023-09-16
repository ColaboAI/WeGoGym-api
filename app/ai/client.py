from app.ai.config import ai_settings
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .prompt import map_prompt, combine_prompt


text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=2000, chunk_overlap=400)


def get_summary_chain(model_name: str = "gpt-3.5-turbo", chain_type="map_reduce", verbose: bool = True, **kwargs):
    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=ai_settings.OPENAI_API_KEY,
        verbose=True,
    )
    return load_summarize_chain(
        llm=llm,
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        chain_type=chain_type,
        verbose=verbose,
        **kwargs,
    )
