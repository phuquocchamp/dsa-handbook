# 03. Hằng số CPython — tại sao đúng asymptotic vẫn TLE

Big-O cố tình vứt bỏ hằng số. CPython thì không: interpreter overhead, boxing từng số nguyên thành object, và chi phí gọi hàm khiến cùng một thuật toán chạy chậm hơn C++ hàng chục lần. Nếu bỏ qua chương này, bạn sẽ có một lời giải `O(n)` đúng về lý thuyết mà vẫn TLE, rồi **đổ lỗi sai cho thuật toán và đi tối ưu nhầm hướng** — thay vì đổi `list` thành `deque` hoặc `list` thành `set`.

> Mọi số đo trong chương chạy trên `Python 3.12.12`, darwin/arm64. Đọc **tỉ lệ**, không đọc số tuyệt đối.

## Lý thuyết

### Hằng số đến từ đâu

Ba nguồn chính, xếp theo mức độ gây đau:

1. **Bytecode dispatch.** Mỗi phép toán Python-level (`a[i] + 1`) là vài lệnh bytecode, mỗi lệnh là một vòng lặp của interpreter. C++ compile ra một lệnh máy.
2. **Boxing.** Mọi `int` trong `list` là một `PyLongObject` đầy đủ trên heap; `list` chỉ chứa con trỏ. Duyệt mảng nghĩa là dereference con trỏ rải rác khắp bộ nhớ — cache-hostile.
3. **Gọi hàm.** Tạo frame, bind tham số, dọn frame. Hàm Python nhỏ gọi trong vòng lặp nóng là một trong những cách đắt nhất để cấu trúc code DSA.

Hệ quả có thể hành động được: **đẩy vòng lặp xuống C bất cứ khi nào có thể.** `sum(a)`, `max(a)`, `''.join(parts)`, `sorted(a)`, `heapq.*`, `collections.Counter` đều là vòng lặp chạy ở tầng C. Một `for` viết tay làm cùng việc luôn chậm hơn nhiều lần.

### Cost model của `list`

| Thao tác | Độ phức tạp | Ghi chú |
| --- | --- | --- |
| `a[i]`, `a[i] = x` | `O(1)` | truy cập theo con trỏ |
| `a.append(x)`, `a.pop()` | `O(1)` amortized | §02 |
| `a.insert(0, x)`, `a.pop(0)` | **`O(n)`** | phải `memmove` toàn bộ đuôi |
| `x in a` | **`O(n)`** | quét tuyến tính |
| `a[i:j]` | `O(j-i)` | **tạo list mới**, không phải view |
| `a.sort()` | `O(n log n)` | Timsort, cài bằng C |

Hai dòng in đậm đầu là nguồn của hai lỗi kinh điển: cài queue cho BFS bằng `list.pop(0)`, và check membership bằng `in` trên `list`.

`collections.deque` là doubly-linked list of blocks: `append`/`appendleft`/`pop`/`popleft` đều `O(1)` thật, nhưng đổi lại `d[i]` ở giữa là `O(n)`. Chọn `deque` khi bạn cần hai đầu, chọn `list` khi bạn cần random access.

### Cost model của `dict` / `set`

`O(1)` **trung bình** cho `in`, `get`, `[]=`, và điều đó phụ thuộc hoàn toàn vào hàm hash của key:

- Key phải **hashable** — tức immutable. `tuple` được, `list` không. `d[(r, c)] = v` là idiom chuẩn cho lưới 2D thưa.
- Hash của `int` nhỏ trong CPython chính bằng giá trị của nó. Nghe có vẻ nguy hiểm (mọi bội của kích thước bảng đụng nhau), nhưng open addressing với probing của CPython xử lý được trong thực tế.
- Hash của `str` được **randomize theo process** (`PYTHONHASHSEED`) để chống hash-flooding DoS. Hệ quả cho DSA: **thứ tự duyệt `set` không ổn định giữa các lần chạy**. Đừng bao giờ dựa vào nó; nếu cần thứ tự xác định, `sorted(s)`.

Sự chênh lệch `in list` vs `in set` không phải "hơi khác", nó khác vài bậc:

```python
import timeit

t_list = timeit.timeit("999999 in L", setup="L=list(range(1000000))", number=100)
t_set  = timeit.timeit("999999 in S", setup="S=set(range(1000000))",  number=100)
print(f"'in list' x100: {t_list:.4f}s")
print(f"'in set'  x100: {t_set:.6f}s")
print(f"ty le: {t_list/t_set:,.0f}x")

t_pop = timeit.timeit("L.pop(0)", setup="L=list(range(20000))", number=20000)
t_dq  = timeit.timeit("d.popleft()",
                      setup="from collections import deque; d=deque(range(20000))",
                      number=20000)
print(f"list.pop(0) x20000: {t_pop:.4f}s | deque.popleft x20000: {t_dq:.6f}s "
      f"| ty le {t_pop/t_dq:.0f}x")
```

