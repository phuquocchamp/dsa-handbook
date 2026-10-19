# 01. Cách học DSA hiệu quả và cách dùng repo `dsa-handbook`

Section này không dạy thuật toán nào cả. Nó chốt **quy trình** làm việc: trước khi gõ dòng code đầu tiên, bạn phải viết ra 5 mục cố định; và chốt **chỗ để file** trong repo này để sau ba tháng bạn vẫn tìm lại được bài đã làm. Nếu bỏ template và làm tùy hứng, bạn sẽ lặp lại đúng một lỗi: "code trước, nghĩ sau" — không phát hiện sai logic hay edge case bị bỏ sót trước khi tối ưu, và không có nơi cố định để quay lại ôn theo từng lớp (lý thuyết → thực hành → áp dụng → use case).

## Lý thuyết

### Quy trình 5 bước — bắt buộc, đúng thứ tự

Thứ tự này không tùy tiện. Mỗi bước sinh ra thông tin mà bước sau cần, nên đảo thứ tự là mất thông tin.

| Bước | Sản phẩm | Nếu bỏ qua thì hỏng ở đâu |
| --- | --- | --- |
| 1. **Requirements** | input/output/constraints/edge cases viết lại bằng lời của mình | Giải sai đề. Đây là nguồn Wrong Answer phổ biến nhất, không phải thuật toán sai |
| 2. **Complexity mục tiêu** | từ ràng buộc n suy ra độ phức tạp cần đạt | Tối ưu nhầm hướng: bỏ 40 phút viết O(n log n) khi O(n²) đã pass, hoặc ngược lại |
| 3. **Idea** | invariant + lập luận tại sao invariant kéo theo tính đúng | Viết code "cảm giác đúng", gặp counterexample thì patch bừa |
| 4. **Naive** | brute-force, thường O(n²) trở lên | Mất **oracle**. Không có gì để đối chiếu khi optimized ra sai |
| 5. **Optimized** | lời giải nộp, kèm câu "đổi gì lấy gì" | Không rút được bài học tái dùng cho bài sau |

Điểm dễ bị bỏ nhất là bước 4. Nhiều người coi naive là "bản nháp rồi xóa". Sai — naive là **ground truth** cho stress test ở §05. Giữ nó lại trong file.

Bước 2 đáng nói thêm: "complexity mục tiêu" được suy **từ ràng buộc**, không phải từ cảm giác. Bảng suy ngược đầy đủ nằm ở §02; ở đây chỉ cần nhớ mốc thô: `n ≤ 5000` → O(n²) là ổn; `n ≤ 10^5` → phải O(n log n) trở xuống.

Bước 3 là bước duy nhất không có code. Invariant nghĩa là: *một mệnh đề luôn đúng ngay trước và ngay sau mỗi vòng lặp*. Ví dụ với two pointers trên mảng sorted: "đáp án, nếu tồn tại, luôn nằm trong `[left, right]`". Chứng minh được mệnh đề đó bảo toàn qua mỗi bước, cộng với vòng lặp kết thúc, là chứng minh được thuật toán đúng. §06–§11 sẽ lặp lại đúng khuôn này.

### Bản đồ repo

```
dsa-handbook/
├── OUTLINE.md                     # hợp đồng nội dung, không sửa khi viết chương
├── docs/                          # handbook: NN-slug.md, mỗi section một file
├── cores/python/                  # thư viện cá nhân: DS/thuật toán tự cài từ đầu
└── practices/
    ├── leetcode/
    │   ├── problems/p-<id>/app.py # luyện tự do, không giới hạn thời gian
    │   ├── problems/_template/app.py
    │   └── contests/              # bài thi có time-limit thật
    └── codeforces/                # hiện trống
```

Ranh giới quan trọng: **`cores/` là thư viện, `practices/` là nơi áp dụng.** Linked list, heap, trie, union-find, segment tree — cài một lần cho tử tế trong `cores/python/`, có test riêng, rồi import lại khi cần. Nếu bạn cài lại union-find lần thứ tư trong bốn file `app.py` khác nhau thì đó là dấu hiệu nó phải được nâng lên `cores/`.

`practices/leetcode/contests/` khác `problems/` ở chỗ có **time-limit thật**. Ghi lại thời gian làm thực tế (đơn giản là một dòng comment `# 23 phút, sai 1 lần ở edge case n=1`) — đó là dữ liệu duy nhất cho biết bạn có đang nhanh lên không. Không ghi thì mọi đánh giá về tốc độ đều là cảm giác.

