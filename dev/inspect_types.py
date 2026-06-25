from google.genai import types
print(dir(types))
try:
    print(types.UserContent)
except Exception as e:
    print(e)
try:
    print(types.Content(role="user", parts=[types.Part.from_text("hi")]))
except Exception as e:
    print(e)
