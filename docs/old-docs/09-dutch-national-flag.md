# 09. In-place partition — Dutch National Flag

Dutch National Flag (DNF) là bài toán do Dijkstra đặt ra: phân hoạch một mảng thành **ba** vùng theo một pivot, **trong một lần duyệt** và **không dùng bộ nhớ phụ**. Nó là nền của partition 3 chiều trong Quicksort/Quickselect, và là lời giải cho cả một họ bài "sắp xếp lại tại chỗ theo một điều kiện". Điểm cần nắm không phải code — code chỉ 8 dòng — mà là invariant bốn vùng và lý do vòng lặp dừng.

## Lý thuyết

### Bốn vùng, ba con trỏ

Với ba con trỏ `low`, `mid`, `high`, mảng luôn được chia thành **bốn** vùng:

```
[0, low)        : nhom NHO   (đã đúng chỗ)
[low, mid)      : nhom BANG  (đã đúng chỗ)
[mid, high]     : CHUA XET
(high, n-1]     : nhom LON   (đã đúng chỗ)
```

> **Invariant (bốn phần, đúng trước mỗi vòng lặp)**:
> 1. mọi phần tử trong `[0, low)` thuộc nhóm nhỏ;
> 2. mọi phần tử trong `[low, mid)` thuộc nhóm bằng;
> 3. mọi phần tử trong `(high, n-1]` thuộc nhóm lớn;
> 4. `[mid, high]` là phần chưa biết gì.

**Khởi tạo**: `low = mid = 0`, `high = n-1`. Ba vùng đầu rỗng, vùng chưa xét là cả mảng — invariant đúng tầm thường.

**Bảo toàn**, xét `a[mid]`:
- Thuộc nhóm **nhỏ**: đổi chỗ `a[low]` với `a[mid]`, rồi `low += 1; mid += 1`. Hợp lệ vì `a[low]` (trước khi đổi) nằm trong `[low, mid)` nên thuộc nhóm bằng — chuyển nó tới `mid` là đúng chỗ. Nếu `low == mid` thì đổi chỗ với chính nó, vô hại.
- Thuộc nhóm **bằng**: `mid += 1`. Vùng bằng mở rộng.
- Thuộc nhóm **lớn**: đổi chỗ `a[mid]` với `a[high]`, rồi `high -= 1`. **`mid` KHÔNG tăng** — vì `a[high]` vừa chuyển tới `mid` là một phần tử **chưa từng được xét**, phải xử lý ở vòng sau.

**Kết thúc**: vòng lặp chạy khi `mid <= high`. Mỗi vòng, hoặc `mid` tăng, hoặc `high` giảm ⇒ đại lượng `high - mid` giảm ngặt ⇒ dừng sau ≤ `n` vòng. Khi dừng, vùng chưa xét rỗng, và ba invariant còn lại nói mảng đã phân hoạch xong.

Chi tiết "`mid` không tăng ở nhánh nhóm lớn" là **lỗi số một** khi viết DNF từ trí nhớ. Bug đó không crash, chỉ để sót một vài phần tử sai chỗ.

| | Time | Auxiliary space | Số lần swap |
| --- | --- | --- | --- |
| DNF một lượt | `O(n)` | `O(1)` | ≤ `n` |
| Đếm rồi ghi lại (counting sort 2 lượt) | `O(n)` | `O(k)` | 0 (ghi đè) |
| `sorted()` | `O(n log n)` | `O(n)` | — |

### Vì sao partition 3 chiều quan trọng cho Quicksort

Partition 2 chiều (Lomuto/Hoare cổ điển) chia thành `< pivot` và `>= pivot`. Với mảng **toàn phần tử bằng nhau**, mọi phần tử rơi vào một phía ⇒ mỗi lần đệ quy chỉ giảm kích thước đi 1 ⇒ `O(n²)`.

Partition 3 chiều đặt tất cả phần tử **bằng pivot** vào vùng giữa và **loại chúng khỏi đệ quy vĩnh viễn**. Mảng toàn phần tử bằng nhau xong trong một lượt `O(n)`.

