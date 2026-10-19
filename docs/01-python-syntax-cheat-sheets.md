# Python cheat sheet + Big-O

Cú pháp Python 3 hay dùng khi code và giải LeetCode, kèm độ phức tạp từng thao tác trên CPython. n = số phần tử, k = số phần tử được thêm/lấy; O(1)\* = trung bình/amortized.

## Chọn nhanh cấu trúc dữ liệu

| Nhu cầu | Dùng | Vì sao |
| --- | --- | --- |
| Truy cập theo vị trí, duyệt tuần tự, bảng DP | `list` | Đọc/ghi theo chỉ số O(1) |
| Stack (LIFO) | `list` với `append` / `pop` | Hai thao tác ở cuối đều O(1) |
| Queue (FIFO), BFS | `deque` | `popleft` O(1); `list.pop(0)` là O(n) |
| Gom nhiều giá trị thành khoá / phần tử set | `tuple` | Bất biến nên hashable |
| Tra cứu theo khoá, ánh xạ giá trị → vị trí | `dict` | `get` / `in` O(1) trung bình |
| Đếm tần suất | `Counter` | Đếm 1 dòng, có `most_common` |
| Nhóm phần tử, danh sách kề của graph | `defaultdict(list)` | Không cần kiểm tra khoá đã có chưa |
| Kiểm tra “đã thấy chưa”, loại trùng | `set` | `in` O(1) thay vì O(n) |
| Lấy liên tục phần tử nhỏ / lớn nhất | `heapq` | push/pop O(log n) |
| Tìm trong dãy đã sắp xếp | `bisect` | O(log n), không tự viết binary search |
| LRU cache | `OrderedDict` | `move_to_end`, `popitem(last=False)` O(1) |

## Cú pháp cơ bản

### Biến, kiểu, toán tử

```python
x, y = 1, 2                 # gán nhiều biến
x, y = y, x                 # hoán đổi
a, *rest = [1, 2, 3]        # unpack: a=1, rest=[2, 3]
n: int = 5                  # type hint (không ép kiểu)
INF = float('inf')          # vô cùng

7 // 2   # 3   chia lấy nguyên (làm tròn xuống: -7 // 2 = -4)
7 % 2    # 1   chia lấy dư
2 ** 10  # 1024
divmod(7, 2)          # (3, 1)
int('42'), str(42), float('3.5'), bool([])   # ép kiểu; [] , '', 0, None là False
x is None             # so sánh định danh; dùng == cho giá trị
1 < x < 10            # so sánh chuỗi
a & b, a | b, a ^ b, ~a, a << 1, a >> 1      # bit
n.bit_count()         # số bit 1 (Python 3.10+)
```

### Điều kiện và vòng lặp

```python
if x > 0:
    ...
elif x == 0:
    ...
else:
    ...
label = 'pos' if x > 0 else 'neg'            # toán tử 3 ngôi

match cmd:                                    # Python 3.10+
    case 'up' | 'down': ...
    case _: ...

for i in range(n): ...                        # 0..n-1
for i in range(n - 1, -1, -1): ...            # đếm ngược
for i, v in enumerate(arr): ...               # chỉ số + giá trị
for a, b in zip(xs, ys): ...                  # duyệt song song
while lo <= hi: ...
for v in arr:
    if v == target: break
else:
    print('không tìm thấy')                  # chạy khi không break
```

### Comprehension

```python
sq   = [x * x for x in nums if x % 2 == 0]   # list
grid = [[0] * cols for _ in range(rows)]     # ma trận 2D đúng cách
pos  = {v: i for i, v in enumerate(nums)}    # dict
seen = {c for c in s}                        # set
gen  = (x * x for x in nums)                 # generator, lười, O(1) bộ nhớ
flat = [v for row in grid for v in row]      # làm phẳng
```

### Hàm

```python
def f(a, b=0, *args, key=None, **kwargs) -> int:
    return a + b

sq = lambda x: x * x

def outer():
    count = 0
    def inner():
        nonlocal count          # sửa biến của hàm ngoài (hay dùng trong DFS)
        count += 1
    inner()
    return count

def gen(n):
    for i in range(n):
        yield i                 # generator
```

