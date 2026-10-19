# 17. Sorting

Trong Python bạn gần như không bao giờ tự viết thuật toán sort — `sorted()` là Timsort viết bằng C và thắng mọi bản Python thuần cả chục lần. Nhưng bạn vẫn phải hiểu ba thứ: **tính ổn định** (nó quyết định cách sort nhiều tiêu chí), **giới hạn Ω(n log n)** (nó nói khi nào có thể phá vỡ giới hạn đó), và **cơ chế partition** (nó tái xuất trong Quickselect, §09, và trong mọi bài chia để trị).

## Lý thuyết

### Timsort — vì sao `sorted()` nhanh bất thường trên dữ liệu thật

Timsort là merge sort thích nghi (adaptive): nó quét mảng tìm các **run** (đoạn đã tăng hoặc giảm sẵn), mở rộng run ngắn bằng insertion sort tới độ dài tối thiểu (32–64), rồi merge các run theo một quy tắc giữ cân bằng. Hệ quả:

- Dữ liệu **ngẫu nhiên** → O(n log n).
- Dữ liệu **đã sort hoặc gần sort** → gần **O(n)**, vì chỉ tìm thấy một (hoặc vài) run khổng lồ.

Đo trên máy này với 2 000 000 số nguyên:

| Input | `sorted()` |
|---|---|
| ngẫu nhiên | 0.242 s |
| đã sort sẵn | **0.039 s** |
| gần sort (1000 phần tử bị xáo) | **0.047 s** |

Nhanh hơn 6 lần trên dữ liệu đã sort. Đây không phải chi tiết học thuật: log file, bản ghi theo timestamp, dữ liệu đã sort theo một tiêu chí khác — tất cả đều "gần sort", và Timsort được thiết kế đúng cho chúng.

### Tính ổn định (stable) — hệ quả thực tế

Một thuật toán sort là **ổn định** nếu các phần tử **so sánh bằng nhau** giữ nguyên thứ tự tương đối như trong input.

Minh chứng đã chạy — sort các bản ghi mà `__lt__` **chỉ so key**, tag chỉ để quan sát:

```
input                : [1a, 0b, 1c, 0d, 1e, 0f]
merge_sort  (ổn định): [0b, 0d, 0f, 1a, 1c, 1e]     <- b,d,f giữ thứ tự; a,c,e giữ thứ tự
heap_sort            : [0f, 0b, 0d, 1c, 1e, 1a]     <- loạn
quick_sort           : [0b, 0d, 0f, 1a, 1e, 1c]     <- loạn (e trước c)
sorted() (Timsort)   : [0b, 0d, 0f, 1a, 1c, 1e]     <- ổn định
```

Ổn định cho ta **sort nhiều tiêu chí bằng cách sort nhiều lần**, từ tiêu chí **phụ tới tiêu chí chính**:

```python
import operator
data = [("bob", 2), ("alice", 1), ("carol", 2), ("dave", 1)]
d = sorted(data, key=operator.itemgetter(0))                    # phụ: tên, tăng
d = sorted(d, key=operator.itemgetter(1), reverse=True)         # chính: điểm, giảm
# [('bob', 2), ('carol', 2), ('alice', 1), ('dave', 1)]
```

Kỹ thuật này **bắt buộc** khi các tiêu chí có chiều sắp xếp khác nhau và khoá không phải số (không thể phủ định một chuỗi để đảo chiều). Với khoá số thì gộp một lần bằng tuple gọn hơn: `key=lambda t: (-t[1], t[0])`.

Chi tiết quan trọng: **`reverse=True` KHÔNG đảo thứ tự các phần tử bằng nhau.** Đã đo:

```python
data = [("bob", 2), ("alice", 1), ("carol", 2), ("dave", 1)]
sorted(data, key=lambda t: t[1], reverse=True)
# [('bob', 2), ('carol', 2), ('alice', 1), ('dave', 1)]   -- bob vẫn trước carol
```

CPython cài `reverse=True` bằng cách đảo mảng, sort, rồi đảo lại — chính là để giữ ổn định. Nếu nó chỉ đơn giản đảo phép so sánh thì tie sẽ bị lật.

### Giới hạn Ω(n log n) và cách phá vỡ nó

Bất kỳ thuật toán sort nào **chỉ dùng phép so sánh** đều cần Ω(n log n) phép so sánh trong trường hợp tệ nhất. Chứng minh bằng cây quyết định: có `n!` hoán vị đầu ra khả dĩ; mỗi phép so sánh cho 1 bit thông tin, nên cây quyết định phải có ≥ `n!` lá và do đó độ sâu ≥ `log₂(n!) = Θ(n log n)` (công thức Stirling).

