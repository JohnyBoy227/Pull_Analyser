import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)
import tkinter as tk

# Load .env variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate key presence
if not ANTHROPIC_API_KEY:
    raise ValueError("Claude API key not found in .env!")

# Set up config using Claude 3.5 Sonnet
anthropic_config = Config.from_default(
    llm_provider=LLMProvider.ANTHROPIC,
    llm_model_name=LLMModel.CLAUDE_3_5_SONNET,
    anthropic_api_key=ANTHROPIC_API_KEY
)

# Initialize Portia
portia = Portia(config=anthropic_config, tools=example_tool_registry)

# Function to run Portia for code review
def review_code(diff: str):
    # Run the code review using Portia and get the result
    review_result = portia.run(f"Review the following code for readability, function length, naming conventions, and possible improvements:\n{diff}")
    return review_result  # Return the entire review result (log)

# Accept and Reject buttons
def accept_input():
    print("Reviewing changes...")
    # Placeholder for actual acceptance logic, like saving the feedback or moving forward with changes
    #portia_comments_box.config(state=tk.NORMAL)
    #portia_comments_box.insert(tk.END, "\nChanges accepted.\n")
    #portia_comments_box.config(state=tk.DISABLED)

    #Now we need to store the line, put it into accepted feedback and 
    #then remove it with the renove line function 
    portia_comments_box.config(state=tk.NORMAL)
    content = portia_comments_box.get("1.0", tk.END)
    
    #Store it: 
    stopIndex = content.find(".")
    substring = content[:stopIndex + 1]
    
    accepted_feedback_box.config(state=tk.NORMAL)
    
    #Get current content
    current_content = accepted_feedback_box.get("1.0", tk.END).strip()

    #If it is empty/ not empty
    if current_content:
        accepted_feedback_box.insert(tk.END, "\n" + substring)
    else:
        accepted_feedback_box.insert(tk.END, substring)

    #Disable the text box again
    accepted_feedback_box.config(state=tk.DISABLED)

    #Now we need to remove
    remove_line()


def remove_line():
    portia_comments_box.config(state=tk.NORMAL)
    content = portia_comments_box.get("1.0", tk.END)
    stopIndex = content.find(".")
    if stopIndex != -1:
        newContent = content[stopIndex + 1:].lstrip()
        portia_comments_box.delete("1.0", tk.END)
        #Removes the line from the text and then replaces the text with 
        #The text without the line 
        portia_comments_box.insert("1.0", newContent)
    portia_comments_box.config(state=tk.DISABLED)

# Review changes callback
def review_changes():
    changes = github_changes_box.get("1.0", tk.END).strip()  # Get the changes entered in the multi-line text box
    if changes:
        # Get the full review including all output from Portia
        review_feedback = (review_code(changes)).model_dump_json(indent=2)
        
        # Display the entire output in the portia_comments_box
        portia_comments_box.config(state=tk.NORMAL)
        portia_comments_box.delete("1.0", tk.END)  # Clear previous feedback

        #Before we put the review feedback into the program we need to filter it for the sectionb of json we want

        #We need to find first all parts after final_output
        
        # Find the first occurrence of 'final_output'
        index = review_feedback.find("final_output")
        substring = ""

        if index != -1: 
            #Extract the part of the string after 'final_output'
            review_feedback = review_feedback[index + len("final_output"):]

        #find the occurance of sumary which we want
        index = review_feedback.find("summary")
        
        if index != -1: 
            #Extract the part of the string after 'final_output'
            review_feedback = review_feedback[index + len("summary"):]


        start = review_feedback.find('": ')
        if start != -1:
            # Move past '#": ' (which is 4 characters)
            start += 4

            end = (len(review_feedback) - 13)
            #end = review_feedback.find('"', start)
            value = review_feedback[start:end]

        sentences = [s.strip() for s in value.split('.') if s.strip()]

        for sentence in sentences:
            portia_comments_box.insert(tk.END, sentence + '.\n')

        
        #portia_comments_box.insert(tk.END, review_feedback)  # Insert full output
        portia_comments_box.config(state=tk.DISABLED)
    else:
        portia_comments_box.config(state=tk.NORMAL)
        portia_comments_box.insert(tk.END, "No changes to review.\n")
        portia_comments_box.config(state=tk.DISABLED)

# Tkinter GUI Setup
window = tk.Tk()
window.geometry("600x600")

# Create a label
label = tk.Label(window, text="Enter your code or changes for review:")
label.pack(pady=10)

# Multi-line text box (Text widget) where the user can input the code/changes to review
github_changes_box = tk.Text(window, height=10, width=60)
github_changes_box.pack(pady=10)

# Create the buttons
review_button = tk.Button(window, text="Review Changes", command=review_changes)
review_button.pack(pady=10, fill=tk.X, padx=20, expand=True)

# Multi-line text box to load the Portia comments into it:
portia_comments_box = tk.Text(window, height=5, width=60)
portia_comments_box.pack(pady=20)
portia_comments_box.config(state=tk.DISABLED)

# Multi-line text box to load the GitHub changes (for context, if applicable)  
accepted_feedback_box = tk.Text(window, height=5, width=60)
accepted_feedback_box.pack(pady=20)
accepted_feedback_box.config(state=tk.DISABLED)

# Create a Frame to hold the buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=10, fill=tk.X)  # Fill horizontally for the frame

# Accept and Reject buttons
accept_button = tk.Button(button_frame, text="Accept Feedback", command=accept_input)
accept_button.pack(side=tk.LEFT, fill=tk.X, padx=20, expand=True)

reject_button = tk.Button(button_frame, text="Reject Feedback", command=remove_line)
reject_button.pack(side=tk.LEFT, fill=tk.X, padx=20, expand=True)

# Run the application 
window.mainloop() 