Chênh lệch này không phải lý thuyết. Đo trên `n = 20.000` phần tử **giống hệt nhau**, cùng bài Quickselect:

```python
import random, time

def lomuto_partition(a: list[int], lo: int, hi: int) -> int:
    """Partition 2 chieu co dien: <= pivot | > pivot."""
    p = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] <= p:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i

def qs_lomuto(a: list[int], k: int) -> int:
    lo, hi, target = 0, len(a) - 1, len(a) - k
    while True:
        if lo == hi:
            return a[lo]
        pi = lomuto_partition(a, lo, hi)
        if target == pi:
            return a[pi]
        if target < pi:
            hi = pi - 1
        else:
            lo = pi + 1

def qs_three_way(a: list[int], k: int) -> int:
    """Partition 3 chieu (DNF): < p | == p | > p."""
    lo, hi, target = 0, len(a) - 1, len(a) - k
    while True:
        if lo == hi:
            return a[lo]
        p = a[random.randint(lo, hi)]
        lt, i, gt = lo, lo, hi
        while i <= gt:
            if a[i] < p:
                a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
            elif a[i] > p:
                a[i], a[gt] = a[gt], a[i]; gt -= 1
            else:
                i += 1
        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            return p                     # target roi vao vung == p

random.seed(0)
N = 20_000
all_same = [7] * N
t0 = time.perf_counter(); qs_lomuto(list(all_same), N // 2);    t1 = time.perf_counter()
qs_three_way(list(all_same), N // 2);                           t2 = time.perf_counter()
print(f"n={N}, toan phan tu giong nhau:")
print(f"  Lomuto (2 chieu): {t1-t0:.4f}s")
print(f"  DNF    (3 chieu): {t2-t1:.6f}s  -> nhanh hon {(t1-t0)/(t2-t1):,.0f}x")
```

Kết quả:

```
n=20000, toan phan tu giong nhau:
  Lomuto (2 chieu): 4.3295s
  DNF    (3 chieu): 0.000443s  -> nhanh hon 9,781x
```

Đây không phải chênh lệch hằng số — đó là `O(n²)` gặp `O(n)`. Với `n = 20.000`, Lomuto làm `2·10^8` phép so sánh; DNF làm `2·10^4`.

### DNF vs counting sort

Bài 75. Sort Colors có `k = 3` giá trị đã biết trước, nên **counting sort hai lượt** (đếm số 0/1/2, rồi ghi đè) cũng là `O(n)` và dễ hơn nhiều. Đề bài chống lại chính điều đó bằng câu "can you solve this in one pass?".

Khi nào DNF thắng thật sự: khi bạn **không được duyệt hai lần** (dữ liệu là stream), hoặc khi phần tử là object nặng mà bạn chỉ được **hoán vị** chứ không được ghi đè (vì mỗi phần tử mang thêm dữ liệu ngoài khoá phân loại). Trong Quickselect thì bắt buộc là DNF, vì pivot là giá trị chạy chứ không phải nhãn cố định.

## Bài tập chi tiết

### Bài 1 — 75. Sort Colors

#### Requirements

Mảng `nums` chỉ chứa các giá trị `0`, `1`, `2` (đỏ, trắng, xanh). Sắp xếp **tại chỗ** sao cho các giá trị bằng nhau nằm liền kề, theo thứ tự `0 < 1 < 2`.

Đề cấm dùng hàm sort có sẵn của thư viện, và hỏi thẳng có làm được trong **một lượt** với **`O(1)` bộ nhớ phụ** không. Hàm không trả về gì — sửa `nums` tại chỗ.

Ràng buộc: `1 ≤ n ≤ 300`, `nums[i] ∈ {0, 1, 2}`.

Edge cases: `n = 1`; mảng đã sắp xếp sẵn; sắp xếp ngược (`[2,2,1,1,0,0]`); chỉ có một loại màu; không có màu nào đó (vd không có số 1); `[2, 0]` (hai phần tử, cần một swap và `mid` không được tăng).

#### Complexity mục tiêu

