# 19. Sorted Container & workaround khi thiếu ordered set/balanced BST

Đây là section về một **lỗ hổng của Python**: stdlib không có ordered set hay balanced BST, trong khi C++ có `std::set`/`std::map` và Java có `TreeMap`. Hệ quả là một lớp bài toán "duy trì tập hợp sorted với insert/delete/rank động" mà mọi ngôn ngữ khác giải trong O(log n) thì Python mặc định chỉ có O(n). Section này chỉ ra khi nào điều đó thật sự đau, và ba cách thay thế — trong đó Fenwick tree là cái bạn phải tự cài được.

## Lý thuyết

### Vấn đề: `bisect` cho tìm kiếm O(log n) nhưng không cho chèn O(log n)

`bisect` trên `list` cho ta:

| Thao tác | Chi phí | Vì sao |
|---|---|---|
| `bisect_left/right` | O(log n) | binary search thuần |
| `a[i]` (phần tử thứ i) | **O(1)** | mảng liên tục |
| `insort(a, x)` | **O(n)** | `memmove` dịch đuôi mảng |
| `a.remove(x)` | **O(n)** | tìm O(n) + dịch O(n) |
| duyệt theo thứ tự | O(n) | |

Hai dòng in đậm là vấn đề. Với `q` lần chèn/xoá, tổng chi phí là O(q·n) — bậc hai.

Điều gây nhầm lẫn là **`memmove` rất nhanh** (code C, tận dụng SIMD), nên với n nhỏ thì O(n) chèn vẫn thắng O(log n) của một cấu trúc Python thuần. Chỉ khi n đủ lớn thì bậc hai mới lộ ra. Đo trên máy này với bài 315 (chi tiết bên dưới), so `bisect + list.insert` với Fenwick tree:

```
n=  50000  bisect+insert   0.097s   Fenwick  0.056s   tỉ lệ   1.7x
n= 100000  bisect+insert   0.379s   Fenwick  0.135s   tỉ lệ   2.8x
n= 200000  bisect+insert   1.645s   Fenwick  0.306s   tỉ lệ   5.4x
n= 400000  bisect+insert   5.883s   Fenwick  0.686s   tỉ lệ   8.6x
```

Đọc bảng theo cột chứ không theo dòng: cột `bisect` **gấp ~3.5 lần khi n gấp đôi** (dấu hiệu O(n²) với hằng số nhỏ), cột Fenwick **gấp ~2.2 lần** (dấu hiệu O(n log n)). Ở n = 5·10⁴ chênh lệch không đáng kể; ở n = 4·10⁵ là 8.6 lần và còn tiếp tục giãn ra. Kết luận thực dụng: **`bisect` + `list` ổn tới khoảng n ~ 10⁵**, sau đó không.

### `sortedcontainers` — chuẩn de-facto, và cái bẫy môi trường

`sortedcontainers` (Grant Jenks) cung cấp `SortedList`, `SortedDict`, `SortedSet` với API rất đầy đủ:

| Thao tác | Chi phí |
|---|---|
| `sl.add(x)`, `sl.remove(x)`, `sl.discard(x)` | O(log n)¹ |
| `sl[i]` (index) | O(log n) |
| `sl.bisect_left(x)` / `bisect_right(x)` | O(log n) |
| `sl.index(x)` (rank) | O(log n) |
| `sl.irange(lo, hi)` (range query) | O(log n + k) |
| duyệt theo thứ tự | O(n) |

¹ Thực chất là O(n^(1/2)) về mặt lý thuyết nhưng với hằng số cực nhỏ — nó **không phải** balanced BST mà là một list-of-lists hai tầng: mảng lớn được chia thành các block ~1000 phần tử, chèn vào một block là `memmove` trên 1000 phần tử (nhanh khủng khiếp trong C), thỉnh thoảng tách block. Trong thực tế nó nhanh hơn nhiều cấu trúc O(log n) thuần vì tận dụng đúng cái mà CPython làm tốt.

**Cái bẫy**: `sortedcontainers` là thư viện ngoài.

