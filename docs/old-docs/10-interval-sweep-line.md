# 10. Interval problems: merge & sweep line

Bài toán khoảng (interval) gần như luôn bắt đầu bằng cùng một bước: **sort theo một đầu**, rồi quét tuyến tính. Cái khó là chọn đúng đầu để sort — điểm bắt đầu cho bài merge, điểm **kết thúc** cho bài greedy chọn nhiều khoảng nhất. Sweep line là dạng tổng quát: biến mỗi khoảng thành hai sự kiện `+1` / `-1`, sort tất cả sự kiện, rồi quét một lượt. Section này chốt cả hai và chỉ ra vì sao chọn sai khoá sort làm sai lời giải chứ không chỉ làm chậm.

## Lý thuyết

### Quy ước khoảng: đóng hay nửa mở

Phải chốt trước khi viết dòng nào, vì mọi công thức phụ thuộc vào nó:

- **Đóng `[s, e]`**: `e` thuộc khoảng. Hai khoảng `[1,2]` và `[2,3]` **chồng lấp** tại điểm 2.
- **Nửa mở `[s, e)`**: `e` không thuộc. `[1,2)` và `[2,3)` **không** chồng lấp.

Bài 56. Merge Intervals dùng khoảng đóng (`[1,4]` và `[4,5]` phải gộp thành `[1,5]`). Bài 253. Meeting Rooms II dùng nửa mở (cuộc họp kết thúc lúc 10 và cuộc khác bắt đầu lúc 10 dùng **chung** một phòng). Điều kiện chồng lấp:

```
dong    : a.start <= b.end  and  b.start <= a.end
nua mo  : a.start <  b.end  and  b.start <  a.end
```

Sai một dấu `=` ở đây là sai lời giải, và test do bạn tự nghĩ hầu như không bao giờ có hai khoảng chạm nhau đúng ở biên.

### Merge: sort theo điểm bắt đầu

> **Invariant**: sau khi xử lý `k` khoảng đầu (theo thứ tự start tăng dần), `out` chứa các khoảng đã gộp, **rời nhau đôi một**, đã sort theo start, và `out[-1]` là khoảng duy nhất còn có thể mở rộng.

Câu cuối là mấu chốt. Vì input đã sort theo start, khoảng tiếp theo có `start` **≥ start của mọi khoảng đã xử lý**, nên nó chỉ có thể chồng lấp với khoảng có `end` lớn nhất — mà đó chính là `out[-1]` (do các khoảng trong `out` rời nhau và sort theo start, cái cuối cùng cũng có end lớn nhất). Vậy chỉ cần so với **một** phần tử, không phải cả danh sách. Đó là thứ cho `O(n)` sau khi sort.

Bảo toàn: nếu `s <= out[-1][1]` thì gộp bằng `out[-1][1] = max(out[-1][1], e)` — **phải có `max`**, vì khoảng mới có thể **nằm gọn bên trong** khoảng cũ (`[1,10]` rồi `[2,3]`). Ngược lại thì `append` khoảng mới.

Tổng: `O(n log n)` cho sort + `O(n)` quét.

### Greedy chọn nhiều khoảng nhất: sort theo điểm KẾT THÚC

Bài 435 (và bài activity selection cổ điển) đòi giữ lại nhiều khoảng rời nhau nhất. Khoá sort là **`end`**, không phải `start`.

> **Định lý trao đổi (exchange argument)**: tồn tại một lời giải tối ưu chứa khoảng có `end` nhỏ nhất.

Chứng minh: lấy một lời giải tối ưu `S` bất kỳ, và `x` là khoảng có `end` nhỏ nhất trong toàn bộ input. Nếu `x ∈ S` thì xong. Nếu không, gọi `y` là khoảng có `end` nhỏ nhất trong `S`. Vì `x.end ≤ y.end` và các khoảng trong `S` rời nhau, thay `y` bằng `x` vẫn cho tập rời nhau (mọi khoảng khác trong `S` bắt đầu sau `y.end ≥ x.end`), cùng kích thước ⇒ vẫn tối ưu. ∎

