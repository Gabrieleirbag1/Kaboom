liste = [1 , 2, 3, 4, 5]
lsite2 = ["a", "b", "c", "d", "e"]

for i in range(len(liste)):
    print(liste[i], lsite2[i])

string_value = "False"
if string_value == "False":
    bool_value = False
else:
    bool_value = bool(string_value)
print(bool_value)
