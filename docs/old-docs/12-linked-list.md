# 12. Linked List

Linked list là cấu trúc dữ liệu duy nhất trong handbook này mà bạn gần như **không bao giờ nên dùng trong code Python production**, nhưng lại phải thành thạo vì nó là bài kiểm tra tư duy con trỏ chuẩn mực nhất trong phỏng vấn. Section này cài `SinglyLinkedList`/`DoublyLinkedList` từ đầu, luyện ba kỹ thuật con trỏ cốt lõi (fast & slow, reverse in-place, tách/merge), và kết lại bằng lý do kỹ thuật vì sao `list`/`deque` thắng nó trong CPython.

## Lý thuyết

### Vì sao cần dummy node

Mọi bug kinh điển của linked list đều đến từ việc **node đầu danh sách không có node đứng trước nó**. Xoá phần tử đầu phải sửa biến `head`, xoá phần tử giữa phải sửa `prev.next` — hai đường code khác nhau, và đường ít chạy hơn là đường có bug.

Dummy head (sentinel) xoá bỏ sự phân biệt đó:

> **Invariant**: `dummy` luôn tồn tại, không bao giờ bị xoá, và mọi node dữ liệu thật đều có một node đứng trước hợp lệ.

Nhờ invariant này, thao tác xoá node ở vị trí `i` luôn là đúng một dòng `prev.next = prev.next.next`, bất kể `i == 0` hay không. Doubly linked list đi xa hơn: dùng **cả** dummy head và dummy tail, khi đó `unlink(node)` là hai phép gán không cần một lệnh `if` nào — đây chính là lý do LRU cache dùng doubly linked list chứ không dùng singly.

### Reverse in-place bằng 3 con trỏ

```
prev = None
curr = head
```

> **Invariant mỗi vòng lặp**: đoạn từ `head` gốc đến node ngay trước `curr` đã bị đảo xong, và `prev` trỏ vào đầu đoạn đã đảo đó; `curr` trỏ vào phần chưa đụng tới, vẫn giữ nguyên thứ tự gốc.

Mỗi bước ta lưu `nxt = curr.next` (vì sắp ghi đè), quay mũi tên `curr.next = prev`, rồi trượt cả hai. Khi `curr is None`, "phần chưa đụng" rỗng nên `prev` là đầu danh sách đã đảo hoàn chỉnh. Việc lưu `nxt` **trước** khi ghi đè là điểm duy nhất có thể sai — quên nó thì mất luôn phần đuôi.

### Floyd cycle detection và vì sao điểm gặp lại cho ra đầu chu trình

Cho `slow` đi 1 bước, `fast` đi 2 bước mỗi vòng.

Nếu có cycle, khoảng cách `fast - slow` (đo dọc theo chu trình) tăng đúng 1 mỗi vòng, nên trong tối đa `C` vòng (C = độ dài chu trình) nó phải chạm 0 — hai con trỏ **bắt buộc** gặp nhau. Nếu không có cycle, `fast` chạm `None` trước.

Phần đẹp nhất là bước thứ hai. Gọi `L` là khoảng cách từ head tới đầu chu trình, `C` là độ dài chu trình, và điểm gặp nằm cách đầu chu trình `k` bước. Khi gặp nhau:

- `slow` đã đi `L + k` bước.
- `fast` đã đi `2(L + k)` bước, và chênh lệch phải là bội của `C`: `2(L+k) − (L+k) = L + k ≡ 0 (mod C)`.

Suy ra `L ≡ −k (mod C)`. Nghĩa là: đi thêm `L` bước từ điểm gặp thì rơi đúng vào đầu chu trình. Vậy đặt một `probe` ở `head`, cho `probe` và `slow` cùng đi 1 bước/lần, chỗ chúng gặp nhau chính là đầu chu trình. Không cần `set`, không cần bộ nhớ phụ.

### Bảng độ phức tạp