Áp dụng đệ quy định lý này cho phần còn lại ⇒ greedy "luôn chọn khoảng kết thúc sớm nhất còn tương thích" là tối ưu.

Trực giác: kết thúc sớm để **để lại nhiều chỗ nhất** cho các khoảng sau. Sort theo `start` là **sai** — một khoảng bắt đầu sớm nhưng rất dài sẽ chiếm chỗ và bị chọn nhầm.

### Sweep line

Tổng quát hơn merge. Biến mỗi khoảng `[s, e)` thành hai sự kiện:

```
(s, +1)   # mot khoang mo ra
(e, -1)   # mot khoang dong lai
```

Sort tất cả sự kiện theo thời điểm, quét, cộng dồn. Giá trị chạy là **số khoảng đang mở tại thời điểm đó**.

> **Invariant**: sau khi xử lý mọi sự kiện có thời điểm ≤ `t`, biến `cur` bằng đúng số khoảng chứa `t` (theo quy ước nửa mở).

Chi tiết quyết định đúng/sai: **thứ tự khi hai sự kiện trùng thời điểm**. Với khoảng nửa mở, sự kiện `-1` phải chạy **trước** `+1` (phòng được trả rồi mới có người vào). Trong Python, sort tuple `(t, delta)` xử lý việc này **miễn phí** vì `-1 < +1` ⇒ tại cùng `t`, sự kiện đóng đứng trước. Nếu đề dùng khoảng đóng, bạn phải đảo ưu tiên — sort theo `(t, -delta)`.

| Cách tiếp cận | Time | Space | Cho biết |
| --- | --- | --- | --- |
| Merge (sort theo start) | `O(n log n)` | `O(n)` output | các khoảng hợp nhất |
| Greedy (sort theo end) | `O(n log n)` | `O(1)` | số khoảng giữ/xoá tối đa |
| Sweep line (2n sự kiện) | `O(n log n)` | `O(n)` | số khoảng chồng lấp tại mọi thời điểm |
| Difference array (§08) | `O(n + M)` | `O(M)` | như sweep line, khi trục là số nguyên **nhỏ** |

Dòng cuối đáng chú ý: sweep line và difference array **là cùng một ý tưởng**. Chọn difference array khi trục thời gian rời rạc và biên nhỏ (bài 1094: vị trí `0..1000`) vì nó `O(n + M)` không cần sort; chọn sweep line khi trục liên tục hoặc miền giá trị khổng lồ (timestamp Unix).

## Bài tập chi tiết

### Bài 1 — 56. Merge Intervals

#### Requirements

Cho danh sách `intervals`, mỗi phần tử `[start, end]`. Gộp mọi khoảng chồng lấp và trả về danh sách các khoảng rời nhau phủ đúng phần input phủ.

Khoảng là **đóng**: `[1,4]` và `[4,5]` chạm nhau tại 4 ⇒ phải gộp thành `[1,5]`.

Input **không** bảo đảm đã sort.

Ràng buộc: `1 ≤ n ≤ 10^4`, `0 ≤ start ≤ end ≤ 10^4`.

Edge cases: một khoảng **chứa trọn** khoảng khác (`[1,10]`, `[2,3]`); khoảng suy biến `start == end` (`[3,3]`); tất cả chồng lấp thành một; không có khoảng nào chồng lấp; hai khoảng chạm nhau đúng ở biên; input đã sort sẵn hoặc sort ngược.

#### Complexity mục tiêu

`n ≤ 10^4`. `O(n²)` là `10^8` — với CPython là ~10 giây, quá rủi ro.

Nhưng ở đây `O(n log n)` **không phải là thoả hiệp** — nó là cận dưới tự nhiên: bài toán này quy về sắp xếp (nếu giải được merge nhanh hơn `O(n log n)` với so sánh, bạn sẽ sort được nhanh hơn `O(n log n)`). Nên: sort `O(n log n)` + quét `O(n)`.

