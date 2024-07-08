import os

def process_email(email):
    # Trim the part after '@' from the email
    trimmed_email = email.split('@')[0]

    # Read the content of chatbot.txt file
    with open('chatbot_template.txt', 'r') as file:
        chatbot_content = file.read()

    with open('javascript_template.txt', 'r') as JS:
        javascript_content = JS.read()

    # Replace '{{ext_user_email}}' with the trimmed email in chatbot_content
    modified_content = chatbot_content.replace('{{ext_user_email}}', trimmed_email)

    modified_content_2 = javascript_content.replace('{{ext_user_folder}}', trimmed_email)

    # Create a new directory in the Users folder with the trimmed email as the folder name
    directory_path = os.path.join('Users', trimmed_email)
    os.makedirs(directory_path, exist_ok=True)

    # Save the modified content to a new HTML file in the created directory
    html_file_path = os.path.join(directory_path, 'chatbot.html')
    with open(html_file_path, 'w') as html_file:
        html_file.write(modified_content)

    js_file_path = os.path.join(directory_path, 'chatbot.js')
    with open(js_file_path, 'w') as js_file:
        js_file.write(modified_content_2)

    addr = f"{js_file_path}"

    return addr

# Example usage:
#email = 'user_name'
#process_email(email)


if __name__ == "__main__":
    # Code to execute when the script is run directly
    import sys
    user_name = sys.argv[1] if len(sys.argv) > 1 else ""

    process_email(user_name)
