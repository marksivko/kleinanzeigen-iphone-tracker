import ollama

task_text = ("Look at the following description of a used phone and give me the information about the condition of the phone. The overall condition metric is your personal approximate judgement based on the description. Any crack in the phone counts as a broken part, however a scratch does not. If there is not enough information to make a conclusion about a stat, write Unknown. The answer must be in the following format:"
             "Any parts broken: True/False/Unknown"
             "Battery health: Percentage/Unknown"
             "Overall Condition: X/10"
             "\n\n"
             "Description: \n")
text = "Verkaufe mein iPhone 13 in Blau. Technisch funktioniert alles einwandfrei: * Face ID funktioniert * Kameras funktionieren * Lautsprecher/Mikrofon okay * Display funktioniert komplett Optisch starke Gebrauchsspuren: * Vorderseite gesprungen * Rückseite beschädigt Kein iCloud-Lock."

def generate(prompt: str) -> str:
    response = ollama.chat(model="gemma4:e4b", messages=[{"role": "user", "content": prompt}], think=False, keep_alive="60m")
    return response["message"]["content"]

def get_description_rating(description: str) -> dict:
    if description.strip() == "":
        description = "No description."

    prompt = task_text + description
    response = ollama.chat(model="gemma4:e4b", messages=[{"role": "user", "content": prompt}], think=False, keep_alive="60m")
    answer_to_dict(response["message"]["content"])
    return answer_to_dict(response["message"]["content"])

def answer_to_dict(answer: str) -> dict:
    dictionary = {
            "parts_broken": "True" in answer.split(),
            "battery_health": 100,
            "overall_condition": 0
            }
    if "%" in answer:
        index = answer.index("%")
        dictionary["battery_health"] = int(answer[index-2:index])
    if "/" in answer:
        index = answer.index("/")
        if answer[index-1].isdigit():
            dictionary["overall_condition"] = int(answer[index-2:index])
    return dictionary

def generate_chichko(prompt: str) -> str:
    response = ollama.chat(model="gemma4:e4b", messages=[{"role": "user", "content": prompt}], think=False,
                       keep_alive="60m")
    return response["message"]["content"]

if __name__ == '__main__':
    print(text)
    print(get_description_rating(text))
