#
# @lc app=leetcode id=41 lang=python3
#
# [41] First Missing Positive
#

# @lc code=start
# MEX pattern
class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        s = set(nums)
        k = 1
        
        while k in s:
            k += 1 
        return k
    

# @lc code=end

sol = Solution()
nums = [3, 4, -1, 1]
print(sol.firstMissingPositive(nums))

