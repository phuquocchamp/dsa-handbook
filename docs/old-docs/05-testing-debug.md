# 05. Testing & debug cho bài DSA

Test case bạn tự nghĩ ra luôn thiên vị theo cách bạn hiểu đề — nếu hiểu sai, test cũng sai theo. Nếu bỏ qua chương này, bạn sẽ nộp bài "tưởng đúng" rồi ăn Wrong Answer ở edge case ẩn (mảng rỗng, số âm, phần tử trùng, n=1) mà không có cách hệ thống nào tìm ra trước khi submit. Section này chốt ba công cụ: **brute-force oracle**, **random stress test**, và **đo thời gian thực nghiệm**.

> Số đo trong chương chạy trên `Python 3.12.12`, darwin/arm64.

## Lý thuyết

### Vì sao brute-force oracle là công cụ mạnh nhất

Kiểm thử phần mềm thông thường phải viết ra **cặp (input, expected output)**. Với bài DSA bạn có một thứ tốt hơn: một lời giải khác cho cùng bài toán, chậm nhưng chắc chắn đúng vì nó chỉ **duyệt hết mọi khả năng**. Có nó rồi thì bạn không cần biết expected output — chỉ cần sinh input.

Đó chính là bước "naive" trong template `app.py` ở §01. Điểm mấu chốt: **đừng xoá nó sau khi viết xong optimized.** Nó là ground truth vĩnh viễn của bài đó.

Điều kiện để oracle dùng được:

1. **Naive phải đơn giản tới mức khó sai.** Nếu naive phức tạp ngang optimized thì nó chẳng chứng minh được gì — hai bản có thể sai giống nhau.
2. **Naive phải đúng ở mọi edge case**, kể cả input rỗng. Nếu naive crash ở `n=0`, stress test sẽ báo lỗi giả.
3. **Kết quả phải so sánh được.** Bài có nhiều đáp án hợp lệ (vd "trả về *một* palindrome dài nhất", "trả về các bộ ba theo thứ tự bất kỳ") thì không so `==` được — phải so **thuộc tính**: cùng độ dài, cùng tập hợp sau khi chuẩn hoá, kết quả có hợp lệ không.

### Random stress test — thiết kế bộ sinh input mới là phần khó

Sinh input là chỗ dễ làm hỏng cả quy trình. Nguyên tắc: **input phải NHỎ**. Với `n ≤ 8` và giá trị trong `[-5, 5]`, không gian input đủ dày để bug lộ ra sau vài trăm lần thử; với `n = 1000` và giá trị trong `[-10^9, 10^9]` thì mọi mảng sinh ra đều "phần tử phân biệt, không trùng, không đối xứng" — đúng vùng mà bug không nằm.

Ba tham số cần siết:
- **`n` nhỏ**: 0 đến ~8. Nhớ cho phép `n = 0` và `n = 1` nếu đề cho phép.
- **Miền giá trị hẹp**: `[-3, 3]` thay vì `[-10^9, 10^9]`, để **ép phần tử trùng nhau xuất hiện**. Rất nhiều bug chỉ hiện khi có giá trị trùng.
- **`random.seed(...)` cố định** khi báo cáo, để counterexample tái lập được. Bỏ seed khi muốn cào rộng.

Khi tìm được counterexample, bước tiếp theo là **shrink**: rút gọn nó về ví dụ nhỏ nhất vẫn còn sai. Debug trên `[-4]` dễ hơn debug trên mảng 8 phần tử vô cùng.

### Checklist edge case bắt buộc

Chạy qua danh sách này trước khi submit, mỗi bài:

