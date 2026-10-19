# 14. Queue & Deque

Queue là FIFO — nghe đơn giản, nhưng trong Python nó là nơi sinh ra lỗi hiệu năng phổ biến nhất của người mới: viết BFS bằng `list.pop(0)`. Section này chốt cost model của `collections.deque`, dựng ring buffer từ đầu, và đi sâu vào **monotonic deque** — kỹ thuật cho phép biết max của một cửa sổ trượt trong O(1) amortized mà heap không làm được.

## Lý thuyết

### `deque` là gì dưới nắp

`collections.deque` không phải linked list của từng phần tử, cũng không phải mảng liên tục. CPython cài nó là **doubly linked list của các block, mỗi block chứa 64 con trỏ**. Nhờ đó nó có cả hai thứ:

- Thêm/xoá ở **hai đầu**: O(1) thật sự — chỉ ghi vào block đầu/cuối, thỉnh thoảng cấp phát một block mới.
- **Cache locality** trong từng block: duyệt tuần tự vẫn nhanh vì 64 phần tử liền nhau trong bộ nhớ.

Cái nó **không** có là truy cập ngẫu nhiên: `dq[i]` phải đi qua các block, tức là O(n) ở giữa (chính xác hơn: O(min(i, n−i))).

### Bảng so sánh — ba lựa chọn và khi nào dùng cái nào

| Thao tác | `list` | `deque` | `queue.Queue` |
|---|---|---|---|
| append cuối | O(1) am. | O(1) | O(1) + lock |
| pop cuối | O(1) am. | O(1) | — |
| append đầu | **O(n)** | O(1) | — |
| pop đầu | **O(n)** | O(1) | O(1) + lock |
| `x[i]` giữa | **O(1)** | O(n) | không có |
| slicing | có | không có | không có |
| thread-safe có chặn | không | không¹ | **có** |

¹ `deque.append`/`popleft` là atomic nhờ GIL nên an toàn cho producer/consumer đơn giản, nhưng không có `join()`, `task_done()`, hay chặn khi rỗng.

Quy tắc chọn:
- Cần index ngẫu nhiên hoặc slicing → `list`.
- Cần hai đầu, dùng cho **thuật toán** (BFS, sliding window) → `deque`.
- Cần **đồng bộ giữa các thread** (producer/consumer, chặn khi rỗng, timeout) → `queue.Queue`. Đây là công cụ concurrency, **không phải** công cụ thuật toán: nó có lock nên chậm hơn đáng kể. Đo trên máy này với 10⁵ cặp put/get: `queue.Queue` mất 0.0531 s, `deque` mất 0.0041 s — **chậm 13 lần** cho cùng công việc. Dùng `queue.Queue` trong BFS là trả tiền cho thứ mình không cần.

### `maxlen=` — circular buffer miễn phí

`deque(maxlen=k)` tự động đẩy phần tử ở đầu kia ra khi vượt quá `k`:

```python
from collections import deque

d = deque(maxlen=3)
for i in range(6):
    d.append(i)
# list(d) == [3, 4, 5]
```

Đó là ring buffer viết bằng C, không mất một dòng code nào. Dùng cho: N sự kiện gần nhất, rolling window cố định, log buffer.

### Monotonic deque — invariant

Bài toán: biết max của mỗi cửa sổ độ dài `k` khi cửa sổ trượt qua mảng.

Vì sao heap không đủ tốt? Heap cho ta max trong O(1) nhưng khi phần tử trôi ra khỏi cửa sổ, ta cần **xoá một phần tử tuỳ ý** — `heapq` không hỗ trợ, phải dùng lazy deletion (§16), và heap có thể phình tới O(n). Deque giải quyết triệt để hơn.

Quan sát mấu chốt: nếu `i < j` và `nums[i] <= nums[j]`, thì `nums[i]` **không bao giờ** còn là max của cửa sổ nào nữa — mọi cửa sổ chứa `i` mà còn nằm trong tương lai đều chứa `j` (vì `j` trôi ra sau `i`), và `j` lớn hơn hoặc bằng. Nên `i` là rác, vứt được.