Đo được:

```
'in list' x100: 0.3007s
'in set'  x100: 0.000003s
ty le: 86,956x
list.pop(0) x20000: 0.0167s | deque.popleft x20000: 0.000163s | ty le 103x
```

~87.000x không phải lỗi đánh máy — nó là `O(n)` vs `O(1)` với n = 10^6, đúng bậc (con số chính xác dao động mạnh giữa các lần chạy vì `in set` ở mức nano-giây, nhưng bậc thì không đổi). Còn 103x cho `pop(0)` vs `popleft` với n = 20.000 cũng đúng bậc: `O(n)` vs `O(1)`.

### String concat: chuyện phức tạp hơn "s += c là O(n²)"

Câu khuyên phổ biến là `s += char` trong vòng lặp là `O(n²)` vì `str` immutable. Điều đó **đúng về nguyên tắc nhưng sai trong trường hợp thường gặp nhất**, vì CPython có một tối ưu hoá: khi biến `s` là **tham chiếu duy nhất** tới chuỗi đó, `+=` được thực hiện bằng `realloc` tại chỗ thay vì copy. Tối ưu này tan biến ngay khi có tham chiếu thứ hai. Đo cả hai:

```python
import time

def concat_refcount1(src: str) -> str:
    s = ""
    for c in src:
        s += c                      # s la tham chieu duy nhat -> CPython realloc tai cho
    return s

def concat_held_ref(src: str) -> str:
    s, hold = "", []
    for c in src:
        hold.append(s)              # giu them 1 tham chieu -> tat toi uu in-place
        s = s + c
    return s

def join_way(src: str) -> str:
    return "".join(src)

for n in (20_000, 40_000, 80_000):
    src = "a" * n
    t0 = time.perf_counter(); concat_refcount1(src); t1 = time.perf_counter()
    concat_held_ref(src);                            t2 = time.perf_counter()
    join_way(src);                                   t3 = time.perf_counter()
    print(f"n={n:6d}  s+=c (refcount 1) {t1-t0:.4f}s | "
          f"s=s+c (bi giu ref) {t2-t1:.4f}s | join {t3-t2:.6f}s")
```

Kết quả:

```
n= 20000  s+=c (refcount 1) 0.0004s | s=s+c (bi giu ref) 0.0168s | join 0.000091s
n= 40000  s+=c (refcount 1) 0.0010s | s=s+c (bi giu ref) 0.0593s | join 0.000157s
n= 80000  s+=c (refcount 1) 0.0019s | s=s+c (bi giu ref) 0.2217s | join 0.000292s
```

Cột 1 tăng ~2x mỗi lần n gấp đôi — tuyến tính, tối ưu hoá đang hoạt động. Cột 2 tăng 3.53x rồi 3.74x — quanh 4x, tức bậc hai, đúng như lý thuyết. Cột 3 nhanh hơn cả hai và luôn tuyến tính.

Kết luận đúng: **`s += c` là một tối ưu hoá phụ thuộc chi tiết cài đặt của CPython, không phải bảo đảm của ngôn ngữ.** Nó biến mất trên PyPy, và biến mất ngay trong CPython khi có tham chiếu khác (lưu vào list, truyền vào hàm khác, đóng gói trong closure). Vẫn dùng `"".join(parts)` — nó nhanh hơn trong mọi trường hợp và không có điều kiện ẩn.

### `array.array` và `bytearray`

Khi n rất lớn (10^6+) và dữ liệu **đồng nhất kiểu**, `list[int]` lãng phí bộ nhớ khủng khiếp vì boxing:

```python
import array, sys

L = list(range(1_000_000))
A = array.array("i", range(1_000_000))

int_obj = sys.getsizeof(1)                       # moi so nguyen nho la 1 object
print("sizeof(one int object):", int_obj, "bytes")
print("list  container       :", sys.getsizeof(L), "bytes (chi chua con tro)")
print("list  + cac int object:", sys.getsizeof(L) + int_obj * 1_000_000, "bytes")
print("array.array('i')      :", sys.getsizeof(A), "bytes")
```

In ra:

```
sizeof(one int object): 28 bytes
list  container       : 8000056 bytes (chi chua con tro)
list  + cac int object: 36000056 bytes
array.array('i')      : 4091948 bytes
```

