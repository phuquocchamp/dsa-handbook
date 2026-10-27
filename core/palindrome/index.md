# Palindrome


1. Using slicing in python (Reverse Order)
```python
def isPalindrome(s:str) -> bool:
    rs = s[::-1]
    return s == rs
```

2. Using 2 Pointers

```python

def isPalindrome(s:str) -> bool:
    l, r = 0, len(s) - 1
    while(l < r):
        if s[l] != s[r]:
            return False
        l += 1, r+= 1
    return True
```