Chú ý câu chữ: **chỉ dùng phép so sánh**. Counting/radix/bucket sort không so sánh phần tử với nhau — chúng dùng **giá trị** của khoá làm địa chỉ. Đó là cách chúng lách qua giới hạn, và đó cũng là lý do chúng cần điều kiện kèm theo:

| Thuật toán | Điều kiện áp dụng | Time | Space | Ổn định |
|---|---|---|---|---|
| Counting sort | khoá nguyên trong `[lo, hi]`, `k = hi-lo` nhỏ | O(n + k) | O(k) | có¹ |
| Radix sort (LSD) | khoá nguyên/chuỗi độ dài cố định `d` | O(d·(n + b)) | O(n + b) | **bắt buộc** |
| Bucket sort | khoá phân bố **đều** trên một khoảng | O(n) trung bình | O(n) | tuỳ cài đặt |

¹ nếu cài bằng prefix sum của mảng đếm; bản đơn giản "in lại theo số đếm" thì mất thông tin gốc nên khái niệm ổn định không áp dụng.

Radix sort có một ràng buộc tinh tế: **mỗi lượt phải ổn định**, nếu không kết quả sắp xếp của các chữ số trước bị phá. Đây là ví dụ hiếm hoi mà tính ổn định là điều kiện đúng đắn chứ không phải tiện lợi.

### Bảng so sánh ba thuật toán tự cài

| | Merge sort | Quick sort | Heap sort |
|---|---|---|---|
| Trung bình | O(n log n) | O(n log n) | O(n log n) |
| Tệ nhất | **O(n log n)** | O(n²)² | **O(n log n)** |
| Bộ nhớ phụ | O(n) | O(log n) stack | **O(1)** |
| Ổn định | **có** | không | không |
| Hằng số thực tế | trung bình | **nhỏ nhất** | lớn (cache-unfriendly) |
| Dùng ở đâu | external sort, Timsort | `sort()` của C/C++, Quickselect | nơi cần đảm bảo worst-case + O(1) bộ nhớ |

² Với pivot ngẫu nhiên, xác suất chạm O(n²) là cực nhỏ và **không phụ thuộc vào input** — kẻ tấn công không thể xây test case xấu cho bạn. Với pivot cố định (phần tử đầu/cuối), mảng đã sort là worst case, và đó là bug đã giết nhiều lời giải trên judge.

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/sorting/merge_sort.py`

```python
def merge_sort(a: list) -> list:
    """O(n log n) mọi trường hợp, ỔN ĐỊNH, cần O(n) bộ nhớ phụ.

    Invariant của merge: mỗi bước lấy phần tử nhỏ nhất còn lại trong hai nửa;
    khi bằng nhau LẤY TỪ NỬA TRÁI (dấu <=) -> giữ tính ổn định.
    """
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    out: list = []
    i = j = 0
    while i < len(left) and j < len(right):
        if right[j] < left[i]:      # dùng < trên right, KHÔNG phải <= trên left
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
```

Chi tiết quyết định tính ổn định nằm ở **một dấu**: điều kiện là `right[j] < left[i]` chứ không phải `left[i] <= right[j]`. Cả hai cho kết quả sắp xếp giống nhau, nhưng chỉ cách viết trên mới đảm bảo khi bằng nhau ta lấy từ nửa trái. Ngoài ra nó chỉ cần `__lt__` được định nghĩa — đúng hợp đồng của Python (`sorted` cũng chỉ dùng `<`).

Đề xuất đường dẫn: `cores/python/sorting/quick_sort.py`

```python
import random


def quick_sort(a: list) -> None:
    """In-place, trung bình O(n log n), KHÔNG ổn định.

    Dùng 3-way partition (Dutch national flag) + pivot ngẫu nhiên:
      - pivot ngẫu nhiên -> worst case O(n^2) chỉ xảy ra với xác suất cực nhỏ,
        không phụ thuộc vào input của kẻ tấn công/của judge;
      - 3-way -> mảng toàn phần tử bằng nhau chạy O(n) thay vì O(n^2).
    """
    _qs(a, 0, len(a) - 1)


