# 13. Stack

Stack là cấu trúc đơn giản nhất trong Part 2 — `list.append`/`list.pop` là xong — nhưng lại là nền của hai kỹ thuật rất khác nhau: **monotonic stack** biến các bài "phần tử lớn hơn kế tiếp" từ O(n²) xuống O(n), và **khử đệ quy** cứu bạn khỏi `RecursionError` khi DFS sâu. Section này đi qua invariant của cả hai, cộng thêm parsing biểu thức — bài toán mà stack sinh ra để giải.

## Lý thuyết

### `list` làm stack: vì sao đúng đầu, sai đuôi kia

CPython cài `list` bằng mảng con trỏ liên tục kèm dư dung lượng (over-allocation). Do đó:

- `append` / `pop()` (cuối): **O(1) amortized** — chỉ ghi/xoá ô cuối, thỉnh thoảng realloc.
- `insert(0, x)` / `pop(0)` (đầu): **O(n)** — phải `memmove` toàn bộ n phần tử.

Nên `list` là stack hoàn hảo và là queue tệ hại. Đây là lý do §14 tồn tại.

### Monotonic stack — invariant

Ý tưởng chung: ta duyệt mảng một lượt và giữ trong stack các **index chưa được "trả lời"**.

> **Invariant (next greater)**: giá trị tại các index trong stack giảm dần (không tăng) từ đáy lên đỉnh. Mọi index còn nằm trong stack là index chưa tìm thấy phần tử lớn hơn ở bên phải.

Tại sao invariant này đúng và đủ? Khi gặp `x` mới, mọi index `j` ở đỉnh stack có `nums[j] < x` đều **vừa tìm được đáp án là `x`** — và đó chắc chắn là đáp án đầu tiên bên phải, vì nếu tồn tại phần tử lớn hơn `nums[j]` nằm giữa `j` và `i`, thì `j` đã bị pop trước rồi. Pop chúng ra, gán đáp án, rồi push `i`. Việc pop giữ nguyên tính giảm dần vì ta chỉ dừng khi gặp phần tử ≥ `x`.

Chi phí: mỗi index được push đúng một lần và pop tối đa một lần → tổng số thao tác ≤ 2n → **O(n) amortized**, dù vòng `while` bên trong nhìn như O(n²).

Bốn biến thể chỉ khác nhau ở hai chỗ — chiều duyệt và chiều bất đẳng thức:

| Muốn tìm | Duyệt | Điều kiện pop |
|---|---|---|
| next greater | trái → phải | `nums[stack[-1]] < x` |
| next smaller | trái → phải | `nums[stack[-1]] > x` |
| previous greater | trái → phải, đọc `stack[-1]` **trước** khi push | `nums[stack[-1]] <= x` |
| previous smaller | trái → phải, đọc `stack[-1]` **trước** khi push | `nums[stack[-1]] >= x` |

Mẹo nhớ: "next" thì **gán đáp án lúc pop**; "previous" thì **đọc đáp án từ đỉnh stack ngay trước khi push**.

### Stack cho parsing: ngữ cảnh lồng nhau

Ngoặc mở nghĩa là "tạm dừng ngữ cảnh hiện tại, bắt đầu ngữ cảnh mới"; ngoặc đóng nghĩa là "kết thúc ngữ cảnh này, hợp nhất kết quả vào ngữ cảnh bị tạm dừng". Cấu trúc dữ liệu duy nhất khớp với ngữ nghĩa đó là stack — vì các ngữ cảnh luôn kết thúc theo thứ tự ngược với thứ tự bắt đầu (LIFO là *định nghĩa* của "lồng nhau").

### Bảng độ phức tạp

| Bài toán | Naive | Với stack |
|---|---|---|
| Next greater element | O(n²) | **O(n)** |
| Largest rectangle in histogram | O(n²) | **O(n)** |
| Basic calculator (có ngoặc) | O(n²) nếu thu gọn lặp | **O(n)** |
| `getMin()` trên stack | O(n) | **O(1)** (đổi lấy O(n) space) |
| DFS trên cây n node | O(n) time / O(h) stack **của CPython** | O(n) time / O(h) stack **của bạn** |

