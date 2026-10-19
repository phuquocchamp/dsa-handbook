# 18. Binary Search

Binary search là thuật toán mà ai cũng nghĩ mình biết viết cho tới lúc phải viết thật. Jon Bentley kể rằng trong hơn 100 lập trình viên chuyên nghiệp được yêu cầu viết nó, **chỉ khoảng 10% viết đúng** — và bản trong `java.util.Arrays` có bug tràn số suốt 9 năm. Section này chốt **một template duy nhất** đã được kiểm chứng vét cạn, rồi dành phần lớn dung lượng cho kỹ thuật quan trọng nhất của chương: **binary search on answer**.

## Lý thuyết

### Vì sao binary search khó viết đúng

Bug off-by-one không phải do bất cẩn mà do **có quá nhiều biến thể**, và người ta trộn lẫn chúng:

- `hi = len(a)` (nửa mở `[lo, hi)`) hay `hi = len(a) - 1` (đóng `[lo, hi]`)?
- `while lo < hi` hay `while lo <= hi`?
- `hi = mid` hay `hi = mid - 1`?
- Trả `lo`, `hi`, hay một biến `res` riêng?

Ghép sai một cặp là vòng lặp vô hạn hoặc kết quả lệch 1. **Giải pháp là chọn một template và không bao giờ đổi.**

### Template 1 — nửa mở `[lo, hi)` cho tìm kiếm trên mảng

```text
lo, hi = 0, len(a)          # hi EXCLUSIVE
while lo < hi:
    mid = (lo + hi) // 2
    if <a[mid] chắc chắn KHÔNG phải đáp án>:
        lo = mid + 1
    else:
        hi = mid            # a[mid] CÓ THỂ là đáp án -> giữ lại
return lo
```

> **Invariant**: đáp án luôn nằm trong khoảng `[lo, hi]`. Cụ thể với `lower_bound`: mọi `j < lo` có `a[j] < target`; mọi `j >= hi` có `a[j] >= target`.

Ba lý do template này đúng và không treo:

1. **Luôn tiến bộ**: `mid` luôn thoả `lo <= mid < hi` (vì `lo < hi` nên `(lo+hi)//2 < hi`). Nhánh `lo = mid + 1` tăng `lo` ít nhất 1; nhánh `hi = mid` giảm `hi` ít nhất 1 (vì `mid < hi`). Khoảng luôn co lại → **không thể vô hạn**.
2. **Không mất nghiệm**: nhánh loại bỏ chỉ loại những chỉ số chắc chắn không phải đáp án.
3. **Kết thúc sạch**: khi `lo == hi`, invariant nói mọi thứ bên trái nhỏ hơn target và mọi thứ từ `lo` trở đi ≥ target — đúng định nghĩa `lower_bound`. Trả về `lo` (hay `hi`, chúng bằng nhau).

Template này trả về **vị trí chèn** chứ không phải "tìm thấy hay không". Đó là điểm mạnh: nó tổng quát hơn, và kiểm tra `lo < len(a) and a[lo] == target` cho ta bài toán tìm kiếm thông thường.

### Template 2 — khoảng đóng `[lo, hi]` cho binary search on answer

Khi không gian tìm kiếm không phải chỉ số mảng mà là **một khoảng giá trị** (tốc độ ăn chuối, sức chứa tàu, độ dài đoạn), khoảng đóng tự nhiên hơn:

```text
res = hi + 1                 # quy ước "không tìm thấy"
while lo <= hi:              # khoảng ĐÓNG
    mid = lo + (hi - lo) // 2
    if pred(mid):
        res = mid            # ghi lại ứng viên
        hi = mid - 1         # thử tìm cái nhỏ hơn
    else:
        lo = mid + 1
return res
```

Biến `res` tường minh loại bỏ hoàn toàn câu hỏi "trả `lo` hay `hi`?" — cái vướng mắc lớn nhất của template này.

### Binary search on answer — kỹ thuật quan trọng nhất chương

**Nhận diện bài toán**. Ba dấu hiệu, thường xuất hiện cùng nhau:

1. Đề hỏi **"nhỏ nhất/lớn nhất X sao cho..."** hoặc "minimize the maximum" / "maximize the minimum".
2. Khó tính X trực tiếp, nhưng **dễ kiểm tra một X cụ thể có khả thi không**.
3. Tính khả thi **đơn điệu**: nếu X khả thi thì mọi X lớn hơn (hoặc nhỏ hơn) cũng khả thi.

Khi có cả ba, bài toán tối ưu hoá biến thành bài toán quyết định lặp `log(khoảng giá trị)` lần.

**Ba bước máy móc**:

