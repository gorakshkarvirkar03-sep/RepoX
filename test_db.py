from modules.db import create_user, verify_user

user, err = create_user("Test User", "test@example.com", "pass1234")
print("CREATE:", user, err)
print("LOGIN OK:", verify_user("test@example.com", "pass1234"))
print("LOGIN WRONG:", verify_user("test@example.com", "wrong"))