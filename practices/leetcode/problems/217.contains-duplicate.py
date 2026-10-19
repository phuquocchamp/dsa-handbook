#
# @lc app=leetcode id=217 lang=python3
#
# [217] Contains Duplicate
#

# @lc code=start

# # Sol 1: 
# # Idea: two loop and find
# # 65/79 cases passed (N/A)

# class Solution:
#     def containsDuplicate(self, nums: list[int]) -> bool:
#         n = len(nums)
#         for i in range(0, n):
#             for j in range(i+1, n):
#                 if nums[i] == nums[j]:
#                     return True
#         return False

# Sol 2: 
# 79/79 cases passed (25 ms)

class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        n = len(nums) # O(1)
        di = {} # 
        for i in range(0, n):
            if nums[i] in di:
                return True
            di[nums[i]] = 1
        return False
    
# @lc code=end

