# 08. Prefix sum, difference array, 2D prefix sum

Prefix sum là dạng đơn giản nhất của "trả trước một lần `O(n)` để mọi truy vấn sau chỉ còn `O(1)`". Difference array là bài toán **đối ngẫu** của nó: cập nhật hàng loạt `O(1)`, đọc giá trị cuối `O(n)`. Section này chốt cả hai chiều, mở rộng lên 2D, và chỉ ra vì sao prefix sum kết hợp hash map biến bài "đếm subarray có tổng = k" từ `O(n²)` xuống `O(n)`.

## Lý thuyết

### Prefix sum 1D

Định nghĩa **có phần tử 0 ở đầu** — đây là quy ước quan trọng:

```
prefix[0] = 0
prefix[i] = a[0] + a[1] + ... + a[i-1]
```

Khi đó `sum(a[i..j])` (bao gồm hai đầu) `= prefix[j+1] - prefix[i]`.

Vì sao phải có `prefix[0] = 0`? Vì nó khiến công thức **không cần trường hợp đặc biệt** cho `i = 0`. Nếu định nghĩa `prefix[i] = a[0]+...+a[i]` thì `sum(a[i..j]) = prefix[j] - prefix[i-1]` và `i = 0` cho `prefix[-1]` — trong Python đó là **phần tử cuối mảng**, tức là một bug im lặng, không phải `IndexError`. Luôn dùng mảng dài `n+1`.

| Thao tác | Prefix sum | Difference array |
| --- | --- | --- |
| Tiền xử lý | `O(n)` | `O(n)` |
| Truy vấn tổng đoạn | `O(1)` | `O(n)` |
| Cập nhật một phần tử | `O(n)` (dựng lại) | `O(1)` |
| Cập nhật cả đoạn `+v` | `O(n)` | **`O(1)`** |
| Bộ nhớ | `O(n)` | `O(n)` |

Bảng này nói rõ cách chọn: **truy vấn nhiều, không sửa** → prefix sum. **Sửa cả đoạn nhiều, chỉ đọc kết quả một lần ở cuối** → difference array. Cần cả hai (vừa update vừa query xen kẽ) → Fenwick tree / segment tree, thuộc PART khác.

### Difference array

Với `diff[i] = a[i] - a[i-1]` (và `diff[0] = a[0]`), cộng `v` vào toàn bộ đoạn `[l, r]` chỉ cần **hai** thao tác:

```
diff[l]   += v
diff[r+1] -= v
```

vì đó là hai vị trí duy nhất mà **hiệu giữa hai phần tử liền kề** thay đổi. Khôi phục mảng gốc bằng prefix sum của `diff`.

> **Invariant**: sau bất kỳ dãy cập nhật nào, `prefix_sum(diff)[i]` luôn bằng giá trị đúng của `a[i]`.

Chứng minh bằng tính tuyến tính: mỗi thao tác `(l, r, v)` đóng góp vào `prefix_sum(diff)[i]` đúng bằng `v` nếu `l ≤ i ≤ r` và `0` nếu ngược lại (vì `+v` ở `l` và `-v` ở `r+1` triệt tiêu nhau khi `i > r`). Tổng các đóng góp chính là kết quả mong muốn.

Cấp phát `diff` dài `n+1` để `diff[r+1]` với `r = n-1` không tràn — cùng lý do với `prefix[0] = 0`.

### 2D prefix sum và inclusion–exclusion

Với ma trận `R × C`, đặt `P` kích thước `(R+1) × (C+1)`, `P[0][*] = P[*][0] = 0`:

```
P[r+1][c+1] = m[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]
```

Số hạng `- P[r][c]` là vì vùng góc trên-trái đã bị cộng **hai lần** (một lần qua `P[r][c+1]`, một lần qua `P[r+1][c]`). Đây là nguyên lý bao hàm–loại trừ.

Truy vấn tổng hình chữ nhật `(r1,c1)–(r2,c2)`:

```
P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

Bốn góc, cùng logic: trừ dải trên, trừ dải trái, cộng lại phần góc đã trừ hai lần.

Tiền xử lý `O(R·C)`, mỗi truy vấn `O(1)`, bộ nhớ `O(R·C)`.

### Prefix sum + hash map: từ tổng đoạn sang **đếm** đoạn

Đây là bước nhảy khái niệm quan trọng nhất của chương. `sum(a[i..j]) = k` tương đương `prefix[j+1] - prefix[i] = k`, tức `prefix[i] = prefix[j+1] - k`.

Vậy khi quét tới `j`, câu hỏi "có bao nhiêu `i ≤ j` mà `prefix[i] = prefix[j+1] - k`" là một truy vấn **đếm** trên tập prefix đã thấy. Một `dict` đếm tần suất trả lời trong `O(1)`.

> **Invariant**: trước khi xử lý phần tử thứ `j`, `cnt[v]` bằng số chỉ số `i ≤ j` sao cho `prefix[i] = v`.

Khởi tạo `cnt[0] = 1` — tương ứng với `prefix[0] = 0`, tức subarray bắt đầu từ chỉ số 0. Quên dòng này là bug số một của bài 560, và nó chỉ sai ở các case mà đáp án bắt đầu từ đầu mảng, nên test tự nghĩ rất dễ bỏ sót.

**Thứ tự thao tác cũng quan trọng**: cộng `cnt[s-k]` vào kết quả **trước**, rồi mới `cnt[s] += 1`. Đảo lại thì với `k = 0` bạn sẽ đếm cả subarray rỗng.

## Bài tập chi tiết

### Bài 1 — 560. Subarray Sum Equals K

#### Requirements

Cho mảng `nums` (có thể âm) và số nguyên `k`. Đếm **số subarray liên tiếp** có tổng đúng bằng `k`.

Chú ý: đếm **số lượng**, không phải tìm một cái. Và **có số âm** — điều này loại thẳng sliding window (§07 cần tính đơn điệu, chỉ có được khi mọi phần tử dương).

Ràng buộc: `1 ≤ n ≤ 2·10^4`, `-1000 ≤ nums[i] ≤ 1000`, `-10^7 ≤ k ≤ 10^7`.

Edge cases: `k = 0` với mảng có nhiều số 0 (đáp án lớn); toàn số âm; subarray đáp án bắt đầu từ chỉ số 0; `n = 1`; các subarray đáp án chồng lấp nhau (vẫn đếm riêng).

#### Complexity mục tiêu

`n ≤ 2·10^4` ⇒ `O(n²)` là `4·10^8`. Với C++ có thể qua, với CPython (§03) là ~40 giây — TLE. Cần `O(n)`.

Không có gì để sort (thứ tự phần tử là bản chất của bài), nên `O(n log n)` không có hình dạng. `O(n)` với `O(n)` bộ nhớ là mục tiêu.

#### Idea

Duyệt một lượt, giữ `s` = prefix sum tới vị trí hiện tại, và một `dict` đếm tần suất các prefix sum đã thấy.

> **Invariant**: ngay trước khi xử lý `nums[j]`, `cnt[v]` = số chỉ số `i` trong `[0, j]` sao cho `prefix[i] = v`, với `prefix[0] = 0` được đếm sẵn (`cnt[0] = 1`).

Tại mỗi `j`: sau khi `s += nums[j]` thì `s = prefix[j+1]`. Mỗi subarray kết thúc tại `j` có tổng `k` ứng với đúng một `i` thoả `prefix[i] = s - k`. Số subarray như vậy là `cnt[s - k]` — cộng vào kết quả. Rồi `cnt[s] += 1` để bảo toàn invariant cho vòng sau.

Vì sao đúng: ánh xạ giữa "subarray `[i, j]` có tổng `k`" và "chỉ số `i` thoả `prefix[i] = prefix[j+1] - k`" là **song ánh**. Nên đếm bên này bằng đếm bên kia. Cộng trên mọi `j` cho tổng số subarray, không trùng không sót (mỗi subarray có đúng một điểm kết thúc).

#### Naive

```python
class SolutionNaive:
    def subarraySum(self, nums: list[int], k: int) -> int:
        count = 0
        for i in range(len(nums)):               # O(n^2)
            s = 0
            for j in range(i, len(nums)):
                s += nums[j]
                if s == k:
                    count += 1
        return count