## Cài đặt trong `cores/python/`

Đề xuất đường dẫn: `cores/python/stack/min_stack.py`

```python
class MinStack:
    """Stack hỗ trợ getMin() trong O(1).

    Invariant: _mins[i] là giá trị nhỏ nhất trong _data[0..i]. Vì vậy đỉnh của
    _mins luôn là min của toàn stack, và pop hai stack song song giữ nguyên
    invariant đó.
    """

    def __init__(self) -> None:
        self._data: list[int] = []
        self._mins: list[int] = []

    def push(self, val: int) -> None:
        self._data.append(val)
        self._mins.append(val if not self._mins else min(val, self._mins[-1]))

    def pop(self) -> int:
        self._mins.pop()
        return self._data.pop()

    def top(self) -> int:
        return self._data[-1]

    def getMin(self) -> int:
        return self._mins[-1]

    def __len__(self) -> int:
        return len(self._data)
```

Điểm cần hiểu: ta **không** giữ "min hiện tại" trong một biến đơn, vì khi pop chính phần tử min đó ra thì không có cách nào khôi phục min cũ mà không quét lại O(n). Giữ cả lịch sử min song song với lịch sử dữ liệu là cách duy nhất để pop cũng O(1). Đó là đổi O(n) bộ nhớ lấy O(1) thời gian.

Đề xuất đường dẫn: `cores/python/stack/monotonic.py`

```python
def next_greater(nums: list[int]) -> list[int]:
    """res[i] = giá trị đầu tiên bên PHẢI i lớn hơn nums[i], -1 nếu không có.

    Invariant: stack chứa các index có giá trị GIẢM dần từ đáy lên đỉnh; mọi
    index còn trong stack là index chưa tìm được phần tử lớn hơn.
    """
    n = len(nums)
    res = [-1] * n
    stack: list[int] = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x
        stack.append(i)
    return res


def previous_smaller(nums: list[int]) -> list[int]:
    """res[i] = index của phần tử đầu tiên bên TRÁI i nhỏ hơn nums[i], -1 nếu không có."""
    n = len(nums)
    res = [-1] * n
    stack: list[int] = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] >= x:
            stack.pop()
        res[i] = stack[-1] if stack else -1
        stack.append(i)
    return res
```

Đã chạy: `next_greater([2,1,2,4,3])` → `[4, 2, 4, -1, -1]`; `previous_smaller([2,1,5,6,2,3])` → `[-1, -1, 1, 2, 1, 4]`.

Đề xuất đường dẫn: `cores/python/stack/iterative_dfs.py` — khử đệ quy bằng kỹ thuật **two-pass push**.

```python
def postorder_iterative(root) -> list[int]:
    """Two-pass push: mỗi node được đẩy vào stack 2 lần.

    Invariant: cờ visited=False nghĩa là "chưa mở rộng con"; visited=True nghĩa
    là "cả hai con đã được xử lý xong, tới lượt mình".
    """
    out: list[int] = []
    stack: list[tuple[object, bool]] = [(root, False)] if root else []
    while stack:
        node, visited = stack.pop()
        if visited:
            out.append(node.val)
            continue
        stack.append((node, True))            # đẩy lại, lần này đã "mở"
        if node.right:
            stack.append((node.right, False))
        if node.left:
            stack.append((node.left, False))
    return out
```

Cờ boolean chính là "program counter" của call frame: `False` = "chưa gọi đệ quy con", `True` = "đã quay về từ hai lời gọi con, thực thi phần thân sau chúng". Đổi thứ tự ba lệnh `append` là đổi giữa preorder/inorder/postorder.

Kiểm chứng đã chạy trên cây lệch hoàn toàn 50 000 node: bản đệ quy ném `RecursionError`, bản iterative trả về đủ 50 000 giá trị. Trên cây nhỏ, hai bản cho kết quả trùng khớp.

## Bài tập chi tiết

### Bài 1 — 739. Daily Temperatures

#### Requirements