`practices/codeforces/` hiện trống. **Quyết định convention trước khi đổ bài vào**, vì Codeforces có style hoàn toàn khác LeetCode: đọc từ stdin, in ra stdout, không có class `Solution`, một file là một chương trình chạy độc lập. Đề xuất: `practices/codeforces/<contest-id>/<problem-letter>.py`, ví dụ `practices/codeforces/1850/a.py`. Trộn hai style vào cùng thư mục sẽ khiến template và cả thói quen đọc code bị lẫn.

### Cấu trúc file `app.py`

Mỗi bài LeetCode nằm ở `practices/leetcode/problems/p-<id>/app.py`. File dùng **cell marker `#%%`** — cú pháp Spyder/VS Code cho phép chạy từng vùng độc lập bằng `Shift+Enter` mà không chạy lại cả file. Các vùng ánh xạ 1-1 với 5 bước ở trên:

`#%% Requirements` → `#%% Complexity` → `#%% Idea` → `#%% Naive` → `#%% Optimized` → `#%% Stress test` → `#%% Debugging`

Hai vùng cuối là phần thực thi: `Stress test` so naive với optimized trên input ngẫu nhiên nhỏ (§05), `Debugging` gọi `Solution().method(...)` với input mẫu của đề.

Quy ước đặt tên, không thương lượng:

- Class tên `Solution`, method **trùng đúng tên hàm LeetCode** (`threeSum`, `maxArea`, `lengthOfLongestSubstring`) — để copy thẳng lên judge không phải sửa.
- Type hint dùng cú pháp Python 3.12: `list[int]`, `list[list[int]]`, `dict[str, int]`. **Không** `typing.List` — cú pháp đó đã lỗi thời từ 3.9 và làm file dài thêm một dòng import vô ích.
- Lời giải naive đặt trong class riêng `SolutionNaive` để cả hai cùng tồn tại, stress test gọi được cả hai.

## Ví dụ minh hoạ: template và một bài chạy qua đủ 5 bước

### Template `_template/app.py`

File thật nằm ở `practices/leetcode/problems/_template/app.py`. Bắt đầu một bài mới = copy thư mục đó thành `p-<id>/`. Đây là bộ khung (đã chạy được nguyên trạng, ví dụ trong template là Kadane — Maximum Subarray):

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 09:00:00 2026

