# 07. Sliding window (fixed & variable)

Sliding window là two pointers cùng chiều, cộng thêm một **trạng thái tăng dần** của cửa sổ (tổng, tần suất, số ký tự phân biệt). Ý tưởng: thay vì tính lại từ đầu cho mỗi cửa sổ, ta **cập nhật trạng thái theo phần biên vừa thêm/bớt** — `O(1)` mỗi bước thay vì `O(k)`. Section này phân biệt cửa sổ cố định với cửa sổ co giãn, và chốt lập luận vì sao tổng thể vẫn `O(n)` dù có vòng `while` lồng bên trong vòng `for`.

## Lý thuyết

### Fixed-size window

Cửa sổ luôn rộng đúng `k`. Trạng thái cập nhật bằng một phép **cộng phần tử mới, trừ phần tử rơi ra**:

```
s = sum(a[:k])
for i in range(k, n):
    s += a[i] - a[i-k]
```

Đây là toàn bộ bài **643. Maximum Average Subarray I**. Chi phí `O(1)` mỗi bước, `O(n)` tổng, thay vì `O(n·k)` nếu gọi `sum(a[i:i+k])` mỗi lần.

Điều kiện để làm được: trạng thái phải **khả nghịch** — biết trạng thái và biết phần tử rơi ra là đủ để khôi phục. Tổng thì khả nghịch (trừ đi). **Max thì không**: bỏ phần tử max ra khỏi cửa sổ, bạn không biết max mới là bao nhiêu. Đó chính là lý do bài 239 cần monotonic deque chứ không cập nhật được bằng một biến.

### Variable-size window

Khuôn chung, gần như copy được cho mọi bài:

```
left = 0
for right in range(n):
    them a[right] vao trang thai
    while <cua so vi pham invariant>:
        bot a[left] khoi trang thai
        left += 1
    cap nhat dap an tu cua so [left, right]
```

Có hai họ, khác nhau ở chỗ đặt câu lệnh cập nhật đáp án:

| Họ | Điều kiện `while` | Cập nhật đáp án | Ví dụ |
| --- | --- | --- | --- |
| Tìm cửa sổ **dài nhất** thoả điều kiện | co khi **vi phạm** | sau `while` (cửa sổ luôn hợp lệ) | 3, 424 |
| Tìm cửa sổ **ngắn nhất** thoả điều kiện | co khi **vẫn thoả** | **bên trong** `while` | 209, 76 |

Nhầm hai họ này là lỗi phổ biến nhất khi làm sliding window: viết đúng khuôn của họ "dài nhất" cho một bài "ngắn nhất" thì code chạy, trả về số, và sai.

### Vì sao vẫn là `O(n)` dù có `while` lồng trong `for`

Nhìn hình dạng code thì như `O(n²)`. Lập luận đúng là **amortized**:

> `left` chỉ **tăng**, không bao giờ giảm, và bị chặn bởi `n`. Vậy tổng số lần thân vòng `while` chạy trên **toàn bộ** chương trình ≤ `n`.

Cộng với `n` lần lặp của `for`, tổng công việc ≤ `2n` ⇒ `O(n)`. Đây đúng là kiểu lập luận amortized ở §02: một lần lặp cụ thể của `for` có thể tốn `O(n)` (nếu `while` co cửa sổ rất nhiều), nhưng trung bình trên `n` bước thì là `O(1)`.

Điều kiện để lập luận này còn đúng: **`left` không được lùi**. Bất kỳ bài nào cần lùi `left` thì không phải sliding window — nó là bài khác.

### Ba cách biểu diễn trạng thái cửa sổ

| Trạng thái | Cấu trúc | Cập nhật khi thêm/bớt | Bài |
| --- | --- | --- | --- |
| Tổng | một biến `int` | `+= x` / `-= x` | 209, 643 |
| Tần suất + "đã đủ chưa" | `Counter` + biến đếm `missing` | `+= 1` rồi so với `need` | 76 |
| Cực trị | monotonic `deque` | pop đuôi khi phần tử mới trội hơn | 239 |

Cột "Cập nhật" là chỗ quyết định `O(1)` hay không. Với 76, mẹo là **không** so hai `Counter` mỗi bước (`O(alphabet)` mỗi lần) mà giữ một biến đếm `missing` = số ký tự **chưa đủ số lượng**; cửa sổ hợp lệ ⟺ `missing == 0`. Điều đó đưa kiểm tra về `O(1)`.

