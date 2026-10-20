#
# @lc app=leetcode id=238 lang=python3
#
# [238] Product of Array Except Self
#

# @lc code=start
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        n = len(nums)
        
        prod = int(1)
        zero_count = 0
        
        for i in range(0,n):
            prod *= nums[i]
            if nums[i] == 0:
                zero_count +=1

        # Array with 1 zero num
        if zero_count == 1:
            tmp = 1
            z_index = 0
            for i in range(0,n):
                if nums[i] == 0:
                    z_index = i
                else:
                    tmp *= nums[i]
            ans = [0]*n
            ans[z_index] = tmp
            return ans

        # Array with 2 zero num
        if zero_count >= 2:
            return [0]*n

        # Array with none zero
        ans = [1] * n
        
        # # Using division
        # for i in range(0, n):
        #     ans[i] = int(prod / nums[i])

        # Idea: using the left, right most array
        # & Don't use division
        l = [1] * n
        r = [1] * n

        l[0] = nums[0]
        for i in range (1, n):
            l[i] = l[i-1] * nums[i]

        r[n-1] = nums[n-1]
        for i in range(n-2, -1, -1):
            r[i] = r[i+1] * nums[i]

        print(l, r)
        for i in range(0,n): 
            if i == 0:
                ans[i] = r[i+1]
            elif i == n-1:
                ans[i] = l[i-1]
            else:
                ans[i] = l[i-1] * r[i+1]
        return ans
# @lc code=end

sol = Solution()
nums = [2,3,4,5]
ans = sol.productExceptSelf(nums)
print(ans)