#### Idea

Sort theo `start`, rồi quét giữ một khoảng "đang mở" ở cuối `out`.

> **Invariant**: `out` luôn chứa các khoảng **rời nhau đôi một**, sort tăng theo start, và mọi khoảng đã đọc đều đã được phủ bởi `out`. Chỉ `out[-1]` còn có thể mở rộng.

Bảo toàn khi đọc khoảng `[s, e]` (với `s >= start` của mọi khoảng đã đọc, nhờ đã sort):
- `s <= out[-1][1]`: hai khoảng chồng lấp ⇒ `out[-1][1] = max(out[-1][1], e)`. Dùng `max` vì `[s, e]` có thể nằm gọn bên trong.
- `s > out[-1][1]`: không chồng với `out[-1]`; và vì `out[-1]` có `end` lớn nhất trong `out`, nó cũng không chồng với bất kỳ khoảng nào khác ⇒ `append`.

Kết thúc: đọc hết ⇒ mọi khoảng đã được phủ, và `out` rời nhau ⇒ đó là đáp án.

#### Naive

```python
class SolutionNaive:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        """Lap lai: tim BAT KY hai khoang chong lap, gop chung. O(n^3) worst case."""
        iv = [list(x) for x in intervals]
        changed = True
        while changed:
            changed = False
            for i in range(len(iv)):
                for j in range(i + 1, len(iv)):
                    a, b = iv[i], iv[j]
                    if a[0] <= b[1] and b[0] <= a[1]:      # khoang DONG
                        iv[i] = [min(a[0], b[0]), max(a[1], b[1])]
                        iv.pop(j)
                        changed = True
                        break
                if changed:
                    break
        return sorted(iv)

print(SolutionNaive().merge([[1, 3], [2, 6], [8, 10], [15, 18]]))
print(SolutionNaive().merge([[1, 4], [4, 5]]))
print(SolutionNaive().merge([[1, 10], [2, 3], [4, 5]]))
```

In ra `[[1, 6], [8, 10], [15, 18]]`, `[[1, 5]]`, `[[1, 10]]`.

`O(n³)` worst case (`O(n²)` để tìm một cặp, lặp `O(n)` lần), `O(n)` space. Chậm vì nó **không dùng thứ tự** — mỗi lần gộp lại quét lại toàn bộ để tìm cặp tiếp theo. Bù lại nó rất khó sai, nên đây là oracle tốt.

#### Optimized

```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
        iv = sorted(intervals)                    # sort theo start (roi end)
        out = [list(iv[0])]
        for s, e in iv[1:]:
            if s <= out[-1][1]:                   # <= vi khoang DONG
                out[-1][1] = max(out[-1][1], e)   # max: [s,e] co the nam gon ben trong
            else:
                out.append([s, e])
        return out

import random

def naive(intervals: list[list[int]]) -> list[list[int]]:
    iv = [list(x) for x in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(iv)):
            for j in range(i + 1, len(iv)):
                a, b = iv[i], iv[j]
                if a[0] <= b[1] and b[0] <= a[1]:
                    iv[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    iv.pop(j); changed = True; break
            if changed:
                break
    return sorted(iv)

random.seed(0)
sol = Solution()
for _ in range(5000):
    case = []
    for _ in range(random.randint(0, 6)):
        s = random.randint(0, 8)
        case.append([s, random.randint(s, 8)])
    if naive([x[:] for x in case]) != sol.merge([x[:] for x in case]):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.merge([[1, 3], [2, 6], [8, 10], [15, 18]]),
      sol.merge([[1, 4], [4, 5]]), sol.merge([[1, 10], [2, 3], [4, 5]]))
```

In ra `khop tren 5000 case ngau nhien` rồi `[[1, 6], [8, 10], [15, 18]] [[1, 5]] [[1, 10]]`.