- **LeetCode**: có sẵn, dùng thoải mái.
- **Codeforces / AtCoder / phần lớn judge khác**: **không có**. Bạn phải paste cả thư viện vào bài nộp (rất dài) hoặc tự viết cấu trúc thay thế.
- **Máy đang viết handbook này**: đã kiểm tra bằng `~/.local/bin/python3.12 -c "import sortedcontainers"` → `ModuleNotFoundError`. Nên **mọi đoạn code `SortedList` trong chương này là minh hoạ, chưa được thực thi**; các đoạn còn lại (Fenwick, heap + lazy deletion, `bisect`) chỉ dùng stdlib và **đã chạy thật**.

Kết luận: học `SortedList` để dùng khi có, và học Fenwick tree để dùng khi không có.

### Fenwick tree (Binary Indexed Tree) — cấu trúc thay thế chính

Fenwick tree giải bài toán **prefix sum động**: cập nhật một phần tử và truy vấn tổng tiền tố, cả hai trong O(log n).

Ý tưởng: `tree[i]` giữ tổng của đoạn `(i - lowbit(i), i]`, với `lowbit(i) = i & (-i)` là bit 1 thấp nhất của `i`.

> **Invariant**: `tree[i]` = tổng của đúng `lowbit(i)` phần tử kết thúc tại `i`.

Nhờ đó, `prefix(i)` = tổng của `[1, i]` được phân tách thành các đoạn theo biểu diễn nhị phân của `i`: bỏ dần bit 1 thấp nhất (`i -= i & -i`) và cộng `tree[i]` — số bước bằng số bit 1 của `i`, tối đa `log n`. Ngược lại, `add(i)` sửa mọi đoạn chứa `i`, tìm bằng cách cộng bit thấp nhất (`i += i & -i`) — cũng `log n` bước.

Vì sao nó thay thế được ordered set: nếu ta dùng Fenwick để **đếm số lần xuất hiện** của mỗi giá trị (sau khi coordinate-compress), thì:

- `prefix(r)` = **số phần tử có hạng < r** = rank của giá trị đó.
- `kth(k)` = **phần tử thứ k theo thứ tự** — order statistics.

Đó chính xác là hai thao tác mà `SortedList.index()` và `SortedList[i]` cung cấp.

**Coordinate compression** là bước ghép cặp bắt buộc: giá trị có thể tới 10⁹ nhưng chỉ có ≤ n giá trị phân biệt, nên ánh xạ chúng về `[0, n)` rồi Fenwick chỉ cần n ô. Cạm bẫy: **phải nén cả giá trị xuất hiện trong truy vấn**, không chỉ giá trị trong mảng — nếu truy vấn hỏi về `x` không có trong mảng, `rank[x]` sẽ ném `KeyError` hoặc (tệ hơn) bạn dùng `bisect` trên mảng nén và lệch 1.

### Bảng so sánh ba workaround

| | `bisect` + `list` | Fenwick tree | heap + lazy deletion |
|---|---|---|---|
| insert | O(n)² | **O(log n)** | **O(log n)** |
| delete tuỳ ý | O(n) | **O(log n)** | O(log n) amortized |
| min / max | O(1) | O(log n) | **O(1)** min |
| phần tử thứ k | **O(1)** | O(log n) | **không có** |
| đếm số phần tử < x | O(log n) | **O(log n)** | **không có** |
| range query | O(log n + k) | O(log n) tổng | **không có** |
| duyệt theo thứ tự | **O(n)** | O(n log n) | **không có** |
| cần coordinate compression | không | **có** | không |
| dòng code | 1 | ~25 | ~20 |

² Hằng số cực nhỏ (`memmove`) — dùng được tới n ~ 10⁵.