### Monotonic deque

Để lấy max của cửa sổ trong `O(1)` amortized: giữ một `deque` **chỉ số** sao cho giá trị tương ứng **giảm dần**.

> **Invariant**: `deque` chứa các chỉ số trong `[left, right]`, giá trị `a[dq[0]] > a[dq[1]] > ...`, và **chỉ số nào bị loại đều không bao giờ có thể là max của bất kỳ cửa sổ tương lai nào**.

Vì sao loại an toàn: khi thêm `a[i]`, mọi chỉ số `j < i` với `a[j] <= a[i]` đều vô dụng — mọi cửa sổ tương lai chứa `j` cũng chứa `i` (vì `i > j` và cửa sổ trượt sang phải), mà `a[i] >= a[j]`. Nên `a[j]` không bao giờ là max.

Mỗi chỉ số vào deque đúng một lần và ra đúng một lần ⇒ `O(n)` tổng, `O(k)` bộ nhớ.

**Tại sao không dùng heap?** Heap cho max trong `O(log k)` push nhưng **không xoá được phần tử ở giữa** — bạn phải dùng lazy deletion (giữ lại rác rồi bỏ khi nó nổi lên đầu), thành `O(n log n)` và tốn bộ nhớ. Deque cho `O(n)` sạch sẽ.

## Bài tập chi tiết

### Bài 1 — 209. Minimum Size Subarray Sum

#### Requirements

Cho mảng `nums` gồm **số nguyên dương** và số `target`. Tìm **độ dài nhỏ nhất** của một subarray liên tiếp có tổng `>= target`. Không tồn tại thì trả `0`.

Điều kiện "số nguyên **dương**" là mấu chốt — nó bảo đảm tổng cửa sổ **đơn điệu tăng** theo chiều rộng. Nếu có số âm hoặc số 0 thì mở rộng cửa sổ có thể làm tổng giảm, và toàn bộ lập luận sụp (bài tương ứng với số âm là 862. Shortest Subarray with Sum at Least K, phải dùng monotonic deque trên prefix sum).

Ràng buộc: `1 ≤ n ≤ 10^5`, `1 ≤ nums[i] ≤ 10^4`, `1 ≤ target ≤ 10^9`.

Edge cases: không subarray nào đủ (trả `0`); một phần tử đơn lẻ đã `>= target` (trả `1`); toàn bộ mảng vừa đúng bằng `target`; `n = 1`.

#### Complexity mục tiêu

`n ≤ 10^5` ⇒ `O(n²)` là `10^10` — không có cửa. Cần `O(n)` hoặc `O(n log n)`.

Đề bài LeetCode còn gợi ý thêm lời giải `O(n log n)` (binary search trên prefix sum). Nhưng `O(n)` bằng sliding window đơn giản hơn và nhanh hơn, nên đó là đích.

#### Idea

> **Invariant**: sau khi xử lý xong `right`, cửa sổ `[left, right]` là cửa sổ **ngắn nhất kết thúc tại `right`** mà tổng vẫn `>= target` — hoặc tổng `< target` (chưa đủ), khi đó không cửa sổ nào kết thúc tại `right` là hợp lệ.

Bảo toàn: thêm `nums[right]` vào tổng. Rồi **co `left` chừng nào tổng vẫn `>= target`** — mỗi lần co, ghi nhận độ dài hiện tại trước khi co. Khi vòng `while` dừng, tổng đã `< target`, tức cửa sổ đã ngắn nhất có thể ứng với `right` này.

Tại sao co `left` là an toàn (không bỏ mất đáp án)? Vì mọi phần tử dương: nếu `[left, right]` đã hợp lệ thì `[left', right]` với `left' < left` cũng hợp lệ nhưng **dài hơn** — không thể là đáp án. Còn các cửa sổ kết thúc ở `right' > right` thì sẽ được xét ở các vòng sau, và `left` không cần lùi vì đáp án ngắn nhất kết thúc tại `right'` có `left` không nhỏ hơn `left` hiện tại (lại nhờ tính dương).

Kết thúc: mọi `right` từ `0` đến `n-1` đều được xét, và với mỗi `right` ta đã có cửa sổ ngắn nhất. Lấy min ⇒ đáp án toàn cục.

#### Naive

