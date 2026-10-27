#
# @lc app=leetcode id=448 lang=python3
#
# [448] Find All Numbers Disappeared in an Array
#

# @lc code=start
class Solution:
    def findDisappearedNumbers(self, nums: list[int]) -> list[int]:
        s = set(nums)
        n = len(nums)
        
        l, r = 1, n
        
        while l in s:
            l += 1
        
        while r in s:
            r -= 1
        
        if l == r:
            return [l]
        if l > r:
            return []     

        ans = []
        for x in range(l, r+1):
            if x not in s:
                ans.append(x)

        return ans
# @lc code=end


sol = Solution()

nums = [4,3,2,7,7,2,3,1]

print(sol.findDisappearedNumbers(nums))