Quy tắc chọn:
- Chỉ cần **min/max động** → heap + lazy deletion (§16). Nhẹ nhất.
- Cần **rank / phần tử thứ k / đếm theo khoảng** → Fenwick tree.
- Ít lần chèn/xoá so với số lần truy vấn, hoặc n ≤ 10⁵ → `bisect` + `list`, đừng phức tạp hoá.
- Có `sortedcontainers` và cần API đầy đủ → `SortedList`.

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/tree/fenwick.py`

```python
class Fenwick:
    """Binary Indexed Tree (Fenwick) — prefix sum động, 1-INDEXED bên trong.

    Invariant: tree[i] giữ tổng của đoạn (i - lowbit(i), i] với lowbit(i) = i & -i.
    Nhờ đó prefix(i) chỉ cần cộng O(log n) node, và add() chỉ cần sửa O(log n) node.
    """

    def __init__(self, size: int) -> None:
        self._n = size
        self._tree = [0] * (size + 1)      # index 0 KHÔNG dùng

    def add(self, i: int, delta: int = 1) -> None:
        """Cộng delta vào vị trí i (0-indexed từ bên ngoài)."""
        i += 1
        while i <= self._n:
            self._tree[i] += delta
            i += i & (-i)

    def prefix(self, i: int) -> int:
        """Tổng của [0, i) — tức là i phần tử đầu tiên."""
        s = 0
        while i > 0:
            s += self._tree[i]
            i -= i & (-i)
        return s

    def range_sum(self, lo: int, hi: int) -> int:
        """Tổng của [lo, hi)."""
        return self.prefix(hi) - self.prefix(lo)

    def kth(self, k: int) -> int:
        """Binary lifting: chỉ số 0-indexed nhỏ nhất i sao cho prefix(i+1) >= k.

        Dùng cho order statistics: 'phần tử thứ k' khi BIT lưu số đếm.
        O(log n), KHÔNG phải O(log^2 n) như binary search + prefix().
        """
        pos = 0
        bit = 1 << (self._n.bit_length())
        while bit:
            nxt = pos + bit
            if nxt <= self._n and self._tree[nxt] < k:
                pos = nxt
                k -= self._tree[nxt]
            bit >>= 1
        return pos                          # 0-indexed


def compress(values) -> dict:
    """Ánh xạ giá trị -> hạng (0-indexed). Nhớ đưa VÀO ĐÂY cả giá trị truy vấn,
    không chỉ giá trị trong mảng."""
    return {v: i for i, v in enumerate(sorted(set(values)))}