```python
class SolutionNaive:
    def minSubArrayLen(self, target: int, nums: list[int]) -> int:
        best = float("inf")
        for i in range(len(nums)):               # O(n^2)
            s = 0
            for j in range(i, len(nums)):
                s += nums[j]
                if s >= target:
                    best = min(best, j - i + 1)
                    break                        # dai hon nua chi te hon
        return 0 if best == float("inf") else int(best)

print(SolutionNaive().minSubArrayLen(7, [2, 3, 1, 2, 4, 3]))
print(SolutionNaive().minSubArrayLen(11, [1, 1, 1, 1, 1, 1, 1, 1]))
print(SolutionNaive().minSubArrayLen(4, [1, 4, 4]))
```

In ra `2`, `0`, `1`.

`O(n²)` time, `O(1)` space. Chậm vì với mỗi điểm bắt đầu `i` nó quét lại từ đầu, dù đã biết rất nhiều về các cửa sổ trước đó. Chú ý bản naive này **đã** có tối ưu `break` — nó vẫn `O(n²)` worst case (khi không bao giờ đạt `target`).

#### Optimized

```python
class Solution:
    def minSubArrayLen(self, target: int, nums: list[int]) -> int:
        left = 0
        total = 0
        best = float("inf")
        for right, x in enumerate(nums):
            total += x
            while total >= target:               # ho "ngan nhat": co khi VAN THOA
                best = min(best, right - left + 1)   # cap nhat BEN TRONG while
                total -= nums[left]
                left += 1
        return 0 if best == float("inf") else int(best)

import random

def naive(target: int, nums: list[int]) -> int:
    best = float("inf")
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s >= target:
                best = min(best, j - i + 1)
                break
    return 0 if best == float("inf") else int(best)

random.seed(0)
sol = Solution()
for _ in range(5000):
    case = [random.randint(1, 6) for _ in range(random.randint(0, 9))]
    tgt = random.randint(1, 20)
    if naive(tgt, list(case)) != sol.minSubArrayLen(tgt, list(case)):
        print("COUNTEREXAMPLE:", tgt, case)
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.minSubArrayLen(7, [2, 3, 1, 2, 4, 3]),
      sol.minSubArrayLen(11, [1, 1, 1, 1, 1, 1, 1, 1]),
      sol.minSubArrayLen(4, [1, 4, 4]))
```

In ra `khop tren 5000 case ngau nhien` rồi `2 0 1`.

**Đánh đổi**: thêm đúng **hai biến** (`left`, `total`) — `O(1)` bộ nhớ — để đổi lấy việc không phải quét lại. Đây là trường hợp đánh đổi rẻ nhất có thể. Cái giá thật là **một tiền đề ẩn**: thuật toán chỉ đúng khi mọi phần tử dương. Viết tiền đề đó vào comment, vì sáu tháng sau bạn sẽ copy đoạn code này sang một bài có số âm.

### Bài 2 — 239. Sliding Window Maximum

#### Requirements

Cho `nums` và số `k`. Cửa sổ rộng `k` trượt từ trái sang phải, mỗi lần một bước. Trả về mảng các **giá trị lớn nhất** của từng vị trí cửa sổ — độ dài `n - k + 1`.

Ràng buộc: `1 ≤ n ≤ 10^5`, `-10^4 ≤ nums[i] ≤ 10^4`, `1 ≤ k ≤ n`.

Edge cases: `k = 1` (kết quả chính là `nums`); `k = n` (một phần tử duy nhất); toàn phần tử bằng nhau; dãy tăng đơn điệu (max luôn ở cuối cửa sổ) và giảm đơn điệu (max luôn ở đầu — trường hợp deque phình to nhất); số âm (không được khởi tạo `best = 0`).

#### Complexity mục tiêu

`n ≤ 10^5`, và có `n - k + 1` cửa sổ. Cách hiển nhiên `max(nums[i:i+k])` cho mỗi cửa sổ là `O(n·k)`, tệ nhất `k ≈ n/2` ⇒ `2.5·10^9`. TLE.

`O(n log k)` bằng heap là khả thi nhưng phức tạp (cần lazy deletion). `O(n)` bằng monotonic deque vừa nhanh hơn vừa gọn hơn. Nhắm `O(n)`.

#### Idea

Giữ một `deque` chứa **chỉ số**, với giá trị giảm dần từ đầu tới cuối.

