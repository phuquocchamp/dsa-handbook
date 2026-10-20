# Python cheat sheet + Big-O

Cú pháp Python 3 hay dùng khi code và giải LeetCode, kèm độ phức tạp của từng thao tác trên CPython.

Mỗi cấu trúc dữ liệu được trình bày theo cùng một khung:

1. **Là gì**: bản chất bên trong.
2. **Dùng để làm gì**: các tình huống cụ thể.
3. **Vì sao chọn nó**: so với lựa chọn khác thì hơn ở đâu.
4. **Big-O tóm tắt**: các thao tác cốt lõi và bộ nhớ.
5. **Code**: mỗi dòng một thao tác, comment `# O(...)` ở cuối.
6. **Bẫy** và **Pattern LeetCode**.

Ký hiệu: `n` = số phần tử, `k` = số phần tử được thêm / lấy / cắt, `O(1)*` = trung bình hoặc amortized (xem [mục 0](#0-đọc-big-o)).

## Mục lục

- [0. Đọc Big-O](#0-đọc-big-o)
- [1. Chọn nhanh cấu trúc dữ liệu](#1-chọn-nhanh-cấu-trúc-dữ-liệu)
- [2. Cú pháp cơ bản](#2-cú-pháp-cơ-bản)
- [3. int và math](#3-int-và-math)
- [4. list](#4-list--mảng-động)
- [5. tuple](#5-tuple--dãy-bất-biến)
- [6. str](#6-str--chuỗi-bất-biến)
- [7. dict](#7-dict--bảng-băm-khoá--giá-trị)
- [8. defaultdict, Counter, OrderedDict](#8-defaultdict-counter-ordereddict)
- [9. set](#9-set--tập-hợp)
- [10. deque](#10-deque--hàng-đợi-hai-đầu)
- [11. heapq](#11-heapq--min-heap)
- [12. bisect](#12-bisect--binary-search-có-sẵn)
- [13. SortedList](#13-sortedlist--dãy-luôn-được-sắp-xếp)
- [14. Sort và built-in](#14-sort-và-built-in)
- [15. itertools và functools](#15-itertools-và-functools)
- [16. Template LeetCode](#16-template-leetcode)
- [17. Bẫy hay gặp](#17-bẫy-hay-gặp)

## 0. Đọc Big-O

**Là gì:** Big-O mô tả chi phí (thời gian hoặc bộ nhớ) tăng thế nào khi input lớn dần. Nó bỏ qua hằng số và chỉ giữ thành phần tăng nhanh nhất: `3n² + 5n + 7` → `O(n²)`.

**Vì sao cần:** trước khi code, nhìn ràng buộc của đề (`n ≤ 10^5`...) là biết lời giải nào sẽ bị TLE (Time Limit Exceeded), lời giải nào chạy kịp.

### Các lớp độ phức tạp thường gặp

| Big-O | Tên | Ví dụ |
| --- | --- | --- |
| O(1) | hằng số | `a[i]`, `d[k]`, `x in set` |
| O(log n) | logarit | binary search, `heappush` |
| O(n) | tuyến tính | duyệt 1 vòng, `x in list`, `sum(a)` |
| O(n log n) | | `sorted(a)`, n lần thao tác heap |
| O(n²) | bình phương | 2 vòng lồng nhau, DP 2 chiều |
| O(2ⁿ) | mũ | duyệt mọi tập con |
| O(n!) | giai thừa | duyệt mọi hoán vị |

### Nhìn ràng buộc, đoán độ phức tạp

Python chạy khoảng **10^7 phép tính đơn giản mỗi giây**. Từ đó suy ra:

| n tối đa | Độ phức tạp chạy kịp | Hướng giải thường gặp |
| --- | --- | --- |
| ≤ 10 | O(n!) | hoán vị, backtracking |
| ≤ 20 | O(2ⁿ) | tập con, bitmask DP |
| ≤ 500 | O(n³) | DP 3 chiều, Floyd–Warshall |
| ≤ 5 · 10³ | O(n²) | DP 2 chiều, 2 vòng lồng |
| ≤ 10⁶ | O(n log n) hoặc O(n) | sort, heap, two pointers, hash map |
| > 10⁶ | O(log n) hoặc O(1) | binary search, công thức toán |

### Trung bình, amortized, xấu nhất

- **Xấu nhất (worst case):** chi phí lớn nhất có thể của một lần gọi.
- **Trung bình (average):** chi phí kỳ vọng. Ví dụ `d[k]` trung bình O(1), nhưng xấu nhất O(n) khi nhiều khoá va chạm hash.
- **Amortized:** chia đều chi phí cho một dãy thao tác. `list.append` thỉnh thoảng phải cấp phát lại và chép cả mảng (O(n)), nhưng tính trung bình trên n lần append thì mỗi lần vẫn O(1).

Trong tài liệu này cả hai trường hợp trung bình và amortized đều ghi là `O(1)*`.

### Cách tính nhanh

```python
for x in a: ...                   # O(n)
for x in a:
    for y in a: ...               # lồng nhau thì nhân: O(n²)
a.sort()                          # nối tiếp thì cộng, giữ phần lớn nhất:
for x in a: ...                   # O(n log n) + O(n) = O(n log n)
while n > 1: n //= 2              # mỗi bước chia đôi: O(log n)
for x in a:
    if x in lst: ...              # thao tác O(n) bên trong vòng O(n): O(n²). Đổi lst thành set: O(n)
```

**Bộ nhớ (space complexity):** tính phần bộ nhớ **phụ** mà thuật toán tạo thêm, không tính input. Đệ quy sâu `d` tầng tốn O(d) bộ nhớ cho call stack. Slice và copy tạo list mới nên cũng tốn bộ nhớ.

## 1. Chọn nhanh cấu trúc dữ liệu

| Nhu cầu | Dùng | Vì sao |
| --- | --- | --- |
| Truy cập theo vị trí, duyệt tuần tự, bảng DP | `list` | Đọc/ghi theo chỉ số O(1) |
| Stack (LIFO) | `list` với `append` / `pop` | Hai thao tác ở cuối đều O(1) |
| Queue (FIFO), BFS | `deque` | `popleft` O(1); `list.pop(0)` là O(n) |
| Gom nhiều giá trị thành khoá / phần tử set | `tuple` | Bất biến nên hashable |
| Tra cứu theo khoá, ánh xạ giá trị → vị trí | `dict` | `get` / `in` O(1)\* |
| Đếm tần suất | `Counter` | Đếm 1 dòng, có `most_common` |
| Nhóm phần tử, danh sách kề của graph | `defaultdict(list)` | Không cần kiểm tra khoá đã có chưa |
| Kiểm tra "đã thấy chưa", loại trùng | `set` | `in` O(1)\* thay vì O(n) |
| Lấy liên tục phần tử nhỏ / lớn nhất | `heapq` | push/pop O(log n) |
| Tìm trong dãy đã sắp xếp (không đổi) | `bisect` | O(log n), khỏi tự viết binary search |
| Dãy sắp xếp mà phải thêm / xoá liên tục | `SortedList` | add/remove/tìm đều O(log n) |
| LRU cache | `OrderedDict` | `move_to_end`, `popitem(last=False)` O(1) |

## 2. Cú pháp cơ bản

### Biến, kiểu, toán tử

```python
x, y = 1, 2                 # gán nhiều biến
x, y = y, x                 # hoán đổi, O(1)
a, *rest = [1, 2, 3]        # unpack: a=1, rest=[2, 3]; tạo list mới O(n)
n: int = 5                  # type hint, chỉ để đọc, không ép kiểu
INF = float('inf')          # vô cùng, dùng làm giá trị khởi tạo cho min

7 // 2                      # 3   chia lấy nguyên, làm tròn XUỐNG: -7 // 2 = -4
7 % 2                       # 1   chia lấy dư, luôn cùng dấu với số chia: -7 % 2 = 1
-(-7 // 2)                  # 4   chia làm tròn LÊN (ceil) không qua float
2 ** 10                     # 1024
divmod(7, 2)                # (3, 1)
int('42'), str(42), float('3.5'), bool([])   # ép kiểu; [], '', 0, None đều là False
x is None                   # so sánh định danh; so sánh giá trị thì dùng ==
1 < x < 10                  # so sánh chuỗi, tương đương 1 < x and x < 10
```

### Toán tử bit

```python
a & b, a | b, a ^ b, ~a     # AND, OR, XOR, NOT                       O(1) với số nhỏ
a << 1, a >> 1              # nhân 2, chia 2 (làm tròn xuống)         O(1)
n & 1                       # kiểm tra lẻ                             O(1)
n & (n - 1)                 # xoá bit 1 thấp nhất; == 0 nghĩa là n là luỹ thừa của 2
n & -n                      # giữ lại bit 1 thấp nhất
(mask >> i) & 1             # bit thứ i có bật không
mask | (1 << i)             # bật bit i
n.bit_count()               # số bit 1 (Python 3.10+)                 O(số bit)
n.bit_length()              # số bit cần để biểu diễn n               O(1)
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

for i in range(n): ...                        # 0..n-1                  O(n)
for i in range(n - 1, -1, -1): ...            # đếm ngược n-1..0        O(n)
for i, v in enumerate(arr): ...               # chỉ số + giá trị        O(n)
for a, b in zip(xs, ys): ...                  # duyệt song song, dừng ở dãy ngắn hơn
while lo <= hi: ...
for v in arr:
    if v == target: break
else:
    print('không tìm thấy')                  # nhánh else chạy khi vòng lặp KHÔNG gặp break
```

### Comprehension

**Là gì:** cú pháp tạo list / dict / set / generator trong một dòng. Nhanh hơn vòng `for` + `append` một chút vì chạy trong C.

```python
sq   = [x * x for x in nums if x % 2 == 0]   # list                    O(n) thời gian, O(n) bộ nhớ
grid = [[0] * cols for _ in range(rows)]     # ma trận 2D đúng cách    O(rows · cols)
pos  = {v: i for i, v in enumerate(nums)}    # dict                    O(n)
seen = {c for c in s}                        # set                     O(n)
gen  = (x * x for x in nums)                 # generator: lười, O(1) bộ nhớ, chỉ duyệt được 1 lần
flat = [v for row in grid for v in row]      # làm phẳng: vòng ngoài viết trước
total = sum(x * x for x in nums)             # truyền generator thẳng vào hàm, không tạo list
```

### Hàm

```python
def f(a, b=0, *args, key=None, **kwargs) -> int:
    return a + b                # *args gom tham số vị trí thừa thành tuple, **kwargs gom tham số tên thành dict

sq = lambda x: x * x            # hàm ẩn danh, hay dùng làm key= khi sort

def outer():
    count = 0
    def inner():
        nonlocal count          # sửa biến của hàm ngoài (hay dùng trong DFS)
        count += 1
    inner()
    return count

def gen(n):
    for i in range(n):
        yield i                 # generator: trả từng giá trị, O(1) bộ nhớ
```

**Chi phí đệ quy:** thời gian = số lần gọi × chi phí mỗi lần gọi; bộ nhớ = độ sâu đệ quy. Python mặc định giới hạn khoảng 1000 tầng, xem [Bẫy](#17-bẫy-hay-gặp).

### Class, dataclass, exception, f-string

```python
class Node:
    def __init__(self, val, next=None):
        self.val, self.next = val, next
    def __lt__(self, other):            # cho phép so sánh <, cần để đưa object vào heapq
        return self.val < other.val
    def __repr__(self):                 # chuỗi hiển thị khi print / debug
        return f'Node({self.val})'

from dataclasses import dataclass
@dataclass(order=True)                  # tự sinh __init__, __repr__, __eq__ và các phép so sánh theo thứ tự trường
class Job:
    priority: int
    name: str

try:
    v = d[k]
except KeyError as e:
    v = None
finally:
    ...                                 # luôn chạy, dù có lỗi hay không

with open('a.txt') as f:               # with tự đóng file khi ra khỏi khối
    lines = f.read().splitlines()

print(f'{name=} {pi:.2f} {n:,} {x:>5} {n:b}')   # debug "name=...", 2 số lẻ, phân cách nghìn, căn phải 5 ô, nhị phân
```

## 3. int và math

**Là gì:** `int` của Python có **độ chính xác tuỳ ý**: không bao giờ tràn số như `int` 32/64 bit của C++/Java.

**Vì sao cần biết:** khỏi lo tràn số khi nhân lớn. Đổi lại, phép tính trên số rất lớn không còn O(1). Với bài "trả kết quả modulo 10^9 + 7", vẫn phải lấy `% MOD` sau mỗi bước để số luôn nhỏ (xem [02-modular-arithmetic-combinatorics.md](02-modular-arithmetic-combinatorics.md)).

```python
import math

MOD = 10**9 + 7                 # đúng; 1e9 + 7 là float, sai
a + b, a * b                    # O(1) khi số vừa 64 bit; số d chữ số: cộng O(d), nhân ~O(d^1.58)
pow(a, b, m)                    # a^b mod m bằng bình phương liên tiếp          O(log b)
pow(a, -1, m)                   # nghịch đảo modulo (3.8+), cần gcd(a, m) = 1    O(log m)
math.gcd(a, b), math.lcm(a, b)  # ước chung lớn nhất, bội chung nhỏ nhất         O(log min(a, b))
math.isqrt(n)                   # căn bậc hai nguyên, chính xác với số lớn       nhanh hơn int(n ** 0.5) và không sai số float
math.comb(n, k), math.perm(n, k)  # tổ hợp C(n, k), chỉnh hợp P(n, k)
math.factorial(n)               # n!
abs(x), max(a, b), min(a, b)    # O(1)
float('inf'), -float('inf')     # dương / âm vô cùng
```

## 4. list — mảng động

**Là gì:** mảng động, các phần tử (thực ra là con trỏ tới object) nằm liên tiếp trong bộ nhớ. Có thứ tự, sửa được, chứa kiểu bất kỳ. Khi đầy, Python cấp phát mảng lớn hơn và chép sang.

**Dùng để làm gì:** truy cập theo chỉ số, duyệt tuần tự, làm stack, lưu bảng DP hoặc kết quả.

**Vì sao chọn nó:** đọc/ghi theo chỉ số O(1), thêm/xoá ở cuối O(1)\*, slice gọn, duyệt nhanh vì bộ nhớ liên tiếp. Nhưng mọi thao tác ở **đầu hoặc giữa** đều O(n) vì phải dịch các phần tử phía sau.

| Truy cập `a[i]` | Tìm `x in a` | Thêm / xoá cuối | Thêm / xoá đầu, giữa | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(1) | O(n) | O(1)\* | O(n) | O(n) |

```python
# Tạo
a = []                          # O(1)
a = [0] * n                     # O(n)
a = list(iterable)              # O(n)
len(a)                          # O(1), độ dài được lưu sẵn

# Đọc / ghi
a[i], a[-1]                     # O(1)   chỉ số âm đếm từ cuối
a[i] = v                        # O(1)

# Thêm / xoá ở cuối: rẻ
a.append(v)                     # O(1)*  amortized
a.pop()                         # O(1)   lấy và xoá phần tử cuối

# Thêm / xoá ở đầu hoặc giữa: đắt, phải dịch phần tử
a.pop(0)                        # O(n)   cần lấy ở đầu thì dùng deque
a.pop(i)                        # O(n - i)
a.insert(i, v)                  # O(n)
del a[i]                        # O(n)
a.remove(v)                     # O(n)   xoá lần xuất hiện đầu tiên, ValueError nếu không có

# Tìm
v in a                          # O(n)   tìm nhiều lần thì chuyển sang set
a.index(v)                      # O(n)   ValueError nếu không có
a.count(v)                      # O(n)
min(a), max(a), sum(a)          # O(n)

# Cắt, nối, sao chép: đều tạo list mới, tốn thêm bộ nhớ
a[i:j], a[::2]                  # O(k)   k = số phần tử lấy ra
a[::-1]                         # O(n)   bản sao đảo ngược
a.reverse()                     # O(n)   đảo tại chỗ, O(1) bộ nhớ phụ
a.extend(b); a += b             # O(k)   k = len(b), sửa a tại chỗ
a + b                           # O(n + k) tạo list mới
a * k                           # O(n · k)
a.copy(), a[:], list(a)         # O(n)   sao chép NÔNG
a.clear()                       # O(n)

# Sắp xếp
a.sort()                        # O(n log n), tại chỗ, ổn định (stable)
a.sort(key=lambda x: -x, reverse=True)
sorted(a)                       # O(n log n) thời gian, O(n) bộ nhớ, trả list mới

# Dùng nhiều
stack = []; stack.append(x); top = stack[-1]; stack.pop()   # list làm stack: mọi thao tác O(1)
matrix = [[0] * m for _ in range(n)]                         # ma trận n x m: O(n · m)
cols = list(zip(*matrix))                                    # chuyển vị ma trận: O(n · m)
prefix = [0, *itertools.accumulate(a)]                       # prefix sum O(n); tổng a[i:j] = prefix[j] - prefix[i] O(1)
```

**Bẫy:**

- `[[0] * m] * n` tạo n tham chiếu tới **cùng một** list. Sửa một hàng thì mọi hàng đổi theo.
- `a.pop(0)` trong vòng lặp làm BFS thành O(n²).
- `b = a` không sao chép mà chỉ thêm một tên mới cho cùng list.

**Pattern LeetCode:** two pointers, sliding window, prefix sum, stack / monotonic stack, bảng DP.

## 5. tuple — dãy bất biến

**Là gì:** dãy có thứ tự, không sửa được. Hashable nếu mọi phần tử bên trong đều hashable.

**Dùng để làm gì:** trả về nhiều giá trị; làm khoá dict hoặc phần tử set (toạ độ `(r, c)`, trạng thái memo); phần tử heap `(priority, item)`; bản ghi cố định.

**Vì sao chọn nó:** hashable nên dùng được làm khoá, khác với list. Nhẹ hơn list và không bị sửa nhầm. So sánh lần lượt từng phần tử (lexicographic), nên tiện cho sort nhiều tiêu chí và cho heap.

| Truy cập `t[i]` | Tìm `x in t` | Hash / so sánh | "Sửa" | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(1) | O(n) | O(n) | O(n), phải tạo tuple mới | O(n) |

```python
t = (1, 2)                      # O(n)
t = (1,)                        # tuple 1 phần tử BẮT BUỘC có dấu phẩy; (1) chỉ là số 1
t = tuple(iterable)             # O(n)
t[i], len(t)                    # O(1)
x in t                          # O(n)
t[i:j]                          # O(k)
t1 + t2                         # O(n + m)
hash(t)                         # O(n), không được cache, mỗi lần dùng làm khoá là tính lại
t1 < t2                         # O(n) xấu nhất, so lần lượt từng phần tử
a, b = t                        # unpack O(n)
x, *rest = t                    # rest là list

from collections import namedtuple
Point = namedtuple('Point', 'x y')       # tuple có tên trường
p = Point(1, 2); p.x                     # O(1)

seen.add((r, c))                         # toạ độ làm phần tử set
heapq.heappush(h, (dist, node))          # heap so sánh dist trước, bằng nhau mới so node
sorted(people, key=lambda p: (-p[1], p[0]))   # sort nhiều tiêu chí: p[1] giảm dần, rồi p[0] tăng dần
key = tuple(sorted(word))                # khoá anagram O(k log k)
```

**Bẫy:** tuple chứa list (`(1, [2])`) thì không hash được. Hash một tuple dài làm khoá dict tốn O(n) mỗi lần tra.

**Pattern LeetCode:** visited trên lưới, khoá anagram, trạng thái cho `@cache`, Dijkstra `(dist, node)`.

## 6. str — chuỗi (bất biến)

**Là gì:** dãy ký tự Unicode bất biến. Hash của chuỗi được tính một lần rồi cache lại.

**Dùng để làm gì:** xử lý văn bản, parse input, làm khoá dict sau khi chuẩn hoá.

**Vì sao cần chú ý:** chuỗi không sửa được tại chỗ, nên mọi thao tác "sửa" đều tạo chuỗi mới O(n). Ghép nhiều mảnh thì gom vào list rồi `''.join()` một lần.

| Truy cập `s[i]` | Tìm chuỗi con | Nối `s + t` | "Sửa" | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(1) | thường ~O(n), xấu nhất O(n · m) | O(n + m) | O(n), tạo chuỗi mới | O(n) |

```python
# Đọc
s[i], len(s)                    # O(1)
s[i:j], s[::-1]                 # O(k), tạo chuỗi mới
ord('a'), chr(97)               # 97, 'a'                O(1)

# Ghép
s + t                           # O(n + m)
''.join(parts)                  # O(tổng độ dài)   cách đúng để ghép nhiều mảnh
s += c                          # trong vòng lặp n lần có thể thành O(n²), tránh

# Tìm
t in s                          # thường ~O(n), xấu nhất O(n · m)
s.find(t)                       # như trên, trả -1 nếu không có
s.index(t)                      # như trên, ValueError nếu không có
s.count(t)                      # O(n)
s.startswith(p), s.endswith(p)  # O(len(p))

# Biến đổi: đều O(n), trả chuỗi mới
s.split(','), s.split()         # split() không tham số tách theo mọi khoảng trắng
s.replace(a, b)
s.strip(), s.lstrip(), s.rstrip()
s.lower(), s.upper()
s == t, s < t                   # O(n) xấu nhất

# Kiểm tra ký tự
c.isalnum(), c.isdigit(), c.isalpha(), c.isspace()   # O(1) với một ký tự, O(n) với cả chuỗi

# Cần sửa nhiều lần: đổi sang list rồi ghép lại
chars = list(s)                 # O(n)
chars[0] = 'X'                  # O(1)
s = ''.join(chars)              # O(n)

# Dùng nhiều
idx = ord(c) - ord('a')                 # ánh xạ a–z → 0–25, dùng mảng đếm 26 ô thay cho dict
key = tuple(sorted(word))               # khoá anagram O(k log k)
is_pal = s == s[::-1]                   # palindrome O(n) thời gian, O(n) bộ nhớ (two pointers thì O(1) bộ nhớ)
bin(n), f'{n:b}', int('1010', 2)        # nhị phân ↔ số
```

**Bẫy:** `s[i] = 'x'` báo `TypeError`. `str(n)` với số hơn 4300 chữ số báo `ValueError` (Python 3.11+, đổi bằng `sys.set_int_max_str_digits`).

**Pattern LeetCode:** palindrome (two pointers), anagram (đếm 26 ô hoặc Counter), sliding window trên chuỗi, trie, DP chuỗi (LCS, edit distance).

## 7. dict — bảng băm khoá → giá trị

**Là gì:** bảng băm (hash table) ánh xạ khoá → giá trị. Giữ thứ tự chèn (Python 3.7+). Khoá phải hashable: `int`, `str`, `tuple` được; `list`, `dict`, `set` thì không.

**Dùng để làm gì:** tra cứu theo khoá, ánh xạ giá trị → chỉ số, đếm, nhóm, memo, danh sách kề của graph.

**Vì sao chọn nó:** get / set / `in` đều O(1)\*. Thường biến lời giải O(n²) thành O(n): Two Sum dùng dict để thay vòng lặp thứ hai.

| Đọc / ghi `d[k]` | Tìm khoá `k in d` | Xoá | Duyệt | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(1)\* | O(1)\* | O(1)\* | O(n) | O(n), nhiều hơn list |

`O(1)*` là trung bình; xấu nhất O(n) khi nhiều khoá va chạm hash, hầu như không gặp trên LeetCode.

```python
d = {}, dict(), {'a': 1}        # O(1) / O(n)
d = dict(zip(keys, vals))       # O(n)

# Đọc / ghi
d[k]                            # O(1)*  KeyError nếu thiếu khoá
d[k] = v                        # O(1)*
d.get(k, 0)                     # O(1)*  trả mặc định nếu thiếu, không thêm khoá
d.setdefault(k, []).append(x)   # O(1)*  thêm khoá với giá trị mặc định nếu thiếu
k in d                          # O(1)*  kiểm tra KHOÁ
v in d.values()                 # O(n)   kiểm tra GIÁ TRỊ phải duyệt hết

# Xoá
del d[k]                        # O(1)*  KeyError nếu thiếu
d.pop(k, None)                  # O(1)*  không lỗi nếu thiếu
d.popitem()                     # O(1)   xoá cặp được chèn sau cùng (LIFO)

# Duyệt: O(n), theo thứ tự chèn
for k, v in d.items(): ...
d.keys(), d.values()            # view, O(1) tạo, O(n) duyệt

# Gộp, sao chép
d.update(other)                 # O(k), k = len(other), sửa d tại chỗ
d | other                       # O(n + k), tạo dict mới (3.9+)
d.copy(), dict(d)               # O(n)   sao chép nông

# Dùng nhiều
pos = {}                                     # Two Sum: O(n) thay vì O(n²)
for i, x in enumerate(nums):
    if target - x in pos: return [pos[target - x], i]
    pos[x] = i

best = max(d, key=d.get)                     # khoá có giá trị lớn nhất: O(n)
by_val = sorted(d.items(), key=lambda kv: kv[1])   # sort theo giá trị: O(n log n)
```

**Bẫy:** thêm hoặc xoá khoá khi đang duyệt dict báo `RuntimeError`, duyệt `list(d)` thay thế. Dùng list làm khoá báo `TypeError`.

**Pattern LeetCode:** hash map lookup (Two Sum), prefix sum + hash map (560), grouping (Group Anagrams), memoization, graph.

## 8. defaultdict, Counter, OrderedDict

Ba lớp con của dict trong `collections`, giữ nguyên O(1)\* cho đọc / ghi, thêm vài tiện ích riêng.

| Lớp | Là gì | Dùng khi | Vì sao chọn |
| --- | --- | --- | --- |
| `defaultdict` | dict tự tạo giá trị mặc định khi truy cập khoá chưa có | danh sách kề, nhóm phần tử, đếm bằng `defaultdict(int)` | bỏ được `if k not in d` |
| `Counter` | dict chuyên đếm, khoá thiếu trả 0 | tần suất, anagram, top-k, sliding window đếm ký tự | đếm 1 dòng, có `most_common`, cộng trừ bộ đếm |
| `OrderedDict` | dict có thao tác đổi thứ tự O(1) | LRU cache | `move_to_end`, `popitem(last=False)` O(1) |

```python
from collections import defaultdict, Counter, OrderedDict

# defaultdict
g = defaultdict(list)           # truyền vào hàm tạo giá trị mặc định: list, int, set...
g[u].append(v)                  # O(1)*  tự tạo [] nếu u chưa có
cnt = defaultdict(int)
cnt[x] += 1                     # O(1)*  tự tạo 0

# Counter
cnt = Counter(s)                # O(n)
cnt[x]                          # O(1)*  khoá thiếu trả 0 và KHÔNG thêm khoá
cnt[x] += 1                     # O(1)*
cnt.most_common(k)              # O(n log k)   k phần tử phổ biến nhất
cnt.most_common()               # O(n log n)   sort toàn bộ
c1 + c2, c1 - c2                # O(len(c1) + len(c2)); phép trừ bỏ các khoá có kết quả ≤ 0
c1 == c2                        # O(n)   so sánh hai bộ đếm, ví dụ kiểm tra anagram
cnt.total()                     # O(n)   tổng các giá trị (3.10+)
list(cnt.elements())            # O(tổng số đếm)  lặp mỗi khoá theo số lần của nó

# OrderedDict
od = OrderedDict()
od.move_to_end(k)               # O(1)   đưa khoá xuống cuối (vừa dùng gần nhất)
od.move_to_end(k, last=False)   # O(1)   đưa khoá lên đầu
od.popitem(last=False)          # O(1)   lấy cặp ở đầu (lâu chưa dùng nhất)
od.popitem()                    # O(1)   lấy cặp ở cuối

# Dùng nhiều
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v); graph[v].append(u)    # danh sách kề vô hướng: O(E)

Counter(s) == Counter(t)                      # kiểm tra anagram: O(n)

class LRU(OrderedDict):                       # LRU cache gọn: get / put đều O(1)
    def __init__(self, cap): super().__init__(); self.cap = cap
    def get(self, k):
        if k not in self: return -1
        self.move_to_end(k); return self[k]
    def put(self, k, v):
        self[k] = v; self.move_to_end(k)
        if len(self) > self.cap: self.popitem(last=False)
```

**Bẫy:** với `defaultdict`, chỉ cần **đọc** `g[k]` là khoá đã được thêm vào, làm `len(g)` và vòng duyệt thay đổi. Muốn chỉ kiểm tra thì dùng `k in g` hoặc `g.get(k)`.

## 9. set — tập hợp

**Là gì:** tập hợp các phần tử không trùng nhau, cài đặt bằng bảng băm như dict nhưng chỉ có khoá. Không có thứ tự.

**Dùng để làm gì:** kiểm tra tồn tại, loại trùng, đánh dấu đã thăm (visited) trong BFS/DFS, phép toán tập hợp.

**Vì sao chọn nó:** `x in s` là O(1)\* thay vì O(n) như list. Có sẵn giao / hợp / hiệu.

| Tìm `x in s` | Thêm / xoá | Truy cập theo chỉ số | Bộ nhớ |
| --- | --- | --- | --- |
| O(1)\* | O(1)\* | không có | O(n) |

```python
s = set()                       # tập rỗng; {} là dict rỗng, không phải set
s = {1, 2}, set(a)              # O(n)

s.add(x)                        # O(1)*
s.remove(x)                     # O(1)*  KeyError nếu không có
s.discard(x)                    # O(1)*  không lỗi nếu không có
s.pop()                         # O(1)*  lấy một phần tử bất kỳ
x in s                          # O(1)*

s | t                           # hợp:            O(len(s) + len(t))
s & t                           # giao:           O(min(len(s), len(t)))
s - t                           # hiệu:           O(len(s))
s ^ t                           # hiệu đối xứng:  O(len(s) + len(t))
s <= t, s.issubset(t)           # tập con:        O(len(s))
s |= t                          # cập nhật tại chỗ: O(len(t))
frozenset(s)                    # set bất biến, hashable, làm được khoá dict / phần tử set: O(n)

# Dùng nhiều
len(set(nums)) < len(nums)              # Contains Duplicate: O(n)
seen = set()
for x in nums:
    if x in seen: ...                   # mỗi lần kiểm tra O(1)*, cả vòng O(n)
    seen.add(x)
```

**Bẫy:** không giữ thứ tự nên đừng dựa vào thứ tự khi in hoặc duyệt. Phần tử lồng nhau phải là tuple hoặc frozenset.

**Pattern LeetCode:** visited, Longest Consecutive Sequence, Contains Duplicate, sliding window không lặp ký tự.

## 10. deque — hàng đợi hai đầu

**Là gì:** hàng đợi hai đầu (double-ended queue), cài đặt bằng danh sách liên kết đôi giữa các khối bộ nhớ, mỗi khối chứa 64 phần tử.

**Dùng để làm gì:** queue FIFO cho BFS, sliding window maximum (monotonic deque), giữ k phần tử gần nhất bằng `maxlen`.

**Vì sao chọn nó:** thêm / lấy ở **cả hai đầu** đều O(1). `list.pop(0)` là O(n).

| Đọc hai đầu | Đọc giữa `q[i]` | Thêm / lấy hai đầu | Tìm | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(1) | O(n) | O(1) | O(n) | O(n) |

```python
from collections import deque

q = deque()                     # O(1)
q = deque(iterable)             # O(n)
q = deque(maxlen=k)             # đầy thì tự bỏ phần tử ở đầu kia, mỗi lần thêm vẫn O(1)

q.append(x)                     # O(1)   thêm cuối
q.appendleft(x)                 # O(1)   thêm đầu
q.pop()                         # O(1)   lấy cuối
q.popleft()                     # O(1)   lấy đầu
q[0], q[-1]                     # O(1)   xem hai đầu
q[i]                            # O(n)   chậm dần khi đi vào giữa
x in q, q.remove(x)             # O(n)
q.rotate(k)                     # O(k)   xoay phải k bước, k âm thì xoay trái
len(q)                          # O(1)

# BFS: mỗi đỉnh vào / ra queue một lần, O(V + E)
q = deque([start]); seen = {start}
while q:
    u = q.popleft()
    for v in graph[u]:
        if v not in seen:
            seen.add(v); q.append(v)
```

**Bẫy:** không slice được (`q[1:3]` báo `TypeError`). Đánh dấu `seen` khi **đưa vào** queue chứ không phải khi lấy ra, nếu không một đỉnh có thể vào queue nhiều lần.

**Pattern LeetCode:** BFS, shortest path trên lưới không trọng số, sliding window maximum, 0-1 BFS.

## 11. heapq — min-heap

**Là gì:** min-heap cài đặt trên một `list` thường (cây nhị phân ngầm: con của `i` là `2i+1` và `2i+2`). Phần tử nhỏ nhất luôn ở `h[0]`.

**Dùng để làm gì:** lấy liên tục phần tử nhỏ / lớn nhất trong một tập đang thay đổi: top-k, Merge k Sorted Lists, Dijkstra, lập lịch, median stream (hai heap).

**Vì sao chọn nó:** push / pop O(log n), xem min O(1). Top-k bằng heap kích thước k là O(n log k), nhanh hơn sort O(n log n). Sort lại sau mỗi lần thêm thì tốn O(n log n) mỗi lần.

| Xem min `h[0]` | Thêm | Lấy min | Tạo từ list | Tìm / xoá phần tử bất kỳ | Bộ nhớ |
| --- | --- | --- | --- | --- | --- |
| O(1) | O(log n) | O(log n) | O(n) | O(n) | O(n) |

```python
import heapq

h = []
heapq.heapify(a)                # O(n)        biến list thành heap tại chỗ, nhanh hơn n lần push
heapq.heappush(h, x)            # O(log n)
heapq.heappop(h)                # O(log n)    lấy và xoá phần tử nhỏ nhất
h[0]                            # O(1)        xem nhỏ nhất, không xoá
heapq.heappushpop(h, x)         # O(log n)    push rồi pop, nhanh hơn gọi 2 hàm
heapq.heapreplace(h, x)         # O(log n)    pop rồi push
heapq.nlargest(k, a)            # O(n log k)
heapq.nsmallest(k, a, key=len)  # O(n log k)
heapq.merge(*sorted_lists)      # O(N log k)  trộn k dãy đã sort, N tổng phần tử, trả iterator

# Max-heap: đẩy số âm
heapq.heappush(h, -x); largest = -h[0]

# Phần tử có độ ưu tiên: tuple so sánh phần tử đầu trước
heapq.heappush(h, (dist, node))

# Top-k phần tử lớn nhất: giữ min-heap kích thước k, O(n log k) thời gian, O(k) bộ nhớ
h = []
for x in nums:
    heapq.heappush(h, x)
    if len(h) > k: heapq.heappop(h)
# h[0] là phần tử lớn thứ k
```

**Bẫy:**

- Chỉ có min-heap. Max-heap thì đẩy `-x` (Python 3.14 có thêm `heapq.heappush_max` và các hàm `*_max`).
- `(d, node)` báo `TypeError` khi hai `d` bằng nhau mà `node` không so sánh được. Thêm số thứ tự tăng dần: `(d, i, node)`.
- Không xoá được phần tử bất kỳ nhanh. Dùng **lazy deletion**: để nguyên phần tử cũ trong heap, khi pop ra thì kiểm tra và bỏ qua nếu nó đã lỗi thời (như Dijkstra ở [mục 16](#16-template-leetcode)).

**Pattern LeetCode:** top-k, k-way merge, Dijkstra, Find Median from Data Stream, Task Scheduler, Meeting Rooms II.

## 12. bisect — binary search có sẵn

**Là gì:** các hàm binary search trên một list **đã sắp xếp**.

**Dùng để làm gì:** tìm vị trí chèn, đếm số phần tử ≤ x hoặc trong khoảng `[lo, hi]`, LIS O(n log n), Time Based Key-Value Store.

**Vì sao chọn nó:** O(log n), tránh được lỗi biên (off-by-one) khi tự viết binary search.

| Tìm | Chèn giữ thứ tự | Bộ nhớ |
| --- | --- | --- |
| O(log n) | O(n): tìm O(log n) + dịch phần tử O(n) | O(1) phụ |

```python
import bisect

i = bisect.bisect_left(a, x)    # O(log n)  vị trí của phần tử đầu tiên >= x
j = bisect.bisect_right(a, x)   # O(log n)  vị trí của phần tử đầu tiên > x
j - i                           # số lần x xuất hiện
bisect.bisect_right(a, x)       # số phần tử <= x
bisect.bisect_left(a, hi + 1) - bisect.bisect_left(a, lo)   # số phần tử trong [lo, hi]
found = i < len(a) and a[i] == x                            # kiểm tra x có trong a: O(log n)
bisect.insort(a, x)             # O(n)      chèn mà vẫn giữ thứ tự
bisect.bisect_left(a, x, key=lambda r: r[0])   # key= từ Python 3.10, a phải sort theo cùng key

# LIS O(n log n): tails[i] = phần tử cuối nhỏ nhất của dãy con tăng dài i + 1
tails = []
for x in nums:
    i = bisect.bisect_left(tails, x)
    if i == len(tails): tails.append(x)
    else: tails[i] = x
# len(tails) là độ dài LIS
```

**Bẫy:** list chưa sort thì kết quả sai mà không báo lỗi. Cần chèn nhiều lần thì `insort` thành O(n) mỗi lần, dùng `SortedList` hoặc heap.

## 13. SortedList — dãy luôn được sắp xếp

**Là gì:** list luôn giữ thứ tự tăng dần, trong thư viện `sortedcontainers` (LeetCode có sẵn; chạy local thì `pip install sortedcontainers`). Bên trong là nhiều list nhỏ đã sort.

**Dùng để làm gì:** khi vừa phải thêm / xoá liên tục vừa phải hỏi "phần tử nhỏ thứ k", "phần tử gần x nhất", "bao nhiêu phần tử < x". Ví dụ: sliding window median, Contains Duplicate III, đếm nghịch thế.

**Vì sao chọn nó:** `bisect.insort` tốn O(n) mỗi lần chèn. Heap chỉ cho xem min và không xoá được phần tử bất kỳ. `SortedList` làm được tất cả với O(log n). Python không có sẵn balanced BST như `TreeMap` của Java hay `std::set` của C++, nên đây là lựa chọn thay thế.

| Thêm / xoá | Tìm `x in sl` | Truy cập `sl[i]` | Tạo từ n phần tử | Bộ nhớ |
| --- | --- | --- | --- | --- |
| O(log n) | O(log n) | O(log n) | O(n log n) | O(n) |

```python
from sortedcontainers import SortedList, SortedDict, SortedSet

sl = SortedList()               # tạo rỗng
sl = SortedList(iterable)       # O(n log n)
sl.add(x)                       # O(log n)
sl.remove(x)                    # O(log n)  ValueError nếu không có
sl.discard(x)                   # O(log n)  không lỗi nếu không có
x in sl                         # O(log n)
sl[0], sl[-1], sl[k]            # O(log n)  nhỏ nhất, lớn nhất, nhỏ thứ k + 1
sl.pop(), sl.pop(0)             # O(log n)
sl.bisect_left(x)               # O(log n)  số phần tử < x
sl.bisect_right(x)              # O(log n)  số phần tử <= x
sl.index(x)                     # O(log n)
list(sl.irange(lo, hi))         # O(log n + k)  các phần tử trong [lo, hi]

sd = SortedDict()               # dict có khoá luôn sort, tương tự TreeMap
sd.peekitem(0), sd.peekitem(-1) # O(log n)  cặp có khoá nhỏ / lớn nhất
```

**Bẫy:** không gán được `sl[i] = v` (sẽ phá thứ tự), phải `remove` rồi `add`. Không dùng được nếu môi trường chấm bài không cài thư viện.

## 14. Sort và built-in

**Sort:** `sorted()` và `.sort()` dùng Timsort: ổn định (phần tử bằng nhau giữ nguyên thứ tự ban đầu), O(n log n) thời gian, O(n) bộ nhớ phụ, nhanh gần O(n) khi dữ liệu đã gần sort. Hàm `key` được gọi đúng 1 lần cho mỗi phần tử.

**Lười (lazy):** `enumerate`, `zip`, `map`, `filter`, `range`, `reversed` không tạo list. Tạo ra là O(1), mỗi bước duyệt O(1).

```python
sorted(a)                                   # O(n log n), list mới
sorted(a, key=lambda x: (-x[1], x[0]))      # nhiều tiêu chí: x[1] giảm dần, rồi x[0] tăng dần
sorted(a, reverse=True)
sorted(d.items(), key=lambda kv: -kv[1])    # sort dict theo giá trị

max(a, key=len), min(d, key=d.get)          # O(n)
max(a, default=0)                           # không lỗi khi a rỗng
sum(a), sum(a, start)                       # O(n)
any(x > 0 for x in a), all(...)             # O(n) xấu nhất, dừng ngay khi biết kết quả

range(a, b, step)                           # tạo O(1)
x in range(n)                               # O(1) với số nguyên (tính toán, không duyệt)
reversed(a)                                 # tạo O(1), duyệt O(n)
enumerate(a, start=1)                       # chỉ số bắt đầu từ 1
zip(a, b), zip(*matrix)                     # duyệt song song / chuyển vị
map(int, s.split())                         # đổi kiểu từng phần tử
filter(None, a)                             # bỏ phần tử falsy
list(map(int, input().split()))             # đọc một dòng số, O(n)
```

## 15. itertools và functools

**Là gì:** hai module chuẩn chứa các khối dựng sẵn cho duyệt (itertools) và cho hàm (functools).

**Vì sao dùng:** viết ngắn hơn, chạy bằng C nên nhanh hơn vòng lặp tự viết. Các hàm của itertools đều lười: trả iterator, chỉ tính khi duyệt.

```python
from itertools import accumulate, combinations, permutations, product, groupby, pairwise, chain
from functools import cache, lru_cache, reduce, cmp_to_key

accumulate(a)                   # O(n)       cộng dồn (prefix sum)
accumulate(a, max)              # O(n)       max dồn
permutations(a, r)              # n!/(n-r)! hoán vị, mỗi cái O(r): tổng O(n! · n) với r = n
combinations(a, r)              # C(n, r) tổ hợp, mỗi cái O(r)
product(a, b)                   # tích Descartes O(len(a) · len(b))
product('01', repeat=n)         # mọi chuỗi nhị phân độ dài n: O(2ⁿ · n)
groupby(sorted(a))              # O(n) sau khi sort; chỉ gom các phần tử BẰNG NHAU LIỀN KỀ
pairwise(a)                     # (a0, a1), (a1, a2), ...   O(n)   (3.10+)
chain(a, b)                     # nối iterable, O(n)
chain.from_iterable(lists)      # làm phẳng 1 cấp, O(n)

reduce(lambda x, y: x * y, a, 1)   # fold: O(n)
sorted(a, key=cmp_to_key(cmp))     # sort bằng hàm so sánh cmp(x, y) trả âm / 0 / dương: O(n log n)

@cache                          # memo hoá, tương đương @lru_cache(maxsize=None)
def dp(i, j):                   # DP top-down: thời gian O(số trạng thái × chi phí mỗi trạng thái), bộ nhớ O(số trạng thái)
    if i == n: return 0
    skip = dp(i + 1, j)
    take = val[i] + dp(i + 1, j - w[i]) if j >= w[i] else 0
    return max(skip, take)
dp.cache_clear()                # xoá cache giữa các test case

# Largest Number: so sánh tùy biến
largest = ''.join(sorted(map(str, nums), key=cmp_to_key(lambda a, b: (b + a > a + b) - (b + a < a + b))))
```

**Bẫy:** `@cache` yêu cầu mọi tham số đều hashable, truyền list sẽ báo `TypeError`; truyền tuple hoặc chỉ số. `groupby` trên dãy chưa sort sẽ tách cùng một giá trị thành nhiều nhóm.

## 16. Template LeetCode

Khung code cho các pattern trong tab LeetCode 16 tuần. V = số đỉnh, E = số cạnh.

| Pattern | Thời gian | Bộ nhớ | Dấu hiệu nhận biết |
| --- | --- | --- | --- |
| Two pointers | O(n) | O(1) | mảng đã sort, tìm cặp, palindrome |
| Prefix sum + hash map | O(n) | O(n) | đếm subarray có tổng = k |
| Sliding window | O(n) | O(k) | subarray / substring liên tiếp dài nhất / ngắn nhất |
| Binary search trên đáp án | O(log(hi − lo) × chi phí ok()) | O(1) | "nhỏ nhất / lớn nhất sao cho...", ok() đơn điệu |
| Monotonic stack | O(n) | O(n) | phần tử lớn / nhỏ hơn kế tiếp |
| BFS / DFS | O(V + E) | O(V) | graph, lưới, đường đi ngắn nhất không trọng số |
| Topological sort (Kahn) | O(V + E) | O(V) | thứ tự phụ thuộc, phát hiện chu trình có hướng |
| Union-Find (nén đường + theo size) | ~O(α(n)) mỗi thao tác | O(n) | thành phần liên thông, gộp nhóm |
| Dijkstra với heapq | O((V + E) log V) | O(V + E) | đường đi ngắn nhất, trọng số không âm |
| Backtracking (subsets) | O(n · 2ⁿ) | O(n) | liệt kê mọi tổ hợp / hoán vị |

```python
# Two pointers trên mảng đã sort: O(n)
lo, hi = 0, len(a) - 1
while lo < hi:
    s = a[lo] + a[hi]
    if s == target: break
    if s < target: lo += 1
    else: hi -= 1

# Prefix sum + hash map: số subarray có tổng = k, O(n)
seen, cur, res = Counter({0: 1}), 0, 0
for x in nums:
    cur += x
    res += seen[cur - k]
    seen[cur] += 1

# Binary search: tìm giá trị nhỏ nhất thỏa ok(), O(log(hi - lo))
lo, hi = 0, 10**9
while lo < hi:
    mid = (lo + hi) // 2
    if ok(mid): hi = mid
    else: lo = mid + 1

# Sliding window co giãn: mỗi phần tử vào / ra cửa sổ 1 lần, O(n)
cnt, left, best = Counter(), 0, 0
for right, c in enumerate(s):
    cnt[c] += 1
    while not valid(cnt):
        cnt[s[left]] -= 1; left += 1
    best = max(best, right - left + 1)

# Monotonic stack: phần tử lớn hơn kế tiếp, mỗi chỉ số push / pop 1 lần, O(n)
res, st = [-1] * n, []
for i, v in enumerate(a):
    while st and a[st[-1]] < v:
        res[st.pop()] = i
    st.append(i)

# BFS trên lưới: O(R · C)
q, seen = deque([(r0, c0)]), {(r0, c0)}
while q:
    r, c = q.popleft()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen and grid[nr][nc] == '1':
            seen.add((nr, nc)); q.append((nr, nc))

# Topological sort (Kahn): O(V + E)
indeg = [0] * n
for u, v in edges: graph[u].append(v); indeg[v] += 1
q = deque(i for i in range(n) if indeg[i] == 0); order = []
while q:
    u = q.popleft(); order.append(u)
    for v in graph[u]:
        indeg[v] -= 1
        if indeg[v] == 0: q.append(v)
has_cycle = len(order) < n

# Union-Find: ~O(α(n)) mỗi lần find / union, gần như O(1)
parent, size = list(range(n)), [1] * n
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]    # nén đường
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb: return False
    if size[ra] < size[rb]: ra, rb = rb, ra             # gộp cây nhỏ vào cây lớn
    parent[rb] = ra; size[ra] += size[rb]; return True

# Dijkstra: O((V + E) log V)
dist = {src: 0}; h = [(0, src)]
while h:
    d, u = heapq.heappop(h)
    if d > dist.get(u, INF): continue                   # lazy deletion: bỏ bản ghi cũ
    for v, w in graph[u]:
        nd = d + w
        if nd < dist.get(v, INF):
            dist[v] = nd; heapq.heappush(h, (nd, v))

# Backtracking (subsets): 2ⁿ tập con, mỗi tập chép O(n), tổng O(n · 2ⁿ)
res, path = [], []
def bt(i):
    if i == len(nums):
        res.append(path[:]); return      # path[:] là bản sao O(n)
    path.append(nums[i]); bt(i + 1); path.pop()
    bt(i + 1)
bt(0)
```

## 17. Bẫy hay gặp

| Bẫy | Sai | Đúng |
| --- | --- | --- |
| Ma trận dùng chung hàng | `[[0] * m] * n` (n hàng cùng 1 list) | `[[0] * m for _ in range(n)]` |
| Queue bằng list | `a.pop(0)` → O(n) | `deque.popleft()` → O(1) |
| Kiểm tra tồn tại trong vòng lặp | `if x in lst` → O(n), cả vòng O(n²) | chuyển sang `set` trước → O(1)\* |
| Nối chuỗi trong vòng lặp | `s += c` | gom list rồi `''.join(parts)` |
| Tham số mặc định mutable | `def f(a=[])` (dùng chung list giữa các lần gọi) | `def f(a=None):` rồi `if a is None: a = []` |
| Lưu path trong backtracking | `res.append(path)` (cùng tham chiếu) | `res.append(path[:])` |
| Đệ quy sâu | mặc định ~1000 tầng → RecursionError | `sys.setrecursionlimit(10**6)` hoặc đổi sang stack / BFS |
| Chia số âm làm tròn về 0 | `-7 // 2 == -4`; `int(-7 / 2)` qua float, sai với số lớn | `q = a // b if a * b >= 0 else -(-a // b)` |
| Hằng modulo | `MOD = 1e9 + 7` là float | `MOD = 10**9 + 7` |
| Sao chép nông | `b = a` hoặc `a[:]` với list lồng | `copy.deepcopy(a)` |
| Sửa dict / set khi đang duyệt | `for k in d: del d[k]` → RuntimeError | `for k in list(d):` |
| Đọc defaultdict để kiểm tra | `if g[k]:` thêm khoá `k` vào g | `if k in g:` hoặc `g.get(k)` |
| heapq với object không so sánh được | `heappush(h, (d, node))` lỗi khi `d` bằng nhau | `(d, i, node)` với `i` tăng dần, hoặc định nghĩa `__lt__` |
| `@cache` trên hàm nhận list | list không hashable → TypeError | truyền `tuple` hoặc chỉ số |
| Đổi số rất lớn sang chuỗi | `str(n)` với n > 4300 chữ số → ValueError (3.11+) | `sys.set_int_max_str_digits(0)` |
| Đánh dấu visited muộn trong BFS | `seen.add(u)` sau khi `popleft` | `seen.add(v)` ngay khi `append(v)` |

Số nguyên Python không tràn số, nhưng phép nhân số rất lớn không còn O(1). Độ phức tạp trong tài liệu này theo CPython. Nguồn tham khảo: [Python Wiki – TimeComplexity](https://wiki.python.org/moin/TimeComplexity), tài liệu [heapq](https://docs.python.org/3/library/heapq.html), [bisect](https://docs.python.org/3/library/bisect.html), [collections](https://docs.python.org/3/library/collections.html), [sortedcontainers](https://grantjenks.com/docs/sortedcontainers/).
