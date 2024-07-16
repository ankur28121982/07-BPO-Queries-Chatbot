import pandas as pd
import random
import tkinter as tk
import re
import os
from nltk.stem import PorterStemmer

# Initialize the Porter stemmer
porter = PorterStemmer()

# Get the current working directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Load the CSV files
file_path = os.path.join(current_directory, "repository.csv")
senti_path = os.path.join(current_directory, "senti.csv")
vuln_path = os.path.join(current_directory, "vuln.csv")

data = pd.read_csv(file_path, encoding='ISO-8859-1')
senti_data = pd.read_csv(senti_path, encoding='ISO-8859-1')
vuln_data = pd.read_csv(vuln_path, encoding='ISO-8859-1')

# Extract sentiment and vulnerability words and categorizations
positive_words = senti_data[senti_data['Sentiment'] == 'positive']['Word'].tolist()
negative_words = senti_data[senti_data['Sentiment'] == 'negative']['Word'].tolist()
senti_categories = senti_data.set_index('Word')['Sentiment'].to_dict()
vuln_categories = vuln_data.set_index('Word')['Categorization'].to_dict()

def score_match(user_input, bot_input):
    user_words = re.findall(r'\b\w+\b', user_input.lower())
    bot_words = re.findall(r'\b\w+\b', bot_input.lower())
    match_score, order_score, matched_words = 0, 0, []

    user_stemmed_words = [porter.stem(word) for word in user_words]
    bot_stemmed_words = [porter.stem(word) for word in bot_words]

    # Exact match condition
    if user_stemmed_words == bot_stemmed_words:
        return 100, 100, 200, user_stemmed_words  # Highest possible score for exact match

    for user_stem in user_stemmed_words:
        for bot_stem in bot_stemmed_words:
            if user_stem == bot_stem:
                match_score += 1
                matched_words.append(user_stem)
                break
    
    for i, user_word in enumerate(user_stemmed_words):
        if i < len(bot_stemmed_words) and user_word == bot_stemmed_words[i]:
            order_score += 1

    match_score_percentage = (match_score / len(user_stemmed_words)) * 100 if user_stemmed_words else 0
    order_score_percentage = (order_score / len(user_stemmed_words)) * 100 if user_stemmed_words else 0
    combined_score = min(match_score_percentage + order_score_percentage * 1.5, 100)

    return match_score_percentage, order_score_percentage, combined_score, matched_words

def get_response(user_input, data):
    best_combined_score, best_response, best_row_index = 0, "Sorry, I don't have an answer for that.", -1

    print(f"User Input: {user_input}")

    for index, row in data.iterrows():
        bot_input = row['Bot Input'].strip().lower()
        if user_input.strip().lower() == bot_input:
            best_response = random.choice([row['Response 1'], row['Response 2']])
            print(f"Exact match found at index {index}")
            print(f"Matched Words: {user_input.strip().lower().split()}")
            return best_response
    
    for index, row in data.iterrows():
        bot_input = row['Bot Input']
        match_score_percentage, order_score_percentage, combined_score, matched_words = score_match(user_input, bot_input)

        if combined_score > best_combined_score:
            best_combined_score = combined_score
            if combined_score >= 50:
                best_response = random.choice([row['Response 1'], row['Response 2']])
            best_row_index = index

    if best_combined_score < 50:
        best_response = "Sorry, I am not trained for this. please update my file repository.csv"

    if best_row_index != -1:
        print(f"Best Matched Row Index: {best_row_index}")
        print(f"Bot Input: {data.iloc[best_row_index]['Bot Input']}")
        print(f"Response 1: {data.iloc[best_row_index]['Response 1']}")
        print(f"Response 2: {data.iloc[best_row_index]['Response 2']}")
        print(f"Matched Words: {user_input.strip().lower().split()}")

    return best_response

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dr. Ankur")
        
        # Set up the blueish color theme
        self.root.configure(bg='#ADD8E6')
        self.chat_history = tk.Text(root, width=50, height=20, state='disabled', bg='#E0FFFF', fg='#00008B')
        self.chat_history.grid(row=0, column=0, padx=10, pady=10)
        self.user_input = tk.Entry(root, width=40, bg='#E0FFFF', fg='#00008B')
        self.user_input.grid(row=1, column=0, padx=10, pady=10)
        self.send_button = tk.Button(root, text="Send", command=self.send_message, bg='#1E90FF', fg='#FFFFFF')
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        self.root.bind('<Return>', lambda event: self.send_message())
        
        welcome_msg = "Greetings from Dr. Ankur! You're using the beta version of our tool, which currently has limited functionality. The full version will provide advanced features like transaction ID searches and more user options. Thank you for being part of our journey!"
        self.update_chat_history(f"Dr. Ankur: {welcome_msg}\n")

    def send_message(self):
        user_text = self.user_input.get()
        self.user_input.delete(0, 'end')
        self.update_chat_history("You: " + user_text + "\n")
        response = get_response(user_text, data)
        self.update_chat_history("Dr. Ankur: " + response + "\n")

    def update_chat_history(self, message):
        self.chat_history.configure(state='normal')
        self.chat_history.insert('end', message)
        self.chat_history.configure(state='disabled')
        self.chat_history.see('end')

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