> **Invariant** (ba phần, đúng ngay trước mỗi lần ghi kết quả):
> 1. Mọi chỉ số trong deque nằm trong cửa sổ hiện tại `[i-k+1, i]`.
> 2. Giá trị tương ứng **giảm ngặt hoặc không tăng** từ đầu đến cuối deque.
> 3. Chỉ số nào đã bị loại khỏi deque **không bao giờ** là max của bất kỳ cửa sổ nào từ đây về sau.

Ba thao tác giữ ba phần đó:
- **Pop đuôi** chừng nào `nums[dq[-1]] <= nums[i]`: giữ phần 2, và hợp lệ theo phần 3 (đã chứng minh ở mục Lý thuyết: `j < i` với `a[j] <= a[i]` là vô dụng vĩnh viễn).
- **Append `i`** vào đuôi.
- **Pop đầu** nếu `dq[0] <= i - k`: chỉ số đã rơi ra khỏi cửa sổ, giữ phần 1.

Từ phần 1 + phần 2 ⇒ `nums[dq[0]]` là max của cửa sổ. Đó là kết quả cần ghi.

Chi phí: mỗi chỉ số `append` một lần và `pop` tối đa một lần ⇒ `O(n)` amortized.

#### Naive

```python
class SolutionNaive:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        # O(n*k): moi cua so goi max() tren mot slice moi
        return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]

print(SolutionNaive().maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3))
print(SolutionNaive().maxSlidingWindow([1], 1))
print(SolutionNaive().maxSlidingWindow([-7, -8, -9], 2))
```

In ra `[3, 3, 5, 5, 6, 7]`, `[1]`, `[-7, -8]`.

`O(n·k)` time, `O(k)` space cho mỗi slice. Nhược điểm kép: mỗi vòng vừa cấp phát một list mới (`nums[i:i+k]`, §04) vừa quét lại toàn bộ `k` phần tử — dù cửa sổ trước đó chỉ khác đúng hai phần tử.

#### Optimized

```python
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        dq: deque[int] = deque()                 # chua CHI SO, gia tri giam dan
        out: list[int] = []
        for i, x in enumerate(nums):
            while dq and nums[dq[-1]] <= x:      # cac chi so nay vinh vien vo dung
                dq.pop()
            dq.append(i)
            if dq[0] <= i - k:                   # dau deque da roi khoi cua so
                dq.popleft()
            if i >= k - 1:                       # cua so da du rong
                out.append(nums[dq[0]])
        return out

import random

def naive(nums: list[int], k: int) -> list[int]:
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]

random.seed(0)
sol = Solution()
for _ in range(5000):
    n = random.randint(1, 9)
    case = [random.randint(-5, 5) for _ in range(n)]
    k = random.randint(1, n)
    if naive(case, k) != sol.maxSlidingWindow(case, k):
        print("COUNTEREXAMPLE:", case, k)
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3),
      sol.maxSlidingWindow([1], 1),
      sol.maxSlidingWindow([-7, -8, -9], 2))
```

In ra `khop tren 5000 case ngau nhien` rồi `[3, 3, 5, 5, 6, 7] [1] [-7, -8]`.

**Đánh đổi**: `O(k)` bộ nhớ cho deque, đổi lấy `O(n)` thời gian thay vì `O(n·k)`. Đây là hình dạng đánh đổi tiêu chuẩn nhất trong DSA — thêm một cấu trúc dữ liệu phụ để **nhớ lại công việc đã làm** thay vì làm lại. Bộ nhớ `O(k)` không phải vấn đề vì `k ≤ n` và ta vốn đã trả `O(n)` cho output.

Một chi tiết cài đặt: `while dq and nums[dq[-1]] <= x` dùng `<=` chứ không phải `<`. Với `<` thì các phần tử **bằng nhau** được giữ lại cả — vẫn cho kết quả đúng, chỉ tốn thêm bộ nhớ. Với `<=` thì deque nhỏ hơn. Cả hai đều đúng ở bài này; nhưng ở các bài monotonic deque khác (như 862) sự khác biệt giữa `<` và `<=` có thể là đúng/sai — luôn kiểm bằng stress test.

### Bài 3 — 76. Minimum Window Substring

#### Requirements

Cho hai chuỗi `s` và `t`. Tìm **substring liên tiếp ngắn nhất** của `s` chứa **mọi ký tự của `t`, kể cả số lần lặp**. Không có thì trả `""`.

