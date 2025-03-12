from flask import Flask, jsonify, request  # Added request import
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Mock database (replace with a real database)
accounts = {
    "123": {"balance": 1000, "transactions": []},
    "456": {"balance": 500, "transactions": []},
}

@app.route('/balance', methods=['GET'])
def get_balance():
    account_number = request.args.get('account') #get account from query parameter
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"balance": accounts[account_number]["balance"]})

@app.route('/transactions', methods=['GET'])
def get_transactions():
    account_number = request.args.get('account')
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"transactions": accounts[account_number]["transactions"]})

@app.route('/transfer', methods=['POST'])
def transfer_funds():
    data = request.get_json()
    from_account = data.get('fromAccount')
    to_account = data.get('toAccount')
    amount = data.get('amount')

    if from_account not in accounts or to_account not in accounts:
        return jsonify({"error": "Invalid account"}), 400

    if accounts[from_account]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    accounts[from_account]["balance"] -= amount
    accounts[to_account]["balance"] += amount

    accounts[from_account]["transactions"].append({"type": "debit", "amount": amount, "to": to_account})
    accounts[to_account]["transactions"].append({"type": "credit", "amount": amount, "from": from_account})

    return jsonify({"message": "Transfer successful"})

@app.route('/help', methods=['GET'])
def get_help():
    help_data = {
        "faq": [
            {"question": "How do I check my balance?", "answer": "Use /balance?account=YOUR_ACCOUNT_NUMBER"},
            {"question": "How do I transfer funds?", "answer": "Use POST /transfer with JSON data."},
        ]
    }
    return jsonify(help_data)

if __name__ == '__main__':
    app.run(debug=True)