Cho mảng `temperatures`, trả về mảng `res` với `res[i]` = số ngày phải chờ kể từ ngày `i` để gặp ngày ấm hơn; nếu không có ngày nào ấm hơn thì `res[i] = 0`. Ràng buộc: `1 ≤ n ≤ 10⁵`, `30 ≤ temperatures[i] ≤ 100`.

Edge cases: mảng giảm dần hoàn toàn (kết quả toàn 0); mọi phần tử bằng nhau (cũng toàn 0 — "ấm hơn" là **nghiêm ngặt**, đây là chỗ dễ nhầm `<` với `<=`); n = 1; giá trị lặp lại nhiều.

Chú ý miền giá trị chỉ 71 giá trị phân biệt — gợi ý rằng có cả lời giải kiểu counting, nhưng monotonic stack tổng quát hơn.

#### Complexity mục tiêu

n = 10⁵ → O(n²) là 10¹⁰ phép, TLE ngay cả với C++, khỏi bàn CPython. Bảng constraint ở §02 nói n ≤ 10⁵–10⁶ cần **O(n log n) hoặc O(n)**. Ở đây có lời giải O(n) sạch nên nhắm thẳng vào đó.

#### Idea

Đây đúng là bài "next greater element" nhưng trả về **khoảng cách index** thay vì giá trị.

> **Invariant**: stack chứa các index chưa có đáp án, và nhiệt độ tại chúng không tăng từ đáy lên đỉnh.

Tính đúng đắn: khi duyệt tới ngày `i` với nhiệt độ `t`, mọi index `j` ở đỉnh stack thoả `temperatures[j] < t` được trả lời `res[j] = i - j`. Đó là ngày ấm hơn **đầu tiên** vì bất kỳ ngày `m` nào với `j < m < i` mà `temperatures[m] > temperatures[j]` đã khiến `j` bị pop ở bước `m` rồi — mâu thuẫn với việc `j` vẫn còn trong stack. Index nào còn lại trong stack lúc kết thúc thì không có đáp án, và ta đã khởi tạo sẵn `res` toàn 0.

#### Naive

```python
class SolutionNaive739:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        n = len(temperatures)
        res = [0] * n
        for i in range(n):
            for j in range(i + 1, n):
                if temperatures[j] > temperatures[i]:
                    res[i] = j - i
                    break
        return res
```

O(n²) worst case — cụ thể là khi mảng giảm dần hoàn toàn: mỗi `i` quét hết đuôi mà không tìm được gì. Với n = 10⁵ đó là 5·10⁹ vòng lặp Python thuần, tính bằng giờ.

#### Optimized

```python
class Solution739:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        res = [0] * len(temperatures)
        stack: list[int] = []          # index, nhiệt độ giảm dần từ đáy lên đỉnh
        for i, t in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < t:
                j = stack.pop()
                res[j] = i - j
            stack.append(i)
        return res
```

O(n) time, O(n) space. Đánh đổi: dùng O(n) bộ nhớ phụ và một invariant phải chứng minh mới tin, đổi lấy việc mỗi cặp (i, j) chỉ được xét đúng một lần thay vì mọi cặp. Trực giác chi phí: cái vòng `while` trông đáng sợ nhưng tổng số lần pop trên toàn bộ chương trình bị chặn bởi tổng số lần push, tức là n.

Đã stress test 3000 lần trên mảng ngẫu nhiên độ dài 0–8 với giá trị 30–40 (cố tình hẹp để ép nhiều giá trị trùng), naive khớp optimized. `dailyTemperatures([73,74,75,71,69,72,76,73])` → `[1,1,4,2,1,1,0,0]`.

### Bài 2 — 84. Largest Rectangle in Histogram

#### Requirements

Cho `heights` là chiều cao các cột rộng 1 đơn vị đứng cạnh nhau. Tìm diện tích hình chữ nhật lớn nhất nằm hoàn toàn trong histogram. `1 ≤ n ≤ 10⁵`, `0 ≤ heights[i] ≤ 10⁴`.

Edge cases: có cột cao 0 (cắt histogram thành hai phần độc lập); mọi cột bằng nhau (đáp án là `h * n`); mảng tăng dần; mảng giảm dần; n = 1.

