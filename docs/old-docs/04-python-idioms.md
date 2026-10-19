# 04. Python idioms cho DSA

Python cho phép viết thuật toán rất gọn, nhưng vài idiom quen tay lại có chi phí ẩn (slicing copy) hoặc semantics khác C++/Java (`//` làm tròn xuống). Section này gom những idiom bạn sẽ dùng ở mọi bài từ §06 trở đi, kèm chỗ chúng phản bội bạn.

## Lý thuyết

### Slicing luôn copy — và đó là cái bẫy complexity lớn nhất

`nums[1:]`, `s[::-1]`, `a[i:j]` **không phải view**. Chúng cấp phát một object mới và copy `k` phần tử, chi phí `O(k)`. Với `list` thì là shallow copy (copy con trỏ, không copy phần tử); với `str` thì là chuỗi mới thật sự.

Hệ quả tàn khốc nhất là đệ quy trên slice: `solve(s[1:])` nhìn như mỗi tầng làm `O(1)` việc, nhưng riêng việc **tạo tham số** đã tốn `O(n)`, `O(n-1)`, `O(n-2)`, … → tổng `O(n²)`. Cách chữa duy nhất: truyền **index** thay vì truyền slice.

```python
import time

def rev_slice(s: str) -> str:
    """O(n^2): moi tang cat mot chuoi moi."""
    return s if len(s) <= 1 else rev_slice(s[1:]) + s[0]

def rev_index(s: str, i: int = 0, out: list[str] | None = None) -> str:
    """O(n): chi truyen chi so, khong copy."""
    if out is None:
        out = []
    if i == len(s):
        return "".join(reversed(out))
    out.append(s[i])
    return rev_index(s, i + 1, out)

import sys
sys.setrecursionlimit(20_000)
prev = None
for n in (2000, 4000, 8000):
    s = "a" * n
    t0 = time.perf_counter(); rev_slice(s);  t1 = time.perf_counter()
    rev_index(s);                            t2 = time.perf_counter()
    ratio = f"{(t1-t0)/prev:.2f}x" if prev else "-"
    prev = t1 - t0
    print(f"n={n:5d}  slice {t1-t0:.4f}s ({ratio})  index {t2-t1:.4f}s")
```

Đo được:

```
n= 2000  slice 0.0005s (-)      index 0.0002s
n= 4000  slice 0.0015s (2.77x)  index 0.0004s
n= 8000  slice 0.0050s (3.39x)  index 0.0007s
```

Bản slice tăng 2.77x rồi 3.39x mỗi lần n gấp đôi — đang bò lên 4x, tức bậc hai; bản index tăng đúng 2x, tuyến tính. Cùng một thuật toán, khác nhau chỉ ở cách truyền tham số.

Quy tắc: **trong vòng lặp hoặc đệ quy, dùng `left`/`right` index. Ngoài vòng lặp, slicing thoải mái** — `s[::-1]` một lần là `O(n)`, hoàn toàn ổn.

### `enumerate`, `zip`, và `zip(*matrix)`

`enumerate(a)` thay cho `for i in range(len(a)): x = a[i]` — bớt một chỗ có thể sai index. `enumerate(a, start=1)` khi bài đánh số từ 1.

`zip(a, b)` duyệt song song, tự dừng ở dãy ngắn hơn. Nếu bạn *muốn* lỗi khi độ dài lệch, `zip(a, b, strict=True)` (từ 3.10) — rất đáng dùng khi hai mảng phải cùng độ dài theo đề bài.

`zip(*matrix)` là **transpose**. Không phải `O(1)` như đôi khi bị nói nhầm — nó là `O(1)` về **số dòng code**, còn chi phí là `O(rows × cols)`:

```python
m = [[1, 2, 3],
     [4, 5, 6]]

print([list(row) for row in zip(*m)])          # transpose 2x3 -> 3x2
print([list(row) for row in zip(*m[::-1])])    # xoay 90 do theo chieu kim dong ho
print(list(zip("abc", [1, 2, 3])))
try:
    list(zip([1, 2, 3], [1, 2], strict=True))
except ValueError as e:
    print("strict=True bat duoc lech do dai:", e)
```