**Đánh đổi**: trả trước `O(n log n)` cho sort để mỗi khoảng sau đó chỉ phải so với **một** phần tử thay vì cả danh sách. Đây là dạng "tiền xử lý đổi lấy thời gian truy vấn" giống §08, nhưng ở đây tiền xử lý là **áp đặt một thứ tự** chứ không phải dựng bảng. Cái giá phụ: `sorted(intervals)` tạo list mới `O(n)` (dùng `intervals.sort()` nếu được phép sửa input), và output bị sort — nếu đề đòi giữ thứ tự gốc thì cách này không dùng được.

### Bài 2 — 435. Non-overlapping Intervals

#### Requirements

Cho danh sách khoảng, trả về **số khoảng ít nhất phải xoá** để phần còn lại không chồng lấp nhau.

Quy ước ở bài này: khoảng chạm nhau ở biên (`[1,2]` và `[2,3]`) **không** tính là chồng lấp — tức nửa mở.

Bài toán tương đương: `n - (số khoảng nhiều nhất có thể giữ rời nhau)`. Đây chính là bài **activity selection**.

Ràng buộc: `1 ≤ n ≤ 10^5`, `-5·10^4 ≤ start < end ≤ 5·10^4`.

Edge cases: `n = 1` (trả 0); mọi khoảng giống hệt nhau (giữ 1, xoá `n-1`); mọi khoảng rời nhau (trả 0); một khoảng khổng lồ phủ tất cả; khoảng chạm nhau đúng ở biên.

#### Complexity mục tiêu

`n ≤ 10^5` ⇒ bắt buộc `O(n log n)` trở xuống. `O(n²)` là `10^10`.

Quan trọng hơn: lời giải "thử mọi tập con" là `O(2^n)` — chỉ dùng được làm oracle với `n ≤ 15`. Và lời giải DP `O(n²)` (kiểu LIS) cũng có, nhưng greedy `O(n log n)` vừa nhanh hơn vừa đơn giản hơn — với điều kiện bạn **chứng minh được** nó đúng.

#### Idea

Sort theo **`end`** tăng dần, rồi quét giữ `end` của khoảng cuối cùng đã **giữ lại**.

> **Invariant**: sau khi xét `k` khoảng đầu (theo thứ tự end tăng dần), `end` là điểm kết thúc **nhỏ nhất có thể** của một tập tối đa các khoảng rời nhau chọn từ `k` khoảng đó, và `cnt` là số khoảng đã xoá.

Với mỗi khoảng `[s, e]`:
- `s >= end`: tương thích ⇒ giữ, cập nhật `end = e`.
- `s < end`: chồng lấp ⇒ **xoá khoảng này**, không xoá khoảng đã giữ. Vì đã sort theo `end`, khoảng đã giữ có `end` **nhỏ hơn hoặc bằng** `e` ⇒ giữ nó luôn không tệ hơn (định lý trao đổi ở mục Lý thuyết).

Đây là chỗ khoá sort quyết định tính đúng: sort theo `start` thì khi gặp xung đột bạn không biết bỏ cái nào, và mọi lựa chọn đều có counterexample.

Kết thúc: `cnt` là số khoảng bị xoá, và theo định lý trao đổi áp dụng lặp, tập giữ lại là tối đa ⇒ `cnt` là tối thiểu.

#### Naive

```python
class SolutionNaive:
    def eraseOverlapIntervals(self, intervals: list[list[int]]) -> int:
        """Thu MOI tap con, giu tap ron nhau lon nhat. O(2^n * n log n).
        Chi dung lam oracle voi n rat nho."""
        n = len(intervals)
        best_keep = 0
        for mask in range(1 << n):
            sel = sorted(intervals[i] for i in range(n) if mask >> i & 1)
            if all(sel[i][1] <= sel[i + 1][0] for i in range(len(sel) - 1)):
                best_keep = max(best_keep, len(sel))
        return n - best_keep

print(SolutionNaive().eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]))
print(SolutionNaive().eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]))
print(SolutionNaive().eraseOverlapIntervals([[1, 2], [2, 3]]))
```

