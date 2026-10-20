#
# @lc app=leetcode id=2514 lang=python3
#
# [2514] Count Anagrams
#
from collections import *

# @lc code=start
class Solution:
    def countAnagrams(self, s: str) -> int:
        MOD = 10**9+7
        
        n = len(s)
        
        fact = [1]*(n+1)
        for i in range (1, n+1):
            fact[i] = fact[i-1] * i % MOD
        
        ans = 1
        
        # Calc Numerator
        for word in s.split(" "):
            ans = ans * fact[len(word)] % MOD
            
            # Calc Denomarator
            for cnt in Counter(word).values():
                ans = ans * pow(fact[cnt], MOD - 2, MOD) % MOD
        
        return ans
        
# @lc code=end

sol = Solution()
arr = "ptx cccbhbq"
print(sol.countAnagrams(arr))

