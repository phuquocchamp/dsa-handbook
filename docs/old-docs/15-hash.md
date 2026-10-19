# 15. Hash — dict, set, Counter

`dict` và `set` là hai cấu trúc bạn dùng nhiều nhất mà lại hiểu ít nhất. Section này mổ đủ sâu phần internals để giải thích ba điều gây bất ngờ trong thực tế: vì sao `dict` giữ thứ tự chèn từ Python 3.7, vì sao `{1: 'a', True: 'b'}` chỉ có một phần tử, và vì sao O(1) trung bình có thể tụt xuống O(n) — kể cả do kẻ tấn công cố ý.

## Lý thuyết

### Hash table hoạt động thế nào trong CPython

Một hash table là mảng các slot cộng với một hàm ánh xạ key → chỉ số slot. CPython dùng:

- **Open addressing**, không phải chaining. Khi hai key đụng cùng slot, key thứ hai không được nối vào một linked list mà đi tìm slot khác theo một dãy probe.
- **Dãy probe có perturb**: chỉ số kế tiếp không phải `i+1` (linear probing thuần) mà là `i = (5*i + 1 + perturb) & mask` với `perturb` được dịch phải 5 bit mỗi vòng. Nghĩa là dãy probe phụ thuộc vào **toàn bộ** bit của hash, không chỉ các bit thấp. Đây là lý do các key kiểu `i * 2^18` (đụng nhau ở bit thấp) vẫn không gây thảm hoạ trong CPython — đo được chỉ chậm ~3 lần.
- **Kích thước bảng luôn là luỹ thừa của 2**, nên `hash(key) & (size - 1)` thay cho phép chia dư.
- **Load factor 2/3**: khi số slot đã dùng vượt 2/3 dung lượng, bảng được resize (thường ×4 với dict nhỏ, ×2 với dict lớn) và toàn bộ key được chèn lại. Đây là nguồn gốc của "O(1) **amortized**": một lần `d[k] = v` cụ thể có thể tốn O(n) vì rehash, nhưng trung bình trên n phép chèn vẫn là O(1).

### Compact dict — vì sao thứ tự chèn được giữ

Từ Python 3.6 (chi tiết cài đặt) và 3.7 (được đảm bảo bởi ngôn ngữ), `dict` tách làm hai mảng:

1. **`entries`**: mảng liền kề các bản ghi `(hash, key, value)`, **ghi theo đúng thứ tự chèn**, không có lỗ trống ở giữa (trừ khi xoá).
2. **`indices`**: mảng thưa chứa **chỉ số** vào `entries`, đây mới là mảng được đánh địa chỉ bằng hash.

Hai hệ quả trực tiếp:

- **Thứ tự chèn được giữ miễn phí** — chỉ cần duyệt `entries` tuần tự. Đây là hệ quả phụ của một tối ưu bộ nhớ, không phải tính năng được thiết kế riêng.
- **Tiết kiệm bộ nhớ 20–25%**: mảng thưa `indices` chỉ chứa số nguyên nhỏ (1, 2, 4 hoặc 8 byte tuỳ kích thước dict) thay vì ba con trỏ 8 byte mỗi slot.

`set` **không** có tối ưu này (`setobject.c` giữ cấu trúc cũ, mảng slot trực tiếp), nên `set` **không đảm bảo thứ tự**. Đây là khác biệt thật giữa hai cấu trúc mà nhiều người tưởng là giống hệt nhau.

```python
od = {}
for ch in "zebra":
    od[ch] = ord(ch)
list(od)   # ['z', 'e', 'b', 'r', 'a']  -- đúng thứ tự chèn
```

### Hashable là gì

`hash(x)` chỉ định nghĩa cho object **immutable**, và hợp đồng là: `a == b` ⟹ `hash(a) == hash(b)`. Nếu key thay đổi sau khi đã nằm trong dict, nó sẽ nằm sai slot và trở nên không tìm thấy được — đó là lý do `list` bị cấm làm key.