#### Complexity mục tiêu

n = 10⁵ nên O(n²) (10¹⁰) bị loại. Cần **O(n)**.

#### Idea

Chìa khoá là đổi cách liệt kê. Thay vì duyệt mọi cặp `(trái, phải)`, ta duyệt mọi **cột `i` và coi nó là cột thấp nhất** của hình chữ nhật. Mỗi hình chữ nhật tối ưu chắc chắn chạm đỉnh của ít nhất một cột (nếu không, ta nâng nó lên được), nên phép liệt kê này không bỏ sót nghiệm nào.

Với cột `i` làm chiều cao, hình chữ nhật rộng nhất kéo dài từ **phần tử nhỏ hơn gần nhất bên trái** đến **phần tử nhỏ hơn gần nhất bên phải**. Đó chính là hai bài monotonic stack, và ta làm được cả hai trong một lượt duy nhất:

> **Invariant**: chiều cao tại các index trong stack **tăng** dần từ đáy lên đỉnh.

Khi gặp `h` mới tại vị trí `i` và pop index `p` ra (vì `heights[p] >= h`), ta biết ngay hai biên: biên phải là `i` (vì `h` là phần tử nhỏ hơn đầu tiên bên phải của `p`), biên trái là `stack[-1]` sau khi pop (phần tử nhỏ hơn gần nhất bên trái, do invariant tăng dần), hoặc `-1` nếu stack rỗng. Bề rộng là `i - left - 1`.

Thêm một sentinel `0` vào cuối để vòng lặp tự xả sạch stack, khỏi viết đoạn dọn dẹp riêng.

#### Naive

```python
class SolutionNaive84:
    def largestRectangleArea(self, heights: list[int]) -> int:
        best = 0
        n = len(heights)
        for i in range(n):
            lo = heights[i]
            for j in range(i, n):
                lo = min(lo, heights[j])
                best = max(best, lo * (j - i + 1))
        return best
```

O(n²) — đã tối ưu hơn bản O(n³) ngây thơ nhất (duy trì `lo` tăng dần thay vì `min(heights[i:j+1])` mỗi lần). Vẫn 5·10⁹ vòng ở n = 10⁵. Nó chậm vì liệt kê mọi đoạn `[i, j]`, trong khi số đoạn có thể là nghiệm tối ưu chỉ là O(n).

#### Optimized

```python
class Solution84:
    def largestRectangleArea(self, heights: list[int]) -> int:
        stack: list[int] = []       # index với chiều cao TĂNG dần
        best = 0
        for i, h in enumerate(heights + [0]):   # sentinel 0 để xả sạch stack
            while stack and heights[stack[-1]] >= h:
                height = heights[stack.pop()]
                left = stack[-1] if stack else -1
                width = i - left - 1
                best = max(best, height * width)
            stack.append(i)
        return best
```

O(n) time, O(n) space. Đánh đổi: mất hoàn toàn tính hiển nhiên — không đọc code này mà hiểu ngay được, phải nắm invariant "stack tăng dần ⇒ `stack[-1]` sau pop là phần tử nhỏ hơn gần nhất bên trái". Đổi lại là O(n).

Hai chi tiết dễ sai: (1) dùng `>=` chứ không `>` khi pop — với chiều cao trùng nhau, cái bị pop sớm sẽ tính bề rộng hụt, nhưng cái pop sau cùng sẽ tính đủ, nên kết quả `max` vẫn đúng; nếu dùng `>` thì cột trùng không bao giờ được pop bởi nhau và logic biên trái sai. (2) `heights + [0]` tạo bản sao O(n) — chấp nhận được, hoặc thay bằng `chain(heights, (0,))` nếu tiếc bộ nhớ.

Đã stress test 4000 lần với mảng độ dài 0–8, giá trị 0–6 (hẹp để ép trùng lặp và cột cao 0), naive khớp optimized. `largestRectangleArea([2,1,5,6,2,3])` → `10`.

### Bài 3 — 224. Basic Calculator

#### Requirements