Chỗ dễ đọc sót: đây là **multiset containment**, không phải set. `t = "AABC"` đòi cửa sổ có ít nhất **hai** chữ `A`. Đề bảo đảm đáp án là duy nhất nếu tồn tại.

Ràng buộc: `1 ≤ len(s), len(t) ≤ 10^5`, chữ cái tiếng Anh hoa và thường (phân biệt hoa thường).

Edge cases: `len(t) > len(s)` (trả `""`); `t` có ký tự không có trong `s`; `s == t`; `t` toàn ký tự giống nhau (`"aaa"`); đáp án nằm ở đầu hoặc cuối `s`.

#### Complexity mục tiêu

`10^5` cho cả hai chuỗi. Brute-force mọi substring là `O(n²)` cặp, mỗi cặp kiểm tra `O(m)` ⇒ `O(n²·m)`. Không có cửa.

Nhắm `O(n + m)`. Bảng chữ cái chỉ 52 ký tự, nhưng vẫn phải tránh nhân thêm hệ số 52 vào mỗi bước (`Counter == Counter` mỗi vòng là `O(52)` — về lý thuyết là `O(1)` nhưng hằng số đủ lớn để thành vấn đề trong CPython, §03).

#### Idea

Cửa sổ co giãn thuộc họ "ngắn nhất". Trạng thái gồm:
- `need`: `Counter(t)`, số lượng cần cho mỗi ký tự.
- `win`: `Counter` đếm ký tự **thuộc `need`** đang có trong cửa sổ.
- `missing`: **số ký tự phân biệt chưa đủ số lượng**. Khởi tạo `len(need)`.

> **Invariant**: `missing == 0` ⟺ cửa sổ `[left, right]` chứa đủ mọi ký tự của `t` với đủ số lượng.

Bảo toàn: khi thêm `s[right]`, nếu nó thuộc `need` thì `win[c] += 1`; **đúng lúc** `win[c] == need[c]` thì `missing -= 1` (dùng `==` chứ không phải `>=`, nếu không sẽ trừ nhiều lần). Khi bớt `s[left]`, nếu nó thuộc `need` thì kiểm `win[c] == need[c]` **trước khi** giảm — nếu đang vừa đủ thì bỏ đi sẽ thành thiếu, `missing += 1`.

Vòng ngoài mở rộng `right`; vòng `while missing == 0` co `left`, và **ghi nhận đáp án bên trong `while`** (họ "ngắn nhất"). Vì `left` chỉ tăng, tổng chi phí `O(n)`.

Kết thúc: mọi `right` đều được xét, và với mỗi `right` ta đã tìm cửa sổ hợp lệ ngắn nhất kết thúc tại đó. Min trên tất cả ⇒ đáp án.

#### Naive

```python
from collections import Counter

class SolutionNaive:
    def minWindow(self, s: str, t: str) -> str:
        """O(n^2 * alphabet): thu moi cap (i, j), dung Counter de kiem tra."""
        if not s or not t or len(t) > len(s):
            return ""
        need = Counter(t)
        best = ""
        for i in range(len(s)):
            for j in range(i, len(s)):
                window = s[i:j + 1]
                have = Counter(window)
                if all(have[c] >= n for c, n in need.items()):
                    if best == "" or len(window) < len(best):
                        best = window
                    break                        # dai hon chi te hon
        return best

print(repr(SolutionNaive().minWindow("ADOBECODEBANC", "ABC")))
print(repr(SolutionNaive().minWindow("a", "aa")))
print(repr(SolutionNaive().minWindow("aa", "aa")))
```

In ra `'BANC'`, `''`, `'aa'`.

`O(n²·|Σ|)` time, `O(n)` space. Chậm vì mỗi cặp `(i, j)` dựng lại một `Counter` từ đầu trên một slice mới — vừa lãng phí thời gian vừa lãng phí bộ nhớ.

#### Optimized