| Kiểu | Hashable? | Ghi chú |
|---|---|---|
| `int`, `float`, `str`, `bytes`, `bool`, `None` | ✅ | `hash(n) == n` với int nhỏ |
| `tuple` | ✅ **nếu** mọi phần tử hashable | `(1, [2])` thì không |
| `frozenset` | ✅ | hash không phụ thuộc thứ tự |
| `list`, `dict`, `set` | ❌ | `TypeError: unhashable type` |
| object tự định nghĩa | ✅ mặc định (theo `id`) | mất nếu định nghĩa `__eq__` mà quên `__hash__` |

### Bảng độ phức tạp

| Thao tác | Trung bình | Tệ nhất | Ghi chú |
|---|---|---|---|
| `d[k]`, `k in d`, `d[k] = v` | O(1) | **O(n)** | O(n) khi mọi key đụng độ |
| `del d[k]` | O(1) | O(n) | để lại tombstone (dummy) |
| duyệt `for k in d` | O(n) | O(n) | O(len(entries)) — có thể > len(d) nếu đã xoá nhiều |
| `x in list` | **O(n)** | O(n) | lỗi hiệu năng phổ biến nhất của người mới |
| `Counter(iterable)` | O(n) | — | |
| `c.most_common(k)` | O(n log k) | — | dùng `heapq.nlargest` bên trong |

Đo trên máy này: 100 lần kiểm tra `in` trên `list` 50 000 phần tử mất 0.0086 s; cùng số lần trên `set` mất 0.000015 s — **nhanh hơn ~570 lần**. Trong vòng lặp n bước, `x in list` biến O(n) thành O(n²) trá hình.

### `Counter` và `defaultdict`

`Counter` là `dict` con với ba khác biệt đáng nhớ:

```python
from collections import Counter

c = Counter("mississippi")
c.most_common(2)            # [('i', 4), ('s', 4)]
c["z"]                      # 0  -- KHÔNG KeyError, và KHÔNG chèn key vào dict
Counter("aabbc") - Counter("abd")   # Counter({'a': 1, 'b': 1, 'c': 1})
Counter("aabbc") & Counter("abd")   # Counter({'a': 1, 'b': 1})  -- giao, lấy min
```

Phép trừ `Counter` **bỏ các giá trị ≤ 0** (`'d'` biến mất chứ không thành -1). Phép `&` lấy min từng key — cực hữu ích cho bài "window đã chứa đủ ký tự cần chưa" (bài 76). Phép `|` lấy max.

`defaultdict(factory)` gọi `factory()` khi key vắng mặt — nhưng **chèn key luôn**, kể cả khi bạn chỉ đọc. Chi tiết này là bẫy, xem phần cuối.

## Cài đặt trong `cores/python/`

Không bắt buộc phải tự cài hash table để làm bài, nhưng cài một bản tối giản là cách nhanh nhất để hiểu vì sao xoá phần tử lại phức tạp hơn tưởng tượng.

Đề xuất đường dẫn: `cores/python/hash/open_addressing.py`