@author: qtphoang
"""

#%% Requirements
# Bài: 53. Maximum Subarray
# Input   : nums: list[int]
# Output  : tổng lớn nhất của một subarray không rỗng
# Ràng buộc: 1 <= n <= 10**5 ; -10**4 <= nums[i] <= 10**4
# Edge cases: n=1 ; toàn số âm ; toàn số 0

#%% Complexity
# n <= 10**5 ==> O(n^2) ~ 10^10 phép tính, chắc chắn TLE.
# Mục tiêu   : time O(n), space O(1).

#%% Idea
# Invariant: sau khi xử lý xong nums[i], `cur` là tổng lớn nhất của
# subarray KẾT THÚC tại i, và `best` là đáp án cho tiền tố nums[:i+1].

#%% Naive
class SolutionNaive:
    def maxSubArray(self, nums: list[int]) -> int:
        n = len(nums)
        best = nums[0]
        for i in range(n):
            s = 0
            for j in range(i, n):
                s += nums[j]
                best = max(best, s)
        return best

#%% Optimized
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        best = cur = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best

#%% Stress test
import random

def stress(iterations: int = 500) -> None:
    naive, fast = SolutionNaive(), Solution()
    for _ in range(iterations):
        case = [random.randint(-5, 5) for _ in range(random.randint(1, 8))]
        exp, got = naive.maxSubArray(case), fast.maxSubArray(case)
        if exp != got:
            print("COUNTEREXAMPLE:", case, exp, got)
            return
    print(f"stress OK ({iterations} random cases)")

#%% Debugging
nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
print(Solution().maxSubArray(nums))
stress()
```

Chạy file này bằng `~/.local/bin/python3.12` in ra `6` rồi `stress OK (500 random cases)`.

### Vì sao naive phải sống sót

Đây là minh hoạ ngắn cho việc naive-as-oracle bắt lỗi mà mắt người không bắt được. Bản "optimized" dưới đây sai đúng một chỗ: quên rằng subarray phải **không rỗng**, nên với mảng toàn âm nó trả về 0.

```python
import random

def naive(nums: list[int]) -> int:
    n = len(nums)
    best = nums[0]
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            best = max(best, s)
    return best

def buggy(nums: list[int]) -> int:
    best = cur = 0                 # BUG: khởi tạo 0 cho phép subarray rỗng
    for x in nums:
        cur = max(0, cur + x)
        best = max(best, cur)
    return best

random.seed(7)
for _ in range(2000):
    case = [random.randint(-5, 5) for _ in range(random.randint(1, 6))]
    if naive(case) != buggy(case):
        print("COUNTEREXAMPLE:", case, "naive =", naive(case), "buggy =", buggy(case))
        break
else:
    print("khong tim thay counterexample")
```

Kết quả thực tế khi chạy: `COUNTEREXAMPLE: [-4] naive = -4 buggy = 0`. Bug này lọt qua mọi test case "trông hợp lý" mà bạn tự nghĩ ra, vì bản năng của người viết là thử mảng có ít nhất một số dương. 2000 lần sinh ngẫu nhiên tìm ra nó trong vài mili-giây.

## Bài luyện thêm

Section này không gắn với bài LeetCode cụ thể nào — outline không liệt kê bài cho §01. Bài tập ở đây là: chọn một bài bất kỳ bạn **đã giải rồi**, viết lại nó vào `p-<id>/app.py` theo đúng 7 cell marker, và bắt buộc điền cả `#%% Requirements` lẫn `#%% Idea` bằng lời của mình. Nếu viết mục Idea mà không nói được invariant, nghĩa là bạn chưa hiểu bài đó — dù đã AC.

## Bài toán áp dụng

Quy trình 5 bước này không chỉ dùng cho LeetCode. Nó là dạng rút gọn của **design doc** trong công việc thật:

- *Requirements* ↔ phần "Problem statement / Non-goals" của design doc.
- *Complexity mục tiêu* ↔ phần "Scale & SLO": bao nhiêu request/giây, dữ liệu bao nhiêu bản ghi.
- *Idea + invariant* ↔ phần "Approach" và các bất biến của hệ thống (vd "balance không bao giờ âm").
- *Naive* ↔ prototype/baseline, đồng thời là oracle khi kiểm thử bản tối ưu.
- *Optimized + trade-off* ↔ phần "Alternatives considered", nêu rõ đổi gì lấy gì (thêm cache lấy latency, thêm index lấy tốc độ đọc và mất tốc độ ghi).

Viết design doc mà không có mục "naive baseline" là lý do nhiều tối ưu hoá production không chứng minh được nó có thực sự nhanh hơn không.

## Use case thực tế

Thư mục `cores/python/` là bản thu nhỏ của **internal library** trong một công ty: code dùng lại nhiều nơi thì tách ra, có test riêng, có API ổn định. Ranh giới `cores/` vs `practices/` chính là ranh giới library vs application.

Khi nào câu trả lời đúng là "dùng thư viện có sẵn"? Gần như **luôn luôn, trong production**. `cores/python/` tồn tại để bạn *hiểu* cấu trúc dữ liệu bằng cách cài nó, không phải để dùng nó thay `heapq`, `collections.deque`, `bisect` hay `graphlib` khi đi làm. Stdlib CPython viết bằng C, nhanh hơn bản Python thuần của bạn hàng chục lần (§03 đo con số cụ thể) và đã qua hàng triệu giờ chạy thật. Tự cài để học, dùng stdlib để ship.

## Bẫy thường gặp trong Python

- **Cell marker `#%%` không phải cú pháp Python.** Nó chỉ là comment; Spyder/VS Code/Jupyter đọc nó để chia cell. Chạy `python3.12 app.py` vẫn thực thi toàn bộ file từ trên xuống. Hệ quả: nếu vùng `#%% Debugging` có code chạy nặng, mỗi lần import file đó từ nơi khác sẽ chạy lại. Bọc bằng `if __name__ == "__main__":` khi file có khả năng bị import.
- **`import` giữa các cell.** Chạy cell rời rạc trong Spyder dễ tạo tình huống "biến còn sống trong namespace nhưng không có trong file". Code chạy được trong IDE mà lỗi `NameError` khi chạy từ terminal gần như luôn là lỗi này. Luôn kiểm bằng một lần chạy `~/.local/bin/python3.12 app.py` từ đầu trước khi tin là file đúng.
- **Mutable input bị naive làm hỏng.** Khi stress test, nếu naive hoặc optimized sửa mảng tại chỗ (`nums.sort()`, `nums[i] = ...`), bản chạy sau sẽ nhận input đã bị biến đổi và so sánh trở nên vô nghĩa. Luôn truyền `list(case)` cho từng bản.
- **`typing.List` vs `list`.** Trên 3.12 cả hai đều chạy, nên lỗi này im lặng. Nó chỉ là nợ kỹ thuật — nhưng vì handbook này chốt 3.12 làm chuẩn, dùng `list[int]` để mọi file đồng nhất.