```python
from collections import Counter

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not s or not t or len(t) > len(s):
            return ""
        need = Counter(t)
        win: Counter[str] = Counter()
        missing = len(need)                      # so ky tu PHAN BIET chua du
        left = 0
        bl, br = 0, -1                           # doan tot nhat; br < 0 = chua co
        for right, ch in enumerate(s):
            if ch in need:
                win[ch] += 1
                if win[ch] == need[ch]:          # == chu khong phai >=
                    missing -= 1
            while missing == 0:                  # ho "ngan nhat": co khi VAN THOA
                if br < 0 or right - left < br - bl:
                    bl, br = left, right
                out_ch = s[left]
                if out_ch in need:
                    if win[out_ch] == need[out_ch]:
                        missing += 1             # bo di se thanh thieu
                    win[out_ch] -= 1
                left += 1
        return s[bl:br + 1] if br >= 0 else ""

import random

def naive(s: str, t: str) -> str:
    if not s or not t or len(t) > len(s):
        return ""
    need = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            w = s[i:j + 1]
            have = Counter(w)
            if all(have[c] >= n for c, n in need.items()):
                if best == "" or len(w) < len(best):
                    best = w
                break
    return best

random.seed(0)
sol = Solution()
for _ in range(4000):
    s = "".join(random.choice("abc") for _ in range(random.randint(0, 10)))
    t = "".join(random.choice("abc") for _ in range(random.randint(0, 4)))
    exp, got = naive(s, t), sol.minWindow(s, t)
    # Co the co nhieu cua so ngan nhat -> so DO DAI, roi kiem tinh hop le
    valid = (got == "") or (got in s and not (Counter(t) - Counter(got)))
    if len(exp) != len(got) or not valid:
        print("COUNTEREXAMPLE:", repr(s), repr(t), repr(exp), repr(got))
        break
else:
    print("khop tren 4000 case ngau nhien")

print(repr(sol.minWindow("ADOBECODEBANC", "ABC")),
      repr(sol.minWindow("a", "aa")), repr(sol.minWindow("aa", "aa")))
```

In ra `khop tren 4000 case ngau nhien` rồi `'BANC' '' 'aa'`.

**Đánh đổi**: `O(|Σ|)` bộ nhớ cho hai `Counter` **cộng với** một biến `missing` — và chính biến `missing` mới là phần tinh tế. Không có nó, mỗi bước phải so hai `Counter` (`O(|Σ|)`), tổng `O(n·|Σ|)`; có nó, kiểm tra hợp lệ là `O(1)`. Đây là ví dụ đẹp của việc **duy trì một đại lượng tổng hợp thay vì tính lại nó** — chính là tinh thần của cả chương.

## Bài luyện thêm

- **643. Maximum Average Subarray I** — cửa sổ cố định rộng `k`; giữ tổng trượt bằng `s += nums[i] - nums[i-k]`, không gọi lại `sum()`. Nhớ chia cho `k` ở dạng float.
- **3. Longest Substring Without Repeating Characters** — họ "dài nhất": `dict` lưu **vị trí cuối** của mỗi ký tự; khi gặp ký tự đã thấy và vị trí đó `>= left` thì nhảy `left = seen[c] + 1`. Đo hiệu năng của nó so với bản slicing ở §03.

## Bài toán áp dụng

Rolling metric trên time-series — bài toán hằng ngày của mọi hệ thống monitoring:

```python
from collections import deque

class RollingWindow:
    """Rolling sum/avg cho k diem gan nhat, O(1) moi diem moi."""

    def __init__(self, k: int) -> None:
        self.k = k
        self.buf: deque[float] = deque(maxlen=k)   # maxlen: tu dong day phan tu cu ra
        self.total = 0.0

    def push(self, x: float) -> float | None:
        if len(self.buf) == self.k:
            self.total -= self.buf[0]              # doc TRUOC khi append day no ra
        self.buf.append(x)
        self.total += x
        return self.total / self.k if len(self.buf) == self.k else None

prices = [10.0, 11.0, 12.0, 9.0, 8.0, 20.0, 21.0]
rw = RollingWindow(3)
for p in prices:
    avg = rw.push(p)
    print(f"gia {p:5.1f} -> MA3 = {avg if avg is None else round(avg, 3)}")

# Doi chieu voi cach tinh lai tu dau
naive_ma = [sum(prices[i - 2:i + 1]) / 3 for i in range(2, len(prices))]
rw2 = RollingWindow(3)
fast_ma = [v for p in prices if (v := rw2.push(p)) is not None]
print("khop:", all(abs(a - b) < 1e-9 for a, b in zip(naive_ma, fast_ma, strict=True)))
```

In ra bảng MA3 và `khop: True`.

