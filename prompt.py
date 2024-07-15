SUMMARIZER_PROMPT = """Please analyze and summarize the following research abstract into a three sentence summary for a research community newsletter. Please answer in the following JSON format, filling in relevant information within square brackets:
{
    "whats new": "[what new things does this research tackle]",
    "technical details": "[technical details related to this research]",
    "results": "[what does this research conclude]"
}
"""