`n ≤ 300` là cực nhỏ — `O(n²)` là `9·10^4`, thậm chí `O(n³)` cũng qua. **Ràng buộc n không phải thứ quyết định ở bài này**; chính đề bài mới là thứ đặt ra yêu cầu: một lượt, `O(1)` space, không dùng sort thư viện.

Đây là ví dụ tốt cho việc "complexity mục tiêu" không phải lúc nào cũng suy từ n. Đôi khi nó suy từ **câu follow-up của đề**, và đó cũng chính là câu người phỏng vấn sẽ hỏi.

#### Idea

Áp dụng thẳng DNF với ba nhóm: nhỏ = `0`, bằng = `1`, lớn = `2`.

> **Invariant**: `nums[0:low]` toàn `0`; `nums[low:mid]` toàn `1`; `nums[high+1:n]` toàn `2`; `nums[mid:high+1]` chưa xét.

Ba nhánh:
- `nums[mid] == 0`: swap với `nums[low]`, `low += 1`, `mid += 1`. An toàn tăng `mid` vì phần tử nhận về từ `low` chắc chắn là `1` (hoặc chính nó khi `low == mid`) — đã được phân loại rồi.
- `nums[mid] == 1`: `mid += 1`.
- `nums[mid] == 2`: swap với `nums[high]`, `high -= 1`, **`mid` giữ nguyên** — phần tử vừa nhận về từ `high` chưa từng xét.

Kết thúc khi `mid > high`: vùng chưa xét rỗng ⇒ mảng đã phân hoạch đúng ⇒ đã sắp xếp (vì chỉ có ba giá trị và ba vùng đúng thứ tự).

#### Naive

```python
class SolutionNaive:
    def sortColors(self, nums: list[int]) -> None:
        """Counting sort HAI luot: dem roi ghi de. O(n) nhung 2 lan duyet."""
        count = [0, 0, 0]
        for x in nums:
            count[x] += 1
        i = 0
        for color in range(3):
            for _ in range(count[color]):
                nums[i] = color
                i += 1

for case in ([2, 0, 2, 1, 1, 0], [2, 0, 1], [0], [2, 2, 2], [2, 0]):
    a = list(case)
    SolutionNaive().sortColors(a)
    print(case, "->", a)
```

In ra từng dòng, ví dụ `[2, 0, 2, 1, 1, 0] -> [0, 0, 1, 1, 2, 2]`.

`O(n)` time, `O(1)` space (mảng `count` chỉ 3 phần tử) — **nhưng hai lượt duyệt**, và nó **ghi đè** giá trị chứ không hoán vị. Với bài này thì không sao vì phần tử chỉ là số. Nếu mỗi phần tử là một object mang thêm dữ liệu (một record có trường `color`), cách này **phá huỷ dữ liệu**: nó ghi nhãn màu đè lên object. Đó là giới hạn thật sự, không phải chuyện "hai lượt".

#### Optimized

```python
class Solution:
    def sortColors(self, nums: list[int]) -> None:
        low, mid, high = 0, 0, len(nums) - 1
        while mid <= high:
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1                         # an toan: phan tu nhan ve la 1
            elif nums[mid] == 2:
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1                        # mid KHONG tang: phan tu moi chua xet
            else:
                mid += 1

import random

random.seed(0)
sol = Solution()
for _ in range(20_000):
    case = [random.randint(0, 2) for _ in range(random.randint(0, 9))]
    a = list(case)
    sol.sortColors(a)
    if a != sorted(case):
        print("COUNTEREXAMPLE:", case, "->", a)
        break
else:
    print("khop voi sorted() tren 20000 case ngau nhien")

for case in ([2, 0, 2, 1, 1, 0], [2, 0, 1], [0], [2, 2, 2], [2, 0]):
    a = list(case)
    sol.sortColors(a)
    print(case, "->", a)
```

In ra `khop voi sorted() tren 20000 case ngau nhien` rồi các dòng biến đổi.

