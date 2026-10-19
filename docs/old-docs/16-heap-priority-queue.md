# 16. Heap / Priority Queue

Heap trả lời một câu hỏi rất hẹp — "phần tử nhỏ nhất là gì?" — nhưng trả lời nó trong O(1) và cho phép cập nhật trong O(log n). Đó vừa đủ để giải cả một họ bài toán top-k, median trên stream, và Dijkstra. Section này cài heap từ đầu, đi qua toàn bộ API `heapq` (kể cả hai hàm hay bị nhầm lẫn `heappushpop`/`heapreplace`), và xử lý điểm yếu chí mạng của nó: **không có decrease-key, không có xoá tuỳ ý**.

## Lý thuyết

### Cây nhị phân lưu trong mảng

Heap là **complete binary tree**: mọi tầng đầy, trừ tầng cuối được lấp từ trái sang. Tính chất "complete" cho phép lưu cây trong một mảng mà **không cần một con trỏ nào**:

```
cha của i   = (i - 1) // 2
con trái    = 2i + 1
con phải    = 2i + 2
```

Đây là lý do heap nhanh trong thực tế dù cùng O(log n) với balanced BST: dữ liệu nằm liên tục trong bộ nhớ, không có object node, không có cache miss vì dereference.

> **Heap property (invariant)**: với mọi `i > 0`, `data[(i-1)//2] <= data[i]`.

Hệ quả trực tiếp: `data[0]` là phần tử nhỏ nhất. Chú ý invariant này **chỉ ràng buộc quan hệ cha–con**, không nói gì về quan hệ giữa hai anh em hay giữa hai nhánh — heap **không phải** cấu trúc sắp xếp. `[1, 3, 2]` và `[1, 2, 3]` đều là heap hợp lệ. Đây là lý do heap rẻ hơn sorting.

Hai thao tác phục hồi invariant:

- **`sift_up(i)`**: dùng sau `push`. Phần tử mới ở cuối mảng có thể nhỏ hơn cha — đổi chỗ lên trên tới khi cha ≤ nó. Đường đi tối đa là chiều cao cây → O(log n).
- **`sift_down(i)`**: dùng sau `pop`. Lấy phần tử cuối mảng đặt lên gốc rồi đẩy xuống, mỗi bước đổi với **con nhỏ hơn trong hai con** (đổi với con lớn hơn sẽ phá invariant ở nhánh kia) → O(log n).

### Vì sao `heapify` là O(n), không phải O(n log n)

`heapify` chạy `sift_down` từ node trong cùng (index `n//2 - 1`) ngược về gốc. Trực giác sai là "n lần sift_down × O(log n) = O(n log n)". Sự thật:

- Một nửa số node là lá — `sift_down` tốn 0 bước.
- 1/4 số node ở tầng áp chót — tốn ≤ 1 bước.
- 1/8 số node — tốn ≤ 2 bước. Và cứ thế.

Tổng chi phí ≤ `n · Σ(h / 2^(h+1))` với h = 0, 1, 2, … Chuỗi này hội tụ về 1, nên tổng là **O(n)**.

Đo thực nghiệm trên máy này với 2 000 000 phần tử: `heapq.heapify` mất **0.0241 s**, còn 2 000 000 lần `heappush` mất **0.0817 s** — nhanh hơn 3.4 lần. Chênh lệch không lớn bằng lý thuyết vì `heappush` cũng là code C và sift_up thường dừng sớm, nhưng quy tắc thì rõ: **có sẵn cả mảng thì `heapify`, đừng push từng cái**.

### Bảng độ phức tạp

| Thao tác | Chi phí | Ghi chú |
|---|---|---|
| `heap[0]` (peek min) | **O(1)** | chỉ đọc mảng |
| `heappush` | O(log n) | |
| `heappop` | O(log n) | |
| `heapify(list)` | **O(n)** | in-place |
| `heappushpop` / `heapreplace` | O(log n) | **1 lần** sift thay vì 2 |
| tìm max trong min-heap | **O(n)** | heap không giúp gì |
| xoá phần tử tuỳ ý | **O(n)** | phải tìm tuyến tính rồi heapify lại |
| decrease-key | **không có API** | xem phần lazy deletion |
| `nlargest(k, it)` / `nsmallest(k, it)` | O(n log k) | |
| `heapq.merge(*iters)` | O(N log k), bộ nhớ O(k) | trả về **iterator** |

