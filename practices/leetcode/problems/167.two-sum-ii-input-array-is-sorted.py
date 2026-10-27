#
# @lc app=leetcode id=167 lang=python3
#
# [167] Two Sum II - Input Array Is Sorted
#

# @lc code=start
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        # Idea: 2 Pointers
        l, r = 0, len(numbers) - 1
        
        while (l < r):
            check = numbers[l] + numbers[r]
            if check == target:
                return [l + 1, r + 1]
            if check < target:
                l += 1
            elif check > target:
                r -= 1
        
        return []

# @lc code=end

sol = Solution()
nums, target = [0,0,3,4], 0
print(sol.twoSum(nums, target))