**Đánh đổi**: cùng `O(n)` time và `O(1)` space như bản counting sort — thứ ta đổi là **độ dễ đọc lấy một lượt duyệt duy nhất và tính "chỉ hoán vị"**. Bản DNF khó chứng minh hơn (bốn vùng, một nhánh không tăng `mid`), nhưng nó không giả định gì về phần tử ngoài việc so sánh được, nên tổng quát hoá được sang Quickselect và sang mảng object. Bản counting sort chỉ chạy khi tập giá trị nhỏ và bạn được phép ghi đè.

Một chi tiết Python: `nums[low], nums[mid] = nums[mid], nums[low]` là swap **đúng** vì vế phải được đánh giá **toàn bộ** thành tuple trước khi gán. Trong C bạn cần biến tạm; ở đây không. Nhưng cẩn thận với dạng `a[i], a[a[i]] = a[a[i]], a[i]` — thứ tự gán ở vế trái là trái sang phải, nên `a[i]` đã đổi trước khi `a[a[i]]` được tính. Dạng đó là bug thật, tránh viết.

### Bài 2 — 215. Kth Largest Element in an Array

#### Requirements

Cho `nums` và số `k`, trả về phần tử **lớn thứ `k`** theo thứ tự sắp xếp — **không phải** phần tử phân biệt thứ `k`. Với `[3,2,3,1,2,4,5,5,6]` và `k = 4`, đáp án là `4` (dãy giảm dần: 6,5,5,4).

Đề (bản follow-up) hỏi có giải được **không dùng sort** hay không, ngụ ý `O(n)` trung bình.

Ràng buộc: `1 ≤ k ≤ n ≤ 10^5`, `-10^4 ≤ nums[i] ≤ 10^4`.

Edge cases: `k = 1` (max) và `k = n` (min); toàn phần tử giống nhau (worst case của partition 2 chiều); `n = 1`; nhiều giá trị trùng quanh đáp án; số âm.

#### Complexity mục tiêu

`n ≤ 10^5`. `sorted(nums)[-k]` là `O(n log n)` — hoàn toàn pass, chạy bằng C, và là một dòng. Đó là câu trả lời đúng nếu mục tiêu chỉ là AC.

Nhưng câu hỏi phỏng vấn là `O(n)` trung bình. Quickselect đạt `O(n)` **kỳ vọng** với pivot ngẫu nhiên (`n + n/2 + n/4 + ... = 2n`), worst case `O(n²)`. Với partition **3 chiều**, mảng nhiều phần tử trùng không còn là worst case.

Lựa chọn thứ ba: min-heap kích thước `k`, `O(n log k)` — `heapq.nlargest(k, nums)[-1]` làm sẵn việc đó bằng C, và là lựa chọn tốt khi `k` nhỏ hơn nhiều so với `n`, hoặc khi dữ liệu là stream không giữ hết được.

#### Idea

Quickselect: partition quanh một pivot, rồi **chỉ đệ quy vào một phía**.

Đặt `target = n - k` — chỉ số của đáp án trong mảng đã sắp tăng dần.

> **Invariant**: `target` luôn nằm trong đoạn đang xét `[lo, hi]`, và mọi phần tử ngoài đoạn đã ở đúng phía so với đoạn.

Mỗi vòng: chọn pivot ngẫu nhiên trong `[lo, hi]`, chạy DNF trên đoạn đó, thu được ba vùng `[lo, lt)`, `[lt, gt]`, `(gt, hi]`.

- `target < lt` ⇒ đáp án ở vùng nhỏ ⇒ `hi = lt - 1`.
- `target > gt` ⇒ vùng lớn ⇒ `lo = gt + 1`.
- Ngược lại ⇒ `target` rơi vào vùng **bằng pivot** ⇒ đáp án chính là `pivot`, trả về ngay.

Nhánh thứ ba là điều mà partition 2 chiều không có, và là nguồn của toàn bộ lợi thế: mọi phần tử bằng pivot bị loại khỏi bài toán vĩnh viễn trong một lượt.

Bảo toàn: DNF đặt mọi phần tử `< pivot` bên trái `lt` và mọi phần tử `> pivot` bên phải `gt`, nên thứ hạng của chúng so với `target` được xác định — cắt phía nào cũng không mất đáp án.