In ra:

```
[[1, 4], [2, 5], [3, 6]]
[[4, 1], [5, 2], [6, 3]]
[('a', 1), ('b', 2), ('c', 3)]
strict=True bat duoc lech do dai: zip() argument 2 is shorter than argument 1
```

`zip(*matrix[::-1])` là toàn bộ lời giải cho bài 48. Rotate Image bản không in-place (§11).

### Comprehension và generator

Comprehension nhanh hơn `for` + `.append` vì nó dùng bytecode chuyên biệt (`LIST_APPEND`) thay vì tra cứu và gọi method `.append` mỗi vòng. Generator expression thì không nhanh hơn — nó **tiết kiệm bộ nhớ** bằng cách sinh lười.

```python
import timeit, sys

n = 100_000
t_loop = timeit.timeit(f"r=[]\nfor i in range({n}): r.append(i*i)", number=20)
t_comp = timeit.timeit(f"[i*i for i in range({n})]",                number=20)
print(f"loop+append x20: {t_loop:.4f}s")
print(f"comprehension x20: {t_comp:.4f}s  -> nhanh hon {t_loop/t_comp:.2f}x")

lst = [i * i for i in range(n)]
gen = (i * i for i in range(n))
print("bo nho list:", sys.getsizeof(lst), "bytes | generator:", sys.getsizeof(gen), "bytes")
print("any() tren generator dung short-circuit:", any(x > 10 for x in range(1_000_000_000)))
```

Đo được:

```
loop+append x20: 0.0423s
comprehension x20: 0.0319s  -> nhanh hon 1.32x
bo nho list: 800984 bytes | generator: 200 bytes
any() tren generator dung short-circuit: True
```

Dòng cuối là điểm quan trọng: `any(...)` trên generator duyệt tỉ phần tử vẫn trả về ngay, vì nó **dừng ở phần tử đầu thoả mãn**. Đổi thành list comprehension `any([x > 10 for x in range(10**9)])` thì sẽ treo máy — nó materialize toàn bộ trước.

Chọn: cần dùng lại nhiều lần / cần index → list comprehension. Duyệt một lần, feed vào `sum`/`any`/`all`/`max`/`min` → generator.

### `sort` / `sorted` và tính stable

CPython dùng **Timsort**: `O(n log n)` worst-case, và **stable** — hai phần tử bằng nhau theo key giữ nguyên thứ tự tương đối ban đầu.

Tính stable cho bạn hai kỹ thuật sort nhiều tiêu chí:

1. **Key là tuple** (cách thường dùng): `a.sort(key=lambda x: (x[0], -x[1]))`. Dấu trừ đảo chiều — chỉ dùng được cho số.
2. **Sort nhiều lần từ tiêu chí phụ đến tiêu chí chính** — cần thiết khi có tiêu chí không đảo được bằng dấu trừ (vd chuỗi giảm dần kèm số tăng dần).

```python
people = [("an", 30), ("binh", 25), ("chi", 30), ("dung", 25)]

print(sorted(people, key=lambda p: p[1]))                 # stable: giu thu tu goc trong nhom
print(sorted(people, key=lambda p: (p[1], p[0])))         # tuple key
best = sorted(people, key=lambda p: p[0])                 # tieu chi PHU truoc
best = sorted(best, key=lambda p: -p[1])                  # tieu chi CHINH sau
print(best)

from functools import cmp_to_key
def cmp(a: str, b: str) -> int:
    """179. Largest Number: dat a truoc b neu a+b > b+a."""
    return -1 if a + b > b + a else (1 if a + b < b + a else 0)

nums = [3, 30, 34, 5, 9]
s = sorted(map(str, nums), key=cmp_to_key(cmp))
print("".join(s).lstrip("0") or "0")
```

In ra:

```
[('binh', 25), ('dung', 25), ('an', 30), ('chi', 30)]
[('binh', 25), ('dung', 25), ('an', 30), ('chi', 30)]
[('an', 30), ('chi', 30), ('binh', 25), ('dung', 25)]
9534330
```

