#include "trie.h"
#include <string>
using std::string;
using std::vector;

constexpr auto MAX_PLAYERS = 20;

void addToTrie(NameTrie &trie, string name, int playerID) {
    auto tr = &trie;
    for(auto c : name) {
        tr->numChld++;
        tr->playerIDs.push_back(playerID);
        if (tr->playerIDs.size() > MAX_PLAYERS) {
            // too many players, free up mem
            tr->playerIDs.clear();
            tr->playerIDs.shrink_to_fit(); 
        }
        if (tr->chld[c] == nullptr) 
            tr->chld[c] = std::make_unique<NameTrie>();
        tr = tr->chld[c].get();
    }
}

const auto empty = vector<int>();

const vector<int>& findInTrie(const NameTrie &trie, string namePartial) {
    auto tr = &trie;
    for(auto c : namePartial) {        
        if (tr == nullptr) 
            return empty;
        tr = tr->chld[c].get();
    }
    return tr->playerIDs;
}