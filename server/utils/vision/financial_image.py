from core.llm import llm


async def summarize_financial_image(base64_str: str) -> str:
    """
    Summarize charts/images from 10-Q filings into retrievable text.
    """
    clean_base64 = base64_str.replace("\n", "").strip()

    prompt = (
        "This image is from a US SEC Form 10-Q filing.\n"
        "If it is a financial chart or table:\n"
        "- Identify the metric\n"
        "- Describe the trend\n"
        "- Extract any visible numbers\n"
        "If it is not financial, briefly describe the image.\n"
        "Do not speculate."
    )

    res = await llm.ainvoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{clean_base64}"},
                },
            ],
        }
    ])

    return res.content.strip()