### Class, dataclass, exception

```python
class Node:
    def __init__(self, val, next=None):
        self.val, self.next = val, next
    def __lt__(self, other):            # để đưa object vào heapq
        return self.val < other.val
    def __repr__(self):
        return f'Node({self.val})'

from dataclasses import dataclass
@dataclass(order=True)
class Job:
    priority: int
    name: str

try:
    v = d[k]
except KeyError as e:
    v = None
finally:
    ...

with open('a.txt') as f:               # tự đóng file
    lines = f.read().splitlines()

print(f'{name=} {pi:.2f} {n:,} {x:>5}')    # f-string: debug, 2 số lẻ, phân cách nghìn, căn phải
```

## list — mảng động

Thao tác ở cuối mảng là O(1); mọi thao tác ở đầu hoặc giữa là O(n) vì phải dịch phần tử.

- **Bản chất:** mảng động, các phần tử nằm liên tiếp trong bộ nhớ; có thứ tự, sửa được, chứa kiểu bất kỳ.
- **Dùng khi:** cần truy cập theo chỉ số, duyệt tuần tự, làm stack, lưu bảng DP hoặc kết quả.
- **Lợi ích:** đọc/ghi theo chỉ số O(1), thêm/xoá cuối O(1), slice gọn, duyệt nhanh nhờ bộ nhớ liên tiếp.
- **Hạn chế:** chèn/xoá ở đầu hoặc giữa O(n); `x in a` O(n).
- **Pattern LeetCode:** two pointers, sliding window, prefix sum, stack / monotonic stack, bảng DP.

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Tạo | `a = []`, `a = [0] * n`, `list(it)` | O(n) |
| Đọc / gán theo chỉ số | `a[i]`, `a[-1]`, `a[i] = v` | O(1) |
| Độ dài | `len(a)` | O(1) |
| Thêm cuối | `a.append(v)` | O(1)\* |
| Lấy cuối | `a.pop()` | O(1) |
| Lấy đầu / giữa | `a.pop(0)`, `a.pop(i)` | O(n) |
| Chèn | `a.insert(i, v)` | O(n) |
| Xoá theo chỉ số | `del a[i]` | O(n) |
| Xoá theo giá trị | `a.remove(v)` | O(n) |
| Kiểm tra tồn tại | `v in a` | O(n) |
| Tìm vị trí / đếm | `a.index(v)`, `a.count(v)` | O(n) |
| Cắt (slice) | `a[i:j]`, `a[::2]` | O(k) |
| Đảo | `a.reverse()` (tại chỗ), `a[::-1]` (bản sao) | O(n) |
| Nối thêm | `a.extend(b)`, `a += b` | O(k) |
| Nối tạo list mới | `a + b` | O(n + k) |
| Sao chép | `a.copy()`, `a[:]`, `list(a)` | O(n) |
| Sắp xếp | `a.sort()`, `a.sort(key=..., reverse=True)` | O(n log n) |
| Min / max / sum | `min(a)`, `max(a)`, `sum(a)` | O(n) |
| Xóa hết | `a.clear()` | O(n) |

```python
stack = []; stack.append(x); top = stack[-1]; stack.pop()   # list làm stack: O(1)
matrix = [[0] * m for _ in range(n)]                         # n x m
cols = list(zip(*matrix))                                    # chuyển vị ma trận
prefix = [0, *itertools.accumulate(a)]                       # prefix sum, O(n)
```

## tuple — dãy bất biến

