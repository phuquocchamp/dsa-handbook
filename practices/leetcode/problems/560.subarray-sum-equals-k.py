#
# @lc app=leetcode id=560 lang=python3
#
# [560] Subarray Sum Equals K
#
from typing import *
from collections import *
# @lc code=start

class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        count = defaultdict(int)
        count[0] = 1   # Achor case
        
        cur = ans = 0
        for x in nums:
            cur += x
            ans += count[cur - k]   # số j < i có P[j] = P[i] - k
            count[cur] += 1         # thêm P[i] SAU khi đã tra
        return ans

# @lc code=end
sol = Solution()
nums = [1]
k = 0
print(sol.subarraySum(nums, k))