| Loại | Ví dụ | Bug điển hình nó bắt được |
| --- | --- | --- |
| Rỗng | `[]`, `""` | `IndexError` ở `a[0]`, `max()` trên dãy rỗng |
| Một phần tử | `[5]` | vòng lặp `for i in range(1, n)` không chạy lần nào |
| Toàn giống nhau | `[2,2,2,2]` | quên xử lý trùng lặp (3Sum), Quicksort worst-case |
| Đã sort xuôi / ngược | `[1,2,3]` / `[3,2,1]` | invariant two pointers, Quicksort pivot |
| Âm và 0 | `[-1, 0, -5]` | khởi tạo `best = 0` thay vì `best = a[0]` |
| Biên constraint | `n = 10^5`, `2^31 - 1` | TLE, và (ở ngôn ngữ khác) overflow |
| Hai đầu | phần tử đầu / cuối là đáp án | off-by-one ở `range` và điều kiện `while` |

Ba dòng đầu là nơi nằm của phần lớn Wrong Answer.

### Đo thời gian: `timeit` vs `perf_counter`

- **`timeit`**: cho đoạn code **nhỏ, lặp nhiều lần**. Nó tự chạy nhiều vòng và tắt garbage collector, nên ổn định hơn. Dùng khi so hai idiom (`d.get()` vs `defaultdict`).
- **`time.perf_counter()`**: cho một lần chạy **dài**. Đồng hồ độ phân giải cao, đơn điệu tăng. Dùng khi đo lời giải trên `n = 10^5`.

Đừng dùng `time.time()` — nó là wall-clock, có thể nhảy lùi khi NTP chỉnh giờ.

### Kiểm chứng độ phức tạp bằng thực nghiệm

Chạy cùng thuật toán với `n, 2n, 4n` rồi nhìn **tỉ lệ** thời gian:

| Tỉ lệ khi n gấp đôi | Bậc khả dĩ |
| --- | --- |
| ~1x | `O(log n)` |
| ~2x | `O(n)` hoặc `O(n log n)` (n log n chỉ hơn 2x một chút) |
| ~4x | `O(n²)` |
| ~8x | `O(n³)` |

Hai cảnh báo phải nhớ: (1) ở n nhỏ chi phí cố định làm tỉ lệ đo được **thấp hơn** tỉ lệ tiệm cận, nên đừng kết luận vội từ hai điểm; (2) ở thang micro-giây thì nhiễu lớn hơn tín hiệu — đo phải đủ lâu (≥ 10ms mỗi lần) mới có ý nghĩa.

## Ví dụ minh hoạ

### Ví dụ 1 — bộ khung stress test dùng lại được

Hàm `stress` dưới đây là thứ bạn copy vào mọi `app.py`. Nó nhận hai lời giải, một bộ sinh input, và một hàm chuẩn hoá kết quả (cho bài có nhiều đáp án hợp lệ):

```python
import random
from typing import Any, Callable

def stress(
    naive: Callable[..., Any],
    fast: Callable[..., Any],
    gen: Callable[[], tuple],
    iterations: int = 1000,
    normalize: Callable[[Any], Any] = lambda x: x,
    seed: int | None = 0,
) -> tuple | None:
    """Tra ve counterexample dau tien (da shrink tho), hoac None neu khong tim thay."""
    if seed is not None:
        random.seed(seed)
    for _ in range(iterations):
        args = gen()
        exp = normalize(naive(*[list(a) if isinstance(a, list) else a for a in args]))
        got = normalize(fast(*[list(a) if isinstance(a, list) else a for a in args]))
        if exp != got:
            print(f"COUNTEREXAMPLE: args={args}\n  naive={exp}\n  fast ={got}")
            return args
    print(f"OK: {iterations} case ngau nhien, khong lech")
    return None


# --- Ap dung: 26. Remove Duplicates from Sorted Array ---
def naive_dedup(nums: list[int]) -> tuple[int, list[int]]:
    out: list[int] = []
    for x in nums:
        if not out or out[-1] != x:
            out.append(x)
    return len(out), out

def fast_dedup(nums: list[int]) -> tuple[int, list[int]]:
    """Two pointers in-place: nums[:k] la ket qua."""
    if not nums:
        return 0, []
    k = 1
    for r in range(1, len(nums)):
        if nums[r] != nums[k - 1]:
            nums[k] = nums[r]
            k += 1
    return k, nums[:k]

def gen_sorted() -> tuple:
    n = random.randint(0, 8)
    return (sorted(random.randint(-3, 3) for _ in range(n)),)

stress(naive_dedup, fast_dedup, gen_sorted, iterations=2000)
```