**36 MB so với 4 MB** — chênh gần 9 lần. (Con số 36 MB là ước lượng trên: CPython cache sẵn các int nhỏ trong khoảng `[-5, 256]`, nên `list(range(10**6))` thật ra chia sẻ 262 object đầu; nhưng với dữ liệu thật rải rác trên 10^9 thì không có cache nào cả và 36 MB là con số đúng.) Đổi lại, `array.array` chậm hơn `list` khi truy cập vì mỗi lần đọc phải **box** giá trị thô thành `PyLongObject` mới. Nên: dùng `array`/`bytearray` khi bị giới hạn **bộ nhớ**, dùng `list` khi bị giới hạn **thời gian**. Nếu cần cả hai và bài toán vectorize được, câu trả lời là `numpy` — nhưng LeetCode/Codeforces thường không có sẵn nó.

## Ví dụ minh hoạ: hằng số quyết định pass/fail

### Ví dụ 1 — 3. Longest Substring Without Repeating Characters

Cùng là "đúng", nhưng bản dùng slicing tạo substring mới ở mỗi cặp `(i, j)` là `O(n³)`:

```python
import random, string, time

def naive(s: str) -> int:
    """O(n^3): moi cap (i,j) cat mot substring O(n) roi set() no."""
    best, n = 0, len(s)
    for i in range(n):
        for j in range(i, n):
            sub = s[i:j + 1]
            if len(set(sub)) == len(sub):
                best = max(best, len(sub))
    return best

def fast(s: str) -> int:
    """O(n): sliding window, dict luu vi tri cuoi cua moi ky tu."""
    seen: dict[str, int] = {}
    left = best = 0
    for r, c in enumerate(s):
        if c in seen and seen[c] >= left:
            left = seen[c] + 1
        seen[c] = r
        best = max(best, r - left + 1)
    return best

random.seed(3)
prev = None
for n in (500, 1000, 2000):
    s = "".join(random.choice(string.ascii_lowercase) for _ in range(n))
    t0 = time.perf_counter(); a = naive(s); t1 = time.perf_counter()
    b = fast(s);                            t2 = time.perf_counter()
    ratio = f"{(t1-t0)/prev:.2f}x" if prev else "-"
    prev = t1 - t0
    print(f"n={n:5d}  naive {t1-t0:8.4f}s ({ratio})  fast {t2-t1:.6f}s  khop={a == b}")
```

Đo được:

```
n=  500  naive   0.1102s (-)      fast 0.000064s  khop=True
n= 1000  naive   0.7425s (6.74x)  fast 0.000088s  khop=True
n= 2000  naive   5.5267s (7.44x)  fast 0.000156s  khop=True
```

Tỉ lệ ~7x khi n gấp đôi (lý thuyết `O(n³)` là 8x) xác nhận bậc ba. Với `n = 5·10^4` của đề bài, naive sẽ cần `5.53 × 25³ ≈ 86.000 giây`. Bản `O(n)` xong trong vài mili-giây. Điểm mấu chốt: cái làm naive thành `O(n³)` chứ không phải `O(n²)` chính là **`s[i:j+1]` tạo bản sao** — một chi tiết hằng số/cost-model của Python, không phải của thuật toán.

### Ví dụ 2 — 5. Longest Palindromic Substring: hai lời giải cùng "đúng"

`O(n²)` expand-around-center với `n ≤ 1000` (ràng buộc thật của bài 5) là hoàn toàn đủ. Manacher `O(n)` mới cần khi n lên 10^5+:

```python
def expand_center(s: str) -> str:
    """O(n^2) - du cho n <= 1000."""
    if not s:
        return ""
    best_l = best_r = 0
    for c in range(len(s)):
        for l, r in ((c, c), (c, c + 1)):           # le va chan
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            l, r = l + 1, r - 1
            if r - l > best_r - best_l:
                best_l, best_r = l, r
    return s[best_l:best_r + 1]

def manacher(s: str) -> str:
    """O(n): dung tinh doi xung de tai su dung ket qua da tinh."""
    if not s:
        return ""
    t = "^#" + "#".join(s) + "#$"                   # sentinel tranh check bien
    p = [0] * len(t)
    center = right = 0
    for i in range(1, len(t) - 1):
        if i < right:
            p[i] = min(right - i, p[2 * center - i]) # <- buoc "mien phi"
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
    length, center_idx = max((v, i) for i, v in enumerate(p))
    start = (center_idx - length) // 2
    return s[start:start + length]

import random, string
random.seed(11)
for _ in range(3000):
    case = "".join(random.choice("ab") for _ in range(random.randint(0, 12)))
    a, b = expand_center(case), manacher(case)
    if len(a) != len(b) or b != b[::-1] or b not in case:
        print("COUNTEREXAMPLE:", repr(case), repr(a), repr(b))
        break
else:
    print("expand_center va manacher khop tren 3000 case ngau nhien")
print(repr(manacher("babad")), repr(manacher("cbbd")), repr(manacher("")))
```