- **Bản chất:** dãy có thứ tự, không sửa được; hashable nếu mọi phần tử hashable.
- **Dùng khi:** trả về nhiều giá trị; làm khoá dict hoặc phần tử set (toạ độ `(r, c)`, trạng thái memo); phần tử heap `(priority, item)`; bản ghi cố định.
- **Lợi ích:** hashable, nhẹ hơn list, không bị sửa nhầm; so sánh lần lượt từng phần tử nên tiện cho sort nhiều tiêu chí và heap.
- **Hạn chế:** muốn “sửa” phải tạo tuple mới O(n).
- **Pattern LeetCode:** visited trên lưới, khoá anagram `tuple(sorted(w))`, trạng thái cho `@cache`, Dijkstra `(dist, node)`.

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Tạo | `t = (1, 2)`, `t = (1,)` (1 phần tử cần dấu phẩy), `tuple(it)` | O(n) |
| Đọc / độ dài | `t[i]`, `len(t)` | O(1) |
| Kiểm tra tồn tại | `x in t` | O(n) |
| Cắt / nối | `t[i:j]`, `t1 + t2` | O(k) / O(n + m) |
| Hash / so sánh | `hash(t)`, `t1 < t2` | O(n) |
| Unpack | `a, b = t`, `x, *rest = t` | O(n) |

```python
from collections import namedtuple
Point = namedtuple('Point', 'x y')       # tuple có tên trường
p = Point(1, 2); p.x
seen.add((r, c))                         # toạ độ làm phần tử set
heapq.heappush(h, (dist, node))          # so sánh theo dist trước
sorted(people, key=lambda p: (-p[1], p[0]))   # sort nhiều tiêu chí
```

## str — chuỗi (bất biến)

Chuỗi không sửa được tại chỗ: mọi thao tác “sửa” đều tạo chuỗi mới O(n). Ghép nhiều mảnh thì gom vào list rồi `''.join()`.

- **Bản chất:** dãy ký tự Unicode bất biến.
- **Dùng khi:** xử lý văn bản, parse input, làm khoá dict sau khi chuẩn hoá.
- **Lợi ích:** hashable, nhiều method có sẵn (`split`, `strip`, `find`...), slice gọn.
- **Hạn chế:** mỗi lần “sửa” tạo chuỗi mới; ghép trong vòng lặp có thể thành O(n²).
- **Pattern LeetCode:** palindrome (two pointers), anagram (đếm 26 ô / Counter), sliding window trên chuỗi, trie, DP chuỗi (LCS, edit distance).

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Đọc ký tự / độ dài | `s[i]`, `len(s)` | O(1) |
| Cắt | `s[i:j]`, `s[::-1]` | O(k) |
| Nối 2 chuỗi | `s + t` | O(n + m) |
| Ghép nhiều mảnh | `''.join(parts)` | O(tổng độ dài) |
| Nối trong vòng lặp | `s += c` (n lần) | O(n²) xấu nhất — tránh |
| Tìm chuỗi con | `t in s`, `s.find(t)`, `s.index(t)`, `s.count(t)` | O(n·m) xấu nhất, thường \~O(n) |
| Tách / thay | `s.split(',')`, `s.replace(a, b)` | O(n) |
| Cắt khoảng trắng | `s.strip()`, `lstrip()`, `rstrip()` | O(n) |
| Hoa / thường | `s.lower()`, `s.upper()` | O(n) |
| Kiểm tra ký tự | `c.isalnum()`, `c.isdigit()`, `c.isalpha()` | O(1) mỗi ký tự |
| Tiền tố / hậu tố | `s.startswith(p)`, `s.endswith(p)` | O(len(p)) |
| Mã ký tự | `ord('a')` → 97, `chr(97)` → 'a' | O(1) |
| So sánh | `s == t`, `s < t` | O(n) |
| Sang list (để sửa) | `list(s)` rồi `''.join(lst)` | O(n) |

```python
idx = ord(c) - ord('a')                 # ánh xạ a–z → 0–25, dùng mảng đếm 26 ô
key = tuple(sorted(word))               # khoá anagram, O(k log k)
words = s.split()                       # tách theo mọi khoảng trắng
is_pal = s == s[::-1]                   # O(n) thời gian, O(n) bộ nhớ
f'{n:b}', bin(n), int('1010', 2)        # nhị phân
```

## dict, Counter, set — bảng băm

Tra cứu, thêm, xoá trung bình O(1), xấu nhất O(n) khi va chạm hash. Khoá phải hashable: `tuple` được, `list` không. dict giữ thứ tự chèn (Python 3.7+).

### dict