Bài **179. Largest Number** là ví dụ chuẩn cho `functools.cmp_to_key`: quan hệ "a nên đứng trước b" ở đây là `a+b > b+a`, một so sánh **giữa hai phần tử** không quy được về một key đơn lẻ. `cmp_to_key` bọc hàm so sánh thành object có `__lt__`, nên nó chậm hơn key thường (mỗi so sánh là một lời gọi Python) — chỉ dùng khi thật sự không viết được key.

Cũng lưu ý `.lstrip("0") or "0"`: với input `[0, 0]` chuỗi ghép là `"00"`, phải trả `"0"` chứ không phải chuỗi rỗng. Đây đúng là loại edge case mà mục `#%% Requirements` sinh ra để bắt.

### `int` không tràn, nhưng không miễn phí

Python `int` là arbitrary precision. Bài "nhân hai số lớn", "tính giai thừa 100", "Fibonacci thứ 1000" đều không cần big-int thủ công. Nhưng **`O(1)` cho phép nhân là giả định sai khi số rất lớn**: nhân hai số d chữ số tốn khoảng `O(d^1.585)` (Karatsuba trong CPython).

```python
import math, time, sys

print("2**100 =", 2**100)
print("khong tran, khac C++ int64:", (2**63) * (2**63) == 2**126)
print("bit_count cua 255:", (255).bit_count(), "| bit_length:", (255).bit_length())

sys.set_int_max_str_digits(100_000)          # tu 3.11: str(int) bi chan o 4300 chu so
f = math.factorial(20000)
print("so chu so cua 20000! :", len(str(f)))
t0 = time.perf_counter(); f * f; t1 = time.perf_counter()
g = 12345
t2 = time.perf_counter(); g * g; t3 = time.perf_counter()
print(f"nhan hai so ~77000 chu so: {t1-t0:.6f}s | nhan hai so nho: {t3-t2:.9f}s")
print("maxsize (chi la co con tro, khong phai gioi han int):", sys.maxsize)
```

Đo được:

```
2**100 = 1267650600228229401496703205376
khong tran, khac C++ int64: True
bit_count cua 255: 8 | bit_length: 8
so chu so cua 20000! : 77338
nhan hai so ~77000 chu so: 0.005559s | nhan hai so nho: 0.000000334s
```

Dòng `sys.set_int_max_str_digits(100_000)` không phải trang trí: **từ Python 3.11, `str(int)` bị chặn ở 4300 chữ số** (biện pháp chống DoS — chuyển int khổng lồ sang chuỗi là thao tác bậc hai). Bỏ dòng đó đi thì `len(str(f))` ném `ValueError: Exceeds the limit (4300 digits) for integer string conversion`. Bản thân phép tính `math.factorial(20000)` và `f * f` không bị ảnh hưởng — chỉ việc **in ra / chuyển sang chuỗi** mới bị chặn.

`int.bit_count()` (từ 3.10) là popcount cài bằng C — dùng cho mọi bài bitmask thay vì `bin(x).count("1")`.

### `//` và `divmod` làm tròn về âm vô cực

Đây là khác biệt semantics gây bug khi port code từ C++/Java:

```python
print("Python  -7 //  2 =", -7 // 2, " (C++/Java cho -3)")
print("Python  -7 %   2 =", -7 % 2,  " (C++/Java cho -1)")
print("divmod(-7, 2)     =", divmod(-7, 2))
print("truncate kieu C   =", int(-7 / 2))
import math
print("math.trunc(-7/2)  =", math.trunc(-7 / 2))
print("mid an toan cho binary search: (-9 + -8)//2 =", (-9 + -8) // 2)
print("modulo luon khong am voi divisor duong: [-3 % 5, 3 % 5] =", [-3 % 5, 3 % 5])
```

In ra:

```
Python  -7 //  2 = -4  (C++/Java cho -3)
Python  -7 %   2 = 1  (C++/Java cho -1)
divmod(-7, 2)     = (-4, 1)
truncate kieu C   = -3
math.trunc(-7/2)  = -3
mid an toan cho binary search: (-9 + -8)//2 = -9
modulo luon khong am voi divisor duong: [-3 % 5, 3 % 5] = [1, 3]
```