```python
class OpenAddressingDict:
    """Hash table dạy học: open addressing + linear probing.

    Invariant: nếu key K tồn tại, nó nằm ở đâu đó trong dãy probe bắt đầu từ
    hash(K) & mask, và KHÔNG có ô EMPTY nào nằm giữa vị trí xuất phát và K.
    Đó là lý do xoá phải đặt TOMBSTONE chứ không đặt lại EMPTY — đặt EMPTY sẽ
    cắt đứt dãy probe và làm mất các key phía sau.
    """

    EMPTY = object()
    TOMBSTONE = object()

    def __init__(self, capacity: int = 8) -> None:
        self._keys: list = [self.EMPTY] * capacity
        self._vals: list = [None] * capacity
        self._mask = capacity - 1          # capacity luôn là luỹ thừa của 2
        self._used = 0                     # số key thật
        self._filled = 0                   # số ô không EMPTY (kể cả tombstone)

    def _probe(self, key):
        """Trả về (index_để_ghi, index_của_key_nếu_có)."""
        i = hash(key) & self._mask
        first_tomb = -1
        while True:
            k = self._keys[i]
            if k is self.EMPTY:
                return (first_tomb if first_tomb >= 0 else i), -1
            if k is self.TOMBSTONE:
                if first_tomb < 0:
                    first_tomb = i
            elif k == key:
                return i, i
            i = (i + 1) & self._mask       # linear probing

    def _resize(self, capacity: int) -> None:
        old = [(k, v) for k, v in zip(self._keys, self._vals)
               if k is not self.EMPTY and k is not self.TOMBSTONE]
        self._keys = [self.EMPTY] * capacity
        self._vals = [None] * capacity
        self._mask = capacity - 1
        self._used = self._filled = 0
        for k, v in old:
            self[k] = v

    def __setitem__(self, key, value) -> None:
        slot, found = self._probe(key)
        if found >= 0:
            self._vals[found] = value
            return
        if self._keys[slot] is self.EMPTY:
            self._filled += 1
        self._keys[slot] = key
        self._vals[slot] = value
        self._used += 1
        # load factor 2/3 giống CPython
        if self._filled * 3 >= len(self._keys) * 2:
            self._resize(len(self._keys) * 4 if self._used * 4 > len(self._keys) else len(self._keys))

    def __getitem__(self, key):
        _, found = self._probe(key)
        if found < 0:
            raise KeyError(key)
        return self._vals[found]

    def __delitem__(self, key) -> None:
        _, found = self._probe(key)
        if found < 0:
            raise KeyError(key)
        self._keys[found] = self.TOMBSTONE   # KHÔNG đặt EMPTY
        self._vals[found] = None
        self._used -= 1

    def __contains__(self, key) -> bool:
        return self._probe(key)[1] >= 0

    def __len__(self) -> int:
        return self._used

    def get(self, key, default=None):
        _, found = self._probe(key)
        return default if found < 0 else self._vals[found]
```

Ba điểm đáng rút ra:

1. **Tombstone là bắt buộc.** Giả sử `A` và `B` cùng hash về slot 3, `A` ở slot 3, `B` ở slot 4. Nếu xoá `A` và đặt slot 3 = EMPTY, thì lần sau tra `B` sẽ dừng ngay ở slot 3 (thấy EMPTY nghĩa là "không có") và báo không tìm thấy — dù `B` vẫn nằm ở slot 4. Tombstone nói "ở đây từng có gì đó, đi tiếp".
2. **Phải đếm hai con số.** `_used` là số key thật (dùng cho `len`), `_filled` là số ô không EMPTY kể cả tombstone (dùng để quyết định resize). Nếu chỉ đếm `_used`, một dict bị xoá nhiều lần sẽ đầy tombstone và dãy probe dài ra vô hạn mà không bao giờ resize.
3. **Resize cũng là cách dọn tombstone.** Trong `_resize`, các tombstone đơn giản không được chép sang bảng mới. Vì vậy khi `_used` không tăng nhưng `_filled` chạm ngưỡng, ta resize về **cùng kích thước** — chỉ để dọn rác.

Đã stress test 20 000 thao tác ngẫu nhiên (`set`/`get`/`del`/`in`/`len`) với key trộn lẫn `int`, `str`, `tuple`, đối chiếu từng bước với `dict` của Python.

## Bài tập chi tiết

### Bài 1 — 128. Longest Consecutive Sequence

#### Requirements

Cho mảng `nums` **chưa sắp xếp**, tìm độ dài dãy số nguyên liên tiếp dài nhất (các số phải xuất hiện trong mảng, nhưng không cần liền nhau về vị trí). `0 ≤ n ≤ 10⁵`, `-10⁹ ≤ nums[i] ≤ 10⁹`. Đề yêu cầu tường minh **O(n)**.

Edge cases: mảng rỗng (trả 0); phần tử trùng lặp (`[1,2,0,1]` → 3, không phải 4); số âm; giá trị cực lớn (không thể dùng mảng đánh dấu theo giá trị); một phần tử duy nhất.

#### Complexity mục tiêu

Đề đã nói O(n), nên `sorted()` rồi quét (O(n log n)) bị loại **về mặt yêu cầu** dù nó pass. Miền giá trị `[-10⁹, 10⁹]` loại luôn phương án bucket/mảng đánh dấu — chỉ còn hash.

