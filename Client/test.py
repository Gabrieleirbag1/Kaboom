import re

text = "**zfzfzfzéézvze  ff ''"
print(text)
text = re.sub(r'[^a-zA-ZÀ-ÿ]', '', text)

print(text)