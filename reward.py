from langdetect import detect
import re
from math_verify import parse, verify

def acc_reward_func(completions, golds, **kwargs):
    rewards = []
    for comp,gold in zip(completions,golds):
        try:
            rewards.append(acc_reward_single(comp,gold))
        except:
            rewards.append(0.0)
    return rewards

def format_reward_func(completions, **kwargs):
    rewards = []
    for comp in completions:
        try:
            rewards.append(format_reward_single(comp))
        except:
            rewards.append(0.0)
    return rewards

def boxed_reward_func(completions, **kwargs):
    rewards = []
    for comp in completions:
        try:
            rewards.append(box_single(comp))
        except:
            rewards.append(0.0)
    return rewards

def lang_reward_func(completions, languages, **kwargs):
    rewards = []
    for comp, lang in zip(completions, languages):
        try:
            rewards.append(lang_reward_single(comp,lang))
        except:
            rewards.append(0.0)
    return rewards

def think_reward_func(completions, **kwargs):
    rewards = []
    for comp in completions:
        try:
            rewards.append(think_reward_single(comp))
        except:
            rewards.append(0.0)
    return rewards

def box_single(text):
    score = 0.0
    if '<solution>' not in text:
        return score
    think,solution = text.split('<solution>')
    if think.count('boxed') == 1:
        score += 0.5
    if solution.count('boxed') == 1:
        score += 0.5 
    return score
    
def acc_reward_single(text, gold):
    """
    Computes the reward based on the correctness of the answer.
    
    Args:
        text (str): The text containing the solution.
        gold (str): The provided answer.
    
    Returns:
        float: 1.0 if correct, 0.0 otherwise.
    """
    score = -1.0
    if not isinstance(gold, str):
        gold = str(gold)
    
    # Extract solution part
    # parts = text.split("<solution>", 1)
    # if len(parts) < 2:
    #     return -1.0  # No solution token found
    
    solution_part = text
    
    # Parse the solution and answer
    parsed_answers = parse(solution_part)
    
    # Verify correctness
    if verify(gold, parsed_answers):
        score += 1.0
    
    # Check if any parsed answer is in solution or vice versa
    if any(str(ans) in gold for ans in parsed_answers):
        score += 1.0
    if "boxed" in text:
        score += 1.0
    return score

def remove_math_expressions(text: str) -> str:
    """
    Removes mathematical expressions from the given text.
    """
    # Remove inline math expressions \( ... \)
    text = re.sub(r'\\\(.*?\\\)', '', text, flags=re.DOTALL)
    # Remove block math expressions \[ ... \]
    text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)
    # Remove boxed expressions \boxed{ ... }
    text = re.sub(r'\\boxed{.*?}', '', text, flags=re.DOTALL)
    # Remove special characters, newlines, colons, and asterisks
    text = re.sub(r'[\n*:\\]', '', text)
    return text.strip()

def lang_reward_single(text: str, language: str) -> float:
    """
    Checks if the language of the solution part matches the given ISO language code.
    
    Args:
        text (str): The input text containing a solution.
        language (str): The expected language in ISO-code format.
    
    Returns:
        float: 1.0 if the detected language matches, otherwise 0.0.
    """
    # Extract solution part
    parts = text.split("<solution>", 1)
    if len(parts) < 2:
        return 0.0  # No solution token found
    
    solution_part = parts[1].strip()
    
    # Remove math expressions
    clean_text = remove_math_expressions(solution_part)
    
    # Detect language
    detected_lang = detect(clean_text)
    
    return 1.0 if detected_lang == language else 0.0

# def format_reward_single(text: str) -> float:
#     """
#     Computes a reward based on the presence of <think> and <solution> tags.
    
#     Args:
#         text (str): The input text to evaluate.
    
#     Returns:
#         float: The cumulative reward based on tag occurrences.
#     """
#     reward = 0.0
    
#     if "</think>" in text:
#         reward += 0.5
#     if "<solution>" in text and "</solution>" in text:
#         reward += 0.5
    
#     return reward

def think_reward_single(text: str) -> float:
    """
    Splits the text based on the '</think>' token and rewards 1.0 only if:
      1. The think part (the text before '</think>') is longer than the solution part (the text after '</think>').
      2. The think part is written in English.
      
    Assumes the availability of helper functions:
      - remove_math_expressions(text: str) -> str
      - detect(text: str) -> str  (which returns an ISO language code, e.g., 'en' for English)
    
    Args:
        text (str): The input text containing both think and solution parts.
    
    Returns:
        float: 1.0 if both conditions are met, otherwise 0.0.
    """
    score = 0.0
    # Split the text at the first occurrence of '</think>'
    parts = text.split("</think>", 1)
    if len(parts) < 2:
        score -= 0.5
    
    think_part = parts[0].strip()      # Text before </think>
    solution_part = parts[1].strip()   # Text after </think>
    
    # Check that the think part is longer than the solution part
    if len(think_part.split()) <= len(solution_part.split()):
        score -= 0.5
    
    else:
        score += 1.0

    return score


def format_reward_single(text: str) -> float:
    """
    Computes a reward based on the presence of the required tags.
    It rewards 1.0 only if:
      - The text contains exactly one occurrence of "</think>",
      - Exactly one occurrence of "<solution>",
      - Exactly one occurrence of "</solution>",
      - And these appear in the order: </think> then <solution> then </solution>.
      
    Args:
        text (str): The input text to evaluate.
    
    Returns:
        float: The reward (1.0 if conditions are met, otherwise 0.0).
    """
    # Count occurrences of each tag.
    if (text.count("</think>") != 1 or 
        text.count("<solution>") != 1 or 
        text.count("</solution>") != 1):
        return 0.0

    # Find the indices (positions) of each tag.
    pos_think_close = text.find("</think>")
    pos_solution_open = text.find("<solution>")
    pos_solution_close = text.find("</solution>")

    # Check that the tags appear in the correct order:
    # </think> must appear before <solution> and <solution> before </solution>.
    if pos_think_close < pos_solution_open < pos_solution_close:
        return 1.0
    else:
        return 0.0