#### Idea

Ý tưởng đơn giản đến mức đáng ngờ: đưa hết vào `set`, rồi với mỗi `x`, đếm `x, x+1, x+2, ...` xem đi được bao xa.

Nhưng làm vậy trên `[1,2,3,...,n]` thì mỗi `x` đi hết đuôi → O(n²). Chìa khoá là **chỉ khởi động từ đầu dãy**:

> **Invariant**: ta chỉ mở rộng từ những `x` thoả `x - 1 not in s`, tức `x` là phần tử nhỏ nhất của dãy liên tiếp chứa nó.

Vì mỗi dãy liên tiếp có **đúng một** phần tử đầu, mỗi dãy được duyệt đúng một lần. Tổng số bước mở rộng trên toàn bộ chương trình = tổng độ dài các dãy = |s| ≤ n. Cộng với n lần kiểm tra `x - 1 in s` → **O(n) tổng**, dù nhìn code có vòng `while` lồng trong `for`.

Đây là mẫu lập luận amortized giống hệt monotonic stack ở §13: vòng lặp trong nhìn như O(n) nhưng tổng công việc bị chặn bởi kích thước dữ liệu.

#### Naive

```python
class SolutionNaive128:
    def longestConsecutive(self, nums: list[int]) -> int:
        best = 0
        for x in nums:
            length = 1
            y = x + 1
            while y in nums:        # `in` trên list là O(n)
                length += 1
                y += 1
            best = max(best, length)
        return best
```

**O(n³)** trong trường hợp tệ nhất: `for` là O(n), `while` chạy tới O(n) lần, mỗi lần `y in nums` là O(n) vì `nums` là list. Đây là ví dụ hoàn hảo của "O(n²) trá hình" mà §03 cảnh báo — thủ phạm là `in` trên `list`, một dòng nhìn vô hại.

#### Optimized

```python
class Solution128:
    def longestConsecutive(self, nums: list[int]) -> int:
        s = set(nums)
        best = 0
        for x in s:
            if x - 1 in s:          # x không phải đầu dãy -> bỏ qua
                continue
            length = 1
            while x + length in s:
                length += 1
            best = max(best, length)
        return best
```

O(n) time, O(n) space. Đánh đổi: dùng O(n) bộ nhớ phụ cho `set` để mua hai thứ — `in` từ O(n) xuống O(1), và loại trùng lặp miễn phí (`[1,2,0,1]` tự đúng mà không cần một dòng xử lý riêng).

Chú ý duyệt `for x in s` chứ không `for x in nums`: với mảng toàn phần tử giống nhau, duyệt `nums` sẽ lặp lại n lần công việc y hệt.

Đã stress test 3000 lần với mảng độ dài 0–8, giá trị `[-5,5]` (hẹp để ép trùng lặp và dãy dài). `longestConsecutive([100,4,200,1,3,2])` → `4`.

### Bài 2 — 560. Subarray Sum Equals K

#### Requirements

Đếm **số lượng** subarray liên tiếp có tổng đúng bằng `k`. `1 ≤ n ≤ 2·10⁴`, `-1000 ≤ nums[i] ≤ 1000`, `-10⁷ ≤ k ≤ 10⁷`.

Edge cases: **có số âm và số 0** — đây là điểm mấu chốt, nó loại bỏ hoàn toàn lời giải sliding window (window không đơn điệu khi có số âm); `k = 0`; subarray rỗng không tính; nhiều subarray khác nhau cùng tổng.

#### Complexity mục tiêu

n = 2·10⁴ → O(n²) là 4·10⁸ phép Python thuần, khoảng vài chục giây — **TLE**. Bảng §02 xếp n ≤ 5000 mới cho phép O(n²). Cần **O(n)**.

#### Idea

Đặt `prefix[i] = nums[0] + ... + nums[i-1]` (prefix[0] = 0). Tổng subarray `[i, j)` là `prefix[j] - prefix[i]`. Vậy:

> đếm subarray tổng `k` ⟺ đếm số cặp `(i, j)` với `i < j` và `prefix[i] = prefix[j] - k`.

Duyệt `j` từ trái sang phải, tại mỗi bước ta cần biết **đã gặp bao nhiêu lần** giá trị `prefix[j] - k` trong các prefix trước đó. Đó chính xác là việc của một `dict` đếm tần suất.

> **Invariant**: trước khi xử lý vị trí `j`, `seen[p]` bằng số chỉ số `i < j` có `prefix[i] == p`.

Thứ tự hai dòng cuối là **bắt buộc**: cộng đáp án **trước**, cập nhật `seen` **sau**. Nếu cập nhật trước, khi `k == 0` ta sẽ đếm cả cặp `i == j` (subarray rỗng).

Khởi tạo `seen[0] = 1` biểu diễn prefix rỗng — đây là cái làm cho các subarray bắt đầu từ index 0 được đếm.

#### Naive

```python
class SolutionNaive560:
    def subarraySum(self, nums: list[int], k: int) -> int:
        count = 0
        for i in range(len(nums)):
            total = 0
            for j in range(i, len(nums)):
                total += nums[j]
                if total == k:
                    count += 1
        return count
```

O(n²) — đã tối ưu hơn bản O(n³) (cộng dồn `total` thay vì `sum(nums[i:j+1])`). Chậm vì liệt kê toàn bộ n²/2 subarray, trong khi thông tin thật sự cần chỉ là tần suất của n+1 giá trị prefix.

#### Optimized

```python
from collections import defaultdict


class Solution560:
    def subarraySum(self, nums: list[int], k: int) -> int:
        seen = defaultdict(int)
        seen[0] = 1                 # tiền tố rỗng: tổng 0 đã xuất hiện 1 lần
        prefix = 0
        count = 0
        for x in nums:
            prefix += x
            count += seen[prefix - k]
            seen[prefix] += 1
        return count
```

O(n) time, O(n) space. Đánh đổi: bộ nhớ O(n) cho dict (worst case mọi prefix phân biệt), và mất khả năng **liệt kê** các subarray — ta chỉ đếm được, không biết chúng nằm ở đâu mà không lưu thêm. Nếu đề yêu cầu trả về chính các subarray, số lượng đầu ra có thể là O(n²) nên O(n) là bất khả thi.

Lưu ý: `seen[prefix - k]` trên `defaultdict` sẽ **chèn key** `prefix - k` với giá trị 0 nếu chưa có. Ở đây vô hại (chỉ tốn bộ nhớ, tối đa gấp đôi), nhưng nếu muốn sạch thì dùng `Counter` và `seen[prefix - k]` — `Counter.__getitem__` trả 0 mà **không** chèn.

Đã stress test 3000 lần với mảng độ dài 0–9, giá trị `[-3,3]` (có âm và 0), `k ∈ [-4,4]`. `subarraySum([1,1,1], 2)` → 2; `subarraySum([1,2,3], 3)` → 2.

### Bài 3 — 49. Group Anagrams

#### Requirements

Gom các chuỗi là anagram của nhau vào cùng nhóm. Trả về list các nhóm, **thứ tự tuỳ ý**. `1 ≤ len(strs) ≤ 10⁴`, `0 ≤ len(strs[i]) ≤ 100`, chỉ chữ thường ASCII.

Edge cases: chuỗi rỗng `""` (hợp lệ, tự thành một nhóm với các chuỗi rỗng khác); chuỗi trùng lặp hoàn toàn; mọi chuỗi đều là anagram của nhau; không chuỗi nào là anagram của chuỗi nào.

#### Complexity mục tiêu

Gọi `n = len(strs)`, `L = max độ dài chuỗi` (≤ 100). Naive so từng cặp là O(n²·L log L) = 10⁸·... — TLE. Mục tiêu: **O(n·L)** bằng cách tạo một "chữ ký" cho mỗi chuỗi rồi gom bằng dict. Bản dùng `sorted(s)` làm chữ ký cho O(n·L log L), cũng pass, nhưng bản đếm ký tự cho O(n·L) và đáng viết vì `L log L` với alphabet cố định thực chất là công việc thừa.

