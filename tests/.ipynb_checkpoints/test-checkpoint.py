import os
did_path = os.getenv("DiD-path")

if did_path:
    # If "DiD-path" is set, use it for your application logic
    print(f"The 'DiD-path' environment variable is set to: {did_path}")
    # Proceed with the logic that uses did_path
else:
    # If "DiD-path" is not set, follow the alternative logic
    print("The 'DiD-path' environment variable is not set.")
    # Proceed with the default logic or manual execution path