In ra `1`, `2`, `0`.

`O(2^n · n log n)` time. Không thể dùng để nộp — nhưng là oracle **hoàn hảo**: nó duyệt đúng định nghĩa bài toán, không giả định gì. Với `n ≤ 12` nó chạy trong mili-giây, vừa đủ cho stress test.

#### Optimized

```python
class Solution:
    def eraseOverlapIntervals(self, intervals: list[list[int]]) -> int:
        if not intervals:
            return 0
        iv = sorted(intervals, key=lambda x: x[1])   # sort theo END, khong phai start
        removed = 0
        end = iv[0][1]
        for s, e in iv[1:]:
            if s >= end:                             # >= vi cham bien khong tinh chong
                end = e                              # giu khoang nay
            else:
                removed += 1                         # xoa khoang HIEN TAI (end lon hon)
        return removed

import random

def naive(intervals: list[list[int]]) -> int:
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        sel = sorted(intervals[i] for i in range(n) if mask >> i & 1)
        if all(sel[i][1] <= sel[i + 1][0] for i in range(len(sel) - 1)):
            best = max(best, len(sel))
    return n - best

random.seed(0)
sol = Solution()
for _ in range(3000):
    case = []
    for _ in range(random.randint(0, 7)):
        s = random.randint(0, 6)
        case.append([s, random.randint(s + 1, 7)])
    if naive([x[:] for x in case]) != sol.eraseOverlapIntervals([x[:] for x in case]):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop voi oracle brute-force tren 3000 case ngau nhien")

print(sol.eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]),
      sol.eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]),
      sol.eraseOverlapIntervals([[1, 2], [2, 3]]))
```

In ra `khop voi oracle brute-force tren 3000 case ngau nhien` rồi `1 2 0`.

**Đánh đổi**: `O(2^n) → O(n log n)`, và bộ nhớ phụ chỉ `O(1)` ngoài bản sort. Cái ta "trả" hoàn toàn là **một chứng minh** — không có cấu trúc dữ liệu nào được thêm vào. Greedy luôn là kiểu tối ưu hoá này: rẻ về tài nguyên, đắt về nghĩa vụ chứng minh. Và vì thế nó nguy hiểm: một greedy sai trông y hệt một greedy đúng. Ở đây `sorted(key=lambda x: x[1])` đổi thành `x[0]` vẫn chạy, vẫn trả số, và sai trên `[[1,100],[2,3],[3,4]]` — hãy tự thử.

### Bài 3 — 253. Meeting Rooms II

#### Requirements

Cho danh sách cuộc họp `[start, end]`, trả về **số phòng ít nhất** cần để tổ chức tất cả mà không xung đột.

Khoảng **nửa mở**: cuộc họp kết thúc lúc 10 và cuộc khác bắt đầu lúc 10 dùng chung được một phòng.

Đáp án bằng đúng **số cuộc họp chồng lấp nhiều nhất tại một thời điểm** (maximum clique của interval graph, mà với interval graph nó bằng chromatic number — đây chính là lý do greedy đạt tối ưu).

Ràng buộc: `1 ≤ n ≤ 10^4`, `0 ≤ start < end ≤ 10^6`.

Edge cases: `n = 0` (trả 0); các cuộc họp rời nhau hoàn toàn (trả 1); tất cả trùng nhau (trả `n`); một cuộc kết thúc đúng lúc cuộc khác bắt đầu (vẫn 1 phòng); nhiều cuộc cùng `start`.

#### Complexity mục tiêu

`n ≤ 10^4` ⇒ `O(n²)` là `10^8`, ~10 giây với Python. Rủi ro. Nhắm `O(n log n)`.

`end ≤ 10^6` nên difference array trên trục thời gian cũng khả thi (`O(n + 10^6)`) — nhưng `10^6` ô cho `10^4` cuộc họp là lãng phí, và cách đó sụp ngay nếu đề đổi sang timestamp Unix. Sweep line trên `2n` sự kiện là lời giải đúng và tổng quát.