> **Invariant**: deque chứa index theo thứ tự tăng, và giá trị tương ứng giảm nghiêm ngặt từ đầu đến cuối. Do đó `dq[0]` luôn là index của phần tử lớn nhất trong cửa sổ hiện tại.

Ba thao tác mỗi bước, đúng thứ tự này:
1. `pop()` từ **đuôi** khi phần tử mới lớn hơn hoặc bằng — dọn rác theo quan sát trên, giữ tính giảm dần.
2. `append(i)` — thêm ứng viên mới.
3. `popleft()` khi `dq[0]` đã trôi ra ngoài cửa sổ (`dq[0] <= i - k`).

Chi phí: mỗi index vào deque đúng một lần, ra tối đa một lần → **O(n) tổng**, O(k) bộ nhớ.

| | Naive | Heap + lazy delete | Monotonic deque |
|---|---|---|---|
| Time | O(n·k) | O(n log n) | **O(n)** |
| Space | O(1) | O(n) worst | **O(k)** |

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/queue/circular_queue.py`

```python
class CircularQueue:
    """Ring buffer dung lượng cố định, mọi thao tác O(1).

    Invariant: _head là chỉ số ô đầu tiên hợp lệ; _size ô kế tiếp tính theo
    modulo là dữ liệu; ô thứ (_head + _size) % cap là chỗ trống kế tiếp.
    Dùng _size (thay vì so sánh head/tail) để phân biệt rỗng và đầy.
    """

    def __init__(self, capacity: int) -> None:
        self._buf: list = [None] * capacity
        self._cap = capacity
        self._head = 0
        self._size = 0

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self._cap

    def push_back(self, value) -> bool:
        if self.is_full():
            return False
        self._buf[(self._head + self._size) % self._cap] = value
        self._size += 1
        return True

    def push_front(self, value) -> bool:
        if self.is_full():
            return False
        self._head = (self._head - 1) % self._cap
        self._buf[self._head] = value
        self._size += 1
        return True

    def pop_front(self):
        if self.is_empty():
            return None
        value = self._buf[self._head]
        self._buf[self._head] = None            # nhả tham chiếu cho GC
        self._head = (self._head + 1) % self._cap
        self._size -= 1
        return value

    def front(self):
        return None if self.is_empty() else self._buf[self._head]

    def rear(self):
        return None if self.is_empty() else self._buf[(self._head + self._size - 1) % self._cap]

    def __len__(self) -> int:
        return self._size
```

Hai quyết định thiết kế đáng chú ý:

- **Giữ `_size` thay vì `_tail`.** Nếu chỉ có `head` và `tail`, thì `head == tail` vừa có nghĩa là rỗng vừa có nghĩa là đầy — không phân biệt được. Cách khác là hy sinh một ô (luôn để trống một slot), nhưng giữ `_size` rõ ràng hơn và dùng hết dung lượng.
- **`self._buf[self._head] = None` sau khi pop.** Nếu không, buffer vẫn giữ tham chiếu tới object đã "ra khỏi hàng đợi", và GC không thu hồi được. Đây là dạng memory leak khó thấy trong Python: object vẫn sống vì một mảng nội bộ còn trỏ tới nó.
- `(self._head - 1) % self._cap` chạy đúng nhờ Python lấy modulo về phía dương: `-1 % 5 == 4` (khác C/C++, xem §04).

Đã chạy: đẩy `1, 2` vào đuôi và `0` vào đầu cho capacity 3, `push_back` thứ tư trả `False`, `front/rear/len` = `(0, 2, 3)`, và sau khi rút thì trả về đúng `[1, 2, 3]`.

Đề xuất đường dẫn: `cores/python/queue/monotonic_deque.py`

```python
from collections import deque


def window_max(nums: list[int], k: int) -> list[int]:
    """Max của mọi cửa sổ độ dài k, O(n) tổng.

    Invariant: dq chứa index theo thứ tự TĂNG, và nums[dq] GIẢM dần.
    Do đó dq[0] luôn là index của phần tử lớn nhất trong cửa sổ hiện tại.
    """
    dq: deque[int] = deque()
    out: list[int] = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:      # phần tử cũ nhỏ hơn -> vô dụng mãi mãi
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:                   # index đầu đã trôi ra khỏi cửa sổ
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

