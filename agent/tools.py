# Don't trigger this prematurely!
def mock_lead_capture(name, email, platform):
    # Mocking the backend API call
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return True