Hai dòng in đậm ở giữa bảng là toàn bộ giới hạn của heap, và là lý do §19 tồn tại.

### `heappushpop` vs `heapreplace`

Cả hai đều là "push + pop trong một lần sift", nhưng **thứ tự ngược nhau**:

```python
import heapq

h = [1, 3, 5]
heapq.heappushpop(h, 0)   # -> 0,  heap vẫn là [1, 3, 5]   (push trước, pop sau)
h = [1, 3, 5]
heapq.heapreplace(h, 0)   # -> 1,  heap thành [0, 3, 5]    (pop trước, push sau)
```

Khác biệt chỉ lộ ra khi phần tử mới **nhỏ hơn root**: `heappushpop` trả về ngay chính nó (không đụng heap), còn `heapreplace` trả về root cũ và đưa phần tử mới vào. `heapreplace` cũng ném `IndexError` trên heap rỗng, còn `heappushpop` thì không.

Quy tắc dùng: giữ heap kích thước `k` cho bài top-k thì dùng `heapreplace` **sau khi đã kiểm tra `x > heap[0]`** — như vậy đúng ngữ nghĩa "thay thế phần tử tệ nhất".

### Max-heap trong Python

`heapq` **chỉ có min-heap**. Ba cách xử lý:

1. **Phủ định giá trị**: push `-x`, pop ra thì `-` lại. Đơn giản nhất, chỉ dùng được với số.
2. **Phủ định priority trong tuple**: `(-priority, tie_breaker, item)`.
3. `heapq._heapify_max` và họ hàng — hàm private, **đừng dùng**, không có `_heappush_max` công khai và API có thể đổi.

Với `float`, phủ định an toàn (kể cả `inf`). Với số nguyên Python (arbitrary precision) cũng an toàn — không có bẫy `-INT_MIN` như C++.

### Tuple làm entry — và bẫy tie-break

Heap so sánh phần tử bằng `<`. Tuple so sánh theo thứ tự từ điển: so phần tử đầu, **bằng nhau thì so phần tử tiếp theo**. Nếu phần tử tiếp theo là object không có `__lt__`:

```python
import heapq


class Task:
    def __init__(self, name): self.name = name


hq = [(1, Task("a"))]
try:
    heapq.heappush(hq, (1, Task("b")))
except TypeError as e:
    print(e)   # '<' not supported between instances of 'Task' and 'Task'
```