1. **Xác định không gian tìm kiếm** `[lo, hi]`. Chọn rộng rãi — `hi` quá lớn chỉ tốn thêm vài vòng lặp (log), `hi` quá nhỏ là sai đáp án.
2. **Viết `check(x)` như một hàm riêng.** Đây là lời khuyên có giá trị thực tế nhất của cả section: tách `check` ra khỏi vòng binary search khiến bạn debug được nó độc lập, và khiến vòng binary search trở thành đúng cái template ở trên, không bao giờ phải nghĩ lại.
3. **Chứng minh `check` đơn điệu.** Nếu không đơn điệu, binary search **cho kết quả sai một cách im lặng** — nó vẫn chạy, vẫn trả về một số, chỉ là số sai. Đây là chế độ hỏng nguy hiểm nhất của kỹ thuật này.

Tổng độ phức tạp: `O(log(hi - lo) × chi_phí_check)`. Vì `log₂(10⁹) ≈ 30`, một `check` O(n) cho tổng O(30n) — gần như miễn phí.

### Tìm kiếm trên số thực

Số thực không có "phần tử kế tiếp", nên `lo <= hi` không bao giờ dừng. Hai cách:

```text
while hi - lo > 1e-7:        # (a) theo epsilon — rủi ro nếu giá trị rất lớn
    ...
for _ in range(100):         # (b) lặp cố định — LUÔN dừng, luôn đủ chính xác
    ...
```

Cách (b) tốt hơn: 100 vòng chia đôi thu hẹp khoảng còn `(hi-lo)/2¹⁰⁰`, vượt xa độ chính xác 53 bit của `double`. Nó **không thể** vô hạn, và không cần bạn đoán epsilon phù hợp với thang giá trị của bài. Thực tế 100 vòng là dư — 60–70 vòng đã chạm giới hạn của `float`.

Đã kiểm chứng: dùng `binary_search_real` tính căn bậc hai của 2000 số ngẫu nhiên trong `[0, 10⁶]`, sai lệch so với `math.sqrt` luôn < 1e-9. `sqrt(2)` cho `1.4142135623730951`.

### Bảng độ phức tạp

| Thao tác | Chi phí | Ghi chú |
|---|---|---|
| binary search trên mảng sorted | O(log n) | |
| `bisect.bisect_left/right` | O(log n) | code C |
| `bisect.insort` | **O(n)** | binary search O(log n) + `memmove` O(n) |
| binary search on answer | O(log(range) × check) | |
| binary search trên số thực | O(iters × check) | ~100 vòng cố định |

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/search/binary_search.py`

```python
def lower_bound(a: list, target) -> int:
    """Chỉ số ĐẦU TIÊN i sao cho a[i] >= target (== bisect.bisect_left).

    Template nửa mở [lo, hi): hi = len(a), điều kiện dừng lo < hi.
    Invariant: đáp án luôn nằm trong [lo, hi]. Mọi j < lo có a[j] < target;
    mọi j >= hi có a[j] >= target. Khi lo == hi, khoảng rỗng -> lo là đáp án.
    """
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1          # a[mid] chắc chắn KHÔNG phải đáp án
        else:
            hi = mid              # a[mid] CÓ THỂ là đáp án -> giữ lại
    return lo


