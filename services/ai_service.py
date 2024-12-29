from openai import AsyncOpenAI
from dependencies import get_settings

async def generate_article_summary(content: str) -> str:
    """
    生成文章摘要
    """ 
    client = AsyncOpenAI(
        api_key=get_settings().OPENAI_API_KEY,
        base_url=get_settings().OPENAI_BASE_URL
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "你是一个文章摘要生成助手。请生成一个简短的摘要，不超过100字。"}, {"role": "user", "content": content}],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
