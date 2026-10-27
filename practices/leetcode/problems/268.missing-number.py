#
# @lc app=leetcode id=268 lang=python3
#
# [268] Missing Number
#

# @lc code=start
class Solution:
    def missingNumber(self, nums: list[int]) -> int:
        s = set(nums)
        k = 0
        
        while k in s:
            k += 1
            
        return k
        
# @lc code=end