In ra `OK: 2000 case ngau nhien, khong lech`.

Chú ý hai chi tiết thiết kế: `list(a)` để mỗi bản nhận **bản sao riêng** (`fast_dedup` sửa in-place — không copy thì bản chạy sau nhận input đã bị biến đổi); và miền giá trị `[-3, 3]` với `n ≤ 8` **cố tình** ép ra rất nhiều phần tử trùng, vì đó là chính bug mà bài này có thể mắc.

### Ví dụ 2 — stress test bắt được bug thật

Đây là một bản 3Sum sai đúng một dòng: nó khử trùng lặp cho phần tử `i` nhưng quên khử cho con trỏ `left` sau khi tìm được một bộ ba.

```python
import random

def naive_3sum(nums: list[int]) -> list[list[int]]:
    """O(n^3) - chac chan dung, dung lam oracle."""
    n = len(nums)
    seen = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    seen.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return sorted(seen)

def buggy_3sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res, n = [], len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append((nums[i], nums[l], nums[r]))
                l += 1          # BUG: khong bo qua cac nums[l] trung nhau
                r -= 1
    return sorted(res)

def gen() -> list[int]:
    return [random.randint(-3, 3) for _ in range(random.randint(0, 8))]

random.seed(42)
for it in range(3000):
    case = gen()
    exp = naive_3sum(list(case))
    got = buggy_3sum(list(case))
    if exp != got:
        print(f"COUNTEREXAMPLE sau {it} vong: {case}")
        print("  naive:", exp)
        print("  buggy:", got)
        # shrink: bo tung phan tu, giu lai neu van con sai
        cur = list(case)
        changed = True
        while changed:
            changed = False
            for i in range(len(cur)):
                cand = cur[:i] + cur[i + 1:]
                if naive_3sum(list(cand)) != buggy_3sum(list(cand)):
                    cur, changed = cand, True
                    break
        print("  sau khi shrink:", cur)
        break
else:
    print("khong tim thay counterexample")
```

Chạy ra:

```
COUNTEREXAMPLE sau 4 vong: [1, -3, 1, -2, 2, 2, 2, 1]
  naive: [(-3, 1, 2), (-2, 1, 1)]
  buggy: [(-3, 1, 2), (-3, 1, 2), (-3, 1, 2), (-2, 1, 1)]
  sau khi shrink: [-3, 1, 2, 2, 1]
```

Hai điều đáng chú ý. Thứ nhất, bug lộ ra ở **vòng thứ 4** — 3000 vòng là quá thừa, nhưng bạn không biết trước điều đó nên cứ để rộng. Thứ hai, **shrink rút từ 8 phần tử xuống `[-3, 1, 2, 2, 1]`** (5 phần tử, sort lại thành `[-3, 1, 1, 2, 2]`) — nhìn vào là hiểu ngay bug: với `i` trỏ vào `-3`, cặp `(1, 2)` được tìm thấy, `l` nhảy sang số `1` thứ hai và `r` lùi về số `2` thứ nhất, ra lại đúng bộ `(-3, 1, 2)`. Vì `l` không nhảy qua các giá trị **trùng nhau**, bộ ba bị đếm lại. Debug trên 5 phần tử mất một phút; debug trên mảng 8 phần tử mất mười phút.

### Ví dụ 3 — đo và suy ra bậc