print(SolutionNaive().subarraySum([1, 1, 1], 2))
print(SolutionNaive().subarraySum([1, 2, 3], 3))
print(SolutionNaive().subarraySum([0, 0, 0], 0))
```

In ra `2`, `2`, `6`.

`O(n²)` time, `O(1)` space. Lưu ý bản này đã khôn hơn bản `O(n³)` (không gọi `sum(nums[i:j+1])` mỗi lần) — nhưng vẫn quét lại mọi điểm bắt đầu. **Không được `break` khi `s == k`**, vì phần tử tiếp theo có thể âm và đưa tổng về `k` lần nữa; đó chính là chỗ bài này khác bài 209 của §07.

#### Optimized

```python
from collections import defaultdict

class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        cnt: defaultdict[int, int] = defaultdict(int)
        cnt[0] = 1                               # prefix[0] = 0, BAT BUOC
        s = res = 0
        for x in nums:
            s += x                               # s = prefix[j+1]
            res += cnt[s - k]                    # DEM truoc...
            cnt[s] += 1                          # ...roi moi ghi nhan
        return res

import random

def naive(nums: list[int], k: int) -> int:
    count = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s == k:
                count += 1
    return count

random.seed(0)
sol = Solution()
for _ in range(5000):
    case = [random.randint(-3, 3) for _ in range(random.randint(0, 9))]
    k = random.randint(-5, 5)
    if naive(case, k) != sol.subarraySum(case, k):
        print("COUNTEREXAMPLE:", case, k)
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.subarraySum([1, 1, 1], 2), sol.subarraySum([1, 2, 3], 3),
      sol.subarraySum([0, 0, 0], 0))
```

In ra `khop tren 5000 case ngau nhien` rồi `2 2 6`.

**Đánh đổi**: `O(n)` bộ nhớ cho `dict` đổi lấy `O(n²) → O(n)` thời gian. Đây là dạng đánh đổi kinh điển nhất — **thêm bộ nhớ để nhớ lại lịch sử** thay vì tính lại. Chú ý bản tối ưu **không** cần dựng mảng `prefix` tường minh: chỉ cần biến `s` chạy, vì ta không bao giờ truy cập `prefix[i]` theo chỉ số, chỉ theo *giá trị*.

### Bài 2 — 1109. Corporate Flight Bookings

#### Requirements

Có `n` chuyến bay, đánh số `1..n`. Mỗi booking là `[first, last, seats]`: đặt `seats` ghế cho **mọi** chuyến từ `first` đến `last` (bao gồm hai đầu). Trả về mảng độ dài `n` với tổng số ghế đã đặt cho từng chuyến.

Chú ý chỉ số **đánh từ 1** trong đề, mảng kết quả **đánh từ 0** — nguồn off-by-one chắc chắn nếu không viết rõ ra.

Ràng buộc: `1 ≤ n ≤ 2·10^4`, `1 ≤ len(bookings) ≤ 2·10^4`, `1 ≤ seats ≤ 10^4`.

Edge cases: booking phủ toàn bộ (`[1, n, s]`); booking một chuyến duy nhất (`first == last`); nhiều booking chồng lấp hoàn toàn; `bookings` rỗng (theo ràng buộc thì không, nhưng code nên chịu được).

#### Complexity mục tiêu

`m` booking × `n` chuyến ⇒ mô phỏng trực tiếp là `O(m·n) = 4·10^8`. TLE.

Nhắm `O(m + n)`: mỗi booking `O(1)`, một lần quét cuối `O(n)`. Đây chính là chữ ký của difference array — và cách nhận ra nó là câu **"range update, chỉ đọc kết quả một lần ở cuối"**.

#### Idea

Giữ `diff` độ dài `n+1`, khởi tạo 0.

> **Invariant**: sau khi xử lý xong `t` booking đầu tiên, `prefix_sum(diff)[i]` bằng đúng số ghế của chuyến `i` tính trên `t` booking đó.

Mỗi booking `[f, l, s]` (đổi sang chỉ số 0: `[f-1, l-1]`) làm hai việc: `diff[f-1] += s`, `diff[l] -= s`.

Vì sao bảo toàn: đóng góp của booking này vào `prefix_sum(diff)[i]` là `+s` khi `i >= f-1` và `-s` khi `i >= l`. Cộng lại: `+s` đúng khi `f-1 ≤ i ≤ l-1`, `0` ngoài khoảng. Đúng bằng ngữ nghĩa của booking. Tính tuyến tính của prefix sum khiến các booking cộng dồn độc lập.

Kết thúc: một lượt prefix sum trên `diff` cho mảng kết quả.

#### Naive

```python
class SolutionNaive:
    def corpFlightBookings(self, bookings: list[list[int]], n: int) -> list[int]:
        res = [0] * n
        for first, last, seats in bookings:      # O(m * n)
            for i in range(first - 1, last):     # de danh so tu 1
                res[i] += seats
        return res