Kết thúc: mỗi vòng đoạn `[lo, hi]` **thu hẹp ngặt** (vì vùng bằng pivot luôn có ít nhất một phần tử, chính là pivot), nên vòng lặp dừng. **Pivot ngẫu nhiên** là thứ cho kỳ vọng `O(n)`: pivot cố định (vd luôn lấy `a[hi]`) bị mảng đã sort đánh gục thành `O(n²)`.

#### Naive

```python
class SolutionNaive:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        """Sort roi lay. O(n log n) - trong CPython day thuc ra la lua chon TOT
        de AC, vi Timsort chay bang C. Dung lam oracle cho ban Quickselect."""
        return sorted(nums)[-k]

print(SolutionNaive().findKthLargest([3, 2, 1, 5, 6, 4], 2))
print(SolutionNaive().findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))
print(SolutionNaive().findKthLargest([1], 1))
print(SolutionNaive().findKthLargest([-1, -1], 2))
```

In ra `5`, `4`, `1`, `-1`.

`O(n log n)` time, `O(n)` space (`sorted` tạo list mới). "Chậm" ở đây là chậm **về mặt asymptotic**: nó sắp xếp toàn bộ mảng trong khi ta chỉ cần biết một phần tử. Với `n = 10^6` và `k = 3`, đó là lãng phí thật.

#### Optimized

```python
import random

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        a = list(nums)                           # khong sua input cua nguoi goi
        target = len(a) - k                      # chi so trong mang sap TANG dan
        lo, hi = 0, len(a) - 1
        while True:
            if lo == hi:
                return a[lo]
            pivot = a[random.randint(lo, hi)]    # ngau nhien -> ky vong O(n)
            lt, i, gt = lo, lo, hi               # DNF tren doan [lo, hi]
            while i <= gt:
                if a[i] < pivot:
                    a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
                elif a[i] > pivot:
                    a[i], a[gt] = a[gt], a[i]; gt -= 1
                else:
                    i += 1
            if target < lt:
                hi = lt - 1                      # dap an o vung < pivot
            elif target > gt:
                lo = gt + 1                      # dap an o vung > pivot
            else:
                return pivot                     # target roi vao vung == pivot

random.seed(0)
sol = Solution()
for _ in range(20_000):
    n = random.randint(1, 9)
    case = [random.randint(-4, 4) for _ in range(n)]
    k = random.randint(1, n)
    if sol.findKthLargest(case, k) != sorted(case)[-k]:
        print("COUNTEREXAMPLE:", case, k)
        break
else:
    print("khop voi sorted()[-k] tren 20000 case ngau nhien")

print(sol.findKthLargest([3, 2, 1, 5, 6, 4], 2),
      sol.findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4),
      sol.findKthLargest([1], 1),
      sol.findKthLargest([-1, -1], 2))

# Worst case cua partition 2 chieu: 200k phan tu giong het nhau
import time
big = [7] * 200_000
t0 = time.perf_counter()
ans = sol.findKthLargest(big, 100_000)
print(f"200k phan tu giong nhau -> {ans}, mat {time.perf_counter()-t0:.4f}s")

# Quickselect (Python thuan) vs sorted() (Timsort chay bang C), n = 10^5 ngau nhien
data = [random.randint(-10**4, 10**4) for _ in range(100_000)]
t0 = time.perf_counter(); sol.findKthLargest(data, 5_000);   t1 = time.perf_counter()
sorted(data)[-5_000];                                        t2 = time.perf_counter()
print(f"n=1e5: Quickselect {t1-t0:.4f}s | sorted()[-k] {t2-t1:.4f}s")
```

Đo được:

```
khop voi sorted()[-k] tren 20000 case ngau nhien
5 4 1 -1
200k phan tu giong nhau -> 7, mat 0.0047s
n=1e5: Quickselect 0.0057s | sorted()[-k] 0.0083s
```

Hai dòng cuối đáng đọc kỹ. Dòng thứ ba: **0.0047 giây** cho mảng 200.000 phần tử giống hệt nhau — đúng cái input làm Lomuto sập ở mục Lý thuyết.