```python
import random, time
from bisect import bisect_left

def linear_search(a: list[int], x: int) -> bool:
    return x in a                                  # O(n)

def binary_search(a: list[int], x: int) -> bool:
    i = bisect_left(a, x)                          # O(log n)
    return i < len(a) and a[i] == x

def has_dup_quadratic(a: list[int]) -> bool:       # O(n^2)
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] == a[j]:
                return True
    return False

def measure(fn, make_args, sizes: tuple[int, ...], label: str) -> None:
    prev = None
    print(label)
    for n in sizes:
        args = make_args(n)
        t0 = time.perf_counter()
        fn(*args)
        dt = time.perf_counter() - t0
        print(f"   n={n:7d}  {dt:9.5f}s  {'ty le ' + format(dt/prev, '.2f') + 'x' if prev else ''}")
        prev = dt

random.seed(0)
big = sorted(random.sample(range(10**9), 4_000_000))

measure(lambda a: [linear_search(a, -1) for _ in range(20)],
        lambda n: (big[:n],), (250_000, 500_000, 1_000_000), "linear_search x20 (ky vong ~2x)")
measure(lambda a: [binary_search(a, -1) for _ in range(200_000)],
        lambda n: (big[:n],), (250_000, 500_000, 1_000_000), "binary_search x200000 (ky vong ~1x)")
measure(has_dup_quadratic,
        lambda n: ([random.randint(0, 10**9) for _ in range(n)],), (1000, 2000, 4000),
        "has_dup_quadratic (ky vong ~4x)")
```

Kết quả đo:

```
linear_search x20 (ky vong ~2x)
   n= 250000    0.15469s
   n= 500000    0.30637s  ty le 1.98x
   n=1000000    0.63432s  ty le 2.07x
binary_search x200000 (ky vong ~1x)
   n= 250000    0.02326s
   n= 500000    0.02151s  ty le 0.92x
   n=1000000    0.02216s  ty le 1.03x
has_dup_quadratic (ky vong ~4x)
   n=   1000    0.00709s
   n=   2000    0.02806s  ty le 3.96x
   n=   4000    0.11473s  ty le 4.09x
```

Ba chữ ký hoàn toàn khác nhau, đọc được bằng mắt: **~2.0x** (tuyến tính), **~1.0x** (logarit — n gấp 4 lần mà thời gian gần như không đổi; dòng `0.92x` thậm chí *giảm*, đó là nhiễu chứ không phải phép màu), **~4.0x** (bậc hai). Đây là cách tự kiểm chứng phân tích lý thuyết ở §02 mà không cần tin vào chính mình.

Lưu ý phương pháp: mỗi phép đo được lặp đủ nhiều lần (`x20`, `x200000`) để tổng thời gian lên trên 10ms. Một lời gọi `bisect_left` mất ~110 nano-giây; đo một lần duy nhất thì bạn chỉ đang đo nhiễu của đồng hồ.

## Bài luyện thêm

Section này không có bài LeetCode riêng trong outline. Bài tập thực hành: chọn ba bài đã AC, thêm `#%% Stress test` vào mỗi `app.py` với bộ sinh input nhỏ, chạy 2000 vòng. Nếu tìm được counterexample cho một bài đã AC — điều này xảy ra thường xuyên hơn bạn nghĩ — nghĩa là LeetCode test suite không phủ hết, và bạn vừa học được điều gì đó thật.

## Bài toán áp dụng

Kỹ thuật "so hai cài đặt trên input ngẫu nhiên" chính là **property-based testing** và **differential testing** trong công nghiệp:

```python
import random

# Kich ban that: refactor mot ham parse, phai bao dam khong doi hanh vi.
def parse_old(line: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in line.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def parse_new(line: str) -> dict[str, str]:
    return {k.strip(): v.strip()
            for part in line.split(";") if "=" in part
            for k, v in [part.split("=", 1)]}

def gen_line() -> str:
    parts = []
    for _ in range(random.randint(0, 4)):
        parts.append(random.choice(["a=1", "b = 2", "c", "", "d=", "=e", "f=g=h", " "]))
    return ";".join(parts)

random.seed(1)
bad = None
for _ in range(5000):
    line = gen_line()
    if parse_old(line) != parse_new(line):
        bad = line
        break
print("khac biet:", repr(bad) if bad else "khong co tren 5000 input ngau nhien")
```

