#
# @lc app=leetcode id=442 lang=python3
#
# [442] Find All Duplicates in an Array
#

from collections import Counter 
# @lc code=start
class Solution:
    def findDuplicates(self, nums: list[int]) -> list[int]:
        s = Counter(nums)
        
        k = 1
        ans = []
        
        for k in s:
            if s[k] == 2:
                ans.append(k)
                
        return ans

# @lc code=end

sol = Solution()
nums = [4,3,2,7,8,2,3,1]
print(sol.findDuplicates(nums))