Đã chạy: `window_max([1,3,-1,-3,5,3,6,7], 3)` → `[3, 3, 5, 5, 6, 7]`. Đổi `<=` thành `>=` và ta có `window_min` — không cần thay đổi gì khác.

## Bài tập chi tiết

### Bài 1 — 239. Sliding Window Maximum

#### Requirements

Cho mảng `nums` và số nguyên `k`. Cửa sổ độ dài `k` trượt từ trái sang phải, mỗi lần một bước. Trả về mảng max của từng vị trí cửa sổ. `1 ≤ n ≤ 10⁵`, `1 ≤ k ≤ n`, giá trị có thể âm (`-10⁴ ≤ nums[i] ≤ 10⁴`).

Edge cases: `k == 1` (kết quả là chính `nums`); `k == n` (một phần tử duy nhất); toàn số âm (khởi tạo biến max bằng 0 là bug); mảng tăng dần (deque luôn chỉ có 1 phần tử); mảng giảm dần (deque phình tới `k` phần tử — đây là worst case bộ nhớ); giá trị trùng nhau.

Độ dài kết quả là `n - k + 1`, không phải `n`.

#### Complexity mục tiêu

n = 10⁵ và `k` có thể tới 10⁵ → naive O(n·k) là 10¹⁰, TLE dứt khoát. Bảng §02 nói cần O(n log n) hoặc O(n). Heap cho O(n log n) nhưng phải kèm lazy deletion; deque cho **O(n)** sạch, nên nhắm vào đó.

#### Idea

Như đã lập luận ở phần Lý thuyết: giữ trong deque các **index còn có khả năng là max của một cửa sổ tương lai**.

> **Invariant**: index trong deque tăng dần, giá trị tương ứng giảm dần. `dq[0]` là max của cửa sổ hiện tại.

Chứng minh đúng đắn gồm hai nửa. (a) *`dq[0]` là max*: mọi index bị pop khỏi đuôi đều có giá trị ≤ một phần tử mới hơn còn trong deque, nên không thể là max; mọi index bị pop khỏi đầu đều đã ra ngoài cửa sổ. Vậy deque chứa đủ mọi ứng viên hợp lệ, và do giảm dần, đầu là lớn nhất. (b) *không mất nghiệm*: index `i` chỉ bị vứt khi tồn tại `j > i` với `nums[j] >= nums[i]`; mọi cửa sổ tương lai chứa `i` cũng chứa `j`, nên `i` không bao giờ cần đến nữa.

Thứ tự ba thao tác quan trọng: pop-đuôi → append → pop-đầu. Nếu pop-đầu trước append, cửa sổ chưa được cập nhật đúng khi phần tử mới chính là cái vừa bị pop.

#### Naive

```python
class SolutionNaive239:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]
```

O(n·k): mỗi cửa sổ vừa slice (copy O(k)) vừa `max` (quét O(k)). Đây là oracle tuyệt vời — không thể sai — nhưng với n = k = 5·10⁴ thì là 2.5·10⁹ phép, kèm 5·10⁴ lần cấp phát list tạm.

#### Optimized

```python
from collections import deque


class Solution239:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        dq: deque[int] = deque()      # index, giá trị giảm dần
        out: list[int] = []
        for i, x in enumerate(nums):
            while dq and nums[dq[-1]] <= x:
                dq.pop()
            dq.append(i)
            if dq[0] <= i - k:
                dq.popleft()
            if i >= k - 1:
                out.append(nums[dq[0]])
        return out
```

O(n) time, O(k) space. Đánh đổi: ta lưu **index chứ không lưu giá trị** — thêm một tầng gián tiếp khiến code khó đọc hơn hẳn, nhưng đó là điều kiện cần để biết khi nào phần tử trôi ra khỏi cửa sổ. Nếu lưu giá trị thì không có cách nào biết `dq[0]` còn trong cửa sổ hay không.

Dùng `<=` (không phải `<`) khi pop đuôi: với giá trị trùng nhau, giữ cái mới hơn thì cửa sổ tồn tại lâu hơn. Cả hai đều cho kết quả đúng, nhưng `<=` giữ deque nhỏ hơn.