#### Idea

Hai chuỗi là anagram ⟺ chúng có **cùng vector đếm ký tự**. Vậy vector đếm là một **hàm chuẩn hoá** (canonical form): mọi anagram cho ra cùng một giá trị, và hai chuỗi cho cùng giá trị thì chắc chắn là anagram.

> **Invariant**: `groups[key]` chứa đúng tập các chuỗi đã duyệt có chữ ký `key`.

Vì chữ ký là hàm của nội dung chuỗi (không phụ thuộc thứ tự duyệt), invariant này giữ tự động, và đáp án là `list(groups.values())`.

Điểm Python quan trọng: vector đếm là một **list**, mà `list` không hashable. Phải chuyển sang `tuple` để làm key.

#### Naive

```python
class SolutionNaive49:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups: list[list[str]] = []
        for s in strs:
            for g in groups:
                if sorted(g[0]) == sorted(s):
                    g.append(s)
                    break
            else:
                groups.append([s])
        return groups
```

O(n²·L log L): với mỗi chuỗi, quét mọi nhóm đã có và sort lại đại diện của nhóm mỗi lần. Chậm gấp đôi vì hai lý do độc lập — tìm tuyến tính thay vì tra hash, và tính lại chữ ký thay vì nhớ. (Chú ý `for...else`: khối `else` chạy khi vòng lặp kết thúc mà không `break` — đây là cú pháp Python ít dùng nhưng đúng ngữ nghĩa "không tìm thấy nhóm nào".)

#### Optimized

```python
from collections import defaultdict


class Solution49:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups: defaultdict[tuple, list[str]] = defaultdict(list)
        for s in strs:
            counts = [0] * 26
            for ch in s:
                counts[ord(ch) - 97] += 1
            groups[tuple(counts)].append(s)   # tuple hashable, list thì không
        return list(groups.values())
```

O(n·L) time, O(n·L) space. Đánh đổi: chữ ký là tuple 26 phần tử — **tốn bộ nhớ và tốn thời gian hash hơn** một chuỗi ngắn. Với `L` rất nhỏ (chuỗi 2–3 ký tự), `tuple(sorted(s))` gọn hơn và thực tế nhanh hơn vì `sorted` là C. Với alphabet lớn (Unicode), vector 26 phần tử không dùng được, phải quay về `sorted` hoặc `frozenset(Counter(s).items())`.

Đáng nhớ: `tuple(counts)` chứ không phải `counts`. `groups[counts]` ném `TypeError: unhashable type: 'list'` — thông báo lỗi rõ ràng, nhưng nếu bạn không biết vì sao thì sẽ mất thời gian.

Đã stress test 2000 lần với 0–7 chuỗi ngẫu nhiên trên alphabet `{a,b,c}` độ dài 0–4 (ép nhiều anagram và chuỗi rỗng), so sánh sau khi chuẩn hoá thứ tự nhóm. `groupAnagrams(["eat","tea","tan","ate","nat","bat"])` → `[['eat','tea','ate'], ['tan','nat'], ['bat']]`.

## Bài luyện thêm

- **1. Two Sum** — một lượt duy nhất: với mỗi `x`, kiểm tra `target - x` đã gặp chưa trong `dict[value] -> index`; kiểm tra **trước** khi chèn để không tự ghép với chính mình.
- **3. Longest Substring Without Repeating Characters** — sliding window với `dict[char] -> vị trí cuối cùng`; khi gặp ký tự lặp, nhảy `left` tới `max(left, last[ch] + 1)` — chữ `max` là chỗ dễ sai nhất.
- **76. Minimum Window Substring** — `Counter` cho chuỗi cần tìm, một biến đếm "số ký tự đã đủ số lượng" để kiểm tra tính hợp lệ của window trong O(1) thay vì so sánh hai Counter mỗi bước.

## Bài toán áp dụng

