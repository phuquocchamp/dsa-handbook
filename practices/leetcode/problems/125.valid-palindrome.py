#
# @lc app=leetcode id=125 lang=python3
#
# [125] Valid Palindrome
#

# @lc code=start
## Sol 1: Python Slicing
# class Solution:
#     def isPalindrome(self, s: str) -> bool:
#         cs = ""
#         for c in s.lower():
#             if c.isalnum() : 
#                 cs += c
                
#         if cs == "":
#             return True
    
#         return cs == cs[::-1]
    
class Solution:
    def isPalindrome(self, s: str) -> bool:
        s = s.lower()
        l, r = 0, len(s) - 1
        while(l < r):
            while l < r and not s[l].isalnum(): l += 1
            while l < r and not s[r].isalnum(): r -= 1
            
            if s[l] != s[r]:
                return False
            l += 1; r -= 1
        return True

                
# @lc code=end

sol = Solution()
s = "A man, a plan, a canal: Panama"
print(sol.isPalindrome(s))