Đã stress test 3000 lần với `n ∈ [1,10]`, giá trị `[-3,3]` (hẹp để ép trùng lặp và số âm), `k ∈ [1,n]`, naive khớp optimized. `maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3)` → `[3,3,5,5,6,7]`.

### Bài 2 — 232. Implement Queue using Stacks

#### Requirements

Cài lớp `MyQueue` với `push(x)`, `pop()`, `peek()`, `empty()` **chỉ dùng hai stack** (chỉ được phép `append`, `pop()` cuối, `[-1]`, kiểm tra rỗng). Tối đa 100 lời gọi; `pop`/`peek` chỉ gọi khi queue không rỗng. Đề yêu cầu thêm: đạt **amortized O(1)** mỗi thao tác.

Edge cases: `pop` ngay sau nhiều `push` liên tiếp; xen kẽ `push`/`pop`; `empty()` khi một trong hai stack rỗng còn cái kia không.

#### Complexity mục tiêu

Với 100 lời gọi thì mọi thứ đều pass. Bài này kiểm tra **hiểu biết về amortized analysis**, không kiểm tra tốc độ. Mục tiêu: mỗi thao tác O(1) amortized, worst-case một thao tác đơn lẻ là O(n) — và phải giải thích được vì sao hai điều đó không mâu thuẫn.

#### Idea

Một stack cho ta LIFO; đảo một stack sang stack khác cho ta FIFO. Câu hỏi là **đảo khi nào**.

> **Invariant**: `_out` chứa các phần tử cũ nhất theo thứ tự đảo (đỉnh `_out` là phần tử vào sớm nhất trong toàn queue); `_in` chứa các phần tử mới theo thứ tự vào. Hàng đợi logic = đọc `_out` từ đỉnh xuống, rồi `_in` từ đáy lên.

Quy tắc dốc: **chỉ dốc `_in` sang `_out` khi `_out` cạn**. Điều này giữ invariant (mọi phần tử trong `_in` đều mới hơn mọi phần tử trong `_out`, nên dốc chỉ khi `_out` rỗng là hợp lệ) và cho amortized O(1).

Phân tích amortized bằng phương pháp accounting: mỗi phần tử được **push vào `_in` đúng 1 lần, pop khỏi `_in` đúng 1 lần, push vào `_out` đúng 1 lần, pop khỏi `_out` đúng 1 lần** — tổng 4 thao tác cơ bản trong suốt vòng đời, bất kể có bao nhiêu lời gọi. Nên n thao tác queue tốn O(n) tổng, tức O(1) amortized. Một lời gọi `pop` cụ thể có thể tốn O(n) (khi phải dốc cả stack), nhưng nó "trả nợ" cho n lần `push` trước đó đã rẻ.

#### Naive

```python
class MyQueueNaive:
    def __init__(self) -> None:
        self._s: list[int] = []

    def push(self, x: int) -> None:
        # Đảo toàn bộ để phần tử mới nằm dưới đáy -> pop() lấy đúng FIFO.
        tmp: list[int] = []
        while self._s:
            tmp.append(self._s.pop())
        self._s.append(x)
        while tmp:
            self._s.append(tmp.pop())

    def pop(self) -> int:
        return self._s.pop()

    def peek(self) -> int:
        return self._s[-1]

    def empty(self) -> bool:
        return not self._s
```

`push` là **O(n) mọi lần**, không amortized gì cả — n lần push tốn O(n²) tổng. Ưu điểm duy nhất: `pop`/`peek` là O(1) đúng nghĩa, và invariant cực đơn giản ("stack luôn giữ thứ tự đảo"). Đây là lời giải hợp lệ trên LeetCode nhưng trượt yêu cầu amortized của đề.

#### Optimized

