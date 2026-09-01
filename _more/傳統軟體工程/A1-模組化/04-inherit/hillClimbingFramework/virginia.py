def encrypt(text, key):
  list = []
  klen = len(key)
  for i in range(len(text)):
    ki = i% klen
    n1 = (ord(text[i])+key[ki])%128
    list.append(chr(n1))
  return ''.join(list)

def neg(key):
  nkey = [0]*len(key)
  for i in range(len(key)):
    nkey[i] = -key[i]
  return nkey

def decrypt(text, key):
  return encrypt(text, neg(key))

commons = ['is', 'of', 'am', 'the', 'a', 'in', 'at', 'on', 'go', 'to']

def fit(text):
  text = text.lower()
  score = 0
  for i in range(len(text)):
    if text[i].isalpha(): score += 0.05
    if i>0 and text[i-1].isalpha(): continue
    head = text[i:i+5]
    for word in commons:
      if head.startswith(word) and not head[len(word)].isalpha():
        score += 1
        break
  return score


