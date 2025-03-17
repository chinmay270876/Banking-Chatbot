require('dotenv').config();
const express = require("express");
const path = require("path");
const multer = require("multer");
const fs = require("fs");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const axios = require("axios");

const app = express();
const uploads = multer({ dest: "uploads/" });

if (!process.env.GEMINI_API_KEY) {
    console.error("Error: env file is missing the API key");
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const BANKING_API_URL = process.env.BANKING_API_URL || "http://127.0.0.1:5000";

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.post("/get", uploads.single("file"), async (req, res) => {
    const userInput = req.body.msg;
    const file = req.file;

    try {
        let geminiText = "";
        let bankingResponse = "";

        // Banking-related request
        if (userInput.toLowerCase().includes("balance") || 
            userInput.toLowerCase().includes("transfer") ||
            userInput.toLowerCase().includes("transactions") ||
            userInput.toLowerCase().includes("help")) {

            if (userInput.toLowerCase().includes("balance")) {
                try {
                    const bankingApiUrl = `${BANKING_API_URL}/balance?account=123`;
                    const bankingApiResponse = await axios.get(bankingApiUrl);
                    const balanceData = bankingApiResponse.data;

                    if (balanceData && balanceData.hasOwnProperty('balance')) {
                        bankingResponse = `balance = ${balanceData.balance}`;
                    } else if (balanceData && balanceData.hasOwnProperty('error')) {
                        bankingResponse = balanceData.error;
                    } else {
                        bankingResponse = "Error retrieving balance.";
                    }
                } catch (bankingError) {
                    console.error("Error calling banking API:", bankingError);
                    bankingResponse = "Error retrieving banking data.";
                }
            } else if (userInput.toLowerCase().includes("transfer")) {
                try {
                    const transferData = {
                        fromAccount: "123",
                        toAccount: "456",
                        amount: 100,
                    };
                    const bankingApiUrl = `${BANKING_API_URL}/transfer`;
                    const bankingApiResponse = await axios.post(bankingApiUrl, transferData);
                    const transferResult = bankingApiResponse.data;

                    if (transferResult && transferResult.hasOwnProperty('message')) {
                        bankingResponse = transferResult.message;
                    } else if (transferResult && transferResult.hasOwnProperty('error')) {
                        bankingResponse = transferResult.error;
                    } else {
                        bankingResponse = "Error processing transfer.";
                    }
                } catch (bankingError) {
                    console.error("Error calling banking API:", bankingError);
                    bankingResponse = "Error processing transfer.";
                }
            } else if (userInput.toLowerCase().includes("transactions")) {
                try {
                    const bankingApiUrl = `${BANKING_API_URL}/transactions?account=123`;
                    const bankingApiResponse = await axios.get(bankingApiUrl);
                    const transactionData = bankingApiResponse.data;

                    if (transactionData && transactionData.hasOwnProperty('transactions')) {
                        bankingResponse = `transactions = ${JSON.stringify(transactionData.transactions)}`;
                    } else if (transactionData && transactionData.hasOwnProperty('error')) {
                        bankingResponse = transactionData.error;
                    } else {
                        bankingResponse = "Error retrieving transactions.";
                    }
                } catch (bankingError) {
                    console.error("Error calling banking API:", bankingError);
                    bankingResponse = "Error retrieving transactions.";
                }
            } else if (userInput.toLowerCase().includes("help")) {
                try {
                    const bankingApiUrl = `${BANKING_API_URL}/help`;
                    const bankingApiResponse = await axios.get(bankingApiUrl);
                    const helpData = bankingApiResponse.data;

                    if (helpData && helpData.hasOwnProperty('faq')) {
                        bankingResponse = `help = ${JSON.stringify(helpData.faq)}`;
                    } else if (helpData && helpData.hasOwnProperty('error')) {
                        bankingResponse = helpData.error;
                    } else {
                        bankingResponse = "Error retrieving help.";
                    }
                } catch (bankingError) {
                    console.error("Error calling banking API:", bankingError);
                    bankingResponse = "Error retrieving help.";
                }
            }
        } else { // Gemini-related request
            const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
            let prompt = userInput;

            if (file) {
                const fileData = fs.readFileSync(file.path);
                const image = {
                    inlineData: {
                        data: fileData.toString("base64"),
                        mimeType: file.mimetype,
                    },
                };
                prompt.push(image);
            }

            const geminiResponse = await model.generateContent(prompt);
            geminiText = geminiResponse.response.text();
        }

        // Combine responses (prioritize banking if both are present)
        let combinedResponse = bankingResponse ? bankingResponse : geminiText;

        res.send(combinedResponse);

    } catch (error) {
        console.error("Error generating response:", error);
        res.status(error.status || 500).send("An error occurred while generating the response");
    } finally {
        if (file) {
            fs.unlinkSync(file.path);
        }
    }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