Giải pháp chuẩn: chèn một số nguyên tăng dần vào giữa — `(priority, counter, item)` với `counter = next(itertools.count())`. Vừa tránh `TypeError`, vừa cho ra thứ tự **FIFO khi cùng priority** (stable priority queue), điều mà heap không tự có.

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/heap/binary_heap.py`

```python
class BinaryHeap:
    """Min-heap nhị phân trên mảng, cài từ đầu để hiểu heapq làm gì.

    Invariant (heap property): với mọi i > 0, data[(i-1)//2] <= data[i].
    Hệ quả: data[0] luôn là phần tử nhỏ nhất. Cây được lưu ẩn trong mảng:
    con của i là 2i+1 và 2i+2, cha của i là (i-1)//2 — không cần con trỏ.
    """

    def __init__(self, items=()) -> None:
        self._data = list(items)
        self._heapify()

    def _heapify(self) -> None:
        # O(n), KHÔNG phải O(n log n): sift_down từ node trong cùng trở về gốc.
        for i in reversed(range(len(self._data) // 2)):
            self._sift_down(i)

    def _sift_up(self, i: int) -> None:
        item = self._data[i]
        while i > 0:
            parent = (i - 1) >> 1
            if self._data[parent] <= item:
                break
            self._data[i] = self._data[parent]     # kéo cha xuống
            i = parent
        self._data[i] = item

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        item = self._data[i]
        while True:
            child = 2 * i + 1
            if child >= n:
                break
            if child + 1 < n and self._data[child + 1] < self._data[child]:
                child += 1                          # chọn con nhỏ hơn
            if item <= self._data[child]:
                break
            self._data[i] = self._data[child]
            i = child
        self._data[i] = item

    def push(self, item) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        last = self._data.pop()
        if not self._data:
            return last
        top = self._data[0]
        self._data[0] = last
        self._sift_down(0)
        return top

    def peek(self):
        return self._data[0]

    def __len__(self) -> int:
        return len(self._data)

    def is_valid(self) -> bool:
        return all(self._data[(i - 1) >> 1] <= self._data[i]
                   for i in range(1, len(self._data)))
```

Chi tiết cài đặt đáng học: `_sift_up`/`_sift_down` **không hoán đổi (swap)** mà "kéo" phần tử cha/con vào vị trí trống rồi mới ghi `item` vào chỗ cuối cùng. Swap tốn 3 phép gán mỗi bước, cách này tốn 1 — CPython cũng làm đúng như vậy.

`is_valid()` là công cụ test: sau mỗi thao tác, invariant phải còn đúng. Đã stress test 2000 lần: dựng heap từ mảng ngẫu nhiên, kiểm `is_valid()`, pop hết ra và đối chiếu với `sorted()`.

Đề xuất đường dẫn: `cores/python/heap/lazy_heap.py` — heap hỗ trợ **xoá tuỳ ý** bằng lazy deletion.

```python
import heapq
from collections import Counter


class LazyDeleteHeap:
    """Min-heap hỗ trợ remove(item) tuỳ ý bằng lazy deletion.

    Invariant: _heap có thể chứa các entry đã bị xoá (stale); nhưng đỉnh heap
    sau khi _clean() luôn là phần tử hợp lệ nhỏ nhất. _pending[x] là số bản sao
    của x đã bị đánh dấu xoá nhưng còn nằm trong _heap.
    """

    def __init__(self) -> None:
        self._heap: list = []
        self._pending: Counter = Counter()
        self._size = 0            # số phần tử hợp lệ

    def push(self, item) -> None:
        heapq.heappush(self._heap, item)
        self._size += 1

    def remove(self, item) -> None:
        self._pending[item] += 1  # chỉ đánh dấu, KHÔNG đụng vào heap
        self._size -= 1

    def _clean(self) -> None:
        while self._heap and self._pending[self._heap[0]] > 0:
            self._pending[self._heap[0]] -= 1
            heapq.heappop(self._heap)

    def peek(self):
        self._clean()
        return self._heap[0]

    def pop(self):
        self._clean()
        self._size -= 1
        return heapq.heappop(self._heap)

    def __len__(self) -> int:
        return self._size
```

Ý tưởng: **không xoá gì cả**, chỉ ghi nợ. Rác chỉ được dọn khi nó nổi lên đỉnh — chỗ duy nhất mà heap cho phép thao tác rẻ. Chi phí amortized vẫn O(log n) mỗi thao tác vì mỗi phần tử được push một lần và pop tối đa một lần. Cái phải trả là **bộ nhớ**: heap có thể chứa nhiều entry stale, worst case O(tổng số push). Nếu tỉ lệ xoá cao, thêm một bước "rebuild khi số rác vượt nửa heap" để chặn bộ nhớ.

Chú ý `_size` được đếm riêng — `len(self._heap)` bao gồm cả rác nên không dùng được. Đã stress test 2000 phiên × 25 thao tác, đối chiếu `peek`/`pop`/`len` với một list reference.

## Bài tập chi tiết

### Bài 1 — 215. Kth Largest Element in an Array

#### Requirements

Trả về phần tử **lớn thứ k** theo thứ tự sắp xếp (không phải phần tử phân biệt thứ k — trùng lặp vẫn tính riêng). `1 ≤ k ≤ n ≤ 10⁵`, `-10⁴ ≤ nums[i] ≤ 10⁴`. Đề gợi ý giải mà không sort toàn bộ.

Edge cases: `k == 1` (max); `k == n` (min); mọi phần tử bằng nhau; số âm; `n == 1`.

#### Complexity mục tiêu

n = 10⁵ nên `sorted()` (O(n log n) ≈ 1.7·10⁶ phép so sánh, code C) thực tế **nhanh nhất** trên LeetCode. Nhưng bài này tồn tại để dạy hai kỹ thuật tốt hơn về mặt lý thuyết: **heap kích thước k** cho O(n log k), và **Quickselect** cho O(n) trung bình (xem §09/§17).

Khi nào O(n log k) thật sự thắng: khi `k ≪ n` (top 10 của 10⁸ bản ghi), và đặc biệt khi dữ liệu là **stream** không thể sort vì không nạp hết vào bộ nhớ. Đó mới là bối cảnh thật.

#### Idea

Duy trì một **min-heap chứa đúng k phần tử lớn nhất đã gặp**.

> **Invariant**: sau khi xử lý tiền tố `nums[0..i]`, `heap` chứa đúng `min(k, i+1)` phần tử lớn nhất của tiền tố đó, và `heap[0]` là nhỏ nhất trong số chúng — tức là "ngưỡng vào cửa".

Với phần tử mới `x`: nếu `x <= heap[0]` thì `x` không thể lọt vào top-k (đã có k phần tử ≥ `heap[0]` ≥ `x`), bỏ qua. Ngược lại, `x` đá văng `heap[0]`. Kết thúc, `heap[0]` chính là phần tử nhỏ nhất trong k phần tử lớn nhất = phần tử lớn thứ k.

Vì sao dùng **min**-heap để tìm phần tử **lớn** thứ k: ta cần truy cập nhanh vào "ứng viên yếu nhất đang được giữ" để quyết định có thay không. Đó là min của tập k phần tử.

#### Naive

```python
class SolutionNaive215:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        return sorted(nums, reverse=True)[k - 1]
```

O(n log n) time, O(n) space. "Chậm" ở đây là chậm về mặt lý thuyết và về mặt bộ nhớ: nó sort **toàn bộ** trong khi ta chỉ cần biết k phần tử đầu, và nó cần cả mảng trong bộ nhớ cùng lúc. Trên LeetCode nó thắng vì Timsort là C; trên một stream 10⁸ bản ghi nó không chạy được.

#### Optimized

```python
import heapq


class Solution215:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        heap = nums[:k]
        heapq.heapify(heap)               # O(k)
        for x in nums[k:]:
            if x > heap[0]:
                heapq.heapreplace(heap, x)   # pop rồi push, 1 lần sift_down
        return heap[0]
```

O(n log k) time, **O(k) space**. Đánh đổi: chậm hơn `sorted()` trên input LeetCode vì vòng lặp là Python thuần thay vì C, đổi lấy bộ nhớ O(k) thay vì O(n) và khả năng chạy trên stream.

Ba chi tiết: (1) `heapify(nums[:k])` là O(k), tốt hơn k lần `heappush`; (2) `if x > heap[0]` **trước** `heapreplace` là bắt buộc — không có nó, một phần tử nhỏ sẽ chui vào heap rồi bị đẩy ra ngay, vẫn đúng nhưng tốn thêm sift, và với `heappushpop` thì có thể viết gọn `heapq.heappushpop(heap, x)` không cần `if`; (3) `heapreplace` chứ không phải `heappop` + `heappush` — một lần sift thay vì hai.

Đã stress test 3000 lần với `n ∈ [1,10]`, giá trị `[-5,5]`, `k ∈ [1,n]`, khớp với `sorted`. `findKthLargest([3,2,1,5,6,4], 2)` → `5`.

### Bài 2 — 347. Top K Frequent Elements

#### Requirements

Trả về `k` phần tử xuất hiện nhiều nhất, **thứ tự tuỳ ý**. `1 ≤ n ≤ 10⁵`, `k` nằm trong khoảng `[1, số phần tử phân biệt]`. Đề đảm bảo đáp án là **duy nhất** (không có tie ở ranh giới thứ k). Yêu cầu tường minh: độ phức tạp **tốt hơn O(n log n)**.

Edge cases: `k` bằng số phần tử phân biệt (trả về tất cả); mọi phần tử phân biệt (mọi tần suất = 1, nhưng đề đảm bảo đáp án duy nhất nên trường hợp này chỉ xảy ra khi k = n); số âm; một phần tử duy nhất.

#### Complexity mục tiêu

Đề nói "tốt hơn O(n log n)" nên `sorted(freq.items())` bị loại về mặt yêu cầu. Gọi `m` là số phần tử phân biệt (m ≤ n). Hai lời giải đạt yêu cầu:

- **Heap kích thước k**: O(n + m log k).
- **Bucket sort theo tần suất**: **O(n)** — vì tần suất là số nguyên trong `[1, n]`, ta bucket theo nó (§17).

#### Idea

Bước 1 giống nhau: `Counter(nums)` cho ra `m` cặp `(value, count)` trong O(n).

**Hướng heap** — cùng invariant với bài 215 nhưng khoá so sánh là `count`:

> **Invariant**: heap chứa ≤ k cặp `(count, value)` có count lớn nhất đã gặp; `heap[0][0]` là ngưỡng.

**Hướng bucket** — quan sát: `count` luôn nằm trong `[1, n]`, một miền số nguyên nhỏ và biết trước. Vậy tạo `n+1` bucket, `buckets[c]` chứa mọi giá trị có tần suất `c`. Duyệt bucket từ `n` về `1` và thu đủ k phần tử.

> **Invariant**: khi duyệt bucket từ cao xuống thấp, mọi phần tử đã thu có tần suất ≥ mọi phần tử chưa thu.

Bucket cho O(n) vì tổng kích thước mọi bucket là `m ≤ n` và số bucket là `n+1`.

#### Naive

```python
from collections import Counter


class SolutionNaive347:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        freq = Counter(nums)
        return [v for v, _ in sorted(freq.items(), key=lambda kv: -kv[1])[:k]]
```

O(n + m log m). Chậm vì sort **toàn bộ** m phần tử trong khi chỉ cần k phần tử đầu — công việc thừa tỉ lệ với `m log m − m log k`. (Bản thân `Counter.most_common(k)` đã làm đúng: nó dùng `heapq.nlargest`, tức là O(m log k). Nên trong đời thực bạn chỉ cần `return [v for v, _ in Counter(nums).most_common(k)]`.)

#### Optimized

Hướng heap:

```python
import heapq
from collections import Counter


class Solution347:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        freq = Counter(nums)
        heap: list[tuple[int, int]] = []      # (count, value), min-heap kích thước k
        for value, count in freq.items():
            if len(heap) < k:
                heapq.heappush(heap, (count, value))
            elif count > heap[0][0]:
                heapq.heapreplace(heap, (count, value))
        return [value for _, value in heap]
```

O(n + m log k) time, O(m) space. Đánh đổi: kết quả **không được sắp xếp** theo tần suất (heap không phải cấu trúc sorted) — đề cho phép, nhưng nếu cần thứ tự thì phải sort k phần tử cuối, thêm O(k log k).

Hướng bucket, nhanh hơn về asymptotic:

```python
from collections import Counter


class Solution347Bucket:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        freq = Counter(nums)
        buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
        for value, count in freq.items():
            buckets[count].append(value)
        out: list[int] = []
        for count in range(len(nums), 0, -1):
            for value in buckets[count]:
                out.append(value)
                if len(out) == k:
                    return out
        return out
```

**O(n)** time, O(n) space. Đánh đổi rõ ràng: cấp phát `n+1` list rỗng dù chỉ vài bucket có dữ liệu — lãng phí bộ nhớ và thời gian khởi tạo khi `m ≪ n`. Kỹ thuật này chỉ dùng được vì tần suất có **miền giá trị nguyên nhỏ, biết trước**; nếu khoá so sánh là số thực hoặc miền lớn thì không áp dụng được, phải quay về heap.

Đã stress test 3000 lần cả hai bản, so sánh theo **multiset tần suất** (không so sánh trực tiếp danh sách giá trị vì tie-break khác nhau giữa các lời giải là hợp lệ). `topKFrequent([1,1,1,2,2,3], 2)` → `[2,1]` (heap) và `[1,2]` (bucket) — cùng tập, khác thứ tự.

### Bài 3 — 295. Find Median from Data Stream

#### Requirements

Thiết kế lớp với `addNum(num)` và `findMedian()`. Median của `n` phần tử: phần tử giữa nếu `n` lẻ, trung bình hai phần tử giữa nếu `n` chẵn. Tối đa 5·10⁴ lời gọi, `-10⁵ ≤ num ≤ 10⁵`.

Edge cases: `findMedian` sau đúng 1 lần `addNum`; số phần tử chẵn (phải trả `float`, ví dụ `(1+2)/2 = 1.5`); mọi phần tử bằng nhau; số âm; thêm phần tử luôn nhỏ hơn/lớn hơn mọi phần tử đã có (kiểm tra việc cân bằng).

Từ khoá quan trọng: **stream** — không biết trước tổng số phần tử, và phải trả lời median tại **mọi** thời điểm.

#### Complexity mục tiêu

5·10⁴ lời gọi. Giữ mảng sorted bằng `bisect.insort` là O(n) mỗi lần chèn → O(n²) = 2.5·10⁹ thao tác dịch bộ nhớ. Thực tế `insort` dùng `memmove` (code C) nên vẫn có thể pass trên LeetCode, nhưng đó là may mắn về hằng số, không phải lời giải đúng. Mục tiêu: **O(log n) cho `addNum`, O(1) cho `findMedian`**.

#### Idea

Chia dữ liệu làm hai nửa và chỉ quan tâm tới **ranh giới** giữa chúng — đó chính xác là thứ heap cho ta trong O(1).

> **Invariant 1 (thứ tự)**: mọi phần tử trong `low` ≤ mọi phần tử trong `high`.
> **Invariant 2 (cân bằng)**: `len(low) == len(high)` hoặc `len(low) == len(high) + 1`.

`low` là **max-heap** (đỉnh là phần tử lớn nhất của nửa nhỏ), `high` là **min-heap** (đỉnh là phần tử nhỏ nhất của nửa lớn). Hai đỉnh này ôm lấy median:

- `n` lẻ → `low` dư 1 phần tử → median = đỉnh `low`.
- `n` chẵn → median = trung bình hai đỉnh.

Kỹ thuật chèn đẹp nhất là **đi vòng**: luôn push vào `low` trước, rồi ngay lập tức chuyển đỉnh `low` sang `high`. Thao tác này **tự động** đảm bảo invariant 1 mà không cần một lệnh `if` so sánh nào — vì bất kỳ giá trị nào cũng bị "lọc" qua `low` trước, và cái được đẩy sang `high` chắc chắn là lớn nhất trong nửa nhỏ. Sau đó chỉ cần một `if` để tái lập invariant 2.

Vì `heapq` không có max-heap, `low` lưu **giá trị phủ định**.

#### Naive

```python
import bisect


class MedianFinderNaive:
    def __init__(self) -> None:
        self._a: list[int] = []

    def addNum(self, num: int) -> None:
        bisect.insort(self._a, num)      # O(n) vì phải dịch mảng

    def findMedian(self) -> float:
        n = len(self._a)
        mid = n // 2
        return float(self._a[mid]) if n % 2 else (self._a[mid - 1] + self._a[mid]) / 2
```

`addNum` là **O(n)** (binary search O(log n) để tìm vị trí, nhưng chèn phải dịch trung bình n/2 phần tử), `findMedian` là O(1). Với n lần thêm là O(n²). Đây là chính xác vấn đề mà §19 mô tả: `bisect` + `list` cho tìm kiếm O(log n) nhưng **không** cho chèn O(log n).

#### Optimized

```python
import heapq


class MedianFinder:
    """Two heaps.

    Invariant:
      1) mọi phần tử trong `low` <= mọi phần tử trong `high`
      2) len(low) == len(high) hoặc len(low) == len(high) + 1
    `low` là max-heap (lưu giá trị PHỦ ĐỊNH vì heapq chỉ có min-heap).
    """

    def __init__(self) -> None:
        self._low: list[int] = []    # max-heap của nửa nhỏ, lưu -value
        self._high: list[int] = []   # min-heap của nửa lớn

    def addNum(self, num: int) -> None:
        # Đẩy qua low trước, rồi chuyển phần tử lớn nhất của low sang high:
        # thao tác này tự bảo toàn invariant (1) mà không cần so sánh thủ công.
        heapq.heappush(self._low, -num)
        heapq.heappush(self._high, -heapq.heappop(self._low))
        if len(self._high) > len(self._low):        # tái lập invariant (2)
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def findMedian(self) -> float:
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2
```

`addNum` O(log n), `findMedian` O(1), space O(n). Đánh đổi: ta biết được median trong O(1) nhưng **mất khả năng truy vấn bất cứ thứ gì khác** — không lấy được phần tử thứ k, không đếm được số phần tử < x, không duyệt theo thứ tự. Heap chỉ cho ta hai đỉnh. Nếu đề đổi thành "trả về phân vị thứ 90" thì cấu trúc này phải viết lại (hoặc dùng `SortedList` của §19).

Ba lần `heappush`/`heappop` mỗi lần thêm nhìn có vẻ lãng phí so với bản "so sánh với đỉnh rồi push vào đúng nửa", nhưng đổi lại là code không có nhánh điều kiện phức tạp — và mọi nhánh điều kiện trong bài này đều là chỗ để sinh bug (đặc biệt khi `low` hoặc `high` rỗng).

Đã stress test 2000 phiên × 20 lần `addNum`, so sánh `findMedian()` sau **mỗi** lần thêm với bản naive. Chuỗi `1, 2, 3` cho `1.0 → 1.5 → 2.0`.

## Bài luyện thêm

- **23. Merge k Sorted Lists** — heap chứa head hiện tại của k list, entry là `(val, idx, node)` để tránh so sánh `ListNode`; đã giải chi tiết ở §12.
- **253. Meeting Rooms II** — min-heap chứa thời điểm kết thúc của các phòng đang bận; với mỗi cuộc họp (đã sort theo start), pop mọi phòng đã trống rồi push thời điểm kết thúc mới — đáp án là kích thước tối đa của heap. (Bài này là **LeetCode Premium**; nếu không truy cập được, làm **1094. Car Pooling** hoặc **1851. Minimum Interval to Include Each Query** để luyện cùng khuôn.)
- **1046. Last Stone Weight** — max-heap bằng cách phủ định; lặp lại: lấy hai viên nặng nhất, đẩy hiệu số vào lại nếu khác 0.

## Bài toán áp dụng

**Dijkstra và cái bẫy không có decrease-key.** Dijkstra sách giáo khoa cần "giảm priority của một đỉnh đã nằm trong hàng đợi" trong O(log n). `heapq` **không có API này**, và mọi nỗ lực tìm-rồi-sửa phần tử giữa heap đều sai: tìm là O(n), và sửa tại chỗ phá vỡ heap invariant.

Cách khắc phục chuẩn — **push entry mới, bỏ qua entry stale khi pop**:

```python
import heapq


def dijkstra(n: int, adj: dict[int, list[tuple[int, int]]], src: int) -> list[float]:
    """heapq không có decrease-key -> push bản ghi mới, bỏ qua entry stale."""
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    pq: list[tuple[int, int]] = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:          # entry stale: đã có đường ngắn hơn tới u
            continue
        for v, w in adj.get(u, ()):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))   # KHÔNG sửa entry cũ, push cái mới
    return dist