#### Idea

Biến mỗi cuộc họp thành hai sự kiện, sort, quét.

> **Invariant**: sau khi xử lý mọi sự kiện tại thời điểm ≤ `t`, `cur` bằng đúng số cuộc họp đang diễn ra tại `t`; `best` là max của `cur` trên mọi thời điểm đã quét.

Tính đúng: giá trị `cur` chỉ thay đổi tại các thời điểm có sự kiện, nên quét qua tập sự kiện là đủ để bắt được cực đại. Và số phòng cần = max số cuộc họp đồng thời, vì (a) rõ ràng cần ít nhất chừng đó phòng, (b) chừng đó phòng là đủ — gán phòng theo thứ tự thời gian, luôn có phòng trống khi số cuộc đang diễn ra chưa vượt max.

Chi tiết quyết định: sort tuple `(time, delta)` với `delta ∈ {+1, -1}`. Khi hai sự kiện cùng thời điểm, `-1 < +1` nên **sự kiện đóng chạy trước** — đúng ngữ nghĩa nửa mở. Nếu đề dùng khoảng đóng thì phải sort theo `(time, -delta)`.

#### Naive

```python
class SolutionNaive:
    def minMeetingRooms(self, intervals: list[list[int]]) -> int:
        """Voi moi thoi diem BAT DAU, dem so cuoc dang dien ra. O(n^2)."""
        if not intervals:
            return 0
        best = 0
        for t, _ in intervals:                   # cuc dai luon dat tai mot diem start
            best = max(best, sum(1 for s, e in intervals if s <= t < e))
        return best

print(SolutionNaive().minMeetingRooms([[0, 30], [5, 10], [15, 20]]))
print(SolutionNaive().minMeetingRooms([[7, 10], [2, 4]]))
print(SolutionNaive().minMeetingRooms([[1, 5], [1, 5], [1, 5]]))
print(SolutionNaive().minMeetingRooms([[1, 10], [10, 20]]))
```

In ra `2`, `1`, `3`, `1`.

`O(n²)` time, `O(1)` space. Nó dựa trên một nhận xét đúng — **cực đại số cuộc đồng thời luôn đạt tại một thời điểm `start` nào đó** (vì `cur` chỉ tăng ở sự kiện start) — nhưng vẫn quét lại toàn bộ danh sách cho mỗi mốc.

#### Optimized

```python
class Solution:
    def minMeetingRooms(self, intervals: list[list[int]]) -> int:
        events: list[tuple[int, int]] = []
        for s, e in intervals:
            events.append((s, +1))               # mot cuoc hop mo ra
            events.append((e, -1))               # mot cuoc hop dong lai
        # (t, -1) < (t, +1): cung thoi diem thi DONG truoc MO -> khoang nua mo
        events.sort()
        cur = best = 0
        for _, delta in events:
            cur += delta
            best = max(best, cur)
        return best


class SolutionHeap:
    """Bien the dung heap: heap chua END time cua cac phong dang ban."""
    def minMeetingRooms(self, intervals: list[list[int]]) -> int:
        import heapq
        if not intervals:
            return 0
        busy: list[int] = []
        for s, e in sorted(intervals):           # sort theo START
            if busy and busy[0] <= s:            # phong ket thuc som nhat da trong
                heapq.heappop(busy)
            heapq.heappush(busy, e)
        return len(busy)                         # so phong dang dung = dap an

import random

def naive(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    return max(sum(1 for s, e in intervals if s <= t < e) for t, _ in intervals)

random.seed(0)
sweep, heap_sol = Solution(), SolutionHeap()
for _ in range(5000):
    case = []
    for _ in range(random.randint(0, 7)):
        s = random.randint(0, 8)
        case.append([s, random.randint(s + 1, 9)])
    exp = naive(case)
    if exp != sweep.minMeetingRooms(case) or exp != heap_sol.minMeetingRooms(case):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("sweep line va heap deu khop voi naive tren 5000 case")

for case in ([[0, 30], [5, 10], [15, 20]], [[7, 10], [2, 4]],
             [[1, 5], [1, 5], [1, 5]], [[1, 10], [10, 20]], []):
    print(case, "->", sweep.minMeetingRooms(case))
```