In ra `khac biet: khong co tren 5000 input ngau nhien`. Đây là hình thức bảo hiểm rẻ nhất cho một refactor: bạn không cần liệt kê hết mọi trường hợp biên của định dạng, chỉ cần sinh chúng ra. Chú ý bộ sinh cố tình chứa các mẩu "xấu" (`""`, `"c"`, `"d="`, `"=e"`, `"f=g=h"`) — bộ sinh chỉ ra `"a=1;b=2"` sẽ không chứng minh được gì cả.

## Use case thực tế

- **Property-based testing**: `hypothesis` (Python) làm đúng việc này ở mức chuyên nghiệp — sinh input, tìm counterexample, rồi **tự shrink** về ví dụ nhỏ nhất. Nếu bạn thấy pattern ở Ví dụ 2 hữu ích, `hypothesis` là phiên bản đóng gói sẵn của nó và nên dùng thay vì tự viết trong production.
- **Differential testing** khi rewrite: chạy hệ thống cũ và mới song song trên traffic thật (shadow traffic), so kết quả. Cùng nguyên lý oracle, khác quy mô.
- **Fuzzing**: `atheris`/AFL sinh input ngẫu nhiên để tìm crash trong parser, decoder, tuần tự hoá. Đây là "stress test" nơi oracle là "không được crash".
- **Khi nào dùng thư viện có sẵn**: trong repo production, dùng `pytest` + `hypothesis` chứ đừng viết vòng lặp stress thủ công. Vòng lặp thủ công trong `app.py` là đúng cho bài LeetCode vì nó phải sống trong một file duy nhất và copy được lên judge.
- **Regression suite**: mỗi counterexample tìm được nên trở thành một test case cố định. Bug đã sửa mà không có test là bug sẽ quay lại.

## Bẫy thường gặp trong Python

- **Quên copy input.** Nếu một trong hai lời giải sửa in-place (`nums.sort()`, gán `nums[i]`), bản chạy sau nhận dữ liệu đã hỏng và so sánh vô nghĩa — thường biểu hiện thành "sai một cách kỳ lạ, chạy lại thì đúng". Luôn `list(case)`.
- **So sánh `==` cho bài nhiều đáp án.** 3Sum trả về các bộ ba theo thứ tự bất kỳ → so `sorted(list_of_tuples)`. "Trả về một palindrome dài nhất" → so `len(...)` rồi kiểm tính hợp lệ, không so chuỗi.
- **So sánh float bằng `==`.** `0.1 + 0.2 != 0.3`. Dùng `math.isclose(a, b, rel_tol=1e-9)`.
- **Miền giá trị sinh quá rộng.** `random.randint(-10**9, 10**9)` gần như không bao giờ sinh phần tử trùng, nên mọi bug liên quan tới trùng lặp sẽ không lộ ra. Dùng miền hẹp.
- **Quên `n = 0`.** Bộ sinh `random.randint(1, 8)` bỏ luôn mảng rỗng — đúng cái edge case hay hỏng nhất.
- **`random.seed` đặt sai chỗ.** Đặt trong vòng lặp thì mọi vòng sinh ra cùng một input. Đặt trước vòng lặp.
- **Dùng `time.time()` để đo.** Wall-clock có thể nhảy lùi. Dùng `time.perf_counter()`.
- **Đo lần chạy đầu tiên.** Lần đầu còn phải warm-up: import module, cache lạnh. Với đoạn code nhỏ hãy để `timeit` lo (nó lặp và bỏ nhiễu giúp bạn).
- **`assert` bị tắt bởi `-O`.** Chạy Python với cờ `-O` sẽ vô hiệu hoá mọi `assert`. Đừng đặt logic thật bên trong `assert` trong code production; trong `app.py` luyện tập thì hoàn toàn ổn.
- **`print` debug trong vòng lặp nóng.** I/O rất chậm và có thể tự nó gây TLE. Xoá hết `print` trước khi submit — hoặc đưa chúng vào `#%% Debugging`, tách khỏi vùng `#%% Optimized` sẽ copy lên judge.
