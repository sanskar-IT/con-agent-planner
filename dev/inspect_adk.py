import google.adk
print(dir(google.adk))
try:
    from google.adk import runner
    print("runner:", dir(runner))
except Exception as e:
    print(e)