print(SolutionNaive().corpFlightBookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5))
print(SolutionNaive().corpFlightBookings([[1, 2, 10], [2, 2, 15]], 2))
```

In ra `[10, 55, 45, 25, 25]` và `[10, 25]`.

`O(m·n)` time, `O(n)` space. Chậm vì nó **ghi vào từng ô** của mỗi khoảng, trong khi thông tin thực sự mới chỉ nằm ở **hai đầu** khoảng.

#### Optimized

```python
class Solution:
    def corpFlightBookings(self, bookings: list[list[int]], n: int) -> list[int]:
        diff = [0] * (n + 1)                     # n+1 de diff[last] luon hop le
        for first, last, seats in bookings:
            diff[first - 1] += seats
            diff[last] -= seats                  # last (1-based) == last-1+1 (0-based)
        res, run = [], 0
        for i in range(n):
            run += diff[i]
            res.append(run)
        return res

import random

def naive(bookings: list[list[int]], n: int) -> list[int]:
    res = [0] * n
    for first, last, seats in bookings:
        for i in range(first - 1, last):
            res[i] += seats
    return res

random.seed(0)
sol = Solution()
for _ in range(3000):
    n = random.randint(1, 8)
    bookings = []
    for _ in range(random.randint(0, 5)):
        f = random.randint(1, n)
        l = random.randint(f, n)
        bookings.append([f, l, random.randint(1, 10)])
    if naive(bookings, n) != sol.corpFlightBookings(bookings, n):
        print("COUNTEREXAMPLE:", bookings, n)
        break
else:
    print("khop tren 3000 case ngau nhien")

print(sol.corpFlightBookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5),
      sol.corpFlightBookings([[1, 2, 10], [2, 2, 15]], 2))