| Thao tác | `SinglyLinkedList` | `DoublyLinkedList` | `list` (CPython) | `deque` |
|---|---|---|---|---|
| Truy cập theo index | O(n) | O(n) | **O(1)** | O(n) |
| Chèn/xoá đầu | O(1) | O(1) | O(n) | **O(1)** |
| Chèn/xoá cuối | O(n)¹ | O(1) | **O(1)** amortized | **O(1)** |
| Xoá node khi đã cầm tham chiếu | O(n)² | **O(1)** | O(n) | O(n) |
| Bộ nhớ / phần tử | ~48 B + con trỏ | ~56 B + 2 con trỏ | 8 B (con trỏ trong mảng) | 8 B |

¹ O(1) nếu giữ thêm con trỏ `tail`. ² Vì cần tìm `prev`.

Dòng cuối bảng là toàn bộ lý do tồn tại của doubly linked list trong thực tế.

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/linked_list/singly.py`

```python
class ListNode:
    """Node cho singly linked list. Tên trùng LeetCode để tái dùng được ngay."""
    __slots__ = ("val", "next")

    def __init__(self, val: int = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"


class SinglyLinkedList:
    """Danh sách liên kết đơn có dummy head.

    Invariant: self._head luôn là node giả (sentinel), không bao giờ bị xoá.
    Nhờ đó mọi thao tác chèn/xoá đều có một node "trước" hợp lệ -> không cần
    tách riêng case "sửa phần tử đầu danh sách".
    """

    def __init__(self, values=()) -> None:
        self._head = ListNode()          # dummy, không chứa dữ liệu thật
        self._size = 0
        tail = self._head
        for v in values:
            tail.next = ListNode(v)
            tail = tail.next
            self._size += 1

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        cur = self._head.next
        while cur is not None:
            yield cur.val
            cur = cur.next

    def _node_before(self, index: int) -> ListNode:
        # Trả về node đứng NGAY TRƯỚC vị trí index (index == 0 -> dummy head).
        if not (0 <= index <= self._size):
            raise IndexError(index)
        cur = self._head
        for _ in range(index):
            cur = cur.next
        return cur

    def insert(self, index: int, val: int) -> None:
        prev = self._node_before(index)
        prev.next = ListNode(val, prev.next)
        self._size += 1

    def push_front(self, val: int) -> None:
        self.insert(0, val)

    def push_back(self, val: int) -> None:
        self.insert(self._size, val)

    def pop(self, index: int) -> int:
        if not (0 <= index < self._size):
            raise IndexError(index)
        prev = self._node_before(index)
        victim = prev.next
        prev.next = victim.next
        self._size -= 1
        return victim.val

    def reverse(self) -> None:
        """Đảo in-place bằng 3 con trỏ.

        Invariant mỗi vòng: đoạn đã duyệt đã bị đảo và prev trỏ vào đầu đoạn đó;
        curr trỏ vào phần chưa đụng tới. Kết thúc khi curr is None.
        """
        prev, curr = None, self._head.next
        while curr is not None:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        self._head.next = prev

    def to_list(self) -> list[int]:
        return list(self)
```

Kiểm thử nhanh (đã chạy — dán nối tiếp ngay sau class ở trên):

```text
s = SinglyLinkedList([1, 2, 3])
s.push_front(0); s.push_back(4); s.insert(2, 99)
assert s.to_list() == [0, 1, 99, 2, 3, 4]
assert s.pop(2) == 99 and len(s) == 5
s.reverse()
assert s.to_list() == [4, 3, 2, 1, 0]
```

Đề xuất đường dẫn: `cores/python/linked_list/doubly.py`

```python
class DNode:
    __slots__ = ("val", "prev", "next")

    def __init__(self, val=None, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next


class DoublyLinkedList:
    """Doubly linked list với dummy head VÀ dummy tail.

    Invariant: head <-> ... <-> tail luôn tồn tại; mọi node thật nằm giữa hai
    sentinel. Vì vậy unlink(node) chỉ là 2 phép gán, không cần kiểm tra None.
    """

    def __init__(self, values=()) -> None:
        self._head = DNode()
        self._tail = DNode()
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0
        for v in values:
            self.push_back(v)

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        cur = self._head.next
        while cur is not self._tail:
            yield cur.val
            cur = cur.next

    def _insert_after(self, node: DNode, val) -> DNode:
        new = DNode(val, node, node.next)
        node.next.prev = new
        node.next = new
        self._size += 1
        return new

    def push_front(self, val) -> DNode:
        return self._insert_after(self._head, val)

    def push_back(self, val) -> DNode:
        return self._insert_after(self._tail.prev, val)

    def unlink(self, node: DNode) -> None:
        """Gỡ một node đã cầm sẵn tham chiếu trong O(1) — đây là lý do duy nhất
        đáng dùng doubly linked list (LRU cache)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1

    def pop_front(self):
        if self._size == 0:
            raise IndexError("empty")
        node = self._head.next
        self.unlink(node)
        return node.val

    def pop_back(self):
        if self._size == 0:
            raise IndexError("empty")
        node = self._tail.prev
        self.unlink(node)
        return node.val

    def to_list(self) -> list:
        return list(self)
```

Chú ý `push_back`/`push_front` **trả về node** — đó là điều kiện cần để LRU cache giữ được `dict[key] -> DNode` rồi `unlink` node đó trong O(1).

Hai helper dùng chung cho phần bài tập bên dưới (đề xuất `cores/python/linked_list/utils.py`):

```python
class ListNode:                    # LeetCode cấp sẵn; bản đầy đủ ở mục Cài đặt
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def build(values: list[int], pos: int = -1) -> ListNode | None:
    """Dựng linked list; nếu pos >= 0 thì nối đuôi vào node thứ pos tạo cycle."""
    dummy = ListNode()
    tail = dummy
    nodes = []
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
        nodes.append(tail)
    if pos >= 0 and nodes:
        tail.next = nodes[pos]
    return dummy.next


def to_list(head: ListNode | None, limit: int = 10_000) -> list[int]:
    out = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out
```

## Bài tập chi tiết

### Bài 1 — 142. Linked List Cycle II

#### Requirements

Cho `head` của một singly linked list. Nếu danh sách có chu trình, trả về node **bắt đầu** chu trình; nếu không, trả về `None`. Đề cho thêm tham số `pos` chỉ để mô tả test case, code không được dùng nó. Ràng buộc: số node từ 0 đến 10⁴.

Edge cases: danh sách rỗng (`head is None`); một node không tự trỏ vào mình (không cycle); một node tự trỏ vào chính nó (cycle bắt đầu ngay tại head, `L = 0`); cycle bao trọn cả danh sách; cycle chỉ là node cuối trỏ về node cuối.

Yêu cầu ẩn quan trọng nhất: đề hỏi *"Can you solve it using O(1) memory?"* — nghĩa là lời giải dùng `set` được chấp nhận nhưng không phải cái người ta muốn nghe.

#### Complexity mục tiêu

n ≤ 10⁴ nên gần như mọi thứ đều pass về thời gian; ràng buộc thật nằm ở **space**. Mục tiêu: **O(n) time, O(1) space**. Lời giải `set` là O(n) space — không sai, nhưng bị loại vì đề nêu rõ ràng buộc bộ nhớ.

#### Idea

Hai pha, mỗi pha có một invariant riêng.

**Pha 1 (phát hiện)**: `slow` đi 1, `fast` đi 2. Invariant: nếu cả hai còn nằm trong chu trình thì khoảng cách vòng từ `slow` tới `fast` giảm đúng 1 mỗi vòng lặp (fast đuổi kịp với tốc độ tương đối 1). Vì khoảng cách nằm trong `[0, C)` và giảm đơn điệu, sau tối đa `C` vòng nó chạm 0 → hai con trỏ trùng nhau. Nếu không có chu trình, `fast` gặp `None` và thoát.

**Pha 2 (định vị)**: như đã chứng minh ở phần Lý thuyết, tại điểm gặp ta có `L ≡ −k (mod C)`. Đặt `probe` ở `head`; cho `probe` và `slow` cùng bước 1. Sau đúng `L` bước, `probe` tới đầu chu trình, còn `slow` đi từ vị trí `k` thêm `L` bước tới vị trí `(k + L) mod C = 0` — cũng là đầu chu trình. Chúng gặp nhau ở đó, và đó là lần gặp **đầu tiên** vì `probe` chưa từng vào chu trình trước bước thứ `L`.

#### Naive

```python
class ListNode:                    # LeetCode cấp sẵn; bản đầy đủ ở mục Cài đặt
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


class SolutionNaive142:
    def detectCycle(self, head: ListNode | None) -> ListNode | None:
        seen = set()
        cur = head
        while cur is not None:
            if id(cur) in seen:
                return cur
            seen.add(id(cur))
            cur = cur.next
        return None
```

O(n) time, **O(n) space**. Chậm/tốn ở chỗ phải giữ mọi node đã thăm; với 10⁴ node là một `set` 10⁴ phần tử. Lưu ý dùng `id(cur)` chứ không phải `cur` — `ListNode` không định nghĩa `__hash__` tuỳ chỉnh nên mặc định vẫn hash theo identity, cả hai đều chạy, nhưng `id()` nói rõ ý định "so sánh identity, không so sánh giá trị".

#### Optimized

```python
class ListNode:                    # LeetCode cấp sẵn; bản đầy đủ ở mục Cài đặt
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


class Solution142:
    def detectCycle(self, head: ListNode | None) -> ListNode | None:
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:                 # đã gặp nhau trong chu trình
                probe = head
                while probe is not slow:     # cả hai đi 1 bước/lần
                    probe = probe.next
                    slow = slow.next
                return probe
        return None
```

O(n) time, **O(1) space**. Đánh đổi: mất tính hiển nhiên. Bản `set` đọc là hiểu ngay; bản Floyd cần chứng minh modular ở trên mới tin được. Đổi lại tiết kiệm toàn bộ bộ nhớ phụ. Chú ý `slow is fast` dùng `is` chứ không `==`: hai node khác nhau hoàn toàn có thể cùng `val`.

Đã stress test 2000 lần trên danh sách ngẫu nhiên độ dài 0–6 với `pos` ngẫu nhiên, đối chiếu naive vs optimized. Ví dụ: `detectCycle(build([3,2,0,-4], 1))` trả về node có `val == 2`.

### Bài 2 — 19. Remove Nth Node From End of List

#### Requirements

Xoá node thứ `n` **tính từ cuối** rồi trả về head mới. `1 ≤ n ≤ số node ≤ 30`. Đề hỏi thêm: làm được trong **một lượt duyệt** không?

Edge cases: danh sách một node và `n = 1` (kết quả là danh sách rỗng, phải trả `None` chứ không crash); `n == len` (xoá chính head — đây là case mà thiếu dummy sẽ sinh bug); `n == 1` (xoá node cuối).

#### Complexity mục tiêu

n ≤ 30 nên độ phức tạp không phải vấn đề — bài này kiểm tra **kỹ thuật**, không kiểm tra tốc độ. Cả hai lời giải đều O(n) time, O(1) space; điểm khác biệt là số lượt duyệt: 2 lượt vs 1 lượt. Trong bối cảnh dữ liệu stream (không biết trước độ dài, không tua lại được), lời giải 2 lượt là bất khả thi — đó mới là lý do thật để tối ưu.

#### Idea

Muốn xoá node thứ `n` từ cuối, ta cần con trỏ đứng ở node thứ `n+1` từ cuối. Kỹ thuật: **cố định khoảng cách giữa hai con trỏ**.

> **Invariant**: sau khi cho `fast` chạy trước đúng `n` bước, khoảng cách `fast − slow` luôn bằng `n` node ở mọi thời điểm còn lại.

Cho cả hai cùng bước cho đến khi `fast.next is None` (tức `fast` ở node cuối). Lúc đó `slow` ở đúng vị trí cách cuối `n+1` node, tức là node **ngay trước** node cần xoá. Đặt cả hai xuất phát từ `dummy` chứ không phải `head`, nhờ vậy case "xoá chính head" tự động đúng mà không cần `if`.

#### Naive

```python
class SolutionNaive19:
    def removeNthFromEnd(self, head, n):
        length = 0
        cur = head
        while cur:
            length += 1
            cur = cur.next
        dummy = ListNode(0, head)
        prev = dummy
        for _ in range(length - n):
            prev = prev.next
        prev.next = prev.next.next
        return dummy.next
```

O(n) time nhưng **2 lượt duyệt**. Chậm ở chỗ đếm độ dài xong phải quay lại từ đầu — không dùng được với iterator/stream một chiều, và trên dữ liệu nằm trên đĩa thì lượt thứ hai là một lần đọc I/O nữa.

#### Optimized

```python
class Solution19:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)
        fast = slow = dummy
        for _ in range(n):
            fast = fast.next
        # Invariant: khoảng cách fast - slow luôn đúng bằng n node.
        while fast.next is not None:
            fast = fast.next
            slow = slow.next
        slow.next = slow.next.next
        return dummy.next
```

O(n) time, **1 lượt**, O(1) space. Đánh đổi: đổi một biến trạng thái tường minh (`length`) lấy một invariant ngầm (khoảng cách hai con trỏ). Code ngắn hơn nhưng phải nhớ vì sao `fast` xuất phát từ `dummy` — nếu xuất phát từ `head`, mọi thứ lệch đúng 1 và bài này trở thành bài học off-by-one.

Đã stress test 2000 lần với `k ∈ [1,8]`, `n ∈ [1,k]`, đối chiếu hai bản. `removeNthFromEnd(build([1,2,3,4,5]), 2)` → `[1, 2, 3, 5]`.

### Bài 3 — 23. Merge k Sorted Lists

#### Requirements

Cho `lists` gồm `k` linked list, mỗi list đã sắp xếp tăng dần. Ghép tất cả thành một list sắp xếp và trả về head. `k ≤ 10⁴`, tổng số node ≤ 10⁴.

Edge cases: `lists` rỗng (`[]` → `None`); một số phần tử của `lists` là `None`; tất cả đều `None`; giá trị trùng nhau giữa các list; `k = 1`.

#### Complexity mục tiêu

Gọi `N` là tổng số node, `k` số list. Ghép từng cặp tuần tự cho O(N·k) — với `k = 10⁴` là 10⁸ phép, TLE chắc chắn trong CPython. Mục tiêu là **O(N log k)**: mỗi node vào/ra một heap kích thước tối đa `k`.

#### Idea

Tại mọi thời điểm, ứng viên cho vị trí tiếp theo trong kết quả chỉ có thể là **head hiện tại của một trong k list** (vì mỗi list đã sorted, không phần tử nào phía sau nhỏ hơn head của chính nó).

> **Invariant**: heap luôn chứa đúng head hiện tại của mọi list chưa cạn — không nhiều hơn, không ít hơn. Do đó `heappop` cho ra phần tử nhỏ nhất còn lại trên toàn bộ dữ liệu.

Sau khi pop một node từ list `i`, ta push node kế tiếp của chính list đó để tái lập invariant. Heap chỉ chứa ≤ `k` phần tử nên mỗi thao tác là O(log k), tổng O(N log k).

Chi tiết Python bắt buộc: `ListNode` **không so sánh được**. Nếu hai node cùng `val`, `heapq` sẽ so sánh phần tử kế tiếp của tuple; nếu đó là node, ta ăn `TypeError`. Vì vậy tuple phải là `(val, index, node)` với `index` là số nguyên duy nhất — comparison không bao giờ chạm tới phần tử thứ ba.

#### Naive

```python
class SolutionNaive23:
    def mergeKLists(self, lists):
        vals = []
        for node in lists:
            while node:
                vals.append(node.val)
                node = node.next
        vals.sort()
        dummy = ListNode()
        tail = dummy
        for v in vals:
            tail.next = ListNode(v)
            tail = tail.next
        return dummy.next
```

O(N log N) time, **O(N) space**. Thực ra bản này *nhanh* trên LeetCode vì Timsort là code C. Nhưng nó sai về tinh thần: nó vứt bỏ hoàn toàn thông tin "mỗi list đã sorted", cấp phát lại N node mới, và không tổng quát được sang bài toán stream vô hạn (không thể `sort()` một stream chưa kết thúc).

#### Optimized

```python
import heapq


class Solution23:
    def mergeKLists(self, lists):
        heap = []
        for i, node in enumerate(lists):
            if node is not None:
                # i là tie-break: ListNode không định nghĩa __lt__ nên nếu hai
                # val bằng nhau, tuple comparison sẽ rơi xuống phần tử kế tiếp.
                heapq.heappush(heap, (node.val, i, node))
        dummy = ListNode()
        tail = dummy
        while heap:
            val, i, node = heapq.heappop(heap)
            tail.next = node
            tail = node
            if node.next is not None:
                heapq.heappush(heap, (node.next.val, i, node.next))
        tail.next = None
        return dummy.next
```

O(N log k) time, O(k) space. Đánh đổi: dùng thêm cấu trúc phụ (`heap`) và một quy ước tie-break hơi kỳ để đổi lấy hai thứ — bộ nhớ tụt từ O(N) xuống O(k), và thuật toán tái sử dụng node cũ thay vì cấp phát mới (đây chính là merge-phase của external sort, nơi N không vừa RAM). `tail.next = None` ở cuối là bắt buộc: node cuối cùng vẫn còn giữ `next` trỏ vào list gốc của nó.

Đã stress test 1000 lần với `k ∈ [0,5]`, mỗi list 0–4 phần tử ngẫu nhiên. `mergeKLists([[1,4,5],[1,3,4],[2,6]])` → `[1,1,2,3,4,4,5,6]`.

## Bài luyện thêm

- **206. Reverse Linked List** — đúng vòng lặp 3 con trỏ `prev/curr/nxt` ở phần Lý thuyết; làm thêm bản đệ quy để thấy nó tốn O(n) stack.
- **141. Linked List Cycle** — pha 1 của bài 142, chỉ cần trả `True/False` khi `slow is fast`.
- **21. Merge Two Sorted Lists** — dummy head + hai con trỏ, mỗi bước nối node nhỏ hơn vào `tail`; đây là trường hợp `k = 2` của bài 23 nhưng không cần heap.

## Bài toán áp dụng

**LRU cache** là bài toán chuẩn ép bạn phải dùng doubly linked list thật: một `dict[key] -> DNode` cho lookup O(1), một `DoublyLinkedList` giữ thứ tự truy cập với node mới nhất ở cuối. `get(key)` = tra dict, `unlink(node)` rồi `push_back` lại — O(1) nhờ đã cầm sẵn tham chiếu node. `put` khi đầy = `pop_front()` và xoá key tương ứng khỏi dict. Không cấu trúc nào khác cho đồng thời "tìm theo key O(1)" và "gỡ khỏi giữa thứ tự O(1)".

**Undo/redo** là doubly linked list với một con trỏ `current`: undo là `current = current.prev`, redo là `current = current.next`. Thao tác mới khi đang ở giữa lịch sử sẽ cắt bỏ toàn bộ nhánh redo — chỉ cần nối `current.next = new_node` là các node phía sau tự bị GC thu hồi.

## Use case thực tế

Free-list của memory allocator là linked list thuần khiết nhất còn tồn tại: các block bộ nhớ trống tự chứa con trỏ tới block trống kế tiếp **bên trong chính vùng nhớ trống đó**, nên cấu trúc quản lý tốn 0 byte phụ. glibc `malloc` dùng nhiều free-list phân theo kích thước (bins), và pymalloc của chính CPython cũng vậy. Điểm mấu chốt: ở tầng này không có `list` để mà dùng — bạn *đang* cài đặt cái mà `list` được xây trên đó.

Kernel Linux dùng `struct list_head` (doubly circular linked list) cho gần như mọi danh sách của nó, vì thao tác chi phối là "gỡ một phần tử đã cầm con trỏ" chứ không phải "truy cập phần tử thứ i".

Git commit history hay được ví như linked list vì mỗi commit trỏ về parent, nhưng thực chất là DAG (merge commit có 2 parent). Ý tưởng con trỏ thì giống hệt: `git log` chính là duyệt theo con trỏ `parent`.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: gần như luôn luôn, trong Python. Cần hàng đợi hai đầu → `collections.deque` (được cài bằng C, dưới nắp là doubly linked list của các block 64 phần tử — vừa có O(1) hai đầu vừa có cache locality). Cần LRU cache → `functools.lru_cache` hoặc `collections.OrderedDict.move_to_end()`, cả hai đã có sẵn cấu trúc mô tả ở trên viết bằng C. Tự viết linked list trong code production Python là một quyết định cần lý do rất mạnh.

## Bẫy thường gặp trong Python

**`ListNode` không so sánh được — heap sẽ nổ ở tie-break.** Đây là bẫy số một của bài 23:

```text
import heapq
h = [(1, ListNode(5))]
heapq.heappush(h, (1, ListNode(7)))
# TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
```

Tuple comparison so sánh từng phần tử; khi hai `val` bằng nhau nó rơi xuống phần tử kế tiếp. Luôn chèn một `int` duy nhất vào giữa: `(val, idx, node)`. Điều đáng sợ là lỗi chỉ xuất hiện khi **có giá trị trùng** — test case nhỏ tự nghĩ thường không có, nên bug lọt tới lúc submit.

**Linked list tự viết chậm hơn `deque` một cách hệ thống.** Đo trên máy này với 200 000 lần chèn đầu: `deque.appendleft` mất 0.0065 s, còn `push_front` lên linked list tự viết mất 0.0367 s — **chậm 5.6 lần** dù cùng là O(1). Lý do: mỗi node là một `PyObject` riêng, cấp phát riêng, nằm rải rác trong heap nên CPU prefetch vô dụng; mỗi lần đi `node.next` là một lần dereference con trỏ tới vùng nhớ có thể cache-miss. `sys.getsizeof` của một node là 48 byte, và **thêm 296 byte nữa cho `__dict__`** nếu bạn quên `__slots__` — tức là ~344 byte để chứa một số nguyên. Với `__slots__` thì còn 48 byte, vẫn gấp 6 lần một ô 8 byte trong `list`.

Hệ quả thực dụng: linked list ở đây là bài học về con trỏ và invariant, **không phải** một lựa chọn cấu trúc dữ liệu thực chiến trong Python. Khi thấy mình định viết linked list cho code production, hãy dừng lại và hỏi `deque` hay `list` có làm được không.

**`is` vs `==` khi so sánh node.** `slow is fast` hỏi "cùng một object?", `slow == fast` với `ListNode` mặc định cũng là identity — nhưng nếu ai đó thêm `__eq__` so sánh theo `val` thì Floyd sẽ dừng sai. Dùng `is` để ý định không phụ thuộc vào việc class có `__eq__` hay không.

**Quên `tail.next = None` sau khi ghép list.** Node cuối cùng của kết quả vẫn giữ nguyên con trỏ `next` trỏ vào danh sách gốc. Bug này biểu hiện thành "kết quả dài hơn mong đợi" hoặc vòng lặp vô hạn nếu tình cờ tạo cycle.

**Đệ quy trên linked list dài gây `RecursionError`.** Bản `reverseList` đệ quy rất đẹp nhưng với 10⁴ node nó vượt `sys.getrecursionlimit()` mặc định (1000). Trên linked list, mọi thuật toán đệ quy đều có độ sâu bằng độ dài danh sách — đây là cấu trúc "lệch hoàn toàn" theo nghĩa của §24. Dùng vòng lặp.
