import requests
import json

API_URL = "http://127.0.0.1:5000"  # Your API URL

def get_user_input():
    return input("You: ")

def process_user_input(user_input):
    user_input = user_input.lower()

    if "balance" in user_input:
        return "balance"
    elif "transfer" in user_input:
        return "transfer"
    elif "help" in user_input:
        return "help"
    elif "exit" in user_input:
        return "exit"
    else:
        return "unknown"

def get_account_balance(account_number):
    url = f"{API_URL}/balance?account={account_number}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json().get("balance")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except (ValueError, KeyError):
        return "Error: Invalid response from server."

def transfer_funds(from_account, to_account, amount):
    url = f"{API_URL}/transfer"
    data = {
        "fromAccount": from_account,
        "toAccount": to_account,
        "amount": amount,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        return response.json().get("message")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except (ValueError, KeyError):
        return "Error: Invalid response from server."

def get_help_info():
    url = f"{API_URL}/help"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("faq")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except (ValueError, KeyError):
        return "Error: Invalid response from server."

def run_chatbot():
    account_number = "123"  # Assuming we have a default account for simplicity
    while True:
        user_input = get_user_input()
        intent = process_user_input(user_input)

        if intent == "balance":
            balance = get_account_balance(account_number)
            print(f"Bot: Your balance is ${balance}")
        elif intent == "transfer":
            try:
                parts = user_input.split()
                to_account = parts[parts.index("to") + 1]
                amount = float(parts[parts.index("$") + 1])
                result = transfer_funds(account_number, to_account, amount)
                print(f"Bot: {result}")
            except (ValueError, IndexError):
                print("Bot: Invalid transfer format. Use 'transfer to ACCOUNT_NUMBER $AMOUNT'")
        elif intent == "help":
            help_info = get_help_info()
            for item in help_info:
                print(f"Bot: {item['question']} - {item['answer']}")
        elif intent == "exit":
            print("Bot: Goodbye!")
            break
        elif intent == "unknown":
            print("Bot: I don't understand.")

if __name__ == "__main__":
    run_chatbot()