```

Dòng `if d > dist[u]: continue` là **toàn bộ** kỹ thuật. Nó nói: "entry này ghi rằng đường tới `u` dài `d`, nhưng `dist[u]` đã tốt hơn — vậy entry này lỗi thời, bỏ". Không có dòng đó thì thuật toán vẫn ra kết quả đúng (vì cập nhật `dist` được bảo vệ bởi `if nd < dist[v]`) nhưng chậm hơn nhiều vì mở rộng lại các đỉnh đã xong.

Cái giá: heap có thể chứa tới `O(E)` entry thay vì `O(V)`, nên độ phức tạp là O(E log E) thay vì O(E log V). Với đồ thị thưa hai cái tương đương; với đồ thị dày thì chênh một hằng số nhỏ. Đổi lại là code 12 dòng thay vì một indexed priority queue tự cài.

Đã stress test 2000 đồ thị ngẫu nhiên (≤ 7 đỉnh, cạnh và trọng số ngẫu nhiên) đối chiếu với Dijkstra brute-force O(V²). Ví dụ đồ thị `0→1(1), 0→2(4), 1→2(2), 1→3(6), 2→3(3)` cho `[0, 1, 3, 6]`.

**Event simulation.** Mô phỏng theo sự kiện (discrete event simulation) giữ một heap các `(thời_điểm, số_thứ_tự, sự_kiện)`; vòng lặp chính pop sự kiện sớm nhất, xử lý nó, và có thể push các sự kiện mới sinh ra ở tương lai. Toàn bộ mô phỏng mạng, hàng đợi khách hàng, hay logic game turn-based đều là khuôn này. Số thứ tự là tie-break bắt buộc — hai sự kiện cùng thời điểm phải xử lý theo thứ tự tạo ra.

**Task scheduler theo priority.** Cùng khuôn, với `(priority, seq, task)`. Nếu cần huỷ task đã lên lịch → dùng `LazyDeleteHeap` ở trên (đây chính xác là cách `sched` và `asyncio` xử lý `Timer.cancel()`).

## Use case thực tế

**Event loop của `asyncio`.** `loop.call_later(delay, cb)` đưa một `TimerHandle` vào một heap sắp theo thời điểm chạy. Mỗi vòng lặp, event loop nhìn `heap[0]` để biết còn bao lâu nữa mới có timer đến hạn, và dùng con số đó làm timeout cho `select()`. `TimerHandle.cancel()` **không xoá khỏi heap** — nó chỉ đặt cờ `_cancelled`, và CPython dọn rác khi số handle đã huỷ vượt một ngưỡng. Đó là lazy deletion trong stdlib thật.

**Module `sched`** trong stdlib là một priority queue thuần: `scheduler.enterabs(time, priority, action)` chèn vào một list giữ sorted bằng `bisect.insort`, và `cancel()` là `list.remove()` — O(n). Với ít sự kiện thì đơn giản thắng.

**OS process scheduler.** CFS của Linux dùng red-black tree chứ không phải heap (vì cần cả xoá tuỳ ý lẫn lấy min), nhưng các scheduler real-time theo priority thì đúng là priority queue. Kubernetes scheduler và Celery cũng xếp task theo priority — tuy ở quy mô đó, cấu trúc dữ liệu không còn là nút thắt.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: dùng `heapq` (C, nhanh), đừng dùng `BinaryHeap` tự viết. Cần top-k một lần → `heapq.nlargest(k, iterable, key=...)`, nó tự chọn chiến lược tốt nhất (`max()` khi k=1, `sorted()` khi k gần n, heap khi ở giữa). Cần đếm rồi lấy top-k → `Counter.most_common(k)`. Cần ghép nhiều iterator đã sort → `heapq.merge(*iters, key=..., reverse=...)`, trả về **iterator** nên bộ nhớ chỉ O(số iterator) — đây là công cụ external sort trong stdlib mà ít người biết:

```python
import heapq