```

In ra `khop tren 3000 case ngau nhien` rồi `[10, 55, 45, 25, 25] [10, 25]`.

**Đánh đổi**: một mảng phụ `O(n)` (thực ra cùng bậc với output nên gần như miễn phí) đổi lấy `O(m·n) → O(m + n)`. Cái giá thật là **mất khả năng đọc giá trị ở giữa chừng**: trong lúc còn đang nhận booking, `diff` không cho biết chuyến số 3 hiện có bao nhiêu ghế mà không quét lại `O(n)`. Nếu bài đòi xen kẽ update và query thì difference array không dùng được — phải lên Fenwick tree.

### Bài 3 — 304. Range Sum Query 2D - Immutable

#### Requirements

Thiết kế một class: khởi tạo bằng ma trận `matrix` (bất biến), sau đó phục vụ nhiều lần gọi `sumRegion(row1, col1, row2, col2)` trả về tổng các phần tử trong hình chữ nhật đó (bao gồm hai góc).

Từ khoá **Immutable** và "nhiều lần gọi" là chỉ dẫn thiết kế: trả trước chi phí ở `__init__`, để `sumRegion` rẻ nhất có thể.

Ràng buộc: `1 ≤ R, C ≤ 200`, `-10^5 ≤ matrix[i][j] ≤ 10^5`, tối đa `10^4` lần gọi `sumRegion`.

Edge cases: hình chữ nhật 1×1; toàn bộ ma trận; một hàng hoặc một cột; giá trị âm; góc nằm ở biên (`row1 = 0`, `col2 = C-1`).

#### Complexity mục tiêu

`R, C ≤ 200` ⇒ ma trận tối đa `4·10^4` ô. Mỗi `sumRegion` naive là `O(R·C) = 4·10^4`; nhân `10^4` lần gọi ⇒ `4·10^8`. TLE với Python.

Nhắm: `__init__` `O(R·C)`, mỗi `sumRegion` `O(1)`. Tổng `4·10^4 + 10^4` — thừa sức.

#### Idea

Dựng `P` kích thước `(R+1) × (C+1)` với `P[r][c]` = tổng của hình chữ nhật từ `(0,0)` tới `(r-1, c-1)`.

> **Invariant khi dựng**: khi tính `P[r+1][c+1]`, ba ô `P[r][c+1]`, `P[r+1][c]`, `P[r][c]` đều đã có giá trị đúng (do duyệt theo thứ tự hàng rồi cột từ trên xuống, trái sang).

Công thức dựng: `P[r+1][c+1] = m[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]`. Hai vùng "trên" và "trái" chồng nhau ở góc trên-trái, nên trừ đi một lần.

Truy vấn theo bao hàm–loại trừ bốn góc:

```
sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

Viền số 0 ở hàng 0 và cột 0 làm cho công thức đúng cả khi `r1 = 0` hoặc `c1 = 0`, không cần `if`.

#### Naive

```python
class NumMatrixNaive:
    def __init__(self, matrix: list[list[int]]) -> None:
        self.m = matrix                          # khong tien xu ly gi

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        # O(R*C) moi lan goi
        return sum(self.m[r][c]
                   for r in range(row1, row2 + 1)
                   for c in range(col1, col2 + 1))

mat = [[3, 0, 1, 4, 2],
       [5, 6, 3, 2, 1],
       [1, 2, 0, 1, 5],
       [4, 1, 0, 1, 7],
       [1, 0, 3, 0, 5]]
nm = NumMatrixNaive(mat)
print(nm.sumRegion(2, 1, 4, 3), nm.sumRegion(1, 1, 2, 2), nm.sumRegion(1, 2, 2, 4))
```

In ra `8 11 12`.

`__init__` là `O(1)`, mỗi truy vấn `O(R·C)`. Chậm vì nó không tận dụng chút nào việc ma trận **bất biến** — cùng một vùng bị cộng lại từ đầu ở mỗi lần gọi.

#### Optimized

```python
class NumMatrix:
    def __init__(self, matrix: list[list[int]]) -> None:
        R = len(matrix)
        C = len(matrix[0]) if R else 0
        # Vien 0 o hang 0 va cot 0 -> cong thuc khong can truong hop dac biet
        self.P = [[0] * (C + 1) for _ in range(R + 1)]
        for r in range(R):
            for c in range(C):
                self.P[r + 1][c + 1] = (matrix[r][c]
                                        + self.P[r][c + 1]
                                        + self.P[r + 1][c]
                                        - self.P[r][c])      # tru phan chong lan

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        P = self.P
        return (P[row2 + 1][col2 + 1] - P[row1][col2 + 1]
                - P[row2 + 1][col1] + P[row1][col1])

import random

random.seed(0)
for _ in range(2000):
    R, C = random.randint(1, 5), random.randint(1, 5)
    m = [[random.randint(-4, 4) for _ in range(C)] for _ in range(R)]
    nm = NumMatrix([row[:] for row in m])
    r1 = random.randint(0, R - 1); r2 = random.randint(r1, R - 1)
    c1 = random.randint(0, C - 1); c2 = random.randint(c1, C - 1)
    exp = sum(m[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))
    if nm.sumRegion(r1, c1, r2, c2) != exp:
        print("COUNTEREXAMPLE:", m, (r1, c1, r2, c2))
        break
else:
    print("khop tren 2000 truy van ngau nhien")

mat = [[3, 0, 1, 4, 2],
       [5, 6, 3, 2, 1],
       [1, 2, 0, 1, 5],
       [4, 1, 0, 1, 7],
       [1, 0, 3, 0, 5]]
nm = NumMatrix(mat)
print(nm.sumRegion(2, 1, 4, 3), nm.sumRegion(1, 1, 2, 2), nm.sumRegion(1, 2, 2, 4))
```

