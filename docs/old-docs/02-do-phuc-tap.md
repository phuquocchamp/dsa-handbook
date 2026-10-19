# 02. Độ phức tạp: Big-O, amortized, và suy ngược từ constraints

Độ phức tạp không phải thứ để phân tích *sau khi* viết xong code — nó là thứ quyết định bạn được phép viết code nào. Section này chốt ba việc: phân biệt cho đúng O/Θ/Ω, hiểu amortized analysis qua chính `list.append` và `dict` của CPython, và thuộc lòng bảng suy ngược từ ràng buộc n ra thuật toán cần dùng.

> Mọi con số đo trong chương này chạy trên `Python 3.12.12`, máy local darwin/arm64. Số tuyệt đối sẽ khác trên máy bạn; **tỉ lệ giữa các dòng** mới là thứ đáng đọc.

## Lý thuyết

### O, Θ, Ω — và vì sao ba ký hiệu này hay bị dùng lẫn

Cả ba đều nói về hành vi của hàm chi phí `T(n)` khi `n → ∞`, bỏ qua hằng số:

| Ký hiệu | Nghĩa | Câu nói tương đương |
| --- | --- | --- |
| `T(n) = O(f(n))` | chặn **trên**: `T(n) ≤ c·f(n)` với n đủ lớn | "không tệ hơn f(n)" |
| `T(n) = Ω(f(n))` | chặn **dưới**: `T(n) ≥ c·f(n)` | "ít nhất cũng tốn f(n)" |
| `T(n) = Θ(f(n))` | chặn **chặt**: vừa O vừa Ω | "đúng bằng f(n) về bậc" |

Về mặt kỹ thuật, nói "binary search là `O(n²)`" **không sai** — nó đúng là bị chặn trên bởi n². Chỉ là vô dụng. Trong thực tế mọi người viết `O` nhưng ngụ ý `Θ`, và điều đó chấp nhận được miễn là bạn biết mình đang làm vậy.

Chỗ thực sự gây nhầm là **worst-case vs average-case**, một trục hoàn toàn khác với O/Θ/Ω. Quicksort là `Θ(n log n)` average nhưng `Θ(n²)` worst. Tra `dict` là `O(1)` average nhưng `O(n)` worst (mọi key đụng độ hash). Interview và LeetCode gần như luôn hỏi **worst-case**; review code production lại quan tâm **average-case** vì worst-case của hash table hầu như không xảy ra với dữ liệu thật (nhưng lại xảy ra với dữ liệu do kẻ tấn công chọn — đó là hash-flooding DoS). Khi trả lời, nói rõ mình đang nói case nào.

### Amortized analysis

Amortized ≠ average. Average nói về phân phối input; **amortized nói về một chuỗi thao tác**: chi phí tệ nhất của n thao tác liên tiếp, chia cho n. Nó là một cận cho *mọi* chuỗi, không phải kỳ vọng thống kê.

Ví dụ kinh điển là `list.append`. `list` của CPython là dynamic array: khi hết chỗ, nó cấp phát vùng nhớ mới lớn hơn và copy toàn bộ sang. Một `append` cụ thể có thể tốn `O(n)`. Nhưng CPython **over-allocate** theo hệ số ~1.125 (`new_allocated = size + size >> 3 + 6`, làm tròn), nên các lần resize thưa dần theo cấp số nhân. Đo thật:

```python
import sys, timeit

t = timeit.timeit("L.append(1)", setup="L=[]", number=1_000_000)
print(f"1e6 append: {t:.4f}s  ->  {t/1e6*1e9:.1f} ns/op")

L, prev, caps = [], sys.getsizeof([]), []
for i in range(1, 200):
    L.append(i)
    s = sys.getsizeof(L)
    if s != prev:
        caps.append(i)
        prev = s
print("resize xay ra khi len =", caps)
```

Kết quả đo được:

```
1e6 append: 0.0090s  ->  9.0 ns/op
resize xay ra khi len = [1, 5, 9, 17, 25, 33, 41, 53, 65, 77, 93, 109, 129, 149, 173]
```

