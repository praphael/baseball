#pragma once

#include <memory>
#include <vector>

struct NameTrie {
    std::unique_ptr<NameTrie> chld[26];
    // players with this name 
    std::vector<int> playerIDs;
    int numChld;
};

void addToTrie(NameTrie &trie, std::string name, int playerID);

const std::vector<int>& findInTrie(const NameTrie &trie, std::string namePartial);
