#pragma once

#include <memory>
#include <vector>

struct NameTrie {
    NameTrie* chld[128];
    // players with this name 
    std::vector<int> playerIDs;
    int numChld;
};

void addToTrie(NameTrie &trie, const std::string& name, int playerID);

void destroyTrie(NameTrie &trie);

const std::vector<int>& findInTrie(const NameTrie &trie, std::string namePartial);
