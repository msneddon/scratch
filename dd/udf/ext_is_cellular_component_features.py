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
    
    words        = feature_obj["pmc_sentences.words"]         # a list of all words
    pos_tags     = feature_obj["pmc_sentences.pos_tags"]      # Part of Speech tags for each word
    lemma        = feature_obj["pmc_sentences.lemma"]         # lemmatization of the word (e.g the base word)
    dependencies = feature_obj["pmc_sentences.dependencies"]  # parsed dependency structure of the sentence
    
    (root,graph,backgraph) = assembleDependencyGraph(words,dependencies)
    
    relation_id    = feature_obj["is_cellular_component.relation_id"]
    term           = feature_obj["is_cellular_component.term"]
    term_start_pos = feature_obj["pmc_terms.start_position"]
    term_length    = feature_obj["pmc_terms.length"]
  
    sys.stderr.write("======\n");
    sys.stderr.write("term: "+term+"\n");
    #sys.stderr.write(' '.join(words).encode('utf-8')+"\n");
    #sys.stderr.write(' '.join(pos_tags).encode('utf-8')+"\n");
    #sys.stderr.write(str(lemma)+"\n");
    #sys.stderr.write(' '.join(dependencies)+"\n");
  
    #sys.stderr.write(graph+"\n");
    #
    #i=0
    #while i < len(graph):
    #    if pos_tags[i].startswith('NN') or pos_tags[i].startswith('FW'):
    #        termIdxs = [i]
    #        for edge in graph[i]:
    #            termIdxs.extend(getNounCompoundModifierList(graph,edge))
    #        termIdxs.sort(); # we sort to get the terms in the order they appear
    #        #print(termIdxs)
    #        
    #        # we only support terms for now if they are consecutive
    #        if isConsecutive(termIdxs):
    #            # if we only have 1 or 2 words, just add them
    #            if len(termIdxs)<= 2 :
    #                term = buildTerm(words,termIdxs)
    #                if isOk(term):
    #                    phrases.append((termIdxs[0],len(termIdxs),term))
    #            # if we have more than two words, we should add every consecutive combo >= length 2
    #            else :
    #                for k1 in range(0,len(termIdxs)):
    #                    for k2 in range(k1+2,len(termIdxs)+1):
    #                        term = buildTerm(words,termIdxs[k1:k2])
    #                        start = termIdxs[k1]
    #                        length = k2-k1
    #                        if isOk(term):
    #                            phrases.append((start, length, term))
    #        # if they are not consecutive, we currently cannot handle this with our pmc_terms schema...
    #        #else:
    #            #phrases2.append((i,len(termIdx),buildterm(words,termIdx)))
    #    i+=1
    ## TODO !! right now the Penn Treebank does not represent branching structures of noun compound
    ## modifiers, so all nouns modify the rightmost noun.  IF this is changed, then the above code
    ## may add the same noun phrase multiple times, so this should be checked to remove duplicates
    #
    ## Output a tuple for each term phrase
    #for start_position, length, text in phrases:
    #    print(json.dumps({
    #      "sentence_id": sentence_id,
    #      "start_position": start_position,
    #      "length": length,
    #      "text": text,
    #      "term_id": None
    #    }))