**Đếm tần suất token/log.** Bài toán "top-k từ xuất hiện nhiều nhất trong một file log" là `Counter` + `most_common(k)`, và `most_common` dùng `heapq.nlargest` bên trong nên là O(n log k) chứ không phải O(n log n). Với file quá lớn để nạp hết, đọc theo dòng và `counter.update(line.split())` — `Counter` cộng dồn được, và bộ nhớ chỉ tỉ lệ với số từ **phân biệt**, không phải tổng số từ.

**Cache kết quả hàm bằng dict với key là tuple tham số.** Đây chính xác là `functools.cache` (và `lru_cache`): nó dựng key từ `(args, tuple(sorted(kwargs.items())))` rồi tra dict. Hệ quả trực tiếp: **mọi tham số phải hashable**, nên `@cache` trên hàm nhận `list` sẽ ném `TypeError` — chuyển sang `tuple` ở biên. Và vì key giữ tham chiếu tới đối số, `@cache` không giới hạn dung lượng là một nguồn memory leak trong service chạy lâu; `@lru_cache(maxsize=1024)` an toàn hơn.

Liên hệ với memoization trong DP: bảng memo là một dict với key là trạng thái. Nếu trạng thái gồm nhiều thành phần thì key là tuple — và tuple hash nhanh vì hash được tính từ hash của các phần tử.

## Use case thực tế

**`dict` là nền của chính interpreter.** Mỗi module, mỗi class, mỗi instance đều có một `__dict__`. Truy cập `obj.attr` là một (hoặc vài) lần tra dict; gọi `len(x)` là tra dict của builtins nếu không tìm thấy ở scope cục bộ. Đây là lý do CPython đầu tư rất nhiều vào tối ưu dict (key-sharing dict cho instance, inline cache cho attribute lookup trong 3.11+) — dict nhanh hơn 5% nghĩa là Python nhanh hơn vài phần trăm.

**Hash index trong database.** PostgreSQL có `CREATE INDEX ... USING hash` — O(1) cho truy vấn bằng (`WHERE id = 5`) nhưng **vô dụng cho range query** (`WHERE id BETWEEN 5 AND 50`) vì hash phá huỷ thứ tự. Đây chính là lý do B-tree là index mặc định và là lý do §19 tồn tại: khi cần thứ tự, hash không giúp được.

**Bloom filter và HyperLogLog** là hai cấu trúc "hash không lưu key": Bloom filter trả lời "có thể có / chắc chắn không" với bộ nhớ hằng số, HyperLogLog đếm số phần tử phân biệt với sai số ~2% trên vài KB. Redis có cả hai. Khi n quá lớn để giữ một `set` thật, đây là hướng đi.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: gần như tuyệt đối trong Python. `dict`/`set` viết bằng C, đã được tối ưu hàng chục năm, và mọi bản tự cài (kể cả bản ở trên) chậm hơn hàng chục lần. Tự cài chỉ để **hiểu**. Cần đếm → `Counter`. Cần group-by → `defaultdict(list)` hoặc `itertools.groupby` (nhớ sort trước). Cần cache → `functools.cache`. Cần dict giữ thứ tự có `move_to_end` → `OrderedDict`.

## Bẫy thường gặp trong Python

**`1`, `1.0` và `True` là cùng một key.** Hợp đồng hash yêu cầu `a == b ⟹ hash(a) == hash(b)`, và trong Python `1 == 1.0 == True` là `True`. Kết quả:

```python
hash(1), hash(1.0), hash(True)      # 1 1 1
{1: "int", 1.0: "float", True: "bool"}   # {1: 'bool'}  -- CHỈ 1 phần tử
```

Value cuối thắng, nhưng **key giữ nguyên cái được chèn đầu tiên** (`1`, không phải `True`). Bẫy này giết người thật khi bạn dùng `dict` để phân loại và dữ liệu trộn lẫn `int` với `bool` hoặc `float`. Cũng vậy: `{0, False}` chỉ có một phần tử, và `Counter([1, True, 1.0])` cho `Counter({1: 3})`.

**Hash của `str` thay đổi giữa các lần chạy.** Đo trên máy này, ba tiến trình khác nhau cho `hash('dsa-handbook')` ra ba giá trị hoàn toàn khác nhau:

