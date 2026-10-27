#
# @lc app=leetcode id=128 lang=python3
#
# [128] Longest Consecutive Sequence
#

from collections import defaultdict
# @lc code=start
class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        
        n = len(nums)
        ans = 0
        nums_set = set(nums)
        
        
        for x in nums_set:
            if x - 1 not in nums_set:
                length = 1
                while x + length in nums_set:
                    length += 1
                ans = max(ans, length)
                
        return ans     
# @lc code=end

