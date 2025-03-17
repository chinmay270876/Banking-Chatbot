import requests
import json
import re  # Import regex for better input extraction

API_URL = "http://127.0.0.1:5000"  

def get_user_input():
    return input("You: ").strip()

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
        response.raise_for_status()
        return response.json().get("balance", "Error: No balance found.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def transfer_funds(from_account, to_account, amount):
    url = f"{API_URL}/transfer"
    data = {"fromAccount": from_account, "toAccount": to_account, "amount": amount}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        return response.json().get("message", "Transfer successful.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def get_help_info():
    url = f"{API_URL}/help"
    try:
        response = requests.get(url)
        response.raise_for_status()
        faq_data = response.json().get("faq", [])
        return faq_data if faq_data else ["No help available."]
    except requests.exceptions.RequestException as e:
        return [f"Error: {e}"]

def extract_transfer_details(user_input):
    """ Extracts account number and amount from a transfer request """
    match = re.search(r'to (\d+) \$?(\d+(\.\d+)?)', user_input)
    if match:
        to_account = match.group(1)
        amount = float(match.group(2))
        return to_account, amount
    return None, None

def run_chatbot():
    account_number = "123"  # Default account
    while True:
        user_input = get_user_input()
        intent = process_user_input(user_input)

        if intent == "balance":
            balance = get_account_balance(account_number)
            print(f"Bot: Your balance is ${balance}")
        
        elif intent == "transfer":
            to_account, amount = extract_transfer_details(user_input)
            if to_account and amount:
                result = transfer_funds(account_number, to_account, amount)
                print(f"Bot: {result}")
            else:
                print("Bot: Invalid transfer format. Use 'transfer to ACCOUNT_NUMBER $AMOUNT'")
        
        elif intent == "help":
            help_info = get_help_info()
            for item in help_info:
                print(f"Bot: {item['question']} - {item['answer']}" if isinstance(item, dict) else f"Bot: {item}")
        
        elif intent == "exit":
            print("Bot: Goodbye!")
            break
        
        else:
            print("Bot: I don't understand. Type 'help' for assistance.")

if __name__ == "__main__":
    run_chatbot()
