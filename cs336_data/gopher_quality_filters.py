def num_words(text):
    words = text.split()
    num_words = len(words)
    return 50 <= num_words <= 100000

def mean_word_length(text):
    words = text.split()
    num_words = len(words)
    total_len = 0.0
    for word in words:
        total_len += len(word)
    avg_len = total_len / num_words
    return 3 < avg_len < 10

def check_ellipsis(text):
    lines = text.split('\n')
    num_lines = len(lines)
    end_with_ellipsis = 0.0
    for line in lines:
        if line.endswith("..."):
            end_with_ellipsis += 1
    return end_with_ellipsis / num_lines < 0.3

def check_single_alpha(text):
    words = text.split()
    num_words = len(words)
    num_single = 0.0
    for word in words:
        if any(ch.isalpha() for ch in word):
            num_single += 1
    return num_single / num_words > 0.8



def run_gopher_rules(text):
    rule1 = num_words(text)
    rule2 = mean_word_length(text)
    rule3 = check_ellipsis(text)
    rule4 = check_single_alpha(text)

    return rule1 and rule2 and rule3 and rule4
