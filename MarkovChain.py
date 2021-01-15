import re
import random
import os
import sys


# Reads the data from each file in the specified directory.
def parse_file(directory):
    content = []
    for filename in os.listdir(directory):
        path = directory + filename
        f = open(path, encoding="utf8")
        content.append(f.read().replace("\n", " "))
    return content


# Converts the input to tokens.
def tokenize_content(contents, stop_words):
    tok = []
    for content in contents:
        content = ''.join(map(str, content))
        content = content.lower()
        content = re.sub(r'[^a-zA-Z0-9]+', ' ', content)
        content = ' '.join(content.split())
        token = content.split(" ")
        token = [word for word in token if word not in stop_words]
        tok.append(token)
    tokens = [item for sublist in tok for item in sublist]
    return tokens


# Constructs n-grams by using the tokens. Here, n = 1, 2, 3.
def construct_ngrams(tokens, n):
    n_grams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in n_grams]


# Calculates the probability of all the uni-grams, i.e; n = 1.
def find_prob_uni(uni_grams):
    prob = {}
    unique_grams = set(uni_grams)
    for uni_gram in unique_grams:
        prob[uni_gram] = uni_grams.count(uni_gram)/len(uni_grams)
    return prob


# Calculates the probability of all the bi-grams, i.e; n = 2.
def find_prob_bi(bi_grams, prob_uni, uni_grams):
    prob = {}
    i = 0
    while i + 1 < len(bi_grams):
        bi_str = bi_grams[i].split(" ")
        if bi_str[0] in prob.keys():
            if bi_str[1] in prob[bi_str[0]].keys():
                prob[bi_str[0]][bi_str[1]] = prob[bi_str[0]][bi_str[1]] + 1/(prob_uni[bi_str[0]] * len(uni_grams))
            else:
                prob[bi_str[0]][bi_str[1]] = 1/(prob_uni[bi_str[0]] * len(uni_grams))
        else:
            prob[bi_str[0]] = {bi_str[1]: 1/(prob_uni[bi_str[0]] * len(uni_grams))}
        i = i + 1
    return prob


# Calculates the probability of all the tri-grams, i.e; n = 3.
def find_prob_tri(tri_grams, prob_bi, uni_grams, prob_uni):
    prob = {}
    i = 0
    while i + 1 < len(tri_grams):
        tri_str = tri_grams[i].split(" ")
        tri_str[0] = tri_str[0] + ' ' + tri_str[1]
        tri_str[1] = tri_str[2]
        tri_str = tri_str[:-1]
        tri = tri_str[0].split(" ")
        if tri_str[0] in prob.keys():
            if tri_str[1] in prob[tri_str[0]].keys():
                prob[tri_str[0]][tri_str[1]] = prob[tri_str[0]][tri_str[1]] + 1/(prob_bi[tri[0]][tri[1]] * prob_uni[tri[0]] * len(uni_grams))
            else:
                prob[tri_str[0]][tri_str[1]] = 1/(prob_bi[tri[0]][tri[1]] * prob_uni[tri[0]] * len(uni_grams))
        else:
            prob[tri_str[0]] = {tri_str[1]: 1/(prob_bi[tri[0]][tri[1]] * prob_uni[tri[0]] * len(uni_grams))}
        i = i + 1
    return prob


# Generates the random sequence and calculates the probability of the sequence.
def generate_sequence(prob_uni, prob_bi, prob_tri):
    s_count = 0
    sequence = []
    while s_count < 10:
        seq = []
        first = random.choice(list(prob_uni))
        second = random.choice(list(prob_bi[first]))
        seq.append(first)
        seq.append(second)
        prob = prob_uni[first] * prob_bi[first][second]
        w_count = 2
        while w_count < 20:
            next_word = random.choice(list(prob_tri[first + " " + second]))
            seq.append(next_word)
            prob = prob * prob_tri[first + " " + second][next_word]
            first = second
            second = next_word
            w_count = w_count + 1
        s_count = s_count + 1
        sequence.append((seq, prob))
    return sequence


# Writes the sequences along with their probabilities to the ResultsFile.txt.
def write_sequence_file(sequence):
    result_file.write("Random sequences and their probabilities for the given author: \r")
    for i in range(len(sequence)):
        seq = ' '.join(sequence[i][0])
        result_file.write("Sequence %s: " % (i+1) + "%s = " % seq + "%s\r" % sequence[i][1])


# Writes the probabilities of all the uni-grams, bi-grams and tri-grams of both the authors into the ProbFile1.txt and
# ProbFile2.txt respectively.
def write_probability_file(prob_uni, prob_bi, prob_tri):
    p_file.write("Probabilities of Unigrams, Bigrams and Trigrams: \r\r")
    p_file.write("Unigrams: \r\r")
    for x in prob_uni.keys():
        p_file.write("P(%s" % x + ") = %s\r" % prob_uni[x])
    p_file.write("\r--------------------------------------------------------------------------------------------\r\r\r")

    p_file.write("Bigrams: \r\r")
    for x in prob_bi.keys():
        for y in prob_bi[x].keys():
            p_file.write("P(%s" % y + " | %s" % x + ") = %s" % prob_bi[x][y] + ";\t")
        p_file.write("\r")
    p_file.write("\r--------------------------------------------------------------------------------------------\r\r\r")

    p_file.write("Trigrams: \r\r")
    for x in prob_tri.keys():
        for y in prob_tri[x].keys():
            p_file.write("P(%s" % y + " | %s" % x + ") = %s" % prob_tri[x][y] + ";\t")
        p_file.write("\r")
    p_file.write("\r--------------------------------------------------------------------------------------------\r\r\r")


def main():
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                  'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
                  'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                  'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                  'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
                  'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                  'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                  'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                  'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                  'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
                  'now']
    directory = sys.argv[1]
    content = parse_file(directory)
    tokens = tokenize_content(content, stop_words)
    uni_grams = construct_ngrams(tokens, 1)
    bi_grams = construct_ngrams(tokens, 2)
    tri_grams = construct_ngrams(tokens, 3)
    prob_uni = find_prob_uni(uni_grams)
    prob_bi = find_prob_bi(bi_grams, prob_uni, uni_grams)
    prob_tri = find_prob_tri(tri_grams, prob_bi, uni_grams, prob_uni)
    write_probability_file(prob_uni, prob_bi, prob_tri)
    sequence = generate_sequence(prob_uni, prob_bi, prob_tri)
    write_sequence_file(sequence)


if __name__ == "__main__":
    probFile = sys.argv[2]
    resultsFile = sys.argv[3]
    open(probFile+".txt", "w").close()
    open(resultsFile+".txt", "w").close()
    p_file = open(probFile+".txt", "a+")
    result_file = open(resultsFile+".txt", "a+")
    main()