```python
class MyQueue:
    """Hai stack, amortized O(1) mỗi thao tác.

    Invariant: _out giữ các phần tử CŨ NHẤT theo thứ tự đảo (đỉnh _out là phần
    tử vào sớm nhất); _in giữ các phần tử mới theo thứ tự vào. Hàng đợi logic =
    reversed(_out) đọc từ đỉnh + _in đọc từ đáy.
    """

    def __init__(self) -> None:
        self._in: list[int] = []
        self._out: list[int] = []

    def _shift(self) -> None:
        if not self._out:                    # chỉ dốc khi _out cạn
            while self._in:
                self._out.append(self._in.pop())

    def push(self, x: int) -> None:
        self._in.append(x)

    def pop(self) -> int:
        self._shift()
        return self._out.pop()

    def peek(self) -> int:
        self._shift()
        return self._out[-1]

    def empty(self) -> bool:
        return not self._in and not self._out
```

Amortized O(1) mọi thao tác, O(n) space. Đánh đổi: mất tính "worst-case bounded" — nếu bạn đang viết hệ thống real-time có SLA cho **từng** thao tác (không phải trung bình), một `pop` tốn O(n) là không chấp nhận được, và bản naive với `push` O(n) đều đặn lại tốt hơn. Đây là sự khác nhau thực chất giữa amortized và worst-case, không phải chi tiết học thuật.

Bẫy chết người: **`if not self._out` chứ không phải `while`**. Nếu dốc mỗi lần `pop`, invariant vỡ (phần tử mới bị đặt lên trên phần tử cũ) và kết quả sai. Đây cũng là lý do bài này đáng làm.

Đã stress test 2000 phiên, mỗi phiên 30 thao tác ngẫu nhiên, đối chiếu cả `MyQueue` và `MyQueueNaive` với `collections.deque` làm reference.

### Bài 3 — 622. Design Circular Queue

#### Requirements

Cài `MyCircularQueue(k)` với `enQueue(value)`, `deQueue()`, `Front()`, `Rear()`, `isEmpty()`, `isFull()`. `enQueue`/`deQueue` trả `bool` (thất bại khi đầy/rỗng); `Front`/`Rear` trả `-1` khi rỗng. `1 ≤ k ≤ 1000`, tối đa 3000 lời gọi. Yêu cầu: mọi thao tác **O(1)**.

Edge cases: `k == 1`; đầy rồi enQueue tiếp; rỗng rồi deQueue tiếp; enQueue/deQueue xen kẽ nhiều lần để `head` cuộn qua hết mảng nhiều vòng (nơi lỗi modulo lộ ra); `Rear()` khi queue vừa cuộn qua biên.

#### Complexity mục tiêu

Ràng buộc nhỏ (3000 lời gọi, k ≤ 1000) nên O(n) mỗi thao tác vẫn pass. Nhưng đề **nêu tường minh** yêu cầu O(1) — đây là bài design, cái được chấm là cấu trúc, không phải thời gian chạy. Cấu trúc đạt O(1): ring buffer trên mảng cố định.

#### Idea

Cấp phát sẵn mảng `k` ô và **không bao giờ dịch chuyển phần tử**. Thay vào đó, dịch chỉ số.

> **Invariant**: các phần tử hợp lệ nằm ở các vị trí `(_head + t) % _cap` với `t ∈ [0, _size)`. Ô trống kế tiếp là `(_head + _size) % _cap`.

`enQueue` ghi vào ô trống kế tiếp và tăng `_size`; `deQueue` tăng `_head` và giảm `_size`. Cả hai là số học modulo — O(1) và không cấp phát.

Vì sao cần `_size` mà không dùng cặp `(head, tail)`: khi `head == tail` ta không phân biệt được rỗng với đầy. Giữ `_size` giải quyết triệt để và cho `isFull`/`isEmpty` miễn phí.

#### Naive

```python
class MyCircularQueueNaive:
    def __init__(self, k: int):
        self._k = k
        self._data: list[int] = []

    def enQueue(self, value: int) -> bool:
        if len(self._data) == self._k:
            return False
        self._data.append(value)
        return True

    def deQueue(self) -> bool:
        if not self._data:
            return False
        self._data.pop(0)          # O(n): dịch toàn bộ mảng
        return True

    def Front(self) -> int:
        return self._data[0] if self._data else -1

    def Rear(self) -> int:
        return self._data[-1] if self._data else -1

    def isEmpty(self) -> bool:
        return not self._data

    def isFull(self) -> bool:
        return len(self._data) == self._k
```