In ra `expand_center va manacher khop tren 3000 case ngau nhien` rồi `'aba' 'bb' ''` — lưu ý `"babad"` có hai đáp án dài 3 là `"bab"` và `"aba"`, Manacher trả về cái thứ hai. (So sánh theo **độ dài** vì có thể có nhiều palindrome dài bằng nhau; đề chấp nhận bất kỳ.)

Bài học: cả hai đều "đúng", chọn cái nào là quyết định về **hằng số và n**, không phải về tính đúng đắn. Với `n ≤ 1000` thì viết Manacher là lãng phí thời gian thi.

### Ví dụ 3 — tự cài heap vs `heapq`

Bài mô phỏng nhiều thao tác heap (kiểu **1046. Last Stone Weight**) là nơi hằng số ăn thịt bạn. Cùng thuật toán `O(n log n)`, khác chỗ vòng lặp chạy ở tầng nào:

```python
import heapq, random, time

class PyHeap:
    """Min-heap Python thuan - dung logic voi heapq, chi khac la chay tren interpreter."""
    def __init__(self) -> None:
        self.a: list[int] = []

    def push(self, x: int) -> None:
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i > 0:
            p = (i - 1) >> 1
            if a[p] <= a[i]:
                break
            a[p], a[i] = a[i], a[p]
            i = p

    def pop(self) -> int:
        a = self.a
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                l, r, s = 2 * i + 1, 2 * i + 2, i
                if l < n and a[l] < a[s]:
                    s = l
                if r < n and a[r] < a[s]:
                    s = r
                if s == i:
                    break
                a[i], a[s] = a[s], a[i]
                i = s
        return top

random.seed(5)
N = 200_000
data = [random.randint(0, 10**9) for _ in range(N)]

t0 = time.perf_counter()
h = PyHeap()
for x in data:
    h.push(x)
out_py = [h.pop() for _ in range(N)]
t1 = time.perf_counter()

hq: list[int] = []
for x in data:
    heapq.heappush(hq, x)
out_c = [heapq.heappop(hq) for _ in range(N)]
t2 = time.perf_counter()

print(f"PyHeap  {N} push+pop: {t1-t0:.3f}s")
print(f"heapq   {N} push+pop: {t2-t1:.3f}s  -> nhanh hon {(t1-t0)/(t2-t1):.1f}x")
print("cung ket qua:", out_py == out_c == sorted(data))
```

Đo được:

```
PyHeap  200000 push+pop: 0.314s
heapq   200000 push+pop: 0.066s  -> nhanh hon 4.7x
```

4.7x chỉ từ việc vòng lặp sift-up/sift-down chạy bằng C thay vì bytecode. Cùng `O(n log n)`, khác hằng số — và 4.7x đúng là khoảng cách giữa "AC 1.2s" và "TLE".

## Bài luyện thêm

- **3. Longest Substring Without Repeating Characters** — sliding window với `dict` lưu vị trí cuối; tránh mọi thao tác cắt substring bên trong vòng lặp. Giải chi tiết ở §07.
- **5. Longest Palindromic Substring** — expand-around-center `O(n²)` đủ cho `n ≤ 1000`; Manacher `O(n)` chỉ cần khi n lớn hơn nhiều.
- **1046. Last Stone Weight** — mỗi bước lấy hai viên nặng nhất; dùng `heapq` với dấu âm để mô phỏng max-heap thay vì tự cài heap Python thuần.

## Bài toán áp dụng

Đếm tần suất trên log lớn: bốn cách cùng `O(n)` về asymptotic, khác nhau ở tầng nào chạy vòng lặp.

```python
import random, string, time
from collections import Counter, defaultdict

random.seed(2)
words = ["".join(random.choices(string.ascii_lowercase, k=4)) for _ in range(300_000)]

def by_if(ws: list[str]) -> dict[str, int]:
    d: dict[str, int] = {}
    for w in ws:
        if w in d:
            d[w] += 1
        else:
            d[w] = 1
    return d

def by_get(ws: list[str]) -> dict[str, int]:
    d: dict[str, int] = {}
    for w in ws:
        d[w] = d.get(w, 0) + 1        # goi method Python-level moi vong -> cham nhat
    return d

def by_defaultdict(ws: list[str]) -> dict[str, int]:
    d: defaultdict[str, int] = defaultdict(int)
    for w in ws:
        d[w] += 1
    return dict(d)

def by_counter(ws: list[str]) -> dict[str, int]:
    return dict(Counter(ws))          # vong lap chay o tang C

results = {}
for fn in (by_if, by_get, by_defaultdict, by_counter):
    t0 = time.perf_counter()
    results[fn.__name__] = fn(words)
    print(f"{fn.__name__:16s} {time.perf_counter()-t0:.4f}s")

print("cung ket qua:", len({tuple(sorted(r.items())) for r in results.values()}) == 1)
```