Hai hệ quả thực dụng:

- **Ưu điểm**: `%` với divisor dương **luôn cho kết quả không âm** trong Python. Idiom `(i + 1) % n` để đi vòng quanh mảng hoạt động đúng cả khi lùi: `(i - 1) % n` cho `n-1` khi `i = 0`. Trong C++ phải viết `((i-1)%n + n)%n`.
- **Cạm bẫy**: bài yêu cầu "chia làm tròn về 0" (như 29. Divide Two Integers, hay tính trung bình của số âm) thì `//` sai. Dùng `int(a / b)` cho số nhỏ, hoặc `-(-a // b)` khi cần chính xác với số lớn (vì `a / b` chuyển sang float và mất chính xác quá 2^53).

### Unpacking

```python
a, b = 1, 2
a, b = b, a                                # swap khong can bien tam
print(a, b)

first, *middle, last = [10, 20, 30, 40, 50]
print(first, middle, last)

def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int]:
    l, r = 0, len(nums) - 1                # khoi tao hai con tro trong mot dong
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return l, r                    # tra ve tuple, unpack o cho goi
        l, r = (l + 1, r) if s < target else (l, r - 1)
    return -1, -1

i, j = two_sum_sorted([2, 7, 11, 15], 18)   # 7 + 11 = 18 -> (1, 2)
print(i, j)

grid = [[0] * 3 for _ in range(2)]         # DUNG
bad  = [[0] * 3] * 2                       # SAI: 2 tham chieu toi CUNG mot list
grid[0][0] = 9
bad[0][0] = 9
print("grid:", grid)
print("bad :", bad)
```

In ra:

```
2 1
10 [20, 30, 40] 50
1 2
grid: [[9, 0, 0], [0, 0, 0]]
bad : [[9, 0, 0], [9, 0, 0]]
```

Ba dòng cuối là bug tạo lưới 2D bằng `[[0]*m]*n` — `*` trên list chỉ nhân **tham chiếu**. Đây là lỗi số một khi làm bài DP 2D hoặc ma trận. Luôn dùng comprehension.

## Bài luyện thêm

- **179. Largest Number** — so sánh hai chuỗi bằng `a + b > b + a` rồi `sorted(key=cmp_to_key(...))`; code đầy đủ đã có ở phần `cmp_to_key` trong mục Lý thuyết bên trên, kèm bẫy `"00" → "0"`.

Đó là bài LeetCode duy nhất outline gắn cho §04. Bài tự luyện đề xuất: lấy lại một bài bạn đã giải và viết lại nó bỏ hết mọi slicing trong vòng lặp, thay bằng index — rồi đo lại bằng cách của §05.

## Bài toán áp dụng

Xếp hạng nhiều tiêu chí là bài toán "sort" thật sự phổ biến nhất ngoài đời: bảng xếp hạng, danh sách sản phẩm, kết quả tìm kiếm. Đây là chỗ tính stable của Timsort có giá trị trực tiếp.

```python
# Bang xep hang: diem giam dan, cung diem thi thoi gian nop TANG dan, cung nua thi ten A-Z.
rows = [
    {"name": "chi",  "score": 90, "t": 120},
    {"name": "an",   "score": 95, "t": 200},
    {"name": "binh", "score": 90, "t": 120},
    {"name": "dung", "score": 95, "t": 150},
]

ranked = sorted(rows, key=lambda r: (-r["score"], r["t"], r["name"]))
for i, r in enumerate(ranked, 1):
    print(i, r["name"], r["score"], r["t"])

# Cach 2 - sort nhieu lan tu tieu chi PHU den CHINH, dung khi tieu chi khong dao duoc bang dau tru
alt = sorted(rows, key=lambda r: r["name"])
alt = sorted(alt,  key=lambda r: r["t"])
alt = sorted(alt,  key=lambda r: r["score"], reverse=True)
print("hai cach cho cung ket qua:", [r["name"] for r in alt] == [r["name"] for r in ranked])
```

In ra:

```
1 dung 95 150
2 an 95 200
3 binh 90 120
4 chi 90 120
hai cach cho cung ket qua: True
```

