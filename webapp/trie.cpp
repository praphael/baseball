#include "trie.h"
#include <string>
#include <iostream>

using std::string;
using std::vector;
using std::cout;
using std::endl;

constexpr auto MAX_PLAYERS = 500;

void addToTrie(NameTrie &trie, const string& name, int playerID) {
    auto tr = &trie;
    tr->numChld++;
    for(unsigned char c : name) {
        // skip whitespace
        if(c == ' ') continue;
        // convert to lowercase
        if (c >= 'A' && c <= 'Z')
            c = 'a' + (c-'A');
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
        // skip whitespace
        if (c == ' ') continue;

        // convert to lowercase
        if (c >= 'A' && c <= 'Z')
            c = 'a' + (c-'A');
        tr = tr->chld[c];
        if (tr == nullptr)
            return empty;
        // cout << endl << c << tr->numChld;
        if (tr->numChld == 1) break;
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