Tính giá trị một biểu thức chuỗi chứa: chữ số, `+`, `-`, `(`, `)`, dấu cách. **Không có `*` và `/`**. Không được dùng `eval`. `1 ≤ len(s) ≤ 3·10⁵`. Kết quả và mọi giá trị trung gian nằm trong 32-bit signed.

Edge cases: dấu cách rải rác bất kỳ đâu (`" 2-1 + 2 "`); dấu trừ **một ngôi** ở đầu biểu thức hoặc ngay sau `(` — ví dụ `"-(3+4)+10"` hay `"(-2+3)"`; số nhiều chữ số; ngoặc lồng nhiều tầng; biểu thức chỉ có một số.

#### Complexity mục tiêu

`len(s)` = 3·10⁵ → cần **O(n)** một lượt. Lời giải "thu gọn dần cặp ngoặc trong cùng" là O(n²) vì mỗi lần thu gọn phải tạo lại chuỗi mới (string immutable, xem §03) — với 10⁵ cặp ngoặc lồng nhau là 3·10¹⁰ byte bị copy.

#### Idea

Chỉ có `+` và `-` nghĩa là biểu thức thực chất là **tổng của các số có dấu**. Cái duy nhất ngoặc làm được là **lật dấu của cả một cụm**.

Duy trì ba biến: `total` (tổng đã chốt của ngữ cảnh hiện tại), `sign` (dấu áp cho số sắp tới), `num` (số đang gom chữ số).

> **Invariant**: tại mọi thời điểm, `total` là giá trị đúng của phần biểu thức thuộc ngữ cảnh hiện tại đã đọc xong, và `sign * num` là số hạng đang dở.

Khi gặp `(`: đẩy `total` và `sign` vào stack rồi reset về `0, +1` — ta bắt đầu tính cụm bên trong như một biểu thức độc lập. Khi gặp `)`: chốt `total` của cụm, rồi hợp nhất ngược bằng `total = total * sign_cũ + total_cũ`. Thứ tự pop phải ngược thứ tự push (`sign` trước, rồi `total`).

Điều làm lời giải này đúng cả với dấu trừ một ngôi: `num` khởi tạo bằng 0, nên `"-("` được đọc là `0 - (...)`, hoàn toàn hợp lệ mà không cần một dòng đặc biệt nào.

#### Naive

```python
import re


class SolutionNaive224:
    def _eval_flat(self, s: str) -> int:
        # Chỉ chứa số và + -
        tokens = re.findall(r"\d+|[+-]", s)
        total, sign = 0, 1
        for t in tokens:
            if t == "+":
                sign = 1
            elif t == "-":
                sign = -1
            else:
                total += sign * int(t)
                sign = 1
        return total

    def calculate(self, s: str) -> int:
        s = s.replace(" ", "")
        while "(" in s:
            close = s.index(")")
            open_ = s.rfind("(", 0, close)
            inner = self._eval_flat(s[open_ + 1:close])
            s = s[:open_] + ("+" if inner >= 0 else "") + str(inner) + s[close + 1:]
            s = s.replace("+-", "-").replace("--", "+").replace("-+", "-").replace("++", "+")
            if s.startswith("+"):
                s = s[1:]
        return self._eval_flat(s)
```

O(n²) và **rất dễ sai**: phải tự tay xử lý việc nối `+` với `-` thành `-`, `-` với `-` thành `+`. Đây là lý do nó chỉ nên tồn tại làm oracle: nó đúng trên input nhỏ đủ để đối chiếu, nhưng logic thay chuỗi là mảnh đất màu mỡ cho bug. Chậm vì mỗi vòng tạo một chuỗi mới O(n).

#### Optimized

```python
class Solution224:
    def calculate(self, s: str) -> int:
        total, sign, num = 0, 1, 0
        stack: list[int] = []       # lưu (total, sign) của ngữ cảnh bên ngoài
        for ch in s:
            if ch.isdigit():
                num = num * 10 + int(ch)      # gộp số nhiều chữ số
            elif ch in "+-":
                total += sign * num
                num = 0
                sign = 1 if ch == "+" else -1
            elif ch == "(":
                stack.append(total)
                stack.append(sign)
                total, sign = 0, 1            # bắt đầu ngữ cảnh mới
            elif ch == ")":
                total += sign * num
                num = 0
                total *= stack.pop()          # dấu đứng trước '('
                total += stack.pop()          # tổng đã tích luỹ trước '('
                sign = 1
        return total + sign * num
```