def upper_bound(a: list, target) -> int:
    """Chỉ số ĐẦU TIÊN i sao cho a[i] > target (== bisect.bisect_right)."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def first_true(lo: int, hi: int, pred) -> int:
    """Binary search on answer: x NHỎ NHẤT trong [lo, hi] có pred(x) True.

    Yêu cầu: pred đơn điệu — False...False True...True.
    Trả về hi + 1 nếu không có x nào thoả (quy ước "không tìm thấy").
    Invariant: pred(j) là False với mọi j < lo; pred(j) là True với mọi j > hi.
    """
    res = hi + 1
    while lo <= hi:               # khoảng ĐÓNG [lo, hi]
        mid = lo + (hi - lo) // 2
        if pred(mid):
            res = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return res


def binary_search_real(lo: float, hi: float, pred, iters: int = 100) -> float:
    """Tìm x nhỏ nhất trong [lo, hi] có pred(x) True, trên số thực.

    Không dùng `while hi - lo > eps` mà lặp CỐ ĐỊNH: 100 vòng chia đôi thu hẹp
    khoảng còn (hi-lo)/2^100, vượt xa độ chính xác của double -> luôn dừng,
    không lo vòng lặp vô hạn do sai số dấu phẩy động.
    """
    for _ in range(iters):
        mid = (lo + hi) / 2
        if pred(mid):
            hi = mid
        else:
            lo = mid
    return hi
```

Khác biệt giữa `lower_bound` và `upper_bound` là **đúng một ký tự** (`<` so với `<=`). Cả hai đều trả về vị trí chèn; `lower_bound` chèn **trước** các phần tử bằng target, `upper_bound` chèn **sau**. Hệ quả hữu dụng: `upper_bound(a, t) - lower_bound(a, t)` là **số lần xuất hiện** của `t`, tính trong O(log n).

Ba hàm này đủ để giải mọi bài binary search. Nếu bạn thấy mình viết một vòng `while lo <= hi` mới, hãy hỏi có phải chỉ cần gọi `first_true` với một `pred` khác không — câu trả lời gần như luôn là có.

### Kiểm chứng vét cạn — artifact quan trọng nhất của section

Template chỉ đáng tin nếu đã được **chứng minh bằng thực nghiệm vét cạn**, không phải bằng "tôi test vài case thấy đúng". Harness sau liệt kê **mọi** mảng sorted độ dài 0–5 trên bảng chữ cái `{0,1,2,3}`, và với mỗi mảng thử **mọi** target trong `range(-1, 5)` — bao gồm target nhỏ hơn mọi phần tử, lớn hơn mọi phần tử, và mọi giá trị ở giữa:

```python
import bisect
from itertools import product


def verify_templates() -> None:
    """Đối chiếu lower_bound/upper_bound với bisect VÀ với quét tuyến tính,
    trên MỌI mảng sorted độ dài 0..5 lấy giá trị trong {0,1,2,3},
    với MỌI target trong range(-1, 5)."""
    cases = 0
    for k in range(6):
        for combo in product(range(4), repeat=k):
            a = sorted(combo)
            for t in range(-1, 5):
                lb_linear = sum(1 for x in a if x < t)   # số phần tử < t
                ub_linear = sum(1 for x in a if x <= t)  # số phần tử <= t
                assert lower_bound(a, t) == bisect.bisect_left(a, t) == lb_linear, (a, t)
                assert upper_bound(a, t) == bisect.bisect_right(a, t) == ub_linear, (a, t)
                cases += 1
    print(f"verify_templates: {cases} trường hợp, khớp bisect + quét tuyến tính")


def verify_first_true() -> None:
    """first_true đối chiếu với quét tuyến tính trên MỌI predicate đơn điệu
    của mọi khoảng [lo, hi] nhỏ."""
    cases = 0
    for lo in range(-3, 4):
        for hi in range(lo - 1, lo + 6):        # gồm cả khoảng rỗng (hi < lo)
            n = hi - lo + 1
            for threshold in range(lo, hi + 2):  # pred(x) = (x >= threshold)
                pred = lambda x, th=threshold: x >= th
                linear = next((x for x in range(lo, hi + 1) if pred(x)), hi + 1)
                assert first_true(lo, hi, pred) == linear, (lo, hi, threshold)
                cases += 1
            # predicate luôn False
            assert first_true(lo, hi, lambda x: False) == hi + 1
            cases += 1
            if n > 0:
                assert first_true(lo, hi, lambda x: True) == lo
                cases += 1
    print(f"verify_first_true: {cases} trường hợp, khớp quét tuyến tính")
```

Kết quả đã chạy:

```
verify_templates: 8190 trường hợp, khớp bisect + quét tuyến tính
verify_first_true: 287 trường hợp, khớp quét tuyến tính
```

Chú ý hai điểm thiết kế của harness: (1) đối chiếu với **hai** oracle độc lập — `bisect` của stdlib và một phép đếm tuyến tính hiển nhiên đúng; (2) `verify_first_true` cố tình bao gồm cả khoảng rỗng (`hi < lo`), predicate luôn `True`, và predicate luôn `False` — ba trường hợp mà template hay hỏng nhất. Nó cũng quét cả khoảng có `lo` âm, chỗ mà `(lo+hi)//2` có hành vi khác `int((lo+hi)/2)`.

Đây là toàn bộ 8477 trường hợp chạy trong chưa tới một giây. Khi đã có nó, bạn không bao giờ phải viết lại binary search bằng trực giác nữa.

## Bài tập chi tiết

### Bài 1 — 875. Koko Eating Bananas

#### Requirements

Koko có `n` đống chuối, đống `i` có `piles[i]` quả, và `h` giờ để ăn hết. Mỗi giờ cô chọn **một** đống và ăn tối đa `k` quả; nếu đống còn ít hơn `k` thì ăn hết và **nghỉ phần giờ còn lại** (không chuyển sang đống khác trong giờ đó). Tìm `k` nguyên nhỏ nhất để ăn hết trong `h` giờ. `1 ≤ n ≤ 10⁴`, `n ≤ h ≤ 10⁹`, `1 ≤ piles[i] ≤ 10⁹`.

Edge cases: `h == n` (mỗi đống đúng một giờ → `k = max(piles)`); `h` rất lớn (`k = 1` đủ); một đống duy nhất; mọi đống bằng nhau; giá trị tới 10⁹ (cẩn thận với `float` khi chia).

Chi tiết đề dễ bỏ sót: **thời gian ăn đống `i` là `ceil(piles[i] / k)`**, không phải `piles[i] / k` — phần giờ dư bị lãng phí.

#### Complexity mục tiêu

Đáp án nằm trong `[1, max(piles)] = [1, 10⁹]` — quá lớn để thử từng giá trị. Nhưng `check(k)` (tính tổng giờ cần với tốc độ `k`) chỉ tốn O(n) = 10⁴. Kết hợp: **O(n log(max(piles))) ≈ 10⁴ × 30 = 3·10⁵** — thoải mái.

Loại được lời giải tuyến tính: thử `k = 1, 2, 3, ...` là O(n × answer), với answer có thể tới 10⁹ → 10¹³ phép. Không thể.

#### Idea

Đây là bài binary search on answer mẫu mực, đủ cả ba dấu hiệu.

Đặt `can_finish(k)` = "với tốc độ `k`, tổng giờ cần ≤ h".

> **Tính đơn điệu (điều kiện then chốt)**: nếu `can_finish(k)` đúng thì `can_finish(k+1)` cũng đúng. Vì `ceil(p/(k+1)) <= ceil(p/k)` với mọi `p > 0` — ăn nhanh hơn thì không bao giờ tốn nhiều giờ hơn. Nên `can_finish` có dạng `False, False, ..., False, True, True, ...` và ta tìm điểm chuyển.

> **Invariant của vòng lặp**: mọi `k < lo` đã bị chứng minh là không đủ; `res` giữ giá trị khả thi nhỏ nhất đã tìm thấy.

Cận tìm kiếm: `lo = 1` (không thể ăn 0 quả/giờ), `hi = max(piles)` (ăn nhanh hơn thế cũng vô ích — mỗi giờ tối đa một đống, nên `k = max(piles)` đã cho `n` giờ, mà đề đảm bảo `h >= n`).

#### Naive

```python
class SolutionNaive875:
    def minEatingSpeed(self, piles: list[int], h: int) -> int:
        def hours(k: int) -> int:
            return sum(-(-p // k) for p in piles)

        k = 1
        while hours(k) > h:      # thử từng tốc độ một
            k += 1
        return k
```

O(n × answer). Với `piles = [10⁹]` và `h = 1` thì answer = 10⁹ và vòng lặp chạy 10⁹ lần — vài chục phút. Nó đúng và là oracle tốt (nó **định nghĩa** đáp án: giá trị nhỏ nhất thoả điều kiện), nhưng nó không khai thác tính đơn điệu chút nào.

#### Optimized

```python
class Solution875:
    def minEatingSpeed(self, piles: list[int], h: int) -> int:
        def can_finish(k: int) -> bool:
            # ceil division bằng số nguyên, không qua float
            return sum(-(-p // k) for p in piles) <= h

        return first_true(1, max(piles), can_finish)
```

O(n log(max piles)) time, O(1) space. Đánh đổi: ta đổi **tính hiển nhiên** lấy tốc độ — bản naive đọc là hiểu ngay, bản này đúng chỉ khi `can_finish` thật sự đơn điệu, và nếu không thì sai im lặng. Đó là lý do lập luận đơn điệu phải viết ra trước khi gõ code.

Chú ý `-(-p // k)` là ceil division bằng số nguyên thuần. Viết `math.ceil(p / k)` phải qua `float`, và với `p = 10¹⁸` thì `float` mất chính xác — sai kết quả một cách khó phát hiện. Trong Python `int` không tràn, nên số học nguyên luôn là lựa chọn an toàn.

Toàn bộ vòng binary search nằm trong `first_true` — code của bài này chỉ còn đúng **một hàm `can_finish` và một lời gọi**. Đó là lợi ích thực tế của việc có template đã kiểm chứng.

Đã stress test 4000 lần với 1–5 đống giá trị `[1,12]` và `h ∈ [n, n+12]`, đối chiếu với bản thử tuần tự. `minEatingSpeed([3,6,7,11], 8)` → `4`; `minEatingSpeed([30,11,23,4,20], 5)` → `30`.

### Bài 2 — 33. Search in Rotated Sorted Array

#### Requirements

Mảng `nums` gồm các giá trị **phân biệt**, ban đầu sort tăng, sau đó bị **xoay** tại một pivot chưa biết (`[0,1,2,4,5,6,7]` → `[4,5,6,7,0,1,2]`). Tìm chỉ số của `target`, trả `-1` nếu không có. `1 ≤ n ≤ 5000`, giá trị phân biệt. Đề yêu cầu **O(log n)**.

Edge cases: mảng **không bị xoay** (xoay 0 vị trí — vẫn phải đúng); `n == 1`; target ở đúng vị trí pivot; target nhỏ hơn mọi phần tử hoặc lớn hơn mọi phần tử; target ngay tại `nums[0]` hoặc `nums[-1]`.

Ràng buộc "giá trị phân biệt" là quan trọng: bài **81** là biến thể cho phép trùng lặp, và ở đó O(log n) **không còn khả thi** trong worst case.

#### Complexity mục tiêu

n ≤ 5000 nên O(n) pass thoải mái. Nhưng đề nói O(log n), và bài này tồn tại để dạy: **binary search không đòi hỏi mảng sorted toàn cục, chỉ đòi hỏi ở mỗi bước ta loại bỏ được một nửa một cách chắc chắn.**

#### Idea

Quan sát mấu chốt: với một mảng xoay và điểm giữa `mid` bất kỳ, **ít nhất một trong hai nửa `[lo, mid]` và `[mid, hi]` là sorted hoàn toàn**. (Điểm xoay chỉ có một, nên nó chỉ nằm trong một nửa.)

Phân biệt bằng `nums[lo] <= nums[mid]`: đúng nghĩa là nửa trái sorted, sai nghĩa là nửa phải sorted.

> **Invariant**: `target`, nếu tồn tại, luôn nằm trong `[lo, hi]`.

Trong nửa đã sorted, ta kiểm tra `target` có nằm trong khoảng giá trị của nó không — chỉ hai phép so sánh. Nếu có thì thu hẹp vào nửa đó; nếu không thì `target` chỉ có thể ở nửa kia. Cả hai trường hợp đều loại bỏ đúng một nửa → O(log n).

Dấu `<=` trong `nums[lo] <= nums[mid]` (không phải `<`) là cần thiết cho trường hợp `lo == mid` (khoảng còn 2 phần tử) — lúc đó nửa trái chỉ có một phần tử và hiển nhiên sorted.

#### Naive

```python
class SolutionNaive33:
    def search(self, nums: list[int], target: int) -> int:
        for i, x in enumerate(nums):
            if x == target:
                return i
        return -1
```

O(n). Nó pass trên LeetCode (n ≤ 5000) và không có gì sai — chỉ là nó bỏ qua hoàn toàn cấu trúc của dữ liệu. Là oracle hoàn hảo cho stress test vì không thể sai.

#### Optimized

```python
class Solution33:
    def search(self, nums: list[int], target: int) -> int:
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[lo] <= nums[mid]:            # nửa TRÁI đang sorted
                if nums[lo] <= target < nums[mid]:
                    hi = mid - 1
                else:
                    lo = mid + 1
            else:                                # nửa PHẢI đang sorted
                if nums[mid] < target <= nums[hi]:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return -1
```

O(log n) time, O(1) space. Đánh đổi: bốn nhánh điều kiện lồng nhau với các dấu `<` và `<=` không đối xứng — đây là loại code mà **bắt buộc** phải stress test, không thể tin vào việc đọc lại. Đổi lấy: mở rộng được sang mảng 10⁶ phần tử, và quan trọng hơn là ý tưởng "chỉ cần loại được một nửa chắc chắn" tổng quát hơn "cần mảng sorted".

Về các dấu bất đẳng thức: `nums[lo] <= target < nums[mid]` dùng `<` ở vế phải vì `nums[mid] != target` (đã kiểm tra ở trên); tương tự `nums[mid] < target <= nums[hi]`. Viết đối xứng (cả hai đều `<=`) vẫn đúng ở đây nhưng khiến người đọc không hiểu vì sao — cách viết trên nói rõ `mid` đã được loại.

Một hướng khác đáng biết: tìm chỉ số pivot bằng binary search trước (O(log n)), rồi binary search thường trên nửa chứa target. Dài hơn nhưng dễ chứng minh hơn, và tái dùng được `lower_bound`.

Đã stress test 5000 mảng xoay ngẫu nhiên (n ∈ [1,9], giá trị phân biệt lấy từ `[-10,10]`, mọi lượng xoay), và với **mỗi** mảng thử **mọi** target trong `[-11, 11]` — tức là cả trường hợp có và không có. `search([4,5,6,7,0,1,2], 0)` → `4`; `search([4,5,6,7,0,1,2], 3)` → `-1`.

### Bài 3 — 4. Median of Two Sorted Arrays

#### Requirements

Cho hai mảng đã sort `nums1` (m phần tử) và `nums2` (n phần tử), tìm median của hợp nhất chúng. `0 ≤ m, n ≤ 1000`, `m + n >= 1`. Đề yêu cầu tường minh **O(log(m+n))**.

Edge cases: **một mảng rỗng** (đây là edge case chính, và nó ép mọi chỉ số phải xử lý biên); `m + n` chẵn (trung bình hai phần tử giữa); mọi phần tử của mảng này đều nhỏ hơn mọi phần tử của mảng kia (không giao nhau); giá trị trùng lặp giữa hai mảng; mỗi mảng đúng một phần tử.

#### Complexity mục tiêu

Đây là bài mà **đề bài chính là ràng buộc**: `m, n ≤ 1000` nên merge O(m+n) hay thậm chí `sorted(a+b)` đều pass dễ dàng. Nhưng đề nói O(log(m+n)), nên lời giải merge bị loại **về mặt yêu cầu**. Điều này khiến bài 4 là ví dụ chuẩn trong §02 về "đọc yêu cầu độ phức tạp trong đề, không chỉ đọc constraint".

#### Idea

Không tìm median trực tiếp. Thay vào đó, tìm một **cách chia** hai mảng thành "nửa trái" và "nửa phải" sao cho:

- Nửa trái có đúng `half = (m+n+1)//2` phần tử (công thức `+1` xử lý luôn cả trường hợp lẻ và chẵn).
- **Mọi phần tử nửa trái ≤ mọi phần tử nửa phải.**

Nếu chia được như vậy, median tính ngay từ bốn giá trị ở biên: `m+n` lẻ → `max(nửa trái)`; chẵn → trung bình `max(nửa trái)` và `min(nửa phải)`.

Cách chia được xác định bởi **một số duy nhất**: `i` = số phần tử lấy từ `A`, khi đó `j = half - i` từ `B`. Vậy không gian tìm kiếm là `i ∈ [0, m]`.

Điều kiện "nửa trái ≤ nửa phải" gồm hai bất đẳng thức chéo: `A[i-1] <= B[j]` và `B[j-1] <= A[i]`.

> **Tính đơn điệu**: khi `i` tăng, `A[i]` tăng và `j = half - i` giảm nên `B[j-1]` giảm. Vậy điều kiện `B[j-1] <= A[i]` có dạng `False...False True...True` theo `i`. Và **`i` nhỏ nhất thoả nó cũng tự động thoả điều kiện chéo còn lại** — vì nếu `i` là nhỏ nhất, thì `i-1` không thoả, nghĩa là phần tử `A[i-1]` đủ nhỏ để không phá vế kia.

Đó là điều kiện đơn điệu — dùng `first_true` là xong. Ta luôn binary search trên mảng **ngắn hơn** để đảm bảo `j` không ra khỏi biên và để độ phức tạp là `O(log min(m, n))`.

Giá trị `-inf`/`+inf` ở biên là mẹo quan trọng: `A[-1]` coi như `-inf` (không có phần tử nào bên trái), `A[m]` coi như `+inf`. Nhờ đó mọi so sánh đều hợp lệ mà không cần một lệnh `if` biên nào trong logic chính.

#### Naive

```python
class SolutionNaive4:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        a = sorted(nums1 + nums2)
        n = len(a)
        return float(a[n // 2]) if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2
```

O((m+n) log(m+n)) — hoặc O(m+n) nếu merge thủ công thay vì `sorted`. Chậm ở chỗ nó vật chất hoá **toàn bộ** mảng hợp nhất trong khi ta chỉ cần 1–2 phần tử ở giữa. Với `m + n` = 10⁹ (hai file trên đĩa) nó không chạy được, còn bản O(log) thì có.

#### Optimized

```python
class Solution4:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        A, B = nums1, nums2
        if len(A) > len(B):
            A, B = B, A                       # binary search trên mảng NGẮN hơn
        m, n = len(A), len(B)
        half = (m + n + 1) // 2               # số phần tử ở nửa trái
        INF = float("inf")

        # i = số phần tử lấy từ A vào nửa trái; j = half - i lấy từ B.
        # Cần: A[i-1] <= B[j] VÀ B[j-1] <= A[i].
        # Điều kiện B[j-1] <= A[i] đơn điệu theo i (A[i] tăng, B[j-1] giảm),
        # và i nhỏ nhất thoả nó cũng tự động thoả điều kiện còn lại.
        def ok(i: int) -> bool:
            j = half - i
            left_b = B[j - 1] if j > 0 else -INF
            right_a = A[i] if i < m else INF
            return left_b <= right_a

        i = first_true(0, m, ok)
        j = half - i
        left_a = A[i - 1] if i > 0 else -INF
        left_b = B[j - 1] if j > 0 else -INF
        max_left = max(left_a, left_b)
        if (m + n) % 2:
            return float(max_left)
        right_a = A[i] if i < m else INF
        right_b = B[j] if j < n else INF
        return (max_left + min(right_a, right_b)) / 2
```

**O(log min(m, n))** time, O(1) space. Đánh đổi rất rõ: 20 dòng dày đặc chỉ số biên thay cho 3 dòng hiển nhiên, và **không đọc được nếu không có lập luận phân hoạch ở trên**. Đổi lấy: độ phức tạp giảm từ tuyến tính xuống logarit, tức là chạy được khi hai mảng không nằm trong bộ nhớ (chỉ cần truy cập ngẫu nhiên theo chỉ số — như hai file đã sort trên đĩa).

Điểm đáng chú ý về mặt kỹ thuật: **vòng binary search hoàn toàn không xuất hiện** trong lời giải này. Nó nằm trong `first_true`, đã kiểm chứng vét cạn. Việc còn lại chỉ là viết đúng `ok(i)` và bốn giá trị biên. Đây là lợi ích lớn nhất của việc có template: bài hard nhất chương cũng chỉ còn là bài "định nghĩa predicate cho đúng".

Ghi chú trung thực: khi viết chương này, lần đầu tôi chọn predicate `A[i-1] <= B[j]` và nó **sai** — stress test bắt được ngay ở `A=[-7,-4,1,3,4], B=[-5,2,4,7,7]`, vì tại `i=0` thì `j=n` nên `B[j]` là `+inf` và predicate đúng một cách vô nghĩa. Predicate đúng là điều kiện chéo còn lại. Đây chính là chế độ hỏng đã cảnh báo ở phần Lý thuyết: binary search với predicate không đơn điệu (hoặc đơn điệu sai chiều) **không báo lỗi**, nó chỉ trả về số sai.

Đã stress test 6000 cặp mảng ngẫu nhiên với `m ∈ [0,6]`, `n ∈ [0,6]` (bao gồm cả mảng rỗng), giá trị `[-8,8]` với nhiều trùng lặp, đối chiếu với bản merge. `findMedianSortedArrays([1,3],[2])` → `2.0`; `findMedianSortedArrays([1,2],[3,4])` → `2.5`.

## Bài luyện thêm

- **704. Binary Search** — bài nền; dùng thẳng `lower_bound` rồi kiểm tra `lo < len(a) and a[lo] == target`.
- **34. Find First and Last Position of Element in Sorted Array** — `bisect_left` cho vị trí đầu, `bisect_right - 1` cho vị trí cuối; nếu `bisect_left == bisect_right` thì target không tồn tại.
- **1011. Capacity To Ship Packages Within D Days** — cùng khuôn với 875: `check(cap)` = "chở hết trong ≤ `days` ngày với sức chứa `cap`"; không gian tìm kiếm là `[max(weights), sum(weights)]` — cận dưới **không phải 1** vì mỗi kiện phải chở nguyên trong một ngày.

## Bài toán áp dụng

**Tìm ngưỡng tối ưu trong phân bổ tài nguyên.** "Chia một file 100 GB thành `k` phần sao cho phần lớn nhất nhỏ nhất có thể", "phân bổ băng thông cho `n` luồng sao cho luồng chậm nhất nhanh nhất có thể", "chọn số worker tối thiểu để xử lý hết queue trong SLA" — tất cả đều là *minimize the maximum* và đều giải bằng binary search on answer với `check(x)` là một phép mô phỏng greedy O(n).

Khuôn chung:

```python
def min_max_partition(a: list[int], k: int) -> int:
    """Chia a thành k đoạn liên tiếp, tối thiểu hoá tổng lớn nhất của một đoạn."""
    def can(limit: int) -> bool:
        parts, cur = 1, 0
        for x in a:
            if cur + x > limit:
                parts += 1
                cur = 0
            cur += x
        return parts <= k

    return first_true(max(a), sum(a), can)
```

Cận dưới là `max(a)` (một phần tử phải nằm gọn trong một đoạn), cận trên là `sum(a)` (một đoạn duy nhất). `can` đơn điệu vì tăng `limit` không bao giờ làm tăng số đoạn cần.

Đã stress test 3000 lần với `n ∈ [1,8]`, giá trị `[1,20]`, `k ∈ [1,n]`, đối chiếu với một bản DP brute-force `f(i, parts) = min over j của max(sum(a[i:j+1]), f(j+1, parts-1))`. `min_max_partition([7,2,5,10,8], 2)` → `18`. (Đây chính là LeetCode 410 Split Array Largest Sum.)

**Tìm nghiệm gần đúng của hàm liên tục.** Với `f` liên tục và đơn điệu, `binary_search_real(lo, hi, lambda x: f(x) >= 0)` tìm nghiệm với độ chính xác của `double` trong 100 vòng. Đây là cách tính `sqrt`, `log`, hay nghiệm của phương trình không có công thức đóng — chậm hơn Newton–Raphson nhưng **không cần đạo hàm và không bao giờ phân kỳ**, chỉ cần đơn điệu.

## Use case thực tế

**`git bisect`** là binary search on answer với `check(commit)` = "commit này có bug không" và không gian tìm kiếm là lịch sử commit. Tính đơn điệu là giả định (bug xuất hiện tại một commit rồi tồn tại tới hiện tại), và khi giả định đó sai — bug xuất hiện rồi biến mất rồi lại xuất hiện — `git bisect` cho kết quả sai đúng như binary search với predicate không đơn điệu. `git bisect run <script>` tự động hoá luôn phần `check`.

**B-tree index trong database.** Mỗi node B-tree chứa hàng chục tới hàng trăm khoá đã sort, và việc tìm khoá **trong một node** là binary search. Tại sao không dùng cây nhị phân? Vì đơn vị đọc từ đĩa/SSD là một page (4–8 KB); B-tree nhét nhiều khoá vào một page để một lần đọc I/O cho nhiều bước tìm kiếm. Binary search vẫn ở đó, chỉ là nằm trong bộ nhớ sau khi đã đọc page.

**Autoscaler và capacity planning.** "Số instance tối thiểu để p99 latency < 200 ms" là binary search on answer, với `check(n)` = chạy load test với `n` instance. Ở đây `check` **rất đắt** (vài phút mỗi lần), nên việc giảm từ tuyến tính xuống logarit là khác biệt giữa vài giờ và vài chục phút. Đây cũng là ví dụ cho thấy tính đơn điệu trong thực tế chỉ là **giả định**: nhiễu đo đạc có thể khiến `check` không đơn điệu và binary search hội tụ về một điểm hơi lệch.

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: với tìm kiếm trên mảng sorted, luôn dùng `bisect` — nó là code C, nhanh hơn, và đã đúng. Từ Python 3.10 nó có `key=`:

```python
import bisect

recs = [("a", 1), ("b", 3), ("c", 5), ("d", 9)]
bisect.bisect_left(recs, 5, key=lambda r: r[1])    # 2
bisect.bisect_right(recs, 5, key=lambda r: r[1])   # 3
```

Trước 3.10 phải dựng một mảng khoá riêng (tốn O(n) bộ nhớ) hoặc bọc trong `SortedKeyList`. Chú ý `key` được áp cho **phần tử trong mảng**, không áp cho `target` — nên target phải đã ở dạng khoá.

Tự viết binary search chỉ đáng khi: không gian tìm kiếm không phải mảng (binary search on answer), hoặc dữ liệu không nằm trong bộ nhớ (tìm trên file/API).

## Bẫy thường gặp trong Python

**`(lo + hi) // 2` KHÔNG tràn số trong Python.** Bug nổi tiếng của `Arrays.binarySearch` trong Java (và trong bản của Bentley) là `(lo + hi) / 2` tràn `int` khi mảng lớn hơn 2³⁰ phần tử. Python có `int` arbitrary precision nên bug này **không tồn tại**. Bạn vẫn có thể viết `lo + (hi - lo) // 2` cho quen tay khi chuyển ngôn ngữ, nhưng trong Python nó không mua thêm gì.

**`//` làm tròn về âm vô cực — quan trọng khi khoảng tìm kiếm chứa số âm.** Đã đo:

```python
(-7 + -6) // 2      # -7   (floor)
int((-7 + -6) / 2)  # -6   (truncate về 0)
```

Với template `[lo, hi]` và `lo` âm, `mid = (lo+hi)//2` cho `mid = -7`, thoả `lo <= mid < hi` — **template vẫn đúng**. Nhưng nếu bạn viết một biến thể dùng `hi = mid` với `mid` được làm tròn về 0, khoảng có thể không co lại và vòng lặp treo. Dùng `lo + (hi - lo) // 2` để `mid` luôn nghiêng về phía `lo` bất kể dấu — đó là lý do `first_true` viết như vậy.

**`bisect.insort` là O(n), không phải O(log n).** Nó tìm vị trí trong O(log n) rồi **chèn** trong O(n) vì phải dịch mảng. Đo trên máy này: 200 000 lần `insort` mất **1.392 s**, trong khi sinh cả list rồi `sort()` một lần mất **0.052 s** — chậm 27 lần. Nếu thuật toán của bạn cần duy trì mảng sorted qua nhiều lần chèn, `insort` cho O(n²) tổng. Đây chính xác là vấn đề mà §19 giải quyết.

**Predicate không đơn điệu → sai im lặng.** Không có exception, không có cảnh báo — chỉ là một số sai. Đây là chế độ hỏng nguy hiểm nhất của binary search on answer, và đã xảy ra thật khi viết bài 4 ở trên. Phòng vệ duy nhất: (a) viết ra lập luận đơn điệu trước khi code, (b) stress test với bản brute-force trên input nhỏ.

**Quên rằng `bisect` cần mảng ĐÃ sort.** Trên mảng chưa sort, `bisect` không báo lỗi mà trả về một số vô nghĩa. Cùng lớp lỗi với trên.

**`bisect(..., key=)` áp key lên phần tử mảng, không lên target.** `bisect_left(recs, ("c", 5), key=lambda r: r[1])` là sai — target phải là `5`, đã ở dạng khoá. Thông báo lỗi (nếu có) sẽ khó hiểu.

**So sánh số thực bằng `==` trong binary search.** `if f(mid) == target` gần như không bao giờ đúng với `float`. Luôn dùng bất đẳng thức (`>=`, `<`) và lặp số vòng cố định thay vì chờ bằng nhau.

**Không gian tìm kiếm đặt sai cận.** Với bài 1011, cận dưới là `max(weights)` chứ không phải 1 — đặt 1 thì `check` sai (không kiện nào chở được) nhưng binary search vẫn chạy và có thể trả về giá trị sai nếu `check` không xử lý đúng trường hợp bất khả thi. Luôn kiểm tra: `check(lo)` phải là `False` (hoặc lo là đáp án hợp lệ) và `check(hi)` phải là `True`.