def _qs(a: list, lo: int, hi: int) -> None:
    while lo < hi:
        pivot = a[random.randint(lo, hi)]
        lt, i, gt = lo, lo, hi
        # Invariant: a[lo..lt) < pivot, a[lt..i) == pivot, a[gt..hi] > pivot
        while i <= gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1; i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1                 # KHÔNG tăng i: phần tử vừa đổi về chưa xét
            else:
                i += 1
        # đệ quy vào nửa NHỎ hơn, lặp trên nửa lớn -> stack O(log n)
        if lt - lo < hi - gt:
            _qs(a, lo, lt - 1)
            lo = gt + 1
        else:
            _qs(a, gt + 1, hi)
            hi = lt - 1
```

Ba kỹ thuật gộp trong 20 dòng, mỗi cái sửa một điểm yếu cụ thể:

1. **Pivot ngẫu nhiên** — chống input độc hại (mảng đã sort với pivot cố định là O(n²)).
2. **3-way partition** (chính là Dutch National Flag của §09) — mảng toàn phần tử bằng nhau chạy O(n) vì mọi phần tử rơi vào vùng giữa và không cần đệ quy tiếp.
3. **Tail-call elimination thủ công**: chỉ đệ quy vào nửa **nhỏ hơn**, dùng vòng `while` cho nửa lớn. Điều này chặn cứng độ sâu đệ quy ở O(log n) — không có nó, một chuỗi phân hoạch xấu có thể gây `RecursionError` (§24).

Kiểm chứng đã chạy trên 200 000 phần tử cho ba input độc hại kinh điển:

```
quick_sort 200k phần tử (đã sort):      0.196s
quick_sort 200k phần tử (sort ngược):   0.189s
quick_sort 200k phần tử (toàn giống nhau): 0.004s
```

Không cái nào suy biến. Con số 0.004 s cho mảng toàn phần tử bằng nhau là bằng chứng trực tiếp của 3-way partition: nó nhận ra cả mảng bằng pivot và kết thúc sau một lượt.

Đề xuất đường dẫn: `cores/python/sorting/heap_sort.py`

```python
def heap_sort(a: list) -> None:
    """In-place, O(n log n) mọi trường hợp, O(1) bộ nhớ phụ, KHÔNG ổn định.

    Dùng MAX-heap: sau heapify, liên tục đổi gốc (max) về cuối rồi thu nhỏ heap.
    Invariant: a[n-k..n) đã là k phần tử lớn nhất, đã ở đúng vị trí cuối cùng.
    """
    n = len(a)
    for i in reversed(range(n // 2)):
        _sift_down_max(a, i, n)
    for end in reversed(range(1, n)):
        a[0], a[end] = a[end], a[0]
        _sift_down_max(a, 0, end)


def _sift_down_max(a: list, i: int, size: int) -> None:
    item = a[i]
    while True:
        child = 2 * i + 1
        if child >= size:
            break
        if child + 1 < size and a[child + 1] > a[child]:
            child += 1
        if item >= a[child]:
            break
        a[i] = a[child]
        i = child
    a[i] = item
```

Điểm cần hiểu: dùng **max**-heap để sort **tăng dần**. Vì heap được lưu trong chính mảng đầu vào, đỉnh (max) nằm ở index 0; đổi nó về cuối là đưa phần tử lớn nhất về đúng chỗ, rồi thu nhỏ vùng heap đi 1. Sau `n-1` bước, mảng sorted tăng dần và không dùng một byte bộ nhớ phụ nào.

Đề xuất đường dẫn: `cores/python/sorting/linear_sorts.py`

```python
def counting_sort(a: list[int], lo: int, hi: int) -> list[int]:
    """O(n + k) với k = hi - lo + 1. Chỉ dùng khi miền giá trị NHỎ và biết trước."""
    counts = [0] * (hi - lo + 1)
    for x in a:
        counts[x - lo] += 1
    out: list[int] = []
    for value, c in enumerate(counts):
        out.extend([value + lo] * c)
    return out


def radix_sort(a: list[int]) -> list[int]:
    """LSD radix sort cơ số 256 cho số nguyên không âm. O(d * (n + 256)).

    Ổn định ở từng lượt là ĐIỀU KIỆN CẦN: nếu một lượt không ổn định thì kết quả
    của các chữ số đã sắp trước đó bị phá.
    """
    if not a:
        return []
    out = list(a)
    max_v = max(out)
    shift = 0
    while max_v >> shift:
        buckets: list[list[int]] = [[] for _ in range(256)]
        for x in out:
            buckets[(x >> shift) & 255].append(x)
        out = [x for b in buckets for x in b]
        shift += 8
    return out
```

Radix cơ số 256 (8 bit mỗi lượt) là điểm cân bằng tốt: số nguyên 32 bit cần 4 lượt, 64 bit cần 8 lượt, và 256 bucket không tốn nhiều bộ nhớ. Cơ số nhỏ hơn (base 10) thì nhiều lượt hơn; cơ số lớn hơn thì mảng bucket phình.

Đã stress test toàn bộ: 3000 lần cho merge/quick/heap trên mảng ngẫu nhiên độ dài 0–15 giá trị `[-9,9]`, 2000 lần cho counting/radix, cộng một lần radix trên 1000 số tới 10⁹.

## Bài tập chi tiết

### Bài 1 — 912. Sort an Array

#### Requirements

Sắp xếp mảng tăng dần. `1 ≤ n ≤ 5·10⁴`, `-5·10⁴ ≤ nums[i] ≤ 5·10⁴`. Đề yêu cầu tường minh: **O(n log n)** và **không dùng hàm sort có sẵn**.

Edge cases: `n == 1`; mọi phần tử bằng nhau (worst case của quicksort 2-way); mảng đã sort tăng (worst case của quicksort pivot cố định); mảng sort giảm; số âm; nhiều giá trị trùng lặp.

#### Complexity mục tiêu

n = 5·10⁴ → O(n²) là 2.5·10⁹ phép, TLE chắc chắn trong Python. Cần O(n log n) ≈ 8·10⁵ phép so sánh.

Chú ý miền giá trị chỉ có 10⁵ + 1 giá trị phân biệt — **counting sort cho O(n + k)** và thực tế là lời giải nhanh nhất cho bài này. Nhưng đề tồn tại để luyện comparison sort nên bản dưới dùng quicksort.

#### Idea

Chia để trị với **partition**: chọn một pivot, đưa mọi phần tử nhỏ hơn sang trái, lớn hơn sang phải, bằng vào giữa. Sau partition, pivot (và cả vùng bằng pivot) đã ở **đúng vị trí cuối cùng** — không bao giờ phải chạm lại.

> **Invariant của vòng partition**: `a[lo..lt) < pivot`, `a[lt..i) == pivot`, `a[gt..hi] > pivot`, và `a[i..gt]` là vùng chưa xét.

Ba nhánh xử lý phần tử `a[i]`: nhỏ hơn → đổi về vùng trái và tiến cả `lt` lẫn `i`; bằng → chỉ tiến `i`; lớn hơn → đổi về vùng phải, **giảm `gt` nhưng không tăng `i`** (phần tử vừa đổi từ bên phải về chưa được xét). Quên chi tiết cuối cùng này là bug kinh điển của Dutch flag.

Kết thúc khi `i > gt` → vùng chưa xét rỗng → invariant nói cả ba vùng đã đúng vị trí tương đối.

Vì sao đúng tổng thể: mỗi lần partition, vùng bằng pivot chốt vĩnh viễn. Đệ quy vào hai vùng còn lại, mỗi vùng nhỏ hơn hẳn. Với pivot ngẫu nhiên, kích thước vùng con kỳ vọng là ~3n/4, cho độ sâu kỳ vọng O(log n).

#### Naive

```python
class SolutionNaive912:
    def sortArray(self, nums: list[int]) -> list[int]:
        a = nums[:]
        for i in range(1, len(a)):          # insertion sort
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key
        return a
```

O(n²) worst case, O(n) best case (mảng đã sort). Insertion sort là lựa chọn tốt cho oracle vì nó **ổn định**, **in-place**, và ngắn đến mức khó viết sai. Với n = 5·10⁴ thì 1.25·10⁹ bước — vài phút. (Timsort dùng chính insertion sort cho các run ngắn, vì với n < 64 hằng số của nó nhỏ hơn merge sort.)

#### Optimized

```python
class Solution912:
    def sortArray(self, nums: list[int]) -> list[int]:
        a = nums[:]
        quick_sort(a)                       # 3-way + pivot ngẫu nhiên
        return a
```

O(n log n) kỳ vọng, O(log n) bộ nhớ stack. Đánh đổi so với merge sort: mất tính ổn định và mất đảm bảo worst-case, đổi lấy bộ nhớ O(log n) thay vì O(n) và hằng số nhỏ hơn. Với mảng số nguyên (không có "thứ tự gốc" cần bảo toàn) thì mất ổn định là vô hại — đó là lý do quicksort thắng ở đây và merge sort thắng khi sort bản ghi.

Đã stress test 2000 lần đối chiếu insertion sort, quicksort và `sorted()` trên cùng dữ liệu, cộng ba input độc hại 200 000 phần tử (đã sort / sort ngược / toàn giống nhau) — không cái nào suy biến.

### Bài 2 — 179. Largest Number

#### Requirements

Cho mảng số nguyên không âm, ghép chúng lại thành **số lớn nhất có thể** và trả về dưới dạng **chuỗi** (vì kết quả có thể vượt mọi kiểu số cố định — dù Python không có vấn đề này, đề vẫn yêu cầu chuỗi). `1 ≤ n ≤ 100`, `0 ≤ nums[i] ≤ 10⁹`.

Edge cases: **`[0, 0]` phải trả `"0"` chứ không phải `"00"`** — đây là edge case duy nhất mà ai cũng quên; các số là tiền tố của nhau (`[3, 30]` → `"330"`, vì `"330" > "303"`); một phần tử duy nhất; số 0 lẫn trong các số khác (`[0, 1]` → `"10"`).

#### Complexity mục tiêu

n ≤ 100 nên độ phức tạp không phải rào cản (thậm chí O(n³) cũng pass). Cái khó là **định nghĩa đúng thứ tự**. Brute-force duyệt `n!` hoán vị bùng nổ ngay từ n = 12, nên nó chỉ dùng làm oracle. Mục tiêu thực tế: O(n log n · L) với L là độ dài chuỗi.

#### Idea

Thứ tự cần dùng **không phải** thứ tự số học, cũng **không phải** thứ tự từ điển. Với `[3, 30]`: thứ tự số cho `30 > 3`; thứ tự từ điển cho `"3" > "30"`. Cái ta cần là: `x` đứng trước `y` khi **`x+y > y+x`** (nối chuỗi).

Vì sao định nghĩa này đúng? Hai lý do phải có cả hai:

1. **Nó là total order hợp lệ** — đặc biệt là **bắc cầu**: nếu `xy > yx` và `yz > zy` thì `xz > zx`. (Chứng minh đầy đủ khá dài; trực giác: quan hệ này tương đương với so sánh `x` và `y` khi lặp vô hạn — `xxx… > yyy…` — và so sánh chuỗi vô hạn thì hiển nhiên bắc cầu.) Không có tính bắc cầu thì `sorted` cho ra kết quả vô nghĩa, không phải chỉ là "chưa tối ưu".
2. **Đổi chỗ hai phần tử kề nhau vi phạm thứ tự này luôn cải thiện kết quả** (exchange argument) — nên nghiệm tối ưu chính là dãy đã sort theo nó. Vì thứ tự này là total order, sắp theo nó là xác định duy nhất.

Python không cho so sánh theo cặp trực tiếp trong `sorted`, chỉ cho `key=`. Ở đây khoá không biểu diễn được bằng một giá trị đơn (nó phụ thuộc **cặp**), nên phải dùng `functools.cmp_to_key`.

> **Invariant sau khi sort**: với mọi cặp kề nhau `s[i], s[i+1]`, ta có `s[i] + s[i+1] >= s[i+1] + s[i]`.

#### Naive

```python
from itertools import permutations


class SolutionNaive179:
    def largestNumber(self, nums: list[int]) -> str:
        best = max("".join(p) for p in permutations(map(str, nums)))
        return "0" if best[0] == "0" else best
```

O(n! · n·L) — bùng nổ. Với n = 10 đã là 3.6 triệu hoán vị; n = 100 thì vô nghĩa. Nhưng nó là oracle **hoàn hảo**: nó thử đúng mọi cách ghép, nên nó đúng theo định nghĩa, và dùng nó để kiểm chứng rằng comparator ở trên thật sự cho ra nghiệm tối ưu chứ không chỉ "trông hợp lý".

#### Optimized

```python
from functools import cmp_to_key


class Solution179:
    def largestNumber(self, nums: list[int]) -> str:
        def cmp(x: str, y: str) -> int:
            if x + y > y + x:
                return -1               # x đứng trước y
            if x + y < y + x:
                return 1
            return 0

        s = sorted(map(str, nums), key=cmp_to_key(cmp))
        out = "".join(s)
        return "0" if out[0] == "0" else out
```

O(n log n) phép so sánh, mỗi phép O(L) → O(n·L·log n). Đánh đổi: `cmp_to_key` **chậm hơn `key=` thật** vì nó bọc mỗi phần tử trong một object Python có `__lt__`, nên mỗi phép so sánh là một lời gọi hàm Python thay vì so sánh nội tại trong C. Với n ≤ 100 thì không đáng kể; với n = 10⁶ thì đó là khác biệt lớn — lúc đó nên tìm một khoá thật (ở bài này có mẹo: `key=lambda x: x * (max_len // len(x) + 1)`, lặp chuỗi cho đủ dài rồi so từ điển).

Dòng `return "0" if out[0] == "0" else out` xử lý trường hợp `[0, 0, 0]`: sau khi sort, nếu ký tự đầu là `'0'` thì mọi số đều là 0.

Đã stress test 1500 lần với 1–6 số trong `[0, 99]` (miền hẹp để ép nhiều tiền tố chung và nhiều số 0), đối chiếu với brute-force hoán vị. `largestNumber([3,30,34,5,9])` → `"9534330"`; `largestNumber([0,0])` → `"0"`.

### Bài 3 — 164. Maximum Gap

#### Requirements

Cho mảng chưa sort, tìm **hiệu lớn nhất giữa hai phần tử liền kề trong dạng đã sort**. Trả 0 nếu mảng có ít hơn 2 phần tử. `1 ≤ n ≤ 10⁵`, `0 ≤ nums[i] ≤ 10⁹`. Đề yêu cầu **O(n) time và O(n) space**.

Edge cases: `n == 1` (trả 0); `n == 2`; mọi phần tử bằng nhau (trả 0 — và đây là chỗ chia cho 0 nếu không cẩn thận); phần tử trùng lặp; giá trị 0 và 10⁹ cùng lúc (miền giá trị cực rộng, loại counting sort).

#### Complexity mục tiêu

`sorted()` cho O(n log n) và **pass trên LeetCode**. Nhưng đề nói O(n), và ở đây O(n) là khả thi thật. Miền giá trị `[0, 10⁹]` loại counting sort (cần 10⁹ ô). Radix sort cho O(n) — hợp lệ. Nhưng có lời giải đẹp hơn không cần sort chút nào.

#### Idea

Đây là bài **pigeonhole principle** trá hình.

Đặt `lo = min`, `hi = max`. Có `n` phần tử nên có `n-1` khoảng trống, tổng chiều dài của chúng là `hi - lo`. Theo nguyên lý chuồng bồ câu, khoảng trống lớn nhất **ít nhất** là `⌈(hi-lo)/(n-1)⌉.

Bây giờ chia `[lo, hi]` thành các bucket rộng đúng `bucket_size = ⌈(hi-lo)/(n-1)⌉`.

> **Invariant then chốt**: hai phần tử nằm trong **cùng một bucket** cách nhau tối đa `bucket_size - 1 < bucket_size ≤ max_gap`. Vậy chúng **không bao giờ** tạo ra max gap.

Hệ quả: max gap luôn xuất hiện **giữa hai bucket** — cụ thể là giữa `max` của một bucket không rỗng và `min` của bucket không rỗng tiếp theo. Nên ta chỉ cần lưu `min` và `max` của mỗi bucket, không cần sort gì bên trong bucket cả.

Duyệt bucket từ trái sang phải, bỏ qua bucket rỗng, và mỗi lần lấy `bmin[b] - prev` với `prev` là max của bucket không rỗng gần nhất bên trái.

#### Naive

```python
class SolutionNaive164:
    def maximumGap(self, nums: list[int]) -> int:
        if len(nums) < 2:
            return 0
        a = sorted(nums)
        return max(a[i + 1] - a[i] for i in range(len(a) - 1))
```

O(n log n) time, O(n) space. Nó không hề chậm trong thực tế (Timsort là C), nhưng nó vi phạm yêu cầu O(n) của đề, và quan trọng hơn: nó làm **nhiều việc hơn cần thiết** — sắp xếp hoàn toàn n phần tử để rồi chỉ dùng n-1 hiệu số liền kề.

#### Optimized

```python
class Solution164:
    def maximumGap(self, nums: list[int]) -> int:
        n = len(nums)
        if n < 2:
            return 0
        lo, hi = min(nums), max(nums)
        if lo == hi:
            return 0
        # Pigeonhole: n-1 khoảng trống, khoảng lớn nhất >= ceil((hi-lo)/(n-1)).
        # Chọn bucket_size đúng bằng cận đó -> hai phần tử trong CÙNG bucket
        # không bao giờ tạo ra max gap, chỉ cần xét gap GIỮA các bucket.
        bucket_size = max(1, -(-(hi - lo) // (n - 1)))
        n_buckets = (hi - lo) // bucket_size + 1
        bmin: list[int | None] = [None] * n_buckets
        bmax: list[int | None] = [None] * n_buckets
        for x in nums:
            b = (x - lo) // bucket_size
            bmin[b] = x if bmin[b] is None else min(bmin[b], x)
            bmax[b] = x if bmax[b] is None else max(bmax[b], x)
        best = 0
        prev = lo
        for b in range(n_buckets):
            if bmin[b] is None:
                continue
            best = max(best, bmin[b] - prev)
            prev = bmax[b]
        return best
```

**O(n)** time, O(n) space. Đánh đổi: code dài gấp 5 lần bản `sorted()`, có ba edge case phải xử lý riêng (`n < 2`, `lo == hi`, `max(1, ...)` chống bucket_size = 0), và tính đúng đắn dựa vào một lập luận pigeonhole mà nếu không viết ra thì không ai đọc code hiểu được. Đổi lại là O(n) thật và một kỹ thuật tổng quát (bucket theo miền giá trị) áp dụng được ở nơi khác.

Chi tiết Python: `-(-(hi - lo) // (n - 1))` là thành ngữ tính `ceil` bằng số nguyên, lợi dụng việc `//` làm tròn xuống. Viết `math.ceil((hi-lo)/(n-1))` thì phải qua `float` — mất chính xác khi giá trị lớn.

Đã stress test 3000 lần trên miền nhỏ `[0,40]` (ép trùng lặp và bucket rỗng) cộng 300 lần trên miền `[0, 10⁹]` với 2–60 phần tử, đối chiếu với bản `sorted`. `maximumGap([3,6,9,1])` → `3`; `maximumGap([10])` → `0`.

## Bài luyện thêm

- **56. Merge Intervals** — sort theo điểm bắt đầu rồi quét tuyến tính; invariant: mảng kết quả luôn giữ các interval rời nhau và đã sort, nên chỉ cần so với interval cuối cùng. Đã đi ở §10.
- **75. Sort Colors** — counting sort 3 giá trị, hoặc Dutch National Flag một lượt O(n) O(1) space; chính là vòng partition ba nhánh trong `quick_sort` ở trên. Đã đi ở §09.

## Bài toán áp dụng

**Sort log giữ thứ tự gốc khi timestamp trùng.** Log từ nhiều nguồn gộp lại, nhiều dòng cùng mili-giây. `sorted(lines, key=lambda l: l.timestamp)` giữ nguyên thứ tự đọc file cho các dòng cùng timestamp — nhờ Timsort ổn định. Nếu dùng một thuật toán không ổn định, thứ tự các dòng cùng thời điểm bị xáo ngẫu nhiên **và khác nhau giữa các lần chạy**, làm việc so sánh output trở nên bất khả thi. Đây là lý do thực tế nhất để quan tâm tới tính ổn định.

**External sort — sort dữ liệu lớn hơn RAM.** Thuật toán hai pha:

1. **Pha chia (run generation)**: đọc từng khối vừa RAM, sort trong bộ nhớ (`list.sort()`), ghi ra file tạm. Kết quả là `k` file, mỗi file đã sort.
2. **Pha trộn (merge)**: mở cả `k` file cùng lúc, dùng một heap kích thước `k` để luôn biết dòng nhỏ nhất trong số các dòng đầu hiện tại, ghi ra output.

Trong Python, pha 2 là **một dòng** nhờ `heapq.merge`:

```text
import heapq
with open("out.txt", "w") as fout:
    files = [open(p) for p in run_paths]
    fout.writelines(heapq.merge(*files, key=extract_key))
```

`heapq.merge` trả về iterator và chỉ giữ `k` phần tử trong bộ nhớ — đúng thứ ta cần. Đây là cùng thuật toán merge của merge sort, chỉ khác là "hai nửa" nằm trên đĩa và có `k` nửa thay vì 2.

## Use case thực tế

**`ORDER BY` trong SQL engine.** Khi kết quả vừa `work_mem`, PostgreSQL sort trong bộ nhớ (quicksort); khi không vừa, nó chuyển sang **external merge sort** đúng như mô tả trên, ghi run ra `pgsql_tmp`. `EXPLAIN ANALYZE` sẽ hiện `Sort Method: quicksort` hay `external merge Disk: 12345kB` — con số đó là tín hiệu trực tiếp rằng bạn cần tăng `work_mem` hoặc thêm index (index đã sort sẵn thì `ORDER BY` là miễn phí).

**Timsort ở khắp nơi.** Được Tim Peters viết cho Python năm 2002, sau đó Java 7 dùng cho `Arrays.sort` trên object, Android, V8 (từ 2018), Swift, Rust (`slice::sort`). Nó thắng vì dữ liệu thật hiếm khi ngẫu nhiên. Có một chi tiết vui: năm 2015, một nhóm dùng formal verification tìm ra bug tràn stack trong Timsort của Java/Android — thuật toán "đã dùng 13 năm" vẫn có lỗi ở invariant merge.

**Radix sort trong xử lý chuỗi.** Xây dựng suffix array (nền của full-text search, bioinformatics) dùng radix sort để đạt O(n log n) thay vì O(n log²n). Sort địa chỉ IP (4 byte, 4 lượt radix) và sort khoá cố định độ dài trong cột database cũng vậy.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: gần như tuyệt đối. Đo được `merge_sort` tự viết trên 200 000 phần tử mất **0.203 s** trong khi `sorted()` mất **0.0174 s** — chậm **12 lần**. Tự cài sort trong production Python chỉ đúng khi bạn cần một tính chất mà `sorted()` không có: sort trên đĩa (dùng `heapq.merge`), sort tăng dần theo stream, hoặc counting/radix trên miền giá trị đặc biệt hẹp. Ngoài ra: `list.sort()` khi có sẵn list và không cần bản gốc (in-place, tiết kiệm O(n) bộ nhớ), `sorted()` cho mọi iterable khác, `operator.itemgetter`/`attrgetter` thay `lambda` (nhanh hơn vì là C).

## Bẫy thường gặp trong Python

**`x = x.sort()` gán `None`.** `list.sort()` sort **in-place** và trả về `None`; `sorted()` trả về list mới.

```python
x = [3, 1, 2]
x.sort()        # -> None
x               # [1, 2, 3]
```

Bug này im lặng cho tới khi bạn dùng biến đó và ăn `TypeError: 'NoneType' object is not iterable`. Cùng họ với `list.reverse()`, `list.append()`, `dict.update()` — mọi hàm sửa tại chỗ trong Python đều trả `None` một cách có chủ ý, để bạn không nhầm chúng với hàm thuần.

**`reverse=True` không đảo tie.** Đã đo ở phần Lý thuyết. Nếu bạn *muốn* đảo cả tie thì phải `sorted(reversed(data), key=...)` hoặc sort với khoá phủ định. Người ta thường giả định sai điều ngược lại.

**`key=` gọi hàm đúng n lần, `cmp_to_key` gọi O(n log n) lần.** `sorted(a, key=f)` tính `f(x)` một lần cho mỗi phần tử rồi sort theo giá trị đã tính (decorate-sort-undecorate). Nên `key` đắt vẫn ổn. Ngược lại, `cmp_to_key(cmp)` gọi `cmp` mỗi phép so sánh — nếu `cmp` đắt thì tổng chi phí là O(n log n × chi phí cmp). Luôn ưu tiên tìm một `key` thật; chỉ dùng `cmp_to_key` khi thứ tự phụ thuộc **cặp** (như bài 179).

**Sort list các tuple/list có thể ném `TypeError` ở phần tử thứ hai.** Cùng bẫy với heap ở §16: `sorted([(1, obj_a), (1, obj_b)])` rơi xuống so sánh `obj_a < obj_b`. Chèn một khoá tie-break, hoặc dùng `key=operator.itemgetter(0)` để chỉ so phần tử đầu.

**Sort trộn kiểu ném `TypeError` từ Python 3.** `sorted([1, "a"])` báo `'<' not supported between instances of 'str' and 'int'`. Trong Python 2 nó chạy được (theo một thứ tự tuỳ tiện), nên code cũ port sang sẽ vỡ. Với `None` lẫn trong dữ liệu: `sorted(a, key=lambda x: (x is None, x))` đẩy `None` về cuối.

**Sort với `key` trả về `float('nan')` cho kết quả vô nghĩa.** `nan` không so sánh được với gì (mọi so sánh trả `False`, kể cả `nan == nan`), nên Timsort đưa ra một hoán vị tuỳ tiện mà không báo lỗi. Lọc `nan` trước bằng `math.isnan`.

**Quicksort với pivot cố định suy biến trên mảng đã sort.** Nếu bạn viết `pivot = a[lo]` thay vì pivot ngẫu nhiên, một mảng đã sort cho phân hoạch `1 : n-1` mỗi lần → O(n²) **và** độ sâu đệ quy O(n) → `RecursionError` trước cả khi kịp TLE. Judge rất hay có test "mảng đã sort".

**Không đệ quy vào nửa nhỏ hơn → tràn stack.** Ngay cả với pivot ngẫu nhiên, không có mẹo "đệ quy nửa nhỏ, lặp nửa lớn" thì độ sâu là O(n) trong trường hợp xấu. Với n = 5·10⁴ và `sys.getrecursionlimit()` mặc định 1000, đó là crash chứ không phải chậm.