In ra `sweep line va heap deu khop voi naive tren 5000 case` rồi năm dòng kết quả `2, 1, 3, 1, 0`.

**Đánh đổi**: `O(n)` bộ nhớ cho `2n` sự kiện, đổi lấy `O(n²) → O(n log n)` (chi phí nằm ở sort). So với bản heap: sweep line **chỉ cho biết số phòng**, còn heap **biết luôn cuộc nào ở phòng nào** nếu bạn lưu thêm. Nếu bài chỉ hỏi con số, sweep line đơn giản hơn và ít cấu trúc dữ liệu hơn; nếu bài đòi gán phòng cụ thể (bài 1094 hay các bài scheduling thật), heap là hướng đúng.

## Bài luyện thêm

- **57. Insert Interval** — input **đã sort và rời nhau**; tận dụng invariant đó để giải `O(n)` không cần sort lại: copy các khoảng kết thúc trước `newInterval`, gộp phần chồng lấp bằng `min`/`max`, rồi copy phần còn lại.
- **1094. Car Pooling** — difference array trên trục vị trí `0..1000` (§08): `diff[from] += num`, `diff[to] -= num`, rồi prefix sum và kiểm không bao giờ vượt `capacity`. Vì miền vị trí nhỏ và cố định, cách này `O(n + 1000)` — nhanh hơn sweep line vì không cần sort.

## Bài toán áp dụng

Tìm khung giờ rảnh chung giữa nhiều người — bài toán lõi của mọi công cụ đặt lịch:

```python
def free_slots(busy_per_person: list[list[tuple[int, int]]],
               day_start: int, day_end: int,
               min_len: int) -> list[tuple[int, int]]:
    """Gop lich ban cua moi nguoi, lay phan bu, giu cac khe >= min_len.
    Khoang NUA MO [s, e). Thoi gian tinh bang phut tu 0h."""
    busy = [iv for person in busy_per_person for iv in person]
    if not busy:
        return [(day_start, day_end)] if day_end - day_start >= min_len else []

    merged: list[list[int]] = []
    for s, e in sorted(busy):
        if merged and s <= merged[-1][1]:        # <= : hai khoang cham nhau cung gop
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])

    free, cursor = [], day_start
    for s, e in merged:
        if s - cursor >= min_len:
            free.append((cursor, s))
        cursor = max(cursor, e)
    if day_end - cursor >= min_len:
        free.append((cursor, day_end))
    return free

alice = [(9 * 60, 10 * 60), (12 * 60, 13 * 60)]
bob   = [(9 * 60 + 30, 11 * 60), (15 * 60, 16 * 60)]
carol = [(13 * 60, 14 * 60)]

def hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"

for s, e in free_slots([alice, bob, carol], 9 * 60, 18 * 60, 30):
    print(f"ranh {hhmm(s)} - {hhmm(e)}  ({e - s} phut)")
```

In ra:

```
ranh 11:00 - 12:00  (60 phut)
ranh 14:00 - 15:00  (60 phut)
ranh 16:00 - 18:00  (120 phut)
```

Hai chi tiết đáng học. `cursor = max(cursor, e)` chứ không phải `cursor = e` — thừa vì `merged` đã rời nhau, nhưng nó khiến hàm vẫn đúng nếu ai đó sau này truyền vào danh sách chưa merge. Và bộ lọc `min_len` biến "khe rảnh" thành "khe **dùng được**": một khe 5 phút giữa hai cuộc họp về mặt kỹ thuật là rảnh, về mặt thực tế thì không.

## Use case thực tế