```

Ba điểm cần nắm:

1. **BIT là 1-indexed về bản chất.** Công thức `i & -i` chỉ hoạt động khi `i >= 1` (với `i = 0` thì `lowbit = 0` và `i += 0` là vòng lặp vô hạn). Bản trên nhận index 0-based từ bên ngoài và `+1` ở ranh giới — đó là cách an toàn nhất, vì trộn lẫn hai hệ chỉ số là nguồn bug số một khi cài Fenwick.

2. **`kth` dùng binary lifting, không dùng binary search.** Cách ngây thơ là binary search trên `i` với `prefix(i)` — O(log²n). Binary lifting đi thẳng xuống cây theo từng bit từ cao xuống thấp, tận dụng chính cấu trúc của `tree`, cho O(log n). Đây là thứ biến Fenwick từ "prefix sum" thành "ordered set thay thế được".

3. **`self._n.bit_length()`** cho bit cao nhất — dùng `int.bit_length()` (có sẵn) thay vì tính `log2` qua `float`.

Đã stress test: 2000 phiên × 30 thao tác `add`/`prefix`/`range_sum` ngẫu nhiên (kể cả `delta` âm) đối chiếu với mảng thường; và 3000 phiên kiểm `kth(k)` với mọi `k` hợp lệ, đối chiếu với danh sách phẳng.

## Bài tập chi tiết

### Bài 1 — 315. Count of Smaller Numbers After Self

#### Requirements

Với mỗi `i`, đếm số phần tử `j > i` có `nums[j] < nums[i]`. Trả về mảng cùng độ dài. `1 ≤ n ≤ 10⁵`, `-10⁴ ≤ nums[i] ≤ 10⁴`.

Edge cases: mảng sort tăng (kết quả toàn 0); sort giảm (kết quả là `[n-1, n-2, ..., 0]`); mọi phần tử bằng nhau (toàn 0 — so sánh là **nghiêm ngặt**); số âm; `n == 1`.

Đây thực chất là bài đếm **inversion** cục bộ cho từng vị trí.

#### Complexity mục tiêu

n = 10⁵ → O(n²) là 10¹⁰ phép, TLE. Cần **O(n log n)**.

Miền giá trị `[-10⁴, 10⁴]` chỉ có 2·10⁴+1 giá trị — đủ nhỏ để dùng Fenwick **không cần nén** (chỉ cần cộng offset 10⁴). Nhưng biến thể tổng quát của bài này có giá trị tới 10⁹, nên bản dưới vẫn nén để dùng lại được.

#### Idea

Duyệt **từ phải sang trái** và duy trì một cấu trúc chứa "các phần tử đã gặp ở bên phải".

> **Invariant**: khi xử lý vị trí `i`, cấu trúc chứa đúng multiset `{nums[i+1], ..., nums[n-1]}`.

Câu hỏi cần trả lời là "trong multiset này, bao nhiêu phần tử nhỏ hơn `nums[i]`?" — đó là **rank**, và đó là điều `SortedList.bisect_left` làm trong O(log n).

Không có `SortedList` thì dùng Fenwick đếm: nén giá trị về hạng `[0, m)`, giữ `bit[r]` = số lần giá trị hạng `r` đã được chèn. Khi đó "số phần tử nhỏ hơn `nums[i]`" chính là `bit.prefix(rank[nums[i]])` — tổng số đếm của mọi hạng < `r`.

Sau khi trả lời xong, chèn `nums[i]` vào cấu trúc (`bit.add(r, 1)`) để tái lập invariant cho bước tiếp theo. **Thứ tự truy vấn-trước-chèn-sau là bắt buộc**: nếu chèn trước, phần tử bằng chính nó sẽ… không ảnh hưởng (vì `prefix(r)` không tính hạng `r`), nhưng với biến thể "đếm số phần tử ≤" thì nó sẽ đếm nhầm chính nó.

#### Naive

```python
class SolutionNaive315:
    def countSmaller(self, nums: list[int]) -> list[int]:
        n = len(nums)
        return [sum(1 for j in range(i + 1, n) if nums[j] < nums[i]) for i in range(n)]
```

O(n²). Với n = 10⁵ là 5·10⁹ so sánh Python thuần — hàng giờ. Là oracle hoàn hảo vì nó là định nghĩa của bài toán viết thành code.

Bản trung gian đáng biết — `bisect` trên list, đúng ý tưởng nhưng sai độ phức tạp:

```python
import bisect


class Solution315Bisect:
    def countSmaller(self, nums: list[int]) -> list[int]:
        sorted_tail: list[int] = []
        res: list[int] = []
        for x in reversed(nums):
            i = bisect.bisect_left(sorted_tail, x)
            res.append(i)                      # số phần tử < x đã gặp ở bên phải
            sorted_tail.insert(i, x)           # O(n) memmove
        res.reverse()
        return res
```

O(n²) về mặt lý thuyết (do `insert`), nhưng hằng số cực nhỏ. Đây là bản mà rất nhiều người nộp và **pass** trên LeetCode — nhìn bảng đo ở phần Lý thuyết: ở n = 10⁵ nó chỉ chậm 2.8 lần so với Fenwick. Nhưng ở n = 4·10⁵ đã là 8.6 lần và tiếp tục xấu đi. Pass trên judge không có nghĩa là đúng độ phức tạp.

#### Optimized

```python
class Solution315:
    def countSmaller(self, nums: list[int]) -> list[int]:
        rank = compress(nums)
        bit = Fenwick(len(rank))
        res = [0] * len(nums)
        for i in reversed(range(len(nums))):
            r = rank[nums[i]]
            res[i] = bit.prefix(r)             # đếm hạng < r đã chèn (ở bên phải i)
            bit.add(r, 1)
        return res