Nhìn dãy `1, 5, 9, 17, 25, 33, 41, 53, 65, 77, 93, 109, 129, 149, 173`: khoảng cách giữa hai lần resize là `4, 4, 8, 8, 8, 8, 12, 12, 12, 16, 16, 20, 20, 24` — tăng dần. Tổng chi phí copy của n lần append là một chuỗi hình học hội tụ, tổng `Θ(n)`, nên **amortized `O(1)` mỗi append**. Con số 9.0 ns/op xác nhận: nếu append là `O(n)` thật, 10^6 append đã tốn hàng phút chứ không phải 10 mili-giây.

`dict` và `set` cũng vậy: khi load factor vượt 2/3, hash table rehash toàn bộ — một `insert` tốn `O(n)`, nhưng vì bảng nhân đôi kích thước, amortized vẫn `O(1)`.

Hệ quả thực dụng: **đừng tự tối ưu bằng cách cấp phát trước.** `[None] * n` rồi gán từng phần tử gần như không nhanh hơn append trong vòng lặp, vì append đã amortized `O(1)` rồi.

### Space complexity: auxiliary vs total

- **Total space**: tất cả bộ nhớ chương trình dùng, kể cả input.
- **Auxiliary space**: phần *thêm* ngoài input.

Khi đề bài nói "giải trong `O(1)` space", họ luôn nói về auxiliary space — vì input `O(n)` thì không tránh được. Bài 75. Sort Colors giải in-place là `O(1)` auxiliary, `O(n)` total.

Đệ quy tốn **`O(depth)` stack frame**, và đây là auxiliary space thật, dễ bị quên. DFS trên cây lệch (skewed tree) hoặc đồ thị đường thẳng 10^5 đỉnh có depth 10^5. CPython mặc định `sys.getrecursionlimit()` là **1000**, nên bạn sẽ ăn `RecursionError` trước khi kịp ăn TLE:

```python
import sys

print("mac dinh:", sys.getrecursionlimit())

def depth(n: int) -> int:
    return 0 if n == 0 else 1 + depth(n - 1)

try:
    depth(100_000)
except RecursionError:
    print("RecursionError o limit mac dinh")

sys.setrecursionlimit(300_000)
print("sau khi nang limit: depth(100000) =", depth(100_000))
```

In ra:

```
mac dinh: 1000
RecursionError o limit mac dinh
sau khi nang limit: depth(100000) = 100000
```

Cảnh báo: `sys.setrecursionlimit` chỉ nới **giới hạn đếm của interpreter**, không nới stack thật của OS. Đặt quá cao rồi đệ quy sâu thật sẽ làm process bị segfault thay vì ném exception sạch sẽ. Trên input rất sâu, cách đúng là **chuyển DFS sang vòng lặp với stack tường minh** — sẽ làm ở PART về đồ thị.

### Bảng suy ngược "constraint → thuật toán"

Đây là bảng phải thuộc. Giả định thô: judge cho khoảng **10^8 phép tính đơn giản/giây** với C++, và CPython chậm hơn ~30–100 lần (§03), nên với Python hãy lấy ngưỡng an toàn khoảng **10^7 thao tác Python-level/giây**.

| Ràng buộc n | Độ phức tạp cho phép | Thuật toán điển hình |
| --- | --- | --- |
| n ≤ 10 | `O(n!)`, `O(2^n · n)` | brute-force hoán vị, backtracking đầy đủ |
| n ≤ 20 | `O(2^n · n)` | bitmask DP, duyệt tập con |
| n ≤ 100 | `O(n^4)` | DP 3 chiều, Floyd-Warshall nhỏ |
| n ≤ 500 | `O(n³)` | Floyd-Warshall, DP interval |
| n ≤ 5000 | `O(n²)` | DP 2 chiều, edit distance, LCS |
| n ≤ 10^5 – 10^6 | `O(n log n)`, `O(n)` | sort, binary search, two pointers, sliding window, heap |
| n ≤ 10^8 | `O(n)` hoặc `O(log n)` | duyệt một lần, hoặc chỉ toán học/binary search trên đáp án |