In ra `khop tren 2000 truy van ngau nhien` rồi `8 11 12`.

**Đánh đổi**: `O(R·C)` bộ nhớ phụ và `O(R·C)` thời gian một lần ở `__init__`, đổi lấy truy vấn `O(1)`. Đây là đánh đổi **có điều kiện**: nó chỉ có lãi khi số truy vấn `Q` đủ lớn. Điểm hoà vốn là `Q · R·C` vs `R·C + Q`, tức có lãi ngay từ `Q ≥ 2`. Nhưng nếu ma trận khổng lồ và chỉ truy vấn một lần thì tiền xử lý là lỗ — chính vì thế đề bài phải nói rõ "immutable" và "nhiều truy vấn".

## Bài luyện thêm

- **303. Range Sum Query - Immutable** — phiên bản 1D của bài 304; dựng `prefix` dài `n+1` trong `__init__`, trả `prefix[j+1] - prefix[i]`.
- **238. Product of Array Except Self** — cùng ý tưởng nhưng với **tích**, và bị cấm dùng phép chia (vì có thể có số 0). Quét trái→phải điền tích tiền tố vào `out`, rồi quét phải→trái nhân với tích hậu tố — dùng một biến chạy, `O(1)` bộ nhớ phụ ngoài output.

## Bài toán áp dụng

Difference array trên trục thời gian: đếm số booking chồng lấp theo ngày. Đây là bài toán thật của mọi hệ thống đặt phòng.

```python
def daily_occupancy(bookings: list[tuple[int, int]], days: int) -> list[int]:
    """bookings: (check_in, check_out) - check_out KHONG tinh (kieu nua mo [in, out)).
    Tra ve so phong ban moi ngay 0..days-1. O(len(bookings) + days)."""
    diff = [0] * (days + 1)
    for start, end in bookings:
        diff[start] += 1
        diff[end] -= 1                    # nua mo: khong +1 o ngay tra phong
    out, run = [], 0
    for d in range(days):
        run += diff[d]
        out.append(run)
    return out

bookings = [(0, 3), (1, 4), (2, 3), (5, 7)]
occ = daily_occupancy(bookings, 8)
print("so phong ban moi ngay:", occ)
print("cao diem:", max(occ), "vao ngay", occ.index(max(occ)))

# Doi chieu voi mo phong truc tiep O(m * days)
naive = [0] * 8
for s, e in bookings:
    for d in range(s, e):
        naive[d] += 1
print("khop voi mo phong truc tiep:", naive == occ)
```

In ra `so phong ban moi ngay: [1, 2, 3, 1, 0, 1, 1, 0]`, `cao diem: 3 vao ngay 2`, `khop voi mo phong truc tiep: True`.

Điểm thiết kế quan trọng: dùng khoảng **nửa mở `[in, out)`**. Khách trả phòng buổi sáng ngày `out` thì ngày đó phòng đã trống — nên `diff[end] -= 1` chứ không phải `diff[end+1]`. Nếu đề dùng khoảng đóng (`[l, r]` cả hai đầu tính) thì phải là `diff[r+1] -= 1`. Chọn nhầm quy ước là bug off-by-one không báo lỗi, chỉ ra số sai ở đúng một ngày. Đây là chỗ §10 sẽ mở rộng thành sweep line tổng quát.

## Use case thực tế

