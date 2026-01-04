def bionic_reading(text):
    words = text.split()
    output = []

    for word in words:
        cut = max(1, int(len(word) * 0.4))
        output.append(f"<strong>{word[:cut]}</strong>{word[cut:]}")

    return " ".join(output)