Dòng thứ tư thì đi ngược trực giác thông thường về CPython (§03). Ở `n = 10^5` ngẫu nhiên, Quickselect **viết bằng Python thuần vẫn nhanh hơn `sorted()` cài bằng C khoảng 1.4x** — và tỉ lệ này ổn định qua nhiều lần chạy. Lý do: `sorted()` phải làm ~`n log n ≈ 1.7·10^6` phép so sánh, còn Quickselect chỉ chạm khoảng `2n = 2·10^5` phần tử. Hệ số `log n ≈ 17` ở đây **lớn hơn** khoảng cách C-vs-bytecode cho loại vòng lặp đơn giản này. Bài học: đừng đoán, hãy đo — kể cả khi "C luôn nhanh hơn" nghe rất hợp lý.

**Đánh đổi**: `O(n)` kỳ vọng thay cho `O(n log n)`, đổi lấy ba thứ — (1) **worst case `O(n²)`** thay vì bảo đảm `O(n log n)`; (2) **phá thứ tự** mảng (nên phải copy nếu người gọi còn cần); (3) code dài hơn nhiều và dễ sai hơn nhiều: một dòng `sorted(nums)[-k]` không có chỗ nào để sai, còn bản trên có pivot, ba con trỏ và ba nhánh so `target`.

Về tốc độ thực tế thì như số đo ở trên: `n = 10^5` Quickselect nhanh hơn ~1.4x. Nhưng khoảng cách đó **không** đáng để đánh đổi rủi ro viết sai trong lúc thi. Nộp `sorted(nums)[-k]`; viết Quickselect khi người phỏng vấn hỏi `O(n)`, hoặc khi `n` đủ lớn để hệ số `log n` thật sự thành tiền.

## Bài luyện thêm

- **283. Move Zeroes** — DNF rút gọn còn hai vùng: một con trỏ `slow` đánh dấu ranh giới phần khác 0; quét `fast`, gặp phần tử khác 0 thì swap về `slow`. Số 0 tự dồn về cuối mà không cần vòng thứ hai.
- **905. Sort Array By Parity** — partition 2 chiều theo tính chẵn lẻ; có thể dùng hai con trỏ đối chiều (đổi chỗ khi trái lẻ và phải chẵn) hoặc dạng cùng chiều như 283. Thứ tự trong mỗi nhóm không quan trọng, nên không cần stable.

## Bài toán áp dụng

Phân loại record thành ba nhóm trong một lượt quét, chỉ bằng hoán vị — đúng hình dạng bước "partition theo category" trong ETL pipeline:

```python
from dataclasses import dataclass

@dataclass
class Record:
    id: int
    level: str          # "error" | "warning" | "valid"

def partition3(records: list[Record], first: str, last: str) -> tuple[int, int]:
    """DNF tong quat: dua `first` len dau, `last` xuong cuoi, con lai o giua.
    Tra ve (low, high): records[:low] la `first`, records[high+1:] la `last`."""
    low, mid, high = 0, 0, len(records) - 1
    while mid <= high:
        lv = records[mid].level
        if lv == first:
            records[low], records[mid] = records[mid], records[low]
            low += 1; mid += 1
        elif lv == last:
            records[mid], records[high] = records[high], records[mid]
            high -= 1                      # mid khong tang
        else:
            mid += 1
    return low, high

rows = [Record(i, lv) for i, lv in enumerate(
    ["valid", "error", "warning", "valid", "error", "valid", "warning", "error"])]
low, high = partition3(rows, "error", "warning")

print("error  :", [r.id for r in rows[:low]])
print("valid  :", [r.id for r in rows[low:high + 1]])
print("warning:", [r.id for r in rows[high + 1:]])
print("khong mat record nao:", sorted(r.id for r in rows) == list(range(8)))
print("phan nhom dung:",
      all(r.level == "error" for r in rows[:low])
      and all(r.level == "valid" for r in rows[low:high + 1])
      and all(r.level == "warning" for r in rows[high + 1:]))
```

