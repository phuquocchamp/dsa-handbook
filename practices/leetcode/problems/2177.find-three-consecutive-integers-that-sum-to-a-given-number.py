#
# @lc app=leetcode id=2177 lang=python3
#
# [2177] Find Three Consecutive Integers That Sum to a Given Number
#

# @lc code=start
class Solution:
    def sumOfThree(self, num: int) -> list[int]:
        if (num - 3) % 3 == 0:
            mi = int((num - 3) / 3)
            
            return [mi, mi + 1, mi + 2]
        return []
        
# @lc code=end

