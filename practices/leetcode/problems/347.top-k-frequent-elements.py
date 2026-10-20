#
# @lc app=leetcode id=347 lang=python3
#
# [347] Top K Frequent Elements
#
from collections import *
# @lc code=start
class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        groups = Counter(nums) # O(n)

        #O(nlogn) => logn here meaning log with base 2 of n
        sgroups = sorted(groups.items(), key=lambda item: item[1], reverse=True)

        return [num for num, _ in sgroups[:k]]
# @lc code=end

sol = Solution()
nums, k = [1,1,1,2,2,3], 2

print(sol.topKFrequent(nums, k))