list(heapq.merge([1, 4, 7], [2, 3], [5, 6]))    # [1, 2, 3, 4, 5, 6, 7]
list(heapq.merge([7, 4, 1], [3, 2], reverse=True))   # [7, 4, 3, 2, 1]
heapq.nlargest(2, [("a", 3), ("b", 9), ("c", 5)], key=lambda t: t[1])
# [('b', 9), ('c', 5)]
```

Cần priority queue có **cập nhật priority** → `heapq` không đủ, dùng `sortedcontainers.SortedList` (§19) hoặc lazy deletion.

## Bẫy thường gặp trong Python

**`heapq` chỉ có min-heap.** Không có `heapq.heapify_max` công khai. Muốn max-heap thì phủ định (`-x` hoặc `-priority` trong tuple). Với object không phải số, phải bọc trong một class có `__lt__` đảo ngược — lúc đó cân nhắc `sorted` hoặc `SortedList`.

**Tie-break rơi vào phần tử không so sánh được.** Đã tái hiện ở phần Lý thuyết: `(1, Task("a"))` và `(1, Task("b"))` ném `TypeError`. Luôn dùng `(priority, counter, item)` với `counter` là `int` duy nhất. Bẫy này **chỉ lộ khi có priority trùng nhau**, nên test nhỏ tự nghĩ thường không bắt được.

**`heap[0]` là min, nhưng `heap[-1]` KHÔNG phải max.** Heap không sắp xếp; `heap[-1]` chỉ là một lá nào đó. Tìm max trong min-heap là O(n) — `max(heap)`. Tương tự, `heap` in ra trông "gần sorted" nhưng không phải, và `list(heap)` không cho thứ tự tăng dần. Muốn sorted phải pop hết ra.

**`heapify` là O(n), nhưng `sorted` không phải `heapify`.** Đo được `heapify` 2·10⁶ phần tử mất 0.024 s trong khi push từng cái mất 0.082 s. Nếu bạn có sẵn cả list, luôn `heapify`.

**Sửa phần tử trong heap tại chỗ phá vỡ invariant.** `heap[i] = new_value` hoặc `heap[i].priority = ...` là bug im lặng — heap không biết gì và tiếp tục hoạt động với dữ liệu sai. Không có API decrease-key; dùng push-entry-mới + kiểm tra stale, hoặc lazy deletion.

**`heapreplace` trên heap rỗng ném `IndexError`, `heappushpop` thì không.** Và hai hàm cho kết quả khác nhau khi phần tử mới nhỏ hơn root — xem bảng ở phần Lý thuyết. Nhầm hai hàm này là bug logic khó thấy vì cả hai đều "chạy được".

**`heapq.merge` trả về iterator, không phải list.** `heapq.merge(a, b)` không tiêu thụ gì cho tới khi bạn duyệt nó; `len()` không dùng được, và duyệt hai lần thì lần thứ hai rỗng. Đó là tính năng (bộ nhớ O(k) thay vì O(N)), nhưng gây bất ngờ.

**`bisect.insort` không phải giải pháp thay thế heap.** Nó cho mảng sorted đầy đủ (mạnh hơn heap) nhưng chèn là O(n). Với n lớn và nhiều lần chèn, đó là O(n²) — chính là bản naive của bài 295.