O(n) time, O(d) space với `d` là độ sâu ngoặc. Đánh đổi: lời giải này **chỉ đúng cho `+`/`-`** — nó khai thác đặc thù rằng hai toán tử này cùng độ ưu tiên và giao hoán theo dấu. Thêm `*` vào (bài 227) là phải viết lại theo hướng khác. Đó là cái giá của việc bỏ parser tổng quát để lấy một vòng `for` 20 dòng.

Nhánh `ch == " "` không cần viết: dấu cách rơi qua tất cả `elif` và bị bỏ qua tự nhiên.

Đã stress test 2000 lần với biểu thức ngoặc lồng sinh ngẫu nhiên (đối chiếu cả naive và optimized với `eval` của Python làm oracle thứ ba). Ví dụ: `"(1+(4+5+2)-3)+(6+8)"` → 23; `" 2-1 + 2 "` → 3; `"-(3+4)+10"` → 3.

## Bài luyện thêm

- **20. Valid Parentheses** — push ngoặc mở, khi gặp ngoặc đóng thì pop và kiểm tra khớp loại; nhớ kiểm tra stack rỗng lúc cuối.
- **155. Min Stack** — chính lớp `MinStack` ở phần Cài đặt: giữ stack min song song, mỗi ô là min của tiền tố tương ứng.
- **496. Next Greater Element I** — chạy `next_greater` trên `nums2` để dựng `dict[value] -> answer`, rồi tra cho từng phần tử `nums1`; bài này được đảm bảo giá trị phân biệt nên dùng value làm key được.

## Bài toán áp dụng

**Viết một calculator hỗ trợ đủ `( ) + - * /`** bằng hai bước cổ điển, mỗi bước một stack:

1. **Shunting Yard** (Dijkstra) chuyển infix → postfix (RPN). Stack chỉ chứa toán tử và `(`, với invariant: trong cùng một cặp ngoặc, độ ưu tiên của các toán tử trong stack không giảm từ đáy lên đỉnh. Khi gặp toán tử mới, xả hết các toán tử ở đỉnh có ưu tiên **≥** rồi mới push (dùng `>=` cho toán tử kết hợp trái, `>` cho kết hợp phải như `^`).
2. **Evaluate postfix** bằng một stack toán hạng: gặp số thì push, gặp toán tử thì pop hai, tính, push lại.

```python
PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def to_postfix(tokens: list[str]) -> list[str]:
    """Infix -> postfix (RPN). Stack chỉ chứa toán tử và '('."""
    out: list[str] = []
    ops: list[str] = []
    for t in tokens:
        if t not in PREC and t not in "()":
            out.append(t)
        elif t == "(":
            ops.append(t)
        elif t == ")":
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()                            # bỏ '('
        else:
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())
            ops.append(t)
    while ops:
        out.append(ops.pop())
    return out


def eval_postfix(rpn: list[str]) -> float:
    st: list[float] = []
    for t in rpn:
        if t in PREC:
            b, a = st.pop(), st.pop()
            # KHÔNG dùng dict literal làm switch ở đây: dict literal tính TẤT CẢ
            # các value trước khi index, nên a / b vẫn chạy khi t == '+'.
            if t == "+":
                st.append(a + b)
            elif t == "-":
                st.append(a - b)
            elif t == "*":
                st.append(a * b)
            else:
                st.append(a / b)
        else:
            st.append(float(t))
    return st[0]


def tokenize(expr: str) -> list[str]:
    import re
    return re.findall(r"\d+\.?\d*|[()+\-*/]", expr)
```

Đã chạy: `to_postfix(tokenize("3 + 4 * (2 - 1) / 2"))` → `['3','4','2','1','-','*','2','/','+']`, evaluate ra `5.0`, khớp với `eval`. Đã stress test 500 biểu thức ngoặc ngẫu nhiên.