```

**O(n log n)** time, O(n) space. Đánh đổi: cần một cấu trúc phụ 25 dòng (Fenwick) cộng bước nén toạ độ, đổi lấy độ phức tạp đúng và khả năng mở rộng sang giá trị tới 10⁹. Với bài này trên LeetCode, đánh đổi đó chưa chắc đáng — nhưng trên Codeforces với n = 10⁶ thì bắt buộc.

Đã stress test 3000 lần trên mảng độ dài 0–10 giá trị `[-6,6]` (ép nhiều trùng lặp), cả bản Fenwick lẫn bản `bisect` khớp với oracle O(n²). `countSmaller([5,2,6,1])` → `[2,1,1,0]`.

#### Bản `SortedList` (minh hoạ — **chưa chạy được, thiếu package**)

```python
from sortedcontainers import SortedList


class Solution315Sorted:
    def countSmaller(self, nums: list[int]) -> list[int]:
        sl = SortedList()
        res = []
        for x in reversed(nums):
            res.append(sl.bisect_left(x))   # O(log n)
            sl.add(x)                       # O(log n) — KHÁC list.insert O(n)
        res.reverse()
        return res
```

So sánh với `Solution315Bisect` ở trên: **chỉ khác đúng một dòng** — `sl.add(x)` thay cho `sorted_tail.insert(i, x)`. Toàn bộ khác biệt về độ phức tạp nằm ở đó. Đây là lý do `sortedcontainers` được ưa chuộng: nó cho phép viết code trực quan như dùng list mà vẫn đạt độ phức tạp đúng.

### Bài 2 — 480. Sliding Window Median

#### Requirements

Cửa sổ độ dài `k` trượt qua `nums`; với mỗi vị trí, trả về median của cửa sổ. `1 ≤ k ≤ n ≤ 10⁵`, giá trị trong phạm vi 32-bit signed. Kết quả là `float`, sai số cho phép 10⁻⁵.

Edge cases: `k == 1` (median là chính phần tử đó); `k` chẵn (trung bình hai phần tử giữa); `k == n` (một kết quả duy nhất); giá trị trùng lặp trong cửa sổ (đây là chỗ lazy deletion dễ sai); giá trị ở biên `2³¹-1` (bản C++ hay tràn khi tính trung bình; Python thì không).

#### Complexity mục tiêu

n = 10⁵, k có thể tới 10⁵ → naive `sorted(window)` mỗi bước là O(n·k log k) ≈ 10¹⁰ — TLE. Cần **O(n log k)**.

Bài này khó hơn 295 (§16) đúng ở một điểm: ngoài **thêm**, còn phải **xoá** phần tử rời khỏi cửa sổ — và heap không hỗ trợ xoá tuỳ ý. Đây là bài tập lớn của lazy deletion.

#### Idea

Vẫn là **two heaps** như bài 295 — `low` là max-heap của nửa nhỏ, `high` là min-heap của nửa lớn — nhưng thêm một tầng: **lazy deletion**.

> **Invariant 1**: mọi phần tử **hợp lệ** trong `low` ≤ mọi phần tử **hợp lệ** trong `high`.
> **Invariant 2**: `low_size == high_size` hoặc `low_size == high_size + 1`, với `low_size`/`high_size` đếm phần tử **hợp lệ** (không tính rác).
> **Invariant 3**: sau mỗi bước, đỉnh của cả hai heap đều là phần tử hợp lệ.

Khi phần tử `old` rời cửa sổ: đánh dấu `pending[old] += 1`, giảm biến đếm kích thước của nửa mà nó thuộc về (xác định bằng cách so với `-low[0]`), và **nếu nó tình cờ đang ở đỉnh** thì `prune` ngay. Nếu nó nằm sâu bên trong heap, cứ để đó — nó sẽ bị dọn khi nổi lên.

Hai thứ tinh tế nhất:

1. **Phải đếm kích thước riêng.** `len(low)` bao gồm cả rác nên không dùng để cân bằng được. Sai lầm này khiến thuật toán vẫn "chạy" nhưng median lệch.
2. **`prune` phải chạy trước mỗi lần đọc/pop đỉnh.** Invariant 3 chỉ đúng nếu ta duy trì nó chủ động.

#### Naive

```python
class SolutionNaive480:
    def medianSlidingWindow(self, nums: list[int], k: int) -> list[float]:
        out: list[float] = []
        for i in range(len(nums) - k + 1):
            w = sorted(nums[i:i + k])
            out.append(float(w[k // 2]) if k % 2 else (w[k // 2 - 1] + w[k // 2]) / 2)
        return out
```

O(n·k log k) — slice O(k) + sort O(k log k) cho mỗi trong `n-k+1` cửa sổ. Với n = k = 5·10⁴ là 4·10⁹ thao tác. Là oracle không thể sai.

#### Optimized

```python
import heapq
from collections import Counter


class Solution480:
    def medianSlidingWindow(self, nums: list[int], k: int) -> list[float]:
        low: list[int] = []      # max-heap (lưu -value) cho nửa nhỏ
        high: list[int] = []     # min-heap cho nửa lớn
        pending: Counter = Counter()   # giá trị đã ra khỏi window nhưng còn trong heap
        low_size = high_size = 0       # kích thước HỢP LỆ (không tính rác)

        def prune(h: list[int], sign: int) -> None:
            # sign = -1 cho low (giá trị lưu là -value), +1 cho high
            while h and pending[sign * h[0]] > 0:
                pending[sign * h[0]] -= 1
                heapq.heappop(h)

        out: list[float] = []
        for i, x in enumerate(nums):
            # --- thêm x ---
            if not low or x <= -low[0]:
                heapq.heappush(low, -x); low_size += 1
            else:
                heapq.heappush(high, x); high_size += 1
            # --- bỏ phần tử rời window ---
            if i >= k:
                old = nums[i - k]
                pending[old] += 1
                if low and old <= -low[0]:
                    low_size -= 1
                    if old == -low[0]:
                        prune(low, -1)
                else:
                    high_size -= 1
                    if high and old == high[0]:
                        prune(high, 1)
            # --- cân bằng: low_size == high_size hoặc high_size + 1 ---
            while low_size > high_size + 1:
                prune(low, -1)
                v = -heapq.heappop(low); low_size -= 1
                heapq.heappush(high, v); high_size += 1
            while low_size < high_size:
                prune(high, 1)
                v = heapq.heappop(high); high_size -= 1
                heapq.heappush(low, -v); low_size += 1
            prune(low, -1); prune(high, 1)
            if i >= k - 1:
                if k % 2:
                    out.append(float(-low[0]))
                else:
                    out.append((-low[0] + high[0]) / 2)
        return out
```

O(n log n) time, O(n) space worst case. Đánh đổi rất đắt: **code dài gấp 8 lần và có ít nhất bốn chỗ có thể sai im lặng** (đếm kích thước, chọn nửa cho `old`, thời điểm `prune`, thứ tự cân bằng). Đổi lại là độ phức tạp đúng.

Nhận xét thẳng thắn: đây là bài mà `SortedList` **thắng áp đảo** — bản `SortedList` dưới đây là 8 dòng và không có chỗ nào để sai. Nếu bạn làm bài này trên LeetCode, dùng `SortedList`. Bản heap + lazy deletion là để dành cho Codeforces, và để hiểu cơ chế mà `asyncio` dùng cho timer đã huỷ (§16).

Chú ý bộ nhớ: `pending` và các heap có thể phình tới O(n) vì rác không được dọn cho tới khi nổi lên. Nếu cần chặn cứng, thêm bước rebuild khi số rác vượt nửa heap.

Đã stress test 4000 lần với `n ∈ [1,12]`, `k ∈ [1,n]`, giá trị `[-6,6]` (miền hẹp để ép trùng lặp — chính là trường hợp lazy deletion dễ sai nhất), đối chiếu với oracle `sorted`. `medianSlidingWindow([1,3,-1,-3,5,3,6,7], 3)` → `[1.0, -1.0, -1.0, 3.0, 5.0, 6.0]`.

#### Bản `SortedList` (minh hoạ — **chưa chạy được, thiếu package**)

```python
from sortedcontainers import SortedList


class Solution480Sorted:
    def medianSlidingWindow(self, nums: list[int], k: int) -> list[float]:
        sl = SortedList(nums[:k])
        out = []
        for i in range(k, len(nums) + 1):
            out.append(float(sl[k // 2]) if k % 2 else (sl[k // 2 - 1] + sl[k // 2]) / 2)
            if i < len(nums):
                sl.remove(nums[i - k])   # O(log n) — list.remove là O(n)
                sl.add(nums[i])          # O(log n)
        return out
```

Hai điều `SortedList` cho mà heap không cho: **`sl[i]` truy cập phần tử thứ i** (heap chỉ cho đỉnh) và **`remove(x)` xoá giá trị tuỳ ý** (heap chỉ cho pop đỉnh). Chính hai thứ đó là toàn bộ phần phức tạp của bản heap.

## Bài luyện thêm

- **327. Count of Range Sum** — đếm số cặp `(i, j)` có `lower <= prefix[j] - prefix[i] <= upper`; với mỗi `prefix[j]`, đếm số `prefix[i]` (i < j) nằm trong `[prefix[j] - upper, prefix[j] - lower]` — Fenwick trên prefix sum đã nén, và **nhớ đưa cả hai giá trị biên truy vấn vào tập nén**; hoặc `SortedList` với `bisect_left`/`bisect_right`; hoặc merge sort đếm inversion.

Theo lời khuyên trong outline, hãy làm **mỗi bài hai lần** — một lần bằng `SortedList` (khi làm trên LeetCode), một lần bằng Fenwick/heap — để quen cả hai hướng.

## Bài toán áp dụng

**Leaderboard động: "top-k đang active" với insert/remove liên tục và cần biết thứ hạng.** Người chơi vào/ra liên tục, điểm số thay đổi, và ta cần trả lời "hạng của người chơi X là bao nhiêu" cùng "ai đang trong top 10". Heap không làm được (không có rank, không có phần tử thứ k); `sorted` lại toàn bộ mỗi lần là O(n log n) mỗi thao tác.

Với Fenwick: nén điểm số về `[0, m)`, `bit[r]` = số người chơi có điểm hạng `r`. Khi đó `rank(X) = tổng_người - bit.prefix(rank_điểm(X) + 1)` và "người thứ k" là `bit.kth(k)`. Đổi điểm là `add(cũ, -1)` rồi `add(mới, +1)`. Mọi thứ O(log n).

Hạn chế của Fenwick ở đây: nó cần **biết trước tập giá trị** để nén. Nếu điểm số là số thực tuỳ ý xuất hiện online, phải dùng `SortedList` hoặc một balanced BST thật.

**Offline query + coordinate compression + Fenwick** là khuôn chuẩn của competitive programming: đọc **toàn bộ** truy vấn trước, gom mọi giá trị (cả trong dữ liệu lẫn trong truy vấn) để nén một lần, sắp xếp truy vấn theo một thứ tự thuận lợi (thường theo `r` tăng dần), rồi quét một lượt cập nhật Fenwick. Kỹ thuật "offline" này biến nhiều bài tưởng cần cấu trúc phức tạp thành một vòng `for` với Fenwick.

## Use case thực tế

**Redis Sorted Set** giải đúng bài toán này ở tầng hạ tầng. `ZADD key score member` chèn/cập nhật trong O(log n), `ZRANGE`/`ZREVRANGE` lấy phần tử thứ k, `ZRANK` cho thứ hạng, `ZRANGEBYSCORE` cho range query. Cấu trúc bên trong là **skip list** cộng một hash map (map member → score). Skip list được chọn thay vì balanced tree vì nó đơn giản hơn để cài đúng, dễ hỗ trợ range query, và thân thiện với concurrency. Nếu bài toán thật của bạn là leaderboard, câu trả lời đúng gần như chắc chắn là Redis chứ không phải tự cài Fenwick.

**B-tree index trong database** là cùng bài toán ở quy mô đĩa: giữ dữ liệu sorted với insert/delete O(log n) và range scan hiệu quả. `SortedList` mô phỏng đúng ý tưởng đó ở tầng ứng dụng — thậm chí cấu trúc list-of-lists của nó rất giống B-tree hai tầng, với cùng lý do: khối liền kề đọc/ghi nhanh hơn con trỏ rải rác.

**Fenwick tree trong hệ thống thật** ít gặp hơn — nó là công cụ của competitive programming và của các bài toán analytics offline (đếm phân vị trên một cửa sổ dữ liệu cố định). Trong production, phân vị động thường được xấp xỉ bằng t-digest hoặc HDR histogram, đổi độ chính xác lấy bộ nhớ hằng số và khả năng gộp giữa nhiều node.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: nếu đang viết code Python thật (không phải thi), `pip install sortedcontainers` và dùng `SortedList` — nó pure Python, không dependency, đã được kiểm chứng kỹ, và nhanh hơn hầu hết bản tự viết. Tự cài Fenwick chỉ khi (a) đang thi trên judge không cho cài package, hoặc (b) bài toán đúng là prefix-sum động và Fenwick là công cụ chính xác nhất. Còn nếu chỉ cần min/max động → `heapq`; chỉ cần một lần sort → `sorted()`.

## Bẫy thường gặp trong Python

**BIT là 1-indexed; trộn hệ chỉ số là bug số một.** `i & -i` với `i = 0` cho 0, và `i += 0` là vòng lặp vô hạn — chương trình **treo** chứ không báo lỗi. Cách phòng: nhận index 0-based ở API công khai và `+1` ngay đầu `add`, như bản ở trên. Và luôn nhớ `prefix(i)` trong bản này nghĩa là "tổng của `i` phần tử đầu", tức `[0, i)` — không phải `[0, i]`.

**Coordinate compression phải bao gồm giá trị truy vấn.** Với bài 327, các giá trị cần nén là `prefix[j]` **và** `prefix[j] - lower` **và** `prefix[j] - upper`. Nén chỉ mảng gốc rồi tra `rank[query_value]` sẽ ném `KeyError`; tệ hơn là nếu bạn "chữa" bằng `bisect` trên mảng đã nén mà không cẩn thận với `bisect_left` vs `bisect_right`, kết quả lệch 1 và không có exception nào.

**`bisect.insort` không phải O(log n).** Đã đo: 10⁵ lần `insort` mất 0.402 s, cùng số lần `Fenwick.add` mất 0.073 s. Và khoảng cách đó giãn theo n — xem bảng ở phần Lý thuyết. Cái nguy hiểm là `insort` trông giống một thao tác O(log n) vì tên nó có chữ "bisect".

**`list.remove(x)` là O(n) và xoá **phần tử đầu tiên bằng x**.** Trong bài 480, nếu dùng list thay `SortedList`, `remove` phải quét tuyến tính rồi dịch mảng. Nó cũng dùng `==` chứ không dùng thứ tự, nên trên list sorted vẫn là O(n) dù về lý thuyết có thể tìm bằng binary search.

**`SortedList.remove(x)` ném `ValueError` nếu không có; `discard(x)` thì không.** Cùng ngữ nghĩa với `set`. Trong sliding window, nếu logic đếm sai và bạn xoá nhầm, `remove` cho bạn một exception rõ ràng — đó là lý do nên dùng `remove` chứ không `discard` khi debug.

**Lazy deletion: đừng dùng `len(heap)` làm kích thước.** Heap chứa cả rác. Phải đếm riêng số phần tử hợp lệ. Đây là bug đã phải xử lý cẩn thận trong bài 480 ở trên, và nó **không gây exception** — chỉ làm median lệch, và chỉ lệch trên một số input.

**`Counter` trong lazy deletion tăng vô hạn nếu quên giảm.** `pending[x] += 1` khi đánh dấu và `pending[x] -= 1` khi thật sự pop — thiếu vế thứ hai thì phần tử `x` hợp lệ trong tương lai sẽ bị prune nhầm. Đó là lý do `prune` giảm `pending` ngay trong vòng lặp.

**`sortedcontainers` không có trên Codeforces.** Kiểm tra môi trường **trước** khi thiết kế lời giải quanh nó. Trên máy đang viết chương này nó cũng không có — nên hai đoạn `SortedList` ở trên là code minh hoạ chưa được thực thi, còn Fenwick, heap + lazy deletion và `bisect` thì đã chạy và stress test đầy đủ.
