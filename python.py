import webview
from transformers import pipeline

# Initialize the fill-mask pipeline
nlp = pipeline("fill-mask")

# Define the function to get suggestions
def get_suggestions(context_text):
    if context_text.strip() == "":
        return []
    masked_text = f"{context_text} {nlp.tokenizer.mask_token}"
    suggestions = nlp(masked_text)
    suggestion_texts = [suggestion['token_str'] for suggestion in suggestions]
    return suggestion_texts

# Define a class to expose Python functions to JavaScript
class API:
    def __init__(self):
        self.context = []
        self.common_phrases = {}

    def get_suggestions(self, text):
        self.context.append(text)
        if len(self.context) > 5:
            self.context = self.context[-5:]
        context_text = " ".join(self.context)

        # Update common phrases
        if text in self.common_phrases:
            self.common_phrases[text] += 1
        else:
            self.common_phrases[text] = 1

        # Use common phrases to influence predictions
        suggestions = get_suggestions(context_text)
        # Prefer commonly used phrases if they appear in suggestions
        suggestions = sorted(suggestions, key=lambda x: self.common_phrases.get(x, 0), reverse=True)
        return suggestions

# HTML content
html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Next Word Prediction</title>
<style>
  body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .chat-container {
    width: 75%;
    height: 75%;
    background: linear-gradient(45deg, purple, skyblue);
    padding: 40px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .chat-box {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 10px;
    padding-right: 10px;
  }

  .chat-message {
    background-color: #f2f2f2;
    color: #333;
    padding: 10px;
    max-width: 100%;
    border-radius: 5px;
    margin-bottom: 5px;
    font-family: poppins;
  }

  .bot-message {
    align-self: flex-start;
  }

  .user-input {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  input[type="text"] {
    padding: 15px;
    margin-bottom: 10px;
    border: none;
    border-radius: 5px;
    background-color: black;
    color: yellow;
    font-size: larger;
    width: 100%;
  }

  .suggestions {
    width: 100%;
    margin-bottom: 10px;
  }

  .suggestion {
    background-color: #444;
    color: white;
    padding: 10px;
    border-radius: 5px;
    cursor: pointer;
    margin-bottom: 5px;
  }

  .suggestion:hover {
    background-color: #666;
  }

  button {
    padding: 15px 30px;
    border: none;
    border-radius: 5px;
    background-color: #4CAF50;
    color: white;
    cursor: pointer;
  }

  button:hover {
    background-color: #45a049;
  }
</style>
</head>
<body>
<div class="chat-container" id="chat-container">
  <h1 style="text-align:center; color:white; margin-bottom: 20px;">Next Word Prediction</h1>
  <div class="chat-box" id="chat-box">
    <div class="chat-message bot-message">
      <span class="message">Welcome my friend! How can I help you?</span>
    </div>
  </div>
  <div class="user-input">
    <div class="suggestions" id="suggestions"></div>
    <input type="text" id="user-input" placeholder="Type your message...">
    <button oninput="sendMessage()">Send</button>
  </div>
</div>

<script>
  var context = [];

  function fetchSuggestions(text) {
    context.push(text);
    if (context.length > 5) {
      context.shift();  // Keep only the last 5 messages
    }
    var contextText = context.join(" ");  // Combine the context
    pywebview.api.get_suggestions(contextText).then(suggestions => {
      displaySuggestions(suggestions);
    }).catch(error => {
      console.error('Error fetching suggestions:', error);
    });
  }

  function displaySuggestions(suggestions) {
    var suggestionsContainer = document.getElementById("suggestions");
    suggestionsContainer.innerHTML = "";
    suggestions.forEach(function(suggestion) {
      var suggestionDiv = document.createElement("div");
      suggestionDiv.className = "suggestion";
      suggestionDiv.textContent = suggestion;
      suggestionDiv.addEventListener("click", function() {
        var userInput = document.getElementById("user-input");
        userInput.value += " " + suggestion;
        clearSuggestions();
        userInput.focus();
        fetchSuggestions(userInput.value.trim());
      });
      suggestionsContainer.appendChild(suggestionDiv);
    });
  }

  function clearSuggestions() {
    document.getElementById("suggestions").innerHTML = "";
  }

  function sendMessage() {
    var userInput = document.getElementById("user-input").value.trim();
    if (userInput !== "") {
      addMessage(userInput, 'user');
      setTimeout(function() {
        addMessage("Sorry, I'm just a simple bot. I don't understand much!", 'bot');
      }, 500);
      document.getElementById("user-input").value = "";
      clearSuggestions();
    }
  }

  function addMessage(message, sender) {
    var chatBox = document.getElementById("chat-box");
    var messageDiv = document.createElement("div");
    messageDiv.className = "chat-message " + sender + "-message";
    messageDiv.innerHTML = "<span class='message'>" + message + "</span>";
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  document.getElementById("user-input").addEventListener("input", function() {
    var text = this.value.trim();
    if (text !== "") {
      fetchSuggestions(text);
    } else {
      clearSuggestions();
    }
  });
</script>
</body>
</html>
"""

if __name__ == '__main__':
    api = API()
    window = webview.create_window('Simple Chat Bot', html=html, js_api=api)
    webview.start(debug=True)