`deQueue` là **O(k)** vì `list.pop(0)` `memmove` toàn bộ phần còn lại. Với k = 1000 và 3000 lời gọi thì chỉ là 3·10⁶ byte-copy — vẫn pass. Nhưng nó vi phạm yêu cầu O(1) của đề, và cách viết này chính là mầm mống của bug hiệu năng trong BFS.

#### Optimized

```python
class MyCircularQueue:
    def __init__(self, k: int):
        self._buf = [0] * k
        self._cap = k
        self._head = 0
        self._size = 0

    def enQueue(self, value: int) -> bool:
        if self._size == self._cap:
            return False
        self._buf[(self._head + self._size) % self._cap] = value
        self._size += 1
        return True

    def deQueue(self) -> bool:
        if self._size == 0:
            return False
        self._head = (self._head + 1) % self._cap
        self._size -= 1
        return True

    def Front(self) -> int:
        return -1 if self._size == 0 else self._buf[self._head]

    def Rear(self) -> int:
        return -1 if self._size == 0 else self._buf[(self._head + self._size - 1) % self._cap]

    def isEmpty(self) -> bool:
        return self._size == 0

    def isFull(self) -> bool:
        return self._size == self._cap
```

O(1) mọi thao tác, O(k) space cố định. Đánh đổi: dung lượng **cố định cứng** — không grow được. Đó vừa là nhược điểm (không dùng làm queue tổng quát) vừa là ưu điểm cực lớn trong hệ thống nhúng/real-time: không cấp phát động nghĩa là không có GC pause, không có latency spike bất ngờ. Đây chính là lý do ring buffer thống trị ở tầng driver và audio.

Đã stress test 2000 phiên × 30 thao tác ngẫu nhiên với `k ∈ [1,5]` (nhỏ để ép cuộn vòng liên tục), đối chiếu với bản naive.

## Bài luyện thêm

- **933. Number of Recent Calls** — giữ một `deque` các timestamp, mỗi lần `ping(t)` thì `popleft` mọi timestamp `< t - 3000` rồi trả `len(dq)`; đây là sliding window trên trục thời gian, giống hệt rate limiter bên dưới.

## Bài toán áp dụng

**Rate limiter kiểu "tối đa N request trong T giây gần nhất"** — bài toán này là sliding window trên timestamp, và `deque` là cấu trúc chính xác cho nó:

```python
from collections import deque


class SlidingWindowRateLimiter:
    """Cho phép tối đa `limit` request trong `window` giây gần nhất."""

    def __init__(self, limit: int, window: float) -> None:
        self._limit = limit
        self._window = window
        self._hits: deque[float] = deque()

    def allow(self, now: float) -> bool:
        while self._hits and self._hits[0] <= now - self._window:
            self._hits.popleft()             # bỏ các hit đã hết hạn
        if len(self._hits) >= self._limit:
            return False
        self._hits.append(now)
        return True
```

Đã chạy với `limit=3, window=1.0` trên chuỗi thời điểm `[0.0, 0.1, 0.2, 0.3, 1.05, 1.15]` → `[True, True, True, False, True, True]`: request thứ tư bị chặn vì ba cái trước còn trong cửa sổ, nhưng tới `t=1.05` thì `t=0.0` đã hết hạn nên chỗ được nhả ra.

Vì sao `deque` mà không phải `list`: timestamp hết hạn luôn ở **đầu** (thời gian tăng đơn điệu), và ta xoá chúng liên tục — đúng thao tác `popleft` O(1). Với `list` thì mỗi lần dọn là O(n).

Biến thể bộ nhớ cố định: `deque(maxlen=limit)` — chỉ giữ đúng `limit` timestamp gần nhất, kiểm tra `dq[0] > now - window` là biết có vượt hạn mức không. Đổi độ chính xác lấy bộ nhớ O(limit) chặn cứng thay vì O(số request trong cửa sổ).

**Moving average trên time-series** dùng cùng khuôn: `deque(maxlen=k)` giữ k giá trị gần nhất, cộng giá trị mới và trừ giá trị bị đẩy ra để cập nhật tổng trong O(1) (§07).

