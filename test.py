#  Problem: Print Words with Frequency K

def frequency_counter (string, k):
    words = string.split()
    freq = {}

    for i in words:
        freq[i] = freq.get(i , 0) + 1
    
    all = []
    for i, count in freq.items():
        if count == k:
            all.append(i)
    return all

    

s = "dog cat dog bird cat"
k = 2
print(frequency_counter(s, k))