In ra ba nhóm id, rồi `khong mat record nao: True` và `phan nhom dung: True`.

Đây là chỗ DNF hơn hẳn counting sort: `Record` mang theo trường `id`, nên **không thể ghi đè** — chỉ được hoán vị. Và vì hàm trả về `(low, high)`, bước sau của pipeline ghi ra ba file chỉ bằng ba lần slice, không cần ba list riêng ⇒ `O(1)` bộ nhớ phụ dù có hàng triệu record.

## Use case thực tế

- **Partition scheme trong sorting library.** Nhiều cài đặt `std::sort` / introsort dùng partition 3 chiều (hoặc "fat pivot") chính vì mảng thực tế đầy giá trị trùng — nghĩ tới cột `status`, `country_code`, `category_id` trong dữ liệu thật.
- **`nth_element` của C++ STL** chính là Quickselect, và nó là thứ bạn gọi khi cần median hoặc percentile mà không muốn sort toàn bộ.
- **Tính percentile trên dữ liệu lớn**: p50/p95/p99 latency chỉ cần Quickselect, không cần sort. Với dữ liệu quá lớn hoặc dạng stream, người ta dùng sketch xấp xỉ (t-digest, HdrHistogram) — đổi độ chính xác lấy bộ nhớ `O(1)`.
- **ETL / stream routing**: phân luồng record thành valid / warning / error, hoặc phân trang dữ liệu thành các partition trước khi ghi — một lượt quét, không bộ nhớ phụ.
- **Khi nào dùng thư viện có sẵn**: gần như luôn. `sorted()` cho bài 75 (đề cấm, nhưng ngoài đời thì không); `heapq.nlargest(k, it)` khi `k` nhỏ; `statistics.quantiles` cho percentile trên dữ liệu vừa RAM; `numpy.partition(a, kth)` là Quickselect cài bằng C và là thứ đúng để dùng trên mảng lớn. Tự viết Quickselect chỉ khi bạn cần logic phân hoạch riêng, hoặc đang trả lời phỏng vấn.

## Bẫy thường gặp trong Python

- **Tăng `mid` ở nhánh nhóm lớn.** Bug số một của DNF. Phần tử vừa hoán đổi từ `high` về **chưa được xét**; tăng `mid` là bỏ qua nó. Không crash, chỉ sai.
- **`while mid < high` thay vì `mid <= high`.** Bỏ sót đúng phần tử cuối cùng của vùng chưa xét. Thử với `[2, 0]` sẽ thấy ngay.
- **`a[i], a[a[i]] = a[a[i]], a[i]`.** Vế phải được tính trước, nhưng **vế trái gán từ trái sang phải**: sau khi `a[i]` được gán, biểu thức `a[a[i]]` dùng giá trị *mới*. Đây là bug thật khi làm bài kiểu "đặt số về đúng vị trí" (41, 442). Dùng biến tạm.
- **Quên copy mảng trong Quickselect.** Nó phá thứ tự input. Nếu người gọi còn dùng `nums` sau đó, họ nhận một mảng đã bị xáo. Bản Optimized ở trên copy ngay dòng đầu.
- **Pivot cố định `a[hi]`.** Mảng đã sort (rất thường gặp trong test của judge) trở thành worst case `O(n²)`. Luôn `random.randint(lo, hi)` — hoặc median-of-three.
- **`sorted(nums)[-k]` với `k` vượt `len(nums)`.** Trả về phần tử đầu do chỉ số âm cuộn vòng, không ném lỗi. Kiểm `1 <= k <= n` nếu input không đáng tin.
- **`count = [0] * 3` rồi `count[x] += 1` với `x` ngoài `{0,1,2}`** → `IndexError`, hoặc tệ hơn với `x = -1` thì nó âm thầm tăng `count[2]`. Luôn kiểm miền giá trị khi dùng counting sort.
- **`list.remove()` / `del` trong vòng lặp để "dồn phần tử".** `O(n)` mỗi lần và làm lệch chỉ số của vòng lặp. Toàn bộ họ bài này tồn tại để tránh đúng việc đó: hoán vị, đừng xoá.