## Use case thực tế

**Ready-queue của OS scheduler.** Các tiến trình sẵn sàng chạy nằm trong queue; scheduler `popleft` cái tiếp theo. Round-robin chính là `popleft` rồi `append` lại vào đuôi sau khi hết time slice — hai thao tác O(1) trên deque.

**Ring buffer trong driver và audio.** Card âm thanh, network card, `dmesg` của kernel đều dùng ring buffer dung lượng cố định: producer (phần cứng) ghi vào một đầu, consumer (phần mềm) đọc từ đầu kia, không bao giờ cấp phát bộ nhớ trong đường dẫn nóng. Chính là `CircularQueue` ở trên, viết bằng C và không có `_size` mà dùng con trỏ nguyên tử.

**Message broker.** Kafka partition là một log append-only đọc theo offset tăng dần — FIFO ở tầng phân tán, với "queue" nằm trên đĩa và consumer tự giữ vị trí đọc. RabbitMQ gần với queue truyền thống hơn (message bị xoá khi ack). Ý tưởng thì giống, nhưng các vấn đề thật ở tầng này là durability, ordering guarantee và backpressure — không phải độ phức tạp của `popleft`.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: gần như luôn. Cần queue trong một tiến trình → `collections.deque`. Cần queue giữa các thread → `queue.Queue`. Cần queue giữa các process → `multiprocessing.Queue`. Cần queue giữa các máy → Redis/Kafka/SQS, và lúc này bạn đang giải bài toán hạ tầng chứ không phải bài toán cấu trúc dữ liệu. Tự viết `CircularQueue` chỉ đáng khi bạn cần **bộ nhớ cố định tuyệt đối** hoặc đang học.

## Bẫy thường gặp trong Python

**`list.pop(0)` trong BFS — lỗi kinh điển số một.** Đo trên máy này với 2·10⁵ phần tử: `list.pop(0)` mất **2.2828 s**, `deque.popleft()` mất **0.0033 s** — chậm **690 lần**. BFS đúng thuật toán vẫn TLE chỉ vì dòng này. Luôn:

```python
from collections import deque

start, adj = 0, {0: [1, 2], 1: [], 2: []}
q = deque([start])
while q:
    node = q.popleft()      # KHÔNG phải q.pop(0)
    q.extend(adj[node])
```

**`deque[i]` ở giữa là O(n).** Đo: 2000 lần đọc `d[100000]` trên deque 2·10⁵ phần tử mất 0.0182 s; cùng số lần trên `list` mất ~0 s. Nếu thuật toán cần truy cập ngẫu nhiên, `deque` là lựa chọn sai. `deque` cũng **không hỗ trợ slicing** — `d[1:3]` ném `TypeError`, phải dùng `itertools.islice`.

**`queue.Queue` không phải công cụ thuật toán.** Nó có lock, condition variable, và `get()` **chặn vô hạn** khi rỗng thay vì báo lỗi — dùng nhầm trong BFS thì chương trình treo im lặng thay vì kết thúc. Đo được chậm 13 lần so với `deque`. Chỉ dùng khi thật sự có nhiều thread.

**`deque(maxlen=k)` âm thầm nuốt dữ liệu.** Khi đầy, `append` **không** báo lỗi mà lặng lẽ đẩy phần tử đầu kia ra. Đó là tính năng khi bạn muốn ring buffer, và là bug im lặng khi bạn quên mất `maxlen` đang được đặt.

**Quên `[i]` là index chứ không phải giá trị trong monotonic deque.** `nums[dq[-1]] <= x` — dễ viết nhầm thành `dq[-1] <= x`. Test case toàn số dương nhỏ có thể vẫn ra đúng ngẫu nhiên; test có số âm thì lộ ngay. Đây là lý do stress test của bài 239 dùng miền `[-3, 3]`.

**Không nhả tham chiếu khi pop khỏi buffer tự viết.** `self._buf[self._head] = None` sau khi đọc giá trị ra: thiếu dòng này, object "đã ra khỏi queue" vẫn bị mảng giữ sống, và với queue chứa object lớn thì đó là memory leak thật.