- **Calendar scheduling.** Google Calendar / Outlook "Find a time" chạy đúng thuật toán trên: gộp lịch bận của mọi người, lấy phần bù, lọc theo độ dài tối thiểu và giờ làm việc.
- **Đặt phòng / đặt chỗ.** Kiểm tra xung đột trước khi ghi: khoảng mới có chồng với khoảng nào đã có không. Ở quy mô lớn, CSDL hỗ trợ trực tiếp — PostgreSQL có kiểu `tsrange` và ràng buộc `EXCLUDE USING gist (room WITH =, during WITH &&)`, đẩy toàn bộ việc kiểm xung đột xuống engine với index GiST.
- **Capacity planning / scheduler.** "Cần bao nhiêu worker để chạy hết các job này?" là bài 253 nguyên xi. CPU scheduler và autoscaler dùng cùng phép đếm chồng lấp.
- **Đếm người dùng online đồng thời** từ log session `(login, logout)` — sweep line trên hàng triệu bản ghi. Đây cũng là cách tính "peak concurrent users" cho hoá đơn licensing.
- **Computational geometry**: sweep line là kỹ thuật nền cho bài "tìm mọi cặp đoạn thẳng cắt nhau" (Bentley–Ottmann) và cho tính diện tích hợp của các hình chữ nhật.
- **Khi nào dùng thư viện có sẵn**: với dữ liệu lịch thật, dùng CSDL có kiểu range + index (PostgreSQL range types) thay vì kéo hết về ứng dụng rồi merge. Với phân tích dữ liệu, `pandas.IntervalIndex` và `IntervalIndex.overlaps` làm sẵn phần kiểm chồng lấp. Tự cài khi logic hợp nhất có quy tắc riêng (vd khoảng có trọng số, hoặc gộp có điều kiện).

## Bẫy thường gặp trong Python

- **Nhầm khoảng đóng và nửa mở.** `s <= out[-1][1]` (đóng) vs `s < out[-1][1]` (nửa mở). Sai một dấu `=` là sai lời giải. Viết quy ước vào comment dòng đầu, và **luôn** cho test case hai khoảng chạm nhau đúng biên.
- **Quên `max()` khi gộp.** `out[-1][1] = e` thay vì `max(out[-1][1], e)` sẽ **thu nhỏ** khoảng khi khoảng mới nằm gọn bên trong (`[1,10]` rồi `[2,3]` → `[1,3]`). Đây là bug im lặng, chỉ lộ ra với input lồng nhau.
- **Sort theo `start` cho bài greedy chọn tối đa.** Chạy được, trả số, sai. Bài 435 phải sort theo `end`.
- **Sửa `out[-1]` khi `out[-1]` là tuple.** `tuple` immutable ⇒ `TypeError`. Dùng `list` cho các khoảng đang gộp, hoặc thay cả phần tử.
- **`intervals.sort()` sửa input của người gọi.** Ở LeetCode không sao; trong code thật thì là side effect bất ngờ. `sorted(intervals)` an toàn hơn, trả list mới.
- **`sorted(intervals)` sort theo cả `[start, end]` từ điển.** Với bài merge thì đúng ý; nhưng nếu bạn *nghĩ* mình đang sort chỉ theo start thì tie-break bằng end có thể là bất ngờ. Viết `key=lambda x: x[0]` khi muốn nói rõ ý định.
- **Sự kiện trùng thời điểm sai thứ tự.** `events.sort()` trên tuple `(t, delta)` cho `-1` trước `+1`, đúng cho nửa mở. Với khoảng đóng phải là `(t, -delta)`. Bug này chỉ lộ ra khi có hai khoảng chạm nhau đúng biên — hãy đưa case đó vào test.
- **`max()` trên dãy rỗng.** `max(... for ... in intervals)` với `intervals = []` ném `ValueError`. Kiểm rỗng trước, hoặc `max(..., default=0)`.
- **Dùng float làm mốc thời gian.** `0.1 + 0.2 != 0.3` (§05) khiến so sánh biên sai. Dùng số nguyên (giây, phút, mili-giây) làm đơn vị trục thời gian.
