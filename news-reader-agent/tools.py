from crewai.tools import tool


@tool
def count_letters(sentence: str):
    """
    This function is for counting the amout of letters in a sentence.
    The input is a 'sentence' string.
    The output is a number.
    """
    return len(sentence)