Chú ý `b, a = st.pop(), st.pop()` — thứ tự đảo là bắt buộc, vì toán hạng phải bị pop ra sau. Viết `a, b = st.pop(), st.pop()` là bug im lặng với `+`/`*` và bug lộ với `-`//`/`.

## Use case thực tế

**Call stack của chính CPython.** Mỗi lời gọi hàm Python đẩy một frame object lên stack của interpreter; `RecursionError` là kết quả của việc stack đó chạm giới hạn `sys.getrecursionlimit()`. Traceback bạn đọc mỗi ngày chính là nội dung stack đó in ngược ra.

**Compiler và runtime.** Biến local, tham số, địa chỉ trở về đều nằm trên stack frame — đó là lý do biến local "biến mất" khi hàm return và là lý do stack overflow tồn tại như một lớp lỗ hổng bảo mật. `ast` module của Python và mọi parser recursive-descent đều là stack ẩn (dùng call stack) hoặc stack tường minh.

**Undo/redo và back/forward của trình duyệt.** Back là stack, forward là stack thứ hai; điều hướng tới trang mới sẽ xoá sạch stack forward — đúng ngữ nghĩa "nhánh tương lai không còn hợp lệ".

**Khi nào câu trả lời đúng là "dùng thư viện có sẵn"**: nếu bạn đang viết Shunting Yard cho code production, hãy hỏi lại vì sao không dùng `ast.parse` + `ast.literal_eval` (biểu thức hằng an toàn), hoặc một parser generator (`lark`, `pyparsing`) cho ngữ pháp thật. Tự viết parser chỉ đáng khi ngữ pháp cực nhỏ và cố định. Và với monotonic stack thì ngược lại: **không có** thư viện nào làm thay, đây là kỹ thuật bạn phải tự viết mỗi lần.

## Bẫy thường gặp trong Python

**`list.pop(0)` là O(n).** Đo trên máy này với 10⁵ phần tử: `pop()` mất 0.0014 s, `pop(0)` mất **0.5943 s** — chậm 420 lần. Stack thì `pop()` luôn đúng; nhưng nếu bạn copy-paste code stack thành code queue mà đổi thành `pop(0)`, BFS của bạn vừa trở thành O(n²). Dùng `collections.deque` (§14).

**Quên kiểm tra stack rỗng.** `stack[-1]` trên list rỗng ném `IndexError`. Trong monotonic stack, điều kiện `while` **phải** bắt đầu bằng `while stack and ...` — Python đánh giá `and` theo short-circuit nên viết đúng thứ tự là an toàn. Trong bài 84, `left = stack[-1] if stack else -1` là cùng một bẫy, và giá trị `-1` không phải tuỳ tiện: nó khiến `width = i - (-1) - 1 = i`, đúng nghĩa "kéo dài tới tận đầu mảng".

**Dict literal làm switch tính hết mọi nhánh.** Lỗi này đã xảy ra thật khi viết `eval_postfix` cho chương này:

```text
st.append({"+": a + b, "-": a - b, "*": a * b, "/": a / b}[t])
# ZeroDivisionError ngay cả khi t == "+", vì a / b được tính TRƯỚC khi index
```

Dict literal là một biểu thức: mọi value được tính xong rồi mới dựng dict rồi mới `[t]`. Muốn lười biếng thì dùng `if/elif`, `match`, hoặc `operator.add`/`operator.truediv` (lưu **hàm**, không lưu kết quả).

**`heights + [0]` trong vòng lặp là bẫy tiềm ẩn.** Ở đây chỉ tạo một bản sao duy nhất nên vô hại, nhưng nếu bạn đặt phép nối list vào trong vòng lặp thì mỗi vòng là O(n) — cùng họ với bẫy `s += char` ở §03.

**Đệ quy DFS chết ở n lớn.** Đã đo: postorder đệ quy trên cây lệch 50 000 node ném `RecursionError`; bản iterative dùng stack tường minh chạy bình thường. Quy tắc: cây/đồ thị có thể lệch với n ≥ 10⁴ thì viết iterative ngay từ đầu, đừng đợi judge báo lỗi.