Kết quả đo được:

```
by_if            0.0166s
by_get           0.0149s
by_defaultdict   0.0243s
by_counter       0.0127s
cung ket qua: True
```

`Counter` nhanh nhất vì toàn bộ vòng lặp đếm nằm trong C. Ba bản còn lại chạy vòng lặp trên bytecode nên xấp xỉ nhau; `by_defaultdict` ở lần đo này lại chậm nhất vì nó trả `dict(d)` — một lần copy toàn bộ bảng mà ba bản kia không phải làm. Thứ tự giữa ba bản Python-level dao động giữa các lần chạy, chỉ khoảng cách của `Counter` là ổn định. Cả bốn đều `O(n)`. Đây là hình dạng điển hình của tối ưu hằng số: không đổi thuật toán, chỉ đổi **ai** chạy vòng lặp.

## Use case thực tế

- **numpy / pandas tồn tại chính vì chương này.** `df["a"] + df["b"]` chạy một vòng lặp C trên buffer liên tục, không boxing; `for i, row in df.iterrows(): ...` chạy vòng lặp Python và tạo một `Series` object cho mỗi hàng. Chênh lệch 50–200x là bình thường. Vì vậy **"for loop thuần trên dữ liệu lớn" là red flag mặc định khi review code data.**
- **Khi nào câu trả lời đúng là "dùng thư viện có sẵn": gần như luôn.** `heapq`, `bisect`, `collections.deque`, `Counter`, `sorted`, `re`, `itertools` đều là C. Bản Python thuần của bạn sẽ đúng, sạch, dễ đọc — và chậm hơn 5–10x. Cài để học (`cores/python/`), dùng stdlib để ship và để AC.
- **Chọn ngôn ngữ cho contest.** Nếu bài yêu cầu `n = 10^6` với hằng số nặng và không vectorize được, Python đôi khi đơn giản là không đủ nhanh — biết trước điều đó tiết kiệm cho bạn 40 phút micro-optimize vô vọng.
- **Profile trước khi tối ưu.** `cProfile` / `time.perf_counter()` cho biết 90% thời gian nằm ở đâu. Tối ưu một hàm chiếm 3% tổng thời gian là công cốc, dù nó xấu đến đâu.

## Bẫy thường gặp trong Python

- **`if x in visited` với `visited` là `list`.** Lỗi complexity phổ biến nhất khi làm BFS/DFS: biến `O(V+E)` thành `O(V²)` mà không có vòng lặp lồng nào lộ ra. `visited` **luôn** là `set`.
- **`queue.pop(0)` cho BFS.** `O(n)` mỗi lần. Dùng `collections.deque` với `popleft()`.
- **Dùng `list` làm key của `dict`.** `TypeError: unhashable type: 'list'`. Chuyển sang `tuple(x)`. Với lưới 2D thưa, `d[(r, c)]` là idiom chuẩn.
- **Dựa vào thứ tự duyệt `set`.** Hash của `str` được randomize theo process, nên `list(some_set_of_strings)` cho thứ tự khác nhau giữa các lần chạy. Code "chạy đúng trên máy tôi" rồi WA trên judge thường là do đây. Cần thứ tự thì `sorted()`. (`dict` thì **có** bảo đảm giữ thứ tự chèn từ 3.7 — chỉ `set` là không.)
- **`s += c` trong vòng lặp.** Có thể nhanh nhờ tối ưu hoá của CPython, có thể `O(n²)` nếu chuỗi bị giữ tham chiếu ở nơi khác. Đừng đánh cược — dùng `"".join(parts)`.
- **Tưởng `array.array` luôn nhanh hơn `list`.** Nó tiết kiệm bộ nhớ nhưng **chậm hơn khi truy cập** vì phải box lại mỗi lần đọc. Chỉ dùng khi bị bó bởi memory.
- **`copy.deepcopy` trong vòng lặp backtracking.** Cực đắt. Thường có thể thay bằng append/pop trên một list dùng chung (undo thay vì copy).
- **`functools.lru_cache` trên tham số `list`.** Không hash được → `TypeError`. Chuyển sang `tuple` trước khi cache.
