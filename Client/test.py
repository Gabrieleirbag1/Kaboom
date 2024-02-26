def process_input(input):
    match input:
        case "hello":
            print("Hello!")
        case "goodbye":
            print("Goodbye!")
        case _:
            print("Invalid input")

process_input("hello")
