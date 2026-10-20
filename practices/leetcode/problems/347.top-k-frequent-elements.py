#
# @lc app=leetcode id=347 lang=python3
#
# [347] Top K Frequent Elements
#
from collections import *
# @lc code=start
class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        nums = sorted(nums)
        groups = defaultdict(int) # defautl dict with value 0
        
        for num in nums:
            groups[num] += 1
        
        sgroups = dict(sorted(groups.items(), key=lambda item: item[1]))
        
        ans = list(sgroups.values())
        return ans[0:k]
# @lc code=end

sol = Solution()
nums, k = [1,1,1,2,2,3], 2

print(sol.topKFrequent(nums, k))