- **Bản chất:** bảng băm khoá → giá trị, giữ thứ tự chèn.
- **Dùng khi:** tra cứu theo khoá, ánh xạ giá trị → chỉ số, đếm, nhóm, memo, danh sách kề của graph.
- **Lợi ích:** get/set/`in` O(1) trung bình; thường biến lời giải O(n²) thành O(n) (Two Sum).
- **Hạn chế:** tốn bộ nhớ hơn list; khoá phải hashable; muốn duyệt theo giá trị phải sort.
- **Pattern LeetCode:** hash map lookup (Two Sum), prefix sum + hash map (560), grouping (Group Anagrams), memoization, graph.

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Đọc / gán | `d[k]`, `d[k] = v` | O(1)\* |
| Đọc có mặc định | `d.get(k, 0)`, `d.setdefault(k, [])` | O(1)\* |
| Kiểm tra khoá | `k in d` | O(1)\* |
| Xoá | `del d[k]`, `d.pop(k, None)` | O(1)\* |
| Xoá phần tử cuối | `d.popitem()` | O(1) |
| Duyệt | `for k, v in d.items()`, `d.keys()`, `d.values()` | O(n) |
| Kiểm tra giá trị | `v in d.values()` | O(n) |
| Gộp | `d \| other`, `d.update(other)` | O(k) |
| Sao chép | `d.copy()`, `dict(d)` | O(n) |

### defaultdict, Counter, OrderedDict

- **defaultdict** — dict tự tạo giá trị mặc định khi khoá chưa có, bỏ được `if k not in d`. Dùng cho danh sách kề của graph, nhóm phần tử, đếm bằng `defaultdict(int)`.
- **Counter** — dict chuyên đếm: có `most_common`, cộng/trừ bộ đếm, so sánh. Dùng cho tần suất, anagram, top-k, sliding window cần đếm ký tự.
- **OrderedDict** — dict có `move_to_end` và `popitem(last=False)` O(1). Dùng khi cần giữ và đổi thứ tự truy cập, điển hình là LRU cache.

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Tự tạo giá trị mặc định | `g = defaultdict(list); g[u].append(v)` | O(1)\* |
| Đếm tần suất | `cnt = Counter(s)` | O(n) |
| Top k phổ biến | `cnt.most_common(k)` | O(n log k) |
| Cộng / trừ bộ đếm | `c1 + c2`, `c1 - c2`, `c1 == c2` | O(n) |
| Đưa khoá xuống cuối | `od.move_to_end(k)` | O(1) |
| Lấy phần tử đầu | `od.popitem(last=False)` | O(1) |

### set

- **Bản chất:** tập hợp trên bảng băm, không trùng, không thứ tự.
- **Dùng khi:** kiểm tra tồn tại, loại trùng, đánh dấu đã thăm (visited) trong BFS/DFS, phép toán tập hợp.
- **Lợi ích:** `in` O(1) thay vì O(n) của list; giao / hợp / hiệu có sẵn.
- **Hạn chế:** không truy cập theo chỉ số, không giữ thứ tự; phần tử phải hashable (phần tử lồng thì dùng tuple / frozenset).
- **Pattern LeetCode:** visited, Longest Consecutive Sequence, Contains Duplicate, sliding window không lặp ký tự.

| Thao tác | Cú pháp | Big-O |
| --- | --- | --- |
| Tạo | `set()`, `{1, 2}`, `set(a)` | O(n) |
| Thêm / xoá | `s.add(x)`, `s.remove(x)` (lỗi nếu thiếu), `s.discard(x)` | O(1)\* |
| Kiểm tra | `x in s` | O(1)\* |
| Hợp | `s \| t` | O(len(s) + len(t)) |
| Giao | `s & t` | O(min(len(s), len(t))) |
| Hiệu / hiệu đối xứng | `s - t`, `s ^ t` | O(len(s)) / O(len(s) + len(t)) |
| Tập con | `s <= t`, `s.issubset(t)` | O(len(s)) |
| Set bất biến (làm khoá dict) | `frozenset(s)` | O(n) |

```python
from collections import defaultdict, Counter, OrderedDict
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v); graph[v].append(u)    # danh sách kề, O(E)

Counter(s) == Counter(t)                      # kiểm tra anagram, O(n)

class LRU(OrderedDict):                       # LRU cache gọn: get/put O(1)
    def __init__(self, cap): super().__init__(); self.cap = cap
    def get(self, k):
        if k not in self: return -1
        self.move_to_end(k); return self[k]
    def put(self, k, v):
        self[k] = v; self.move_to_end(k)
        if len(self) > self.cap: self.popitem(last=False)
```

## deque, heapq, bisect

`deque` cho queue/BFS, `heapq` cho top-k/Dijkstra (chỉ có min-heap), `bisect` cho binary search trên list đã sort.

- **deque**
  - Bản chất: hàng đợi hai đầu (danh sách liên kết các khối bộ nhớ).
  - Dùng khi: queue FIFO cho BFS, sliding window maximum (monotonic deque), giữ k phần tử gần nhất với `maxlen`.
  - Lợi ích: thêm/lấy ở cả hai đầu O(1).
  - Hạn chế: truy cập giữa O(n), không slice được.
- **heapq**
  - Bản chất: min-heap trên list thường (cây nhị phân ngầm), phần tử nhỏ nhất luôn ở `h[0]`.
  - Dùng khi: cần lấy liên tục phần tử nhỏ/lớn nhất trong tập đang thay đổi: top-k, Merge k Sorted Lists, Dijkstra, lập lịch, median stream (hai heap).
  - Lợi ích: push/pop O(log n), xem min O(1); top-k O(n log k) nhanh hơn sort O(n log n).
  - Hạn chế: chỉ có min-heap (max-heap dùng số âm); không tìm/xoá phần tử bất kỳ nhanh (dùng lazy deletion).
- **bisect**
  - Bản chất: binary search có sẵn trên list đã sắp xếp.
  - Dùng khi: tìm vị trí chèn, đếm số phần tử ≤ x, LIS O(n log n), Time Based Key-Value Store.
  - Lợi ích: O(log n), tránh lỗi biên khi tự viết binary search.
  - Hạn chế: list phải đã sort; `insort` chèn O(n), nên chèn nhiều thì dùng heap hoặc `SortedList` (thư viện sortedcontainers, LeetCode có sẵn).

| Cấu trúc | Thao tác | Cú pháp | Big-O |
| --- | --- | --- | --- |
| deque | Thêm / lấy hai đầu | `q.append(x)`, `q.appendleft(x)`, `q.pop()`, `q.popleft()` | O(1) |
| deque | Đọc hai đầu | `q[0]`, `q[-1]` | O(1) |
| deque | Đọc giữa | `q[i]` | O(n) |
| deque | Giới hạn độ dài | `deque(maxlen=k)` (tự bỏ phần tử cũ) | O(1) mỗi lần thêm |
| deque | Xoay | `q.rotate(k)` | O(k) |
| heapq | Tạo heap từ list | `heapq.heapify(a)` (tại chỗ) | O(n) |
| heapq | Thêm | `heapq.heappush(h, x)` | O(log n) |
| heapq | Lấy nhỏ nhất | `heapq.heappop(h)` | O(log n) |
| heapq | Xem nhỏ nhất | `h[0]` | O(1) |
| heapq | Push rồi pop / pop rồi push | `heapq.heappushpop(h, x)`, `heapq.heapreplace(h, x)` | O(log n) |
| heapq | k lớn / nhỏ nhất | `heapq.nlargest(k, a)`, `heapq.nsmallest(k, a, key=...)` | O(n log k) |
| heapq | Trộn các dãy đã sort | `heapq.merge(*lists)` | O(N log k) |
| bisect | Vị trí chèn | `bisect.bisect_left(a, x)`, `bisect.bisect_right(a, x)` | O(log n) |
| bisect | Chèn giữ thứ tự | `bisect.insort(a, x)` | O(n) (tìm O(log n) + dịch O(n)) |

```python
from collections import deque
import heapq, bisect

q = deque([start]); seen = {start}            # BFS
while q:
    u = q.popleft()

h = []
heapq.heappush(h, -x)                         # max-heap: đẩy số âm
heapq.heappush(h, (dist, node))               # tuple so sánh theo phần tử đầu

h = []                                        # top-k lớn nhất, O(n log k)
for x in nums:
    heapq.heappush(h, x)
    if len(h) > k: heapq.heappop(h)

i = bisect.bisect_left(a, x)                  # phần tử đầu tiên >= x
bisect.bisect_left(a, x, key=lambda r: r[0])  # key= từ Python 3.10
```

## Built-in, sort, itertools, functools

`sorted`/`.sort()` dùng Timsort, ổn định (stable), O(n log n) và O(n) bộ nhớ phụ. `enumerate`, `zip`, `map`, `filter`, `range` là lười: mỗi bước O(1), không tạo list.

| Hàm | Cú pháp | Big-O |
| --- | --- | --- |
| Sắp xếp | `sorted(a, key=lambda x: (-x[1], x[0]), reverse=False)` | O(n log n) |
| Min / max có key | `max(a, key=len)`, `min(d, key=d.get)` | O(n) |
| Tổng / any / all | `sum(a)`, `any(x > 0 for x in a)`, `all(...)` | O(n), any/all dừng sớm |
| range | `range(a, b, step)`, `x in range(n)` | tạo O(1); `in` O(1) với số nguyên |
| Đảo lười | `reversed(a)` | O(1) tạo, O(n) duyệt |
| Lũy thừa modulo | `pow(a, b, m)` | O(log b) |
| ƯCLN / tổ hợp | `math.gcd(a, b)`, `math.lcm`, `math.comb(n, k)`, `math.isqrt(n)` | gcd O(log min(a, b)) |
| Cộng dồn | `itertools.accumulate(a)`, `accumulate(a, max)` | O(n) |
| Hoán vị / tổ hợp | `permutations(a, r)`, `combinations(a, r)` | O(n!) / O(C(n, r)) |
| Tích Descartes | `product(a, b)`, `product('01', repeat=n)` | O(∏ kích thước) |
| Nhóm liên tiếp | `groupby(sorted(a))` | O(n) |
| Cặp liền kề | `itertools.pairwise(a)` (3.10+) | O(n) |
| Nối iterable | `chain(a, b)`, `chain.from_iterable(lists)` | O(n) |
| Memo hoá | `@functools.cache`, `@lru_cache(maxsize=None)` | mỗi trạng thái tính 1 lần |
| Fold | `functools.reduce(op, a, init)` | O(n) |
| So sánh tùy biến khi sort | `sorted(a, key=functools.cmp_to_key(cmp))` | O(n log n) |

```python
from functools import cache, cmp_to_key
from itertools import accumulate, combinations, permutations, product, groupby, pairwise

@cache
def dp(i, j):                       # DP top-down: O(số trạng thái × chi phí mỗi trạng thái)
    if i == n: return 0
    return max(dp(i + 1, j), val[i] + dp(i + 1, j - w[i]) if j >= w[i] else 0)

largest_number = ''.join(sorted(map(str, nums), key=cmp_to_key(lambda a, b: (b + a > a + b) - (b + a < a + b))))
```

## Template LeetCode

Khung code cho các pattern trong tab LeetCode 16 tuần. V = số đỉnh, E = số cạnh.

| Pattern | Thời gian | Bộ nhớ |
| --- | --- | --- |
| Binary search trên đáp án | O(log(hi − lo) × chi phí ok()) | O(1) |
| Sliding window | O(n) | O(k) |
| Monotonic stack | O(n) | O(n) |
| BFS / DFS | O(V + E) | O(V) |
| Topological sort (Kahn) | O(V + E) | O(V) |
| Union-Find (nén đường + theo size) | \~O(α(n)) mỗi thao tác | O(n) |
| Dijkstra với heapq | O((V + E) log V) | O(V + E) |
| Backtracking (subsets) | O(n · 2ⁿ) | O(n) |

```python
# Binary search: tìm giá trị nhỏ nhất thỏa ok()
lo, hi = 0, 10**9
while lo < hi:
    mid = (lo + hi) // 2
    if ok(mid): hi = mid
    else: lo = mid + 1

# Sliding window co giãn
cnt, left, best = Counter(), 0, 0
for right, c in enumerate(s):
    cnt[c] += 1
    while not valid(cnt):
        cnt[s[left]] -= 1; left += 1
    best = max(best, right - left + 1)

# Monotonic stack: phần tử lớn hơn kế tiếp
res, st = [-1] * n, []
for i, v in enumerate(a):
    while st and a[st[-1]] < v:
        res[st.pop()] = i
    st.append(i)

# BFS trên lưới
q, seen = deque([(r0, c0)]), {(r0, c0)}
while q:
    r, c = q.popleft()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen and grid[nr][nc] == '1':
            seen.add((nr, nc)); q.append((nr, nc))

# Topological sort (Kahn)
indeg = [0] * n
for u, v in edges: graph[u].append(v); indeg[v] += 1
q = deque(i for i in range(n) if indeg[i] == 0); order = []
while q:
    u = q.popleft(); order.append(u)
    for v in graph[u]:
        indeg[v] -= 1
        if indeg[v] == 0: q.append(v)
has_cycle = len(order) < n

# Union-Find
parent, size = list(range(n)), [1] * n
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb: return False
    if size[ra] < size[rb]: ra, rb = rb, ra
    parent[rb] = ra; size[ra] += size[rb]; return True

# Dijkstra
dist = {src: 0}; h = [(0, src)]
while h:
    d, u = heapq.heappop(h)
    if d > dist.get(u, INF): continue
    for v, w in graph[u]:
        nd = d + w
        if nd < dist.get(v, INF):
            dist[v] = nd; heapq.heappush(h, (nd, v))

# Backtracking
res, path = [], []
def bt(i):
    if i == len(nums):
        res.append(path[:]); return      # path[:] là bản sao O(n)
    path.append(nums[i]); bt(i + 1); path.pop()
    bt(i + 1)
bt(0)
```

## Bẫy hay gặp

| Bẫy | Sai | Đúng |
| --- | --- | --- |
| Ma trận dùng chung hàng | `[[0] * m] * n` (n hàng cùng 1 list) | `[[0] * m for _ in range(n)]` |
| Queue bằng list | `a.pop(0)` → O(n) | `deque.popleft()` → O(1) |
| Kiểm tra tồn tại trong vòng lặp | `if x in lst` → O(n), cả vòng O(n²) | chuyển sang `set` trước → O(1) |
| Nối chuỗi trong vòng lặp | `s += c` | gom list rồi `''.join(parts)` |
| Tham số mặc định mutable | `def f(a=[])` (dùng chung giữa các lần gọi) | `def f(a=None): a = a or []` |
| Lưu path trong backtracking | `res.append(path)` (cùng tham chiếu) | `res.append(path[:])` |
| Đệ quy sâu | mặc định \~1.000 tầng → RecursionError | `sys.setrecursionlimit(10**6)` hoặc đổi sang stack/BFS |
| Chia số âm | `-7 // 2 == -4` | làm tròn về 0: `int(-7 / 2)` |
| Sao chép nông | `b = a` hoặc `a[:]` với list lồng | `copy.deepcopy(a)` |
| Sửa dict/set khi đang duyệt | `for k in d: del d[k]` → RuntimeError | `for k in list(d):` |
| heapq với object không so sánh được | `heappush(h, (d, node))` lỗi khi d bằng nhau | `(d, id_tang_dan, node)` hoặc định nghĩa `__lt__` |
| `@cache` trên hàm nhận list | list không hashable → TypeError | truyền `tuple` hoặc chỉ số |

Số nguyên Python không tràn số (độ chính xác tùy ý), nhưng phép nhân số rất lớn không còn O(1). Độ phức tạp trong tab này theo CPython; nguồn tham khảo: [Python Wiki – TimeComplexity](https://wiki.python.org/moin/TimeComplexity) và [tài liệu heapq](https://docs.python.org/3/library/heapq.html), [bisect](https://docs.python.org/3/library/bisect.html), [collections](https://docs.python.org/3/library/collections.html).
