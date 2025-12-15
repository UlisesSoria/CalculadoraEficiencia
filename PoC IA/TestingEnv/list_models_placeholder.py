import google.generativeai as genai
import os

# You might need to set your API key here if it's not in the environment variables
# For now, I'll assume the user might have it set or I'll ask them to run it with their key if it fails.
# However, the previous script took it as input. 
# I will try to list models without an API key first, but usually it requires one.
# Since I don't have the user's API key, I will create a script that the user can run 
# OR I can try to use a placeholder and see if the error message changes, but listing models definitely needs auth.

# Wait, the user is running the streamlit app and inputting the key there.
# I cannot easily run a script that requires the key unless I ask the user for it or if it's in the env.
# The error message "Call ListModels" implies I should do that.

# Let's create a script that asks for the API key or tries to grab it from env.
# But better yet, I will modify LicitationAI.py temporarily to print the models 
# when the button is clicked, or just create a separate script and ask the user to run it 
# providing their key if they have it in env, or I can just try to guess the model `gemini-1.5-flash-001`.

# Actually, the error `models/gemini-1.5-flash is not found` is quite specific.
# It often means the model name is slightly different, like `gemini-1.5-flash-001`.
# Let's try `gemini-1.5-flash-001` directly as it's the most common versioned name.
# But to be sure, listing models is better.

# I will create a small script `list_models.py` and ask the user to run it, 
# or I can try to run it if I can find the key. 
# The user inputs the key in the Streamlit UI. I don't have access to it.

# Alternative: I will modify `LicitationAI.py` to catch the 404 error and print the available models 
# to the Streamlit UI. This is a much better user experience.

print("Listing models...")
try:
    # We need an API key to list models. 
    # Since I don't have it, I can't run this script successfully without user intervention.
    # So I will modify the main application to help debug this.
    pass
except Exception as e:
    print(e)
