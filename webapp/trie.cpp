#include "trie.h"
#include <string>
#include <iostream>

using std::string;
using std::vector;
using std::cout;
using std::endl;

constexpr auto MAX_PLAYERS = 20;

void addToTrie(NameTrie &trie, const string& name, int playerID) {
    auto tr = &trie;
    tr->numChld++;
    for(unsigned char c : name) {
        //cout << endl << c << " " << int(c) << " " << tr->numChld;
        if (tr->chld[c] == nullptr) 
            tr->chld[c] = new NameTrie();
        tr = tr->chld[c];
        tr->numChld++;
        if (tr->numChld <= MAX_PLAYERS) {
            tr->playerIDs.push_back(playerID);
            if (tr->playerIDs.size() > MAX_PLAYERS) {
                // too many players, free up mem
                tr->playerIDs.clear();
                tr->playerIDs.shrink_to_fit();
            }
        }        
    }
}

const auto empty = vector<int>();

const vector<int>& findInTrie(const NameTrie &trie, string namePartial) {
    auto tr = &trie;
    for(unsigned char c : namePartial) {
        if (tr == nullptr)
            return empty;
        tr = tr->chld[c];
    }
    return tr->playerIDs;
}

void deallocTrie(NameTrie *trie) {
    if (trie == nullptr) return;

    for (int c=0; c<128; c++) {
        deallocTrie(trie->chld[c]);
    }
}

void destroyTrie(NameTrie &trie) {
    for (int c=0; c<128; c++) {
        deallocTrie(trie.chld[c]);
    }
}
