#! /usr/bin/env python

import json, sys

TARGET=0
FROM=0
TYPE=1

def assembleDependencyGraph(words,dependencies):
    root = []
    graph = []
    backgraph = []
    for i in range(0,len(words)):
        graph.append([])
        backgraph.append([])
    for d in dependencies:
        tokens = d[:-1].split("(")
        edge_type = tokens[0]
        
        # must be an integer index into the words array
        nodes = tokens[1].split(', ') # assume there are no spaces in tokens???
        fromNode = int(nodes[0].split("-")[-1])
        toNode   = int(nodes[1].split("-")[-1])
        if fromNode==0:
            root.append((toNode-1,edge_type))
        else:
            graph[fromNode-1].append((toNode-1,edge_type))
            backgraph[toNode-1].append((fromNode-1,edge_type)) #add the back pointer
            
    return (root,graph,backgraph)



def getNearbyWords(features, start_pos, length, words, pos_tags):
    span = 6 # the max distance from this word
    start = start_pos-span if start_pos-span > 0 else 0
    end   = start_pos+length+span if start_pos+length+span<=len(words) else len(words)
    for k in range(start,end):
        if ( pos_tags[k].startswith('NN') or # noun
             pos_tags[k].startswith('VB') or # verb
             pos_tags[k].startswith('JJ') or # adjective
             pos_tags[k].startswith('RB') or # adverb
             pos_tags[k].startswith('FW') ): # foreign word (often a species/chemical name)
            features.add("nearby:"+words[k])

def getNounCompoundModifierList(graph,edge):
    if not edge:
        return
    cm = []
    if(edge[TYPE]=='nn'):
        cm.append(edge[TARGET])
        for nextEdge in graph[edge[TARGET]]:
            cm.extend(getNounCompoundModifierList(graph,nextEdge))
    return cm

# For each sentence
for row in sys.stdin:
    feature_obj = json.loads(row)
    
    features = set()
    
    words        = feature_obj["pmc_sentences.words"]         # a list of all words
    pos_tags     = feature_obj["pmc_sentences.pos_tags"]      # Part of Speech tags for each word
    lemma        = feature_obj["pmc_sentences.lemma"]         # lemmatization of the word (e.g the base word)
    dependencies = feature_obj["pmc_sentences.dependencies"]  # parsed dependency structure of the sentence
    
    (root,graph,backgraph) = assembleDependencyGraph(words,dependencies)
    
    relation_id    = feature_obj["is_cellular_component.relation_id"]
    term           = feature_obj["is_cellular_component.term"]
    term_start_pos = feature_obj["pmc_terms.start_position"]
    term_length    = feature_obj["pmc_terms.length"]
    try:
        sys.stderr.write("======\n");
        sys.stderr.write("term: "+term+"\n");
        #sys.stderr.write("sentence: "+' '.join(words).encode('utf-8')+"\n");
        #sys.stderr.write(' '.join(pos_tags)+"\n");
        #sys.stderr.write(str(lemma)+"\n");
        #sys.stderr.write("deps: "+' '.join(dependencies)+"\n");
    except:
        temp = 2
    
    # the stupid feature: get some nearby nouns and verbs (but we use lemma-ized words instead at least)
    getNearbyWords(features, term_start_pos, term_length, lemma, pos_tags)
    
    for feature in features:  
       # sys.stderr.write("out:"+json.dumps({
       #   "relation_id": relation_id,
       #   "feature": feature
       # })+"\n")
       print json.dumps({
          "relation_id": relation_id,
          "feature": feature
        })
    
    






