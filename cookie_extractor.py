import browser_cookie3
import os
import platform

def get_cookies_and_save():
    """
    Extracts cookies from all supported browsers and saves them into files
    named after the domain they were extracted from.
    """
    # Create a directory to save cookies if it doesn't exist
    output_directory = "cookies"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        # Load cookies from all browsers.
        # This might ask for the system password on macOS.
        cj = browser_cookie3.load()

        if not cj:
            print("No cookies were found.")
            return

        # Iterate over the cookies and save them
        for cookie in cj:
            domain = cookie.domain
            
            # Clean the domain name to be a valid filename
            if domain.startswith("."):
                domain = domain[1:]
            
            # Remove invalid characters from the filename
            filename = "".join(c for c in domain if c.isalnum() or c in ('-', '_')).strip()
            
            if not filename:
                continue

            filepath = os.path.join(output_directory, f"{filename}.txt")
            
            # Append the cookie data to the file
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"Domain: {cookie.domain}\n")
                f.write(f"Name: {cookie.name}\n")
                f.write(f"Value: {cookie.value}\n")
                f.write(f"Expires: {cookie.expires}\n")
                f.write(f"Path: {cookie.path}\n")
                f.write(f"Secure: {cookie.secure}\n")
                f.write("-" * 20 + "\n\n")
        
        print(f"Successfully saved cookies to the '{output_directory}' folder.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if platform.system() == "Linux":
            print("On Linux, some browsers may require 'keyring' to be installed.")
        elif platform.system() == "Darwin": # macOS
             print("On macOS, you might need to grant access to the Keychain.")


if __name__ == "__main__":
    get_cookies_and_save()
