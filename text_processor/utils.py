def bionic_reading(text):
    words = text.split()
    output = []

    for word in words:
        cut = max(1, int(len(word) * 0.4))
        bold_part = word[:cut]   # FIRST N letters, no duplication
        rest_part = word[cut:]   # rest of the word
        output.append(f"<strong>{bold_part}</strong>{rest_part}")
    return " ".join(output)