- **Integral image (summed-area table)** trong xử lý ảnh chính là 2D prefix sum. Thuật toán Viola–Jones cho face detection dựa hoàn toàn vào nó: các Haar feature là hiệu tổng cường độ giữa vài hình chữ nhật, và integral image cho phép tính mỗi hình chữ nhật trong `O(1)` bất kể kích thước. Đó là thứ khiến detection chạy realtime trên phần cứng năm 2001.
- **Box blur / mean filter** với cửa sổ `k×k` trên ảnh: `O(1)` mỗi pixel nhờ integral image, thay vì `O(k²)`.
- **Difference array cho log phân tích**: "có bao nhiêu session đang active tại mỗi thời điểm" từ danh sách `(start, end)` — đúng bài `daily_occupancy` ở trên, quy mô hàng triệu bản ghi.
- **Cột `SUM(...) OVER (ORDER BY ...)`** trong SQL (window function) chính là prefix sum, và CSDL cài nó bằng một lượt quét trên dữ liệu đã sort.
- **Khi nào dùng thư viện có sẵn**: `itertools.accumulate(a)` cho prefix sum 1D (chạy bằng C, và có tham số `initial=0` để có luôn phần tử 0 ở đầu); `numpy.cumsum` / `cumsum(axis=...)` cho 2D. Trong production với ảnh hoặc ma trận lớn, `numpy` không phải lựa chọn mà là mặc định. Tự cài chỉ khi bạn ở trên judge không có numpy, hoặc cần logic riêng trong vòng lặp.

## Bẫy thường gặp trong Python

- **`prefix[-1]` không phải lỗi.** Trong C++ chỉ số âm là undefined behavior, thường crash. Trong Python nó lấy **phần tử cuối mảng** và bạn nhận một con số sai hoàn toàn hợp lệ. Đây là lý do luôn dùng mảng dài `n+1` với phần tử 0 ở đầu.
- **Quên `cnt[0] = 1`** ở bài 560. Kết quả sai đúng ở các subarray bắt đầu từ chỉ số 0 — dạng bug mà test tự nghĩ hiếm khi phủ.
- **Đảo thứ tự `res += cnt[s-k]` và `cnt[s] += 1`.** Với `k = 0`, đảo thứ tự sẽ đếm cả subarray rỗng.
- **`defaultdict` tạo key khi bạn chỉ *đọc*.** `cnt[s - k]` với key chưa có sẽ **chèn** entry giá trị 0 vào dict. Không sai kết quả ở bài này, nhưng làm dict phình ra, và nếu ở đâu đó bạn duyệt `cnt.items()` thì sẽ thấy rác. Dùng `cnt.get(s - k, 0)` khi chỉ muốn đọc.
- **`diff` chỉ dài `n`** thay vì `n+1` → `IndexError` khi khoảng chạm biên phải, hoặc tệ hơn, nếu bạn "sửa" bằng `if r+1 < n` thì logic sai im lặng.
- **Nhầm khoảng đóng và nửa mở.** `[l, r]` cần `diff[r+1] -= v`; `[l, r)` cần `diff[r] -= v`. Viết quy ước vào comment ngay dòng đầu.
- **Chỉ số 1-based của đề vs 0-based của mảng.** Bài 1109 là ví dụ; luôn đổi ngay ở đầu vòng lặp và ghi rõ.
- **`[[0] * (C+1)] * (R+1)`** cho 2D prefix — tất cả các hàng là **cùng một list** (§04). Dùng comprehension.
- **Tràn số?** Không phải vấn đề trong Python (`int` arbitrary precision, §04) — nhưng nếu bạn port sang C++/Java thì prefix sum của `2·10^4` phần tử cỡ `10^5` vượt `int32`. Đây là chỗ Python dễ hơn thật, và cũng là chỗ dễ quên khi đổi ngôn ngữ.
- **`itertools.accumulate` không có phần tử 0 ở đầu theo mặc định.** Dùng `accumulate(a, initial=0)` để có mảng dài `n+1` đúng quy ước của chương này.