Chiều ngược lại cũng hữu ích: nhìn thấy `n ≤ 20` thì gần như chắc chắn là bitmask; nhìn thấy đề nói "phải đạt `O(log n)`" thì đó là binary search, không có lựa chọn khác.

### Kiểm chứng bảng bằng đo thật

Chạy naive `O(n²)` và optimized `O(n)` cho cùng bài Maximum Subarray, với n gấp đôi mỗi lần:

```python
import random, time

def naive(a: list[int]) -> int:
    best, n = a[0], len(a)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += a[j]
            if s > best:
                best = s
    return best

def fast(a: list[int]) -> int:
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        if cur > best:
            best = cur
    return best

random.seed(1)
prev_n = prev_f = None
for n in (1000, 2000, 4000):
    a = [random.randint(-5, 5) for _ in range(n)]
    t0 = time.perf_counter(); naive(a); t1 = time.perf_counter()
    fast(a);                  t2 = time.perf_counter()
    tn, tf = t1 - t0, t2 - t1
    rn = f"{tn/prev_n:.2f}x" if prev_n else "-"
    rf = f"{tf/prev_f:.2f}x" if prev_f else "-"
    print(f"n={n:5d}  naive {tn:.4f}s ({rn})   fast {tf:.6f}s ({rf})")
    prev_n, prev_f = tn, tf
```

Kết quả trên máy đo:

```
n= 1000  naive 0.0112s (-)      fast 0.000081s (-)
n= 2000  naive 0.0334s (2.99x)   fast 0.000089s (1.10x)
n= 4000  naive 0.1342s (4.01x)   fast 0.000186s (2.09x)
```

Đọc bảng này cho đúng. Naive tăng **2.99x rồi 4.01x** khi n gấp đôi: bước đầu *chưa* đạt 4x vì ở n nhỏ chi phí cố định (khởi tạo hàm, cache còn nóng) chiếm tỉ trọng đáng kể, nên tỉ lệ đo được thấp hơn tỉ lệ tiệm cận; đến bước sau nó bò lên đúng 4x. `fast` tăng **1.10x rồi 2.09x** — bước đầu gần như không tăng vì ở mức chục micro-giây, nhiễu đo lớn hơn cả tín hiệu. Bài học: dùng tỉ lệ để **phân biệt bậc** (quanh 2x vs quanh 4x), đừng dùng nó để "chứng minh" một hằng số chính xác, và đừng tin tỉ lệ đo ở thang micro-giây.

Từ đây suy ra ngay: với `n = 10^5`, naive sẽ tốn khoảng `0.134 × (100000/4000)² ≈ 84 giây`. Đó là TLE. Bảng constraint không phải lý thuyết suông.

## Bài luyện thêm

Ba bài dưới đây được chọn vì chúng **được giải bằng cách đọc constraint**, không phải bằng cách nghĩ ra mẹo:

- **1. Two Sum** — `n ≤ 10^4` cho phép `O(n²)` (10^8 thì hơi căng với Python), nhưng dấu hiệu "tìm cặp có tổng = target" cộng constraint này là lời mời dùng hash map một lượt `O(n)`: lưu `value → index` đã thấy, mỗi phần tử tra `target - x`.
- **55. Jump Game** — `n ≤ 10^4` nên DP `O(n²)` vẫn bò được, nhưng greedy `O(n)` mới là lời giải: duy trì `reach` là chỉ số xa nhất tới được, nếu `i > reach` thì thất bại.
- **4. Median of Two Sorted Arrays** — đề **nói thẳng** yêu cầu `O(log(m+n))`. Câu đó loại luôn merge `O(m+n)`; bắt buộc binary search trên vị trí phân hoạch của mảng ngắn hơn.

## Bài toán áp dụng

Ước lượng Big-O khi review PR. Đoạn code này xuất hiện thường xuyên trong code xử lý dữ liệu:

```python
users  = [{"id": i, "name": f"u{i}"} for i in range(5)]
orders = [{"user_id": i % 5, "amount": i} for i in range(12)]

# O(U * R): với mỗi user quét lại toàn bộ orders
def total_slow(users: list[dict], orders: list[dict]) -> dict[int, int]:
    return {u["id"]: sum(o["amount"] for o in orders if o["user_id"] == u["id"])
            for u in users}

# O(U + R): gom orders theo user_id một lần
from collections import defaultdict

def total_fast(users: list[dict], orders: list[dict]) -> dict[int, int]:
    agg: dict[int, int] = defaultdict(int)
    for o in orders:
        agg[o["user_id"]] += o["amount"]
    return {u["id"]: agg[u["id"]] for u in users}

print(total_slow(users, orders) == total_fast(users, orders), total_fast(users, orders))
```

In ra `True {0: 15, 1: 18, 2: 9, 3: 11, 4: 13}`. Với 5 user và 12 order thì hai bản như nhau. Với **50.000 user × 200.000 order** thì bản chậm là 10^10 phép so sánh — nó không "hơi chậm", nó là một sự cố production. Câu hỏi cần đặt ra khi review là "N và M ở đây thực tế bằng bao nhiêu?", và câu trả lời "hiện tại chỉ vài trăm" nên kèm theo "vài trăm *hôm nay*".

## Use case thực tế

- **Review PR**: bất kỳ vòng lặp lồng nào chạy trên hai tập dữ liệu từ DB đều đáng hỏi Big-O. Pattern hay gặp nhất là "N+1 query": vòng lặp qua N bản ghi, mỗi vòng gọi một query — `O(N)` round-trip mạng, mỗi round-trip ~1ms, nên N=1000 là 1 giây. Fix là `JOIN` hoặc một query `IN (...)`.
- **Capacity planning**: biết thuật toán là `Θ(n log n)` cho phép ngoại suy từ benchmark ở n nhỏ ra thời gian ở n production, thay vì phải chạy thử trên toàn bộ dataset.
- **Khi nào Big-O *không* phải câu trả lời**: khi n bị chặn nhỏ và cố định. Sắp xếp 10 phần tử thì insertion sort `O(n²)` nhanh hơn merge sort `O(n log n)` vì hằng số nhỏ hơn — đây chính là lý do Timsort của CPython chuyển sang binary insertion sort cho các run ngắn. Asymptotic chỉ thắng khi n đủ lớn; §03 nói về phần "hằng số" mà Big-O cố tình bỏ qua.

## Bẫy thường gặp trong Python

- **`in` trên `list` là `O(n)`.** `if x in some_list` bên trong vòng lặp biến thuật toán `O(n)` của bạn thành `O(n²)` một cách vô hình — không có vòng lặp lồng nào hiện ra trong code. Đây là lỗi complexity phổ biến nhất của người viết Python.
- **Slicing tạo bản sao `O(k)`.** `nums[1:]` không phải view. Đệ quy kiểu `solve(s[1:])` là `O(n²)` tổng dù nhìn như `O(n)`. Chi tiết ở §04.
- **`sum()`, `max()`, `min()` trong vòng lặp.** Mỗi lời gọi là `O(n)`. `for i in range(n): total = sum(a[:i])` là `O(n²)`, giải bằng prefix sum ở §08.
- **`list.pop(0)` / `list.insert(0, x)` là `O(n)`.** Cài queue bằng `list` cho BFS biến `O(V+E)` thành `O(V²)`. Dùng `collections.deque` (§03 đo tỉ lệ chênh lệch thật).
- **Amortized không có nghĩa là "không bao giờ chậm".** Một `append` cụ thể vẫn có thể tốn `O(n)`. Với hệ thống realtime quan tâm p99 latency, amortized `O(1)` vẫn có thể là tail latency tệ — đó là lý do một số hệ thống dùng cấu trúc có worst-case bound thay vì amortized bound.
- **`sys.setrecursionlimit` không phải thuốc chữa bách bệnh.** Nó nới bộ đếm của interpreter chứ không nới stack của OS; đặt quá cao rồi đệ quy sâu thật sẽ crash process. Chuyển sang vòng lặp mới là lời giải.