Ba chi tiết đáng học ở đoạn này: `deque(maxlen=k)` tự đẩy phần tử cũ nhất ra khi đầy — nhưng phải **đọc `buf[0]` trước khi `append`**, vì sau đó nó đã biến mất; `zip(..., strict=True)` (§04) bắt lỗi nếu hai dãy lệch độ dài; và `:=` (walrus) cho phép vừa gọi vừa lọc trong một comprehension.

## Use case thực tế

- **TCP sliding window.** Bên gửi giữ một cửa sổ các byte đã gửi mà chưa được ACK; cửa sổ trượt sang phải khi ACK về, và co lại khi bên nhận báo hết chỗ. Cùng invariant: "cửa sổ luôn thoả điều kiện tài nguyên", điều chỉnh bằng cách di chuyển hai biên.
- **Rate limiter "N request trong T giây gần nhất".** Đây đúng là sliding window trên trục timestamp: giữ một `deque` các mốc thời gian, `popleft` mọi mốc cũ hơn `now - T`, rồi kiểm `len(deque) < N`. Biến thể rẻ hơn về bộ nhớ là *sliding window counter* (chia thời gian thành ô, nội suy giữa hai ô liền kề) — đánh đổi độ chính xác lấy `O(1)` bộ nhớ, và là thứ được dùng thật trong API gateway.
- **Rolling aggregate trong stream processing.** Flink/Spark Streaming có khái niệm "tumbling window" (cố định, không chồng lấp — chính là fixed window) và "sliding window" (chồng lấp). Cùng bài toán, khác quy mô.
- **Anomaly detection**: so giá trị hiện tại với trung bình/độ lệch chuẩn của cửa sổ gần nhất.
- **Khi nào dùng thư viện có sẵn**: với time-series thật, `pandas.Series.rolling(k).mean()` đã cài sẵn và chạy bằng C. Với cửa sổ có `maxlen`, `collections.deque(maxlen=k)` xử lý phần đẩy phần tử cũ giúp bạn. Tự cài chỉ khi logic cửa sổ không phải là aggregate chuẩn.

## Bẫy thường gặp trong Python

- **Nhầm hai họ "dài nhất" / "ngắn nhất".** Đặt câu cập nhật đáp án sai chỗ (sau `while` thay vì trong `while`) cho kết quả sai mà code vẫn chạy trơn tru. Xác định họ **trước** khi gõ.
- **`Counter[c]` trên key không tồn tại trả `0` và KHÔNG ném lỗi** — tiện, nhưng nó cũng **âm thầm chèn** key vào `Counter` khi bạn dùng `counter[c] -= 1`. Kết quả là `Counter` phình ra với các entry giá trị 0, và `len(win) == len(need)` không còn là điều kiện hợp lệ. Đó là lý do bản Optimized dùng biến `missing` chứ không so `len`.
- **So `win == need` mỗi bước.** Đúng nhưng `O(|Σ|)` mỗi lần và có bug tinh vi: `Counter` có entry giá trị 0 thì `==` cho `False` dù nội dung tương đương. Dùng biến đếm.
- **`dict` mặc định không có `defaultdict`.** `d[c] += 1` với `c` chưa có sẽ `KeyError`. Dùng `collections.Counter` hoặc `defaultdict(int)`.
- **`deque(maxlen=k)` im lặng đẩy phần tử ra.** Nếu bạn còn cần giá trị bị đẩy (để trừ khỏi tổng), phải đọc `buf[0]` **trước** khi `append`. Sau đó nó đã mất, không có cách nào lấy lại.
- **`nums[i:i+k]` trong vòng lặp** — cấp phát `O(k)` mỗi bước. Đó chính là thứ sliding window sinh ra để loại bỏ.
- **Khởi tạo `best = 0` cho bài có số âm.** Bài 239 với `nums = [-7, -8, -9]` sẽ trả về `[0, 0]` thay vì `[-7, -8]`. Dùng `float("inf")` / `-float("inf")` hoặc lấy phần tử đầu làm mốc.
- **Quên `if i >= k - 1` ở bài cửa sổ cố định.** Không có nó, các cửa sổ chưa đủ rộng cũng bị ghi vào kết quả, và độ dài output sai.
- **`float("inf")` trả về từ hàm khai báo `-> int`.** Type checker sẽ phàn nàn, và giá trị `inf` lọt ra ngoài sẽ gây lỗi ở nơi khác. Ép về `int(...)` hoặc `0` trước khi `return`, như bản Optimized của bài 209.
