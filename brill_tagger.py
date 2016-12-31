"""
Parts of speech tagger based upon the paper 
http://www.aclweb.org/anthology/A92-1021

We use the Brown corpus for training the tagger and split it into 3 distinct parts
  90% - initial corpus = used to train the initial tagger
  10% - patch corpus = used to train the patch rules
  10% - test corpus = used to test the patch rules found from our training
"""

import random
import re

BROWNTAGS_BAD = set(['HL','TL','FW','NC'])
BROWNTAGS_PROPERNOUN = 'NP'

# Helper functions
def build_wordtag(word, tag): return (word, tag)
def tag(index, corpus): return corpus[index][0]
def word(index, corpus): return corpus[index][1]
def get_tagset(corpus): return set([tag for _, tag in corpus])

def initial_tagger(word, most_likely_tag, tag_set):
  if word in most_likely_tag:
    return most_likely_tag[word]
  elif ("A" <= word[0]) and (word[0] <= "Z"):
    return BROWNTAGS_PROPERNOUN  # Word is capitilized so most likely a proper noun
  else:
    return random.sample(tag_set, 1)[0]  # Return a random tag

# returns dictionary d where 
#  d[w][t] = num times word w is tagged as t
def gen_tagcnts(corpus):
  d = {w: {} for w,_ in corpus}
  for w, t in corpus:
    d[w][t] = (d[w][t]+1) if (t in d[w]) else 0
  return d

def parse_brown_wordtag(word_tag):
  # Remove hl (words in headlines),  tl (words in titles), fw (foreign word) or nc (cited word) hypenations 
  x = word_tag.rsplit('/', 1)
  if len(x) < 2: return None

  word, tag = x
  for t in tag.upper().split('-'):
    if (t not in BROWNTAGS_BAD):
      return build_wordtag(word, t)

  return None

# returns array of (word, tag) pairs
def load_corpus(fn):
  corpus = open(fn, 'r')
  word_tags = [parse_brown_wordtag(word_tag) for line in corpus for word_tag in line.strip('\n\t ').split(' ')]
  return [wt for wt in word_tags if wt != None]

# return a key which has the maximum value (note there may be more than one)
def max_elem(d):
  max_k, max_v = None, 0 
  for k in d:
    v = d[k]
    if v > max_v: max_k, max_v = k, v 
  return max_k
  
def errors(tagged, actual): 
  return [i for i in len(x) if tag(i, tagged) != tag(i, actual)]

# Return set of mismatches
def tag_mismatches(tagged, actual): 
  return set([(tag(i, tagged), tag(i, actual)) for i in len(tagged) if tag(i, tagged) != tag(i, actual)])

# rule has the form (match rule, replacement rule)
# returns list of transformed tags
def apply_rule(rule, corpus_tags):
  match_rule, replacement_rule = rule
  in_tagstr = ' '.join(corpus_tags)
  match_re = re.compile(match_rule)
  out_tagstr = match_re.sub(replacement_rule, in_tagstr)
  return out_tagstr.split(' ')
  
def gen_rules1(tag_a, tag_b, tag_set):
  rules = []
  for tag in tag_set:
    in_rule = ' '.join(tag, tag_a)
    out_rule = ' '.join(tag, tag_b)
    rules.append((in_rule, out_rule))
  return rules

### MAIN ###
def main():
  initial_corpus = load_corpus("./data/brown/initial_corpus.txt")

  tag_set = get_tagset(intial_corpus)
  tag_cnts = gen_tagcnts(initial_corpus)

  most_likely_tag = {w: max_elem(tag_cnts[w]) for w in tag_cnts}

  # perform the initial tagging on the patch corpus
  patch_corpus = load_corpus("./data/brown/patch_corpus.txt")
  x = [initial_tagger(word, most_likely_tag, tag_set) for word, _ in patch_corpus]

  # Now x most likely contains some errors. Store all such errors in a list.
  for tag_a, tag_b in tag_mismatches(x, patch_corpus):
    # iterate through rules (1-8) of Brill paper

    # Change tag_a to tag_b when

    # 1. The preceding (following) word is tagged z 
    rules = gen_rules1(tag_a, tag_b, tag_set)
    best_rule = None
    for rule in rules:
      new_x = apply_rule(rule, x)
      if len(errors(new_x)) < len(errors(x)): x, best_rule = new_x, rule

if __name__ == "__main__":
  main()
      