`dung` xếp trên `an` dù cùng 95 điểm, vì nộp sớm hơn (150 < 200). `binh` xếp trên `chi` dù cùng 90 điểm và cùng thời gian 120 — tiêu chí thứ ba (tên A-Z) phân định.

Chú ý bẫy ở cách 2: `reverse=True` **vẫn giữ tính stable** (nó không phải "sort xuôi rồi đảo list"), nên chuỗi sort nhiều lần vẫn cho kết quả đúng. Nếu Timsort không stable, kỹ thuật này sẽ sai hoàn toàn.

## Use case thực tế

- **`key=` là idiom xuyên suốt stdlib**, không chỉ `sorted`: `max(items, key=...)`, `min`, `heapq.nlargest/nsmallest(n, it, key=...)`, và từ Python 3.10 cả `bisect.bisect_left(a, x, key=...)`. Học một lần dùng khắp nơi.
- **`itertools` là thư viện thuật toán bị bỏ quên**: `accumulate` cho prefix sum (§08), `pairwise` cho duyệt cặp liền kề, `groupby` trên dãy đã sort, `combinations`/`permutations` cho brute-force `n ≤ 10`, và `batched` (mới ở 3.12) để chia dãy thành chunk. Tất cả chạy bằng C.
- **Khi nào dùng thư viện có sẵn**: sort, nhị phân (`bisect`), heap (`heapq`), đếm (`Counter`), sắp xếp topo (`graphlib.TopologicalSorter`) — luôn dùng stdlib trong production. Tự cài chỉ để hiểu (`cores/python/`).
- **Chỗ ngôn ngữ khác biệt gây bug thật**: hệ thống phân tán viết bằng nhiều ngôn ngữ, cùng một công thức sharding `hash(key) % n` sẽ cho shard khác nhau giữa Python và Java khi hash âm, chính vì `%` khác semantics. Đây là bug production có thật, không phải chuyện thi cử.

## Bẫy thường gặp trong Python

- **`[[0] * m] * n`** tạo n tham chiếu tới cùng một hàng. Dùng `[[0] * m for _ in range(n)]`.
- **Mutable default argument**: `def f(acc=[])` — list đó được tạo **một lần** lúc định nghĩa hàm và dùng lại giữa các lời gọi. Dùng `def f(acc=None)` rồi `if acc is None: acc = []` (như `rev_index` ở trên).
- **Slicing trong vòng lặp/đệ quy** biến `O(n)` thành `O(n²)` một cách vô hình. Truyền index.
- **`lambda` bắt biến theo tham chiếu (late binding)**: `[lambda: i for i in range(3)]` cho ba closure đều trả về `2`. Dùng `lambda i=i: i` khi cần bắt giá trị.
- **`sorted()` trả list mới, `.sort()` sửa tại chỗ và trả `None`.** `nums = nums.sort()` biến `nums` thành `None` — lỗi im lặng cho tới khi vỡ ở chỗ khác.
- **`reverse=True` ≠ `sorted(...)[::-1]`** khi có phần tử bằng nhau: bản đầu giữ stable, bản sau đảo cả thứ tự trong nhóm.
- **`-7 // 2 == -4`**, không phải `-3`. Với binary search viết `mid = (lo + hi) // 2` là an toàn trong Python (`int` không tràn), nhưng nếu range có thể âm thì hãy nghĩ kỹ xem bạn muốn floor hay trunc.
- **`str()` của `int` rất lớn bị chặn từ 3.11.** Quá 4300 chữ số là `ValueError`. Gặp khi in kết quả `math.factorial` hoặc `2**n` lớn; nới bằng `sys.set_int_max_str_digits(...)`.
- **`x is y` với số nguyên.** CPython cache `int` trong `[-5, 256]`, nên `256 is 256` là `True` còn `257 is 257` có thể `False`. So sánh giá trị bằng `==`, `is` chỉ dành cho `None`/`True`/`False`.
- **Copy nông vs sâu**: `b = a[:]` copy list nhưng các phần tử bên trong vẫn dùng chung. Với ma trận `[row[:] for row in matrix]`, hoặc `copy.deepcopy` (đắt — tránh trong vòng lặp backtracking).