```
-8711122894615947575
-7888331045182906202
-5054193718453810080
```

Với `PYTHONHASHSEED=0` (tắt random hoá) thì cố định. Hệ quả thực dụng: **không bao giờ persist một giá trị hash của str ra file/DB/cache key** — lần chạy sau nó khác. Dùng `hashlib.sha256` nếu cần hash ổn định. Cũng vì lý do này, thứ tự duyệt `set` các chuỗi khác nhau giữa các lần chạy, làm test flaky nếu bạn phụ thuộc vào nó.

**Hash collision DoS.** Vì sao Python random hoá hash của `str`? Vì nếu không, kẻ tấn công biết trước hàm hash có thể sinh hàng nghìn key **cố ý đụng độ** rồi gửi vào một web server phân tích JSON/form — mọi thao tác dict tụt xuống O(n), n key tốn O(n²), server treo. Đây là lỗ hổng CVE-2011-4815 (ảnh hưởng Python, PHP, Ruby, Java, Node cùng lúc); Python vá bằng `PYTHONHASHSEED` random, bật mặc định từ 3.3.

Mức độ nghiêm trọng đo được — chèn N object có `__hash__` trả về hằng số so với hash bình thường:

```
N= 1000  hash hằng số: 0.0258s   hash tốt: 0.00016s   chậm 162x
N= 2000  hash hằng số: 0.0780s   hash tốt: 0.00024s   chậm 326x
N= 4000  hash hằng số: 0.3215s   hash tốt: 0.00047s   chậm 687x
```

Thời gian **gấp 4 khi N gấp đôi** — đúng chữ ký của O(n²). Bài học: khi tự viết `__hash__` cho class của mình, đừng "tối ưu" bằng cách hash chỉ vài trường hoặc vài ký tự đầu. Cách an toàn là `def __hash__(self): return hash((self.a, self.b))` — dùng tuple của các trường tham gia `__eq__`.

Lưu ý ngược lại: các key kiểu `i * 2^18` (đụng nhau ở bit thấp) chỉ chậm ~3 lần trên CPython, vì dãy probe có perturb dùng cả bit cao. Kiến trúc của CPython đã phòng vệ khá tốt; điểm yếu còn lại là `__hash__` do **bạn** viết.

**`defaultdict` chèn key khi chỉ ĐỌC.**

```python
from collections import defaultdict

g = defaultdict(list)
_ = g["chưa-tồn-tại"]
dict(g)      # {'chưa-tồn-tại': []}   -- key đã bị chèn!
```

Hậu quả: `len(g)` sai, duyệt `g` sinh ra key không mong muốn, và trong vòng lặp lớn thì bộ nhớ phình. Muốn đọc mà không chèn, dùng `g.get(key, [])` hoặc `key in g`. `Counter` **không** có vấn đề này: `c["z"]` trả 0 mà không chèn (nhưng `c["z"] += 1` thì có, đương nhiên).

**Định nghĩa `__eq__` mà quên `__hash__` làm class mất tính hashable.** Python tự đặt `__hash__ = None` khi bạn định nghĩa `__eq__`, và mọi lần dùng object đó làm key sẽ ném `TypeError: unhashable type`. Với `@dataclass`, dùng `@dataclass(frozen=True)` để có cả hai.

**`x in list` trong vòng lặp.** Lỗi phổ biến nhất khi mới học, và là thủ phạm của bản naive bài 128. Đo được `in set` nhanh hơn ~570 lần trên 50 000 phần tử. Nếu thấy `in` bên trong một vòng lặp, hãy kiểm tra vế phải là `set`/`dict`, không phải `list`/`tuple`.

**`dict` giữ thứ tự, `set` thì không.** Nhiều người khái quát hoá sai từ đảm bảo của `dict` sang `set`. `set` dùng cấu trúc cũ, thứ tự duyệt phụ thuộc hash và lịch sử chèn — và với `str` thì còn phụ thuộc `PYTHONHASHSEED`. Nếu cần thứ tự, `sorted(s)` hoặc `dict.fromkeys(iterable)` (khử trùng lặp **có** giữ thứ tự).
