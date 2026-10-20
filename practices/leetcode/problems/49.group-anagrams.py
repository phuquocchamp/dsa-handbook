#
# @lc app=leetcode id=49 lang=python3
#
# [49] Group Anagrams
#
from collections import *
# @lc code=start

# Sol 1:
# Idea:
# eat, tea, ate => sorted => aet -> key
# => then use dict to save the same key
class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups = defaultdict(list)
        
        for s in strs:
            key = "".join(sorted(s))
            groups[key].append(s)
        
        return list(groups.values())        
# @lc code=end

