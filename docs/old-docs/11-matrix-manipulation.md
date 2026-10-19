# 11. Matrix manipulation: rotate & spiral

Ma trận trong Python là `list[list[int]]` — không phải mảng 2D liền khối, mà là một list chứa con trỏ tới các list hàng. Điều đó khiến vài thao tác rẻ bất ngờ (`zip(*m)` transpose, `row.reverse()`) và vài thao tác nguy hiểm bất ngờ (`[[0]*m]*n`). Section này chốt ba pattern: xoay tại chỗ bằng transpose + reverse, duyệt xoắn ốc bằng bốn biên co dần, và mẹo dùng chính ma trận làm bộ nhớ đánh dấu để đạt `O(1)` space.

## Lý thuyết

### Xoay 90° = transpose rồi reverse từng hàng

Với ma trận vuông `n × n`, xoay 90° **theo chiều kim đồng hồ** đưa `m[r][c]` tới vị trí `[c][n-1-r]`. Phân tích thành hai phép đơn giản:

1. **Transpose**: `m[r][c] ↔ m[c][r]` — lật qua đường chéo chính.
2. **Reverse từng hàng**: `m[r]` đảo ngược.

Kiểm tra: sau transpose, phần tử ở `(r, c)` là `m[c][r]` gốc. Sau reverse hàng, vị trí `(r, c)` chứa cái vốn ở `(r, n-1-c)` sau transpose, tức `m[n-1-c][r]` gốc. Đặt `r' = n-1-c, c' = r` thì `m[r'][c']` chuyển tới `(c', n-1-r')` — đúng công thức xoay thuận chiều kim đồng hồ. ∎

> **Invariant của bước transpose**: vòng lặp trong chạy `c` từ `r+1` (không phải từ `0`), nên mỗi cặp `(r, c)` được hoán đổi **đúng một lần**. Nếu chạy `c` từ `0`, mỗi cặp bị đổi hai lần và ma trận trở lại như cũ — bug im lặng kinh điển.

Xoay **ngược** chiều kim đồng hồ: reverse từng hàng **trước** rồi transpose, hoặc transpose rồi reverse thứ tự các hàng.

Bản không in-place trong Python là một dòng: `[list(r) for r in zip(*m[::-1])]`. `m[::-1]` đảo thứ tự hàng, `zip(*...)` transpose. Nó tốn `O(n²)` bộ nhớ nhưng đọc như một công thức toán.

### Spiral: bốn biên co dần

Giữ bốn biên `top`, `bottom`, `left`, `right`. Mỗi vòng thực hiện bốn lượt quét và co biên tương ứng:

```
1. quet TRAI -> PHAI  tren hang `top`      roi top    += 1
2. quet TREN -> DUOI  tren cot `right`     roi right  -= 1
3. quet PHAI -> TRAI  tren hang `bottom`   roi bottom -= 1
4. quet DUOI -> TREN  tren cot `left`      roi left   += 1
```

> **Invariant**: vùng `[top..bottom] × [left..right]` là phần **chưa được duyệt**, và mọi ô ngoài vùng đó đã được ghi vào kết quả **đúng một lần**, theo đúng thứ tự xoắn ốc.

Vòng lặp chạy khi `top <= bottom and left <= right`.

Cạm bẫy nằm ở bước 3 và 4. Với ma trận **một hàng** (`top == bottom`), bước 1 đã quét hết hàng đó và tăng `top`; nếu bước 3 vẫn chạy, nó quét lại hàng đó lần nữa. Vì thế bước 3 cần điều kiện `if top <= bottom` **kiểm tra lại sau khi `top` đã tăng**, và bước 4 cần `if left <= right` sau khi `right` đã giảm. Đây là chỗ 90% cài đặt sai lần đầu, và nó chỉ sai với ma trận `1 × k` hoặc `k × 1` — đúng loại edge case mà test tự nghĩ hay bỏ qua.

### Dùng chính ma trận làm bộ nhớ đánh dấu

Bài 73. Set Matrix Zeroes cần biết "hàng nào, cột nào chứa số 0" trước khi ghi. Cách hiển nhiên là hai `set` — `O(R + C)` bộ nhớ. Để đạt `O(1)`, dùng **hàng 0 và cột 0 của chính ma trận** làm hai mảng cờ.

Xung đột: ô `m[0][0]` phải đại diện cho **cả** hàng 0 lẫn cột 0 — một ô không mang được hai bit. Giải bằng cách tách riêng một biến boolean cho một trong hai (thường là cột 0), rồi xử lý hàng 0 / cột 0 **sau cùng**.

> **Invariant giai đoạn 1**: sau khi quét vùng `[1..R-1] × [1..C-1]`, `m[r][0] == 0` ⟺ hàng `r` (r ≥ 1) cần bị xoá; `m[0][c] == 0` ⟺ cột `c` (c ≥ 1) cần bị xoá.

Thứ tự ba giai đoạn là bắt buộc: (1) đọc và ghi cờ, (2) áp cờ cho vùng trong, (3) áp cho hàng 0 và cột 0. Nếu làm giai đoạn 3 trước giai đoạn 2, cờ bị xoá mất.

| Thao tác | Time | Auxiliary space |
| --- | --- | --- |
| Rotate in-place (transpose + reverse) | `O(n²)` | `O(1)` |
| `zip(*m[::-1])` | `O(n²)` | `O(n²)` |
| Spiral traversal | `O(R·C)` | `O(1)` ngoài output |
| Set zeroes với hai `set` | `O(R·C)` | `O(R + C)` |
| Set zeroes dùng hàng/cột đầu | `O(R·C)` | `O(1)` |
| Search 2D Matrix II (loại từ góc) | `O(R + C)` | `O(1)` |

Dòng cuối là two pointers trên 2D: bắt đầu từ **góc trên-phải**, nếu giá trị lớn hơn target thì bỏ cả cột (đi trái), nhỏ hơn thì bỏ cả hàng (đi xuống). Mỗi bước loại vĩnh viễn một hàng hoặc một cột — cùng hình dạng invariant với §06.

## Bài tập chi tiết

### Bài 1 — 48. Rotate Image

#### Requirements

Cho ma trận **vuông** `n × n`. Xoay 90° **theo chiều kim đồng hồ**, **tại chỗ** — đề cấm cấp phát ma trận thứ hai.

Ràng buộc: `1 ≤ n ≤ 20`, `-1000 ≤ matrix[i][j] ≤ 1000`.

Edge cases: `n = 1` (không đổi); `n = 2` (một chu kỳ 4 phần tử); `n` lẻ (ô giữa đứng yên); giá trị âm và giá trị trùng nhau (không ảnh hưởng logic nhưng làm test khó đọc hơn).

#### Complexity mục tiêu

`n ≤ 20` ⇒ chỉ 400 ô, mọi thứ đều pass. **Ràng buộc n không quyết định gì ở bài này** — như bài 75 ở §09, chính đề bài mới đặt yêu cầu: `O(1)` bộ nhớ phụ.

`O(n²)` thời gian là cận dưới hiển nhiên: mỗi ô phải di chuyển, nên phải chạm vào cả `n²` ô.

#### Idea

Hai bước, mỗi bước là một phép đối xứng đơn giản đã chứng minh ở mục Lý thuyết:

> **Bước 1 — transpose.** Với `r` từ `0` đến `n-1`, `c` từ **`r+1`** đến `n-1`: đổi chỗ `m[r][c]` và `m[c][r]`.
>
> **Invariant**: sau khi xử lý hàng `r`, mọi cặp `(i, j)` với `i ≤ r` đã được hoán đổi đúng một lần. Điều kiện `c > r` bảo đảm chỉ duyệt **tam giác trên**, nên không cặp nào bị đổi hai lần.

> **Bước 2 — reverse từng hàng.** `m[r].reverse()` cho mọi `r`, `O(n)` mỗi hàng.

Hợp thành: `m[r][c] → m[c][r] → m[c][n-1-r]`, đúng công thức xoay thuận chiều kim đồng hồ.

Tại sao không xoay trực tiếp theo chu kỳ 4 phần tử? Cũng được và cũng `O(1)` space, nhưng chỉ số của bốn ô trong chu kỳ (`m[r][c]`, `m[n-1-c][r]`, `m[n-1-r][n-1-c]`, `m[c][n-1-r]`) rất dễ viết sai, còn transpose + reverse thì mỗi bước tự nó hiển nhiên đúng.

#### Naive

```python
class SolutionNaive:
    def rotate(self, matrix: list[list[int]]) -> None:
        """Dung ma tran phu roi copy nguoc lai. O(n^2) space - VI PHAM de bai,
        nhung la oracle hoan hao vi no viet thang tu cong thuc xoay."""
        n = len(matrix)
        rotated = [[matrix[n - 1 - c][r] for c in range(n)] for r in range(n)]
        for r in range(n):
            matrix[r][:] = rotated[r]            # ghi de tai cho de giu tham chieu

for case in ([[1, 2], [3, 4]],
             [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
             [[5]]):
    m = [row[:] for row in case]
    SolutionNaive().rotate(m)
    print(case, "->", m)
```

In ra ví dụ `[[1, 2, 3], [4, 5, 6], [7, 8, 9]] -> [[7, 4, 1], [8, 5, 2], [9, 6, 3]]`.

`O(n²)` time, `O(n²)` space. Nó vi phạm ràng buộc của đề — nhưng chính vì viết thẳng từ công thức `new[r][c] = old[n-1-c][r]` nên nó khó sai, và đó là điều ta cần ở oracle.

Chú ý `matrix[r][:] = rotated[r]` chứ không phải `matrix[r] = rotated[r]`: dạng thứ hai thay **con trỏ hàng** trong list ngoài, còn dạng thứ nhất ghi đè **nội dung** hàng cũ. Ở LeetCode cả hai đều được vì `matrix` là list ngoài cũng bị sửa; nhưng nếu ai đó giữ tham chiếu tới một hàng cụ thể thì hai cách cho kết quả khác nhau.

#### Optimized

```python
class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        n = len(matrix)
        # Buoc 1: transpose. c chay tu r+1 -> moi cap doi cho DUNG MOT LAN.
        for r in range(n):
            for c in range(r + 1, n):
                matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
        # Buoc 2: reverse tung hang
        for row in matrix:
            row.reverse()

import random

def naive(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    return [[matrix[n - 1 - c][r] for c in range(n)] for r in range(n)]

random.seed(0)
sol = Solution()
for _ in range(3000):
    n = random.randint(1, 5)
    case = [[random.randint(0, 9) for _ in range(n)] for _ in range(n)]
    got = [row[:] for row in case]
    sol.rotate(got)
    if got != naive(case):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop tren 3000 ma tran ngau nhien")

for case in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[5]]):
    m = [row[:] for row in case]
    sol.rotate(m)
    print(case, "->", m)

# Ban khong in-place, mot dong - dung khi khong bi cam cap phat
m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print("zip(*m[::-1]) =", [list(r) for r in zip(*m[::-1])])
```

In ra `khop tren 3000 ma tran ngau nhien`, ba dòng biến đổi, rồi `zip(*m[::-1]) = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]`.

**Đánh đổi**: `O(n²)` → `O(1)` bộ nhớ phụ, cùng `O(n²)` thời gian. Cái ta trả là **tính hiển nhiên**: bản naive đọc phát hiểu, bản in-place cần biết rằng "transpose ∘ reverse-hàng = xoay 90°". Đổi lại, `row.reverse()` chạy bằng C nên bản in-place thực tế còn **nhanh hơn** trên đồng hồ, chứ không chỉ tiết kiệm bộ nhớ.

Một cảnh báo: `zip(*m[::-1])` chỉ dùng được khi bạn **được phép** tạo ma trận mới. Nó không phải lời giải cho bài 48 (đề cấm), nhưng là lời giải đúng cho 95% tình huống ngoài đời.

### Bài 2 — 54. Spiral Matrix

#### Requirements

Cho ma trận `R × C` (**không** nhất thiết vuông), trả về danh sách mọi phần tử theo thứ tự xoắn ốc: từ góc trên-trái đi sang phải, xuống, sang trái, lên, rồi vòng vào trong.

Ràng buộc: `1 ≤ R, C ≤ 10`, `-100 ≤ matrix[i][j] ≤ 100`.

Edge cases — đây là phần khó thật sự của bài: ma trận **một hàng** (`1 × C`); ma trận **một cột** (`R × 1`); ma trận `1 × 1`; `R` và `C` chênh lệch lớn (`2 × 7`); `R` hoặc `C` lẻ (vòng trong cùng suy biến thành một hàng hoặc một cột).

#### Complexity mục tiêu

`R, C ≤ 10` ⇒ tối đa 100 ô. Không có áp lực hiệu năng gì cả.

`O(R·C)` là cận dưới (phải xuất mọi phần tử). Mục tiêu thật ở bài này là `O(1)` bộ nhớ phụ **và**, quan trọng hơn, **đúng ở mọi hình dạng ma trận**. Đây là bài kiểm tra kỷ luật edge case chứ không phải kiểm tra thuật toán.

#### Idea

Bốn biên `top, bottom, left, right`, co dần vào trong.

> **Invariant**: vùng chữ nhật `[top..bottom] × [left..right]` chứa **chính xác** các ô chưa được xuất; mọi ô ngoài vùng đã được xuất đúng một lần, theo đúng thứ tự xoắn ốc.

Mỗi vòng lặp (khi `top <= bottom and left <= right`):

1. Quét hàng `top` từ `left` tới `right`, rồi `top += 1`. Invariant giữ: hàng đó vừa rời khỏi vùng.
2. Quét cột `right` từ `top` tới `bottom` (dùng `top` **đã tăng**), rồi `right -= 1`.
3. **`if top <= bottom`**: quét hàng `bottom` từ `right` xuống `left`, rồi `bottom -= 1`.
4. **`if left <= right`**: quét cột `left` từ `bottom` lên `top`, rồi `left += 1`.

Hai điều kiện `if` ở bước 3, 4 là bắt buộc. Với ma trận `1 × 3`: bước 1 xuất cả ba ô và `top` thành 1 > `bottom` = 0. Bước 2 không chạy (range rỗng). Nếu bước 3 không có `if`, nó sẽ quét lại hàng `bottom = 0` — **xuất trùng**. Tương tự bước 4 với ma trận `3 × 1`.

Kết thúc: mỗi vòng làm vùng chữ nhật thu hẹp theo cả hai chiều ⇒ dừng; khi dừng vùng rỗng ⇒ đã xuất hết.

#### Naive

```python
class SolutionNaive:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        """Lay hang dau, xoay phan con lai 90 do NGUOC kim dong ho, lap lai.
        O(R*C) tong cong nhung cap phat ma tran moi moi vong -> O(R*C) space."""
        m = [row[:] for row in matrix]
        out: list[int] = []
        while m and m[0]:
            out += m.pop(0)                      # lay hang tren cung
            m = [list(r) for r in zip(*m)][::-1]  # xoay nguoc kim dong ho
        return out

print(SolutionNaive().spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
print(SolutionNaive().spiralOrder([[1, 2, 3, 4]]))
print(SolutionNaive().spiralOrder([[1], [2], [3]]))
print(SolutionNaive().spiralOrder([[7]]))
```

In ra `[1, 2, 3, 6, 9, 8, 7, 4, 5]`, `[1, 2, 3, 4]`, `[1, 2, 3]`, `[7]`.

`O(R·C)` time tổng cộng nhưng với hằng số lớn, `O(R·C)` space vì mỗi vòng dựng lại ma trận. **Rất khó sai** — nó không có biên nào để off-by-one, chỉ có "lấy hàng đầu, xoay, lặp". Chính vì thế nó là oracle lý tưởng cho bản bốn-biên.

`m.pop(0)` là `O(R)` (§03) nhưng ở đây `R ≤ 10` nên không đáng bận tâm; trong lời giải thật thì đây là red flag.

#### Optimized

```python
class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix or not matrix[0]:
            return []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        out: list[int] = []
        while top <= bottom and left <= right:
            for c in range(left, right + 1):         # 1. trai -> phai
                out.append(matrix[top][c])
            top += 1
            for r in range(top, bottom + 1):         # 2. tren -> duoi
                out.append(matrix[r][right])
            right -= 1
            if top <= bottom:                        # 3. BAT BUOC kiem lai
                for c in range(right, left - 1, -1): # phai -> trai
                    out.append(matrix[bottom][c])
                bottom -= 1
            if left <= right:                        # 4. BAT BUOC kiem lai
                for r in range(bottom, top - 1, -1): # duoi -> tren
                    out.append(matrix[r][left])
                left += 1
        return out

import random

def naive(matrix: list[list[int]]) -> list[int]:
    m = [row[:] for row in matrix]
    out: list[int] = []
    while m and m[0]:
        out += m.pop(0)
        m = [list(r) for r in zip(*m)][::-1]
    return out

random.seed(0)
sol = Solution()
for _ in range(3000):
    R, C = random.randint(1, 5), random.randint(1, 5)
    case = [[random.randint(0, 9) for _ in range(C)] for _ in range(R)]
    if naive(case) != sol.spiralOrder(case):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop tren 3000 ma tran ngau nhien (ke ca 1xC va Rx1)")

print(sol.spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
print(sol.spiralOrder([[1, 2, 3, 4]]), sol.spiralOrder([[1], [2], [3]]),
      sol.spiralOrder([[7]]))
```

In ra `khop tren 3000 ma tran ngau nhien (ke ca 1xC va Rx1)`, rồi `[1, 2, 3, 6, 9, 8, 7, 4, 5]` và `[1, 2, 3, 4] [1, 2, 3] [7]`.

**Đánh đổi**: `O(R·C)` bộ nhớ phụ → `O(1)` (ngoài output), và bỏ được `pop(0)` cùng việc dựng lại ma trận. Cái giá là **bốn điều kiện biên phải đúng tuyệt đối**. Bộ sinh ngẫu nhiên ở trên cố tình cho `R, C` từ 1 đến 5 để chắc chắn phủ cả `1 × C`, `R × 1` và `1 × 1` — bỏ `1` ra khỏi miền sinh là bỏ mất đúng những case mà bản này có thể sai.

### Bài 3 — 73. Set Matrix Zeroes

#### Requirements

Cho ma trận `R × C`. Nếu một ô bằng `0`, đặt **toàn bộ hàng và toàn bộ cột** của nó về `0`. Sửa **tại chỗ**.

Bẫy đọc đề: phải quyết định dựa trên các số 0 **ban đầu**. Nếu vừa quét vừa ghi, các số 0 mới tạo ra sẽ kích hoạt thêm hàng/cột khác và lan ra cả ma trận.

Đề hỏi follow-up: `O(R + C)` space thì dễ, còn `O(1)` thì sao?

Ràng buộc: `1 ≤ R, C ≤ 200`, `-2^31 ≤ matrix[i][j] ≤ 2^31 - 1`.

Edge cases: không có số 0 nào; toàn số 0; số 0 nằm ở hàng 0 hoặc cột 0 (chính là chỗ mẹo `O(1)` xung đột); `m[0][0] == 0`; ma trận `1 × 1`; `1 × C` và `R × 1`.

#### Complexity mục tiêu

`R, C ≤ 200` ⇒ `4·10^4` ô. `O(R·C)` là hiển nhiên và đủ. Áp lực nằm ở **bộ nhớ**, do câu follow-up.

Ba mức: `O(R·C)` (copy cả ma trận) → `O(R + C)` (hai `set`) → `O(1)` (dùng hàng 0 / cột 0 làm cờ). Trong phỏng vấn, trình bày bản `O(R + C)` trước — nó đúng và rõ — rồi mới nén xuống.

#### Idea

Dùng **hàng 0** làm mảng cờ cho các cột, **cột 0** làm mảng cờ cho các hàng. Vấn đề: ô `m[0][0]` phải mang hai bit. Tách một biến riêng cho cột 0.

> **Giai đoạn 0**: ghi nhớ `first_row_zero` (hàng 0 gốc có số 0 không) và `first_col_zero` (cột 0 gốc có số 0 không) vào hai biến boolean. Phải làm **trước tiên**, vì các giai đoạn sau sẽ ghi đè lên hàng 0 và cột 0.
>
> **Giai đoạn 1** — quét vùng trong `[1..R-1] × [1..C-1]`; gặp `m[r][c] == 0` thì đặt `m[r][0] = 0` và `m[0][c] = 0`.
>
> **Invariant sau giai đoạn 1**: với `r ≥ 1`, `m[r][0] == 0` ⟺ hàng `r` cần xoá; với `c ≥ 1`, `m[0][c] == 0` ⟺ cột `c` cần xoá.
>
> **Giai đoạn 2** — quét lại vùng trong, đặt `m[r][c] = 0` nếu `m[r][0] == 0` hoặc `m[0][c] == 0`. Chỉ đọc cờ, không ghi cờ ⇒ invariant giữ nguyên suốt giai đoạn.
>
> **Giai đoạn 3** — nếu `first_row_zero` thì xoá cả hàng 0; nếu `first_col_zero` thì xoá cả cột 0.

Thứ tự 0 → 1 → 2 → 3 là bắt buộc. Làm giai đoạn 3 trước giai đoạn 2 sẽ xoá sạch cờ; đọc cờ trong lúc còn đang ghi cờ (gộp giai đoạn 1 và 2) sẽ lan số 0 ra toàn ma trận.

#### Naive

```python
class SolutionNaive:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        """Hai set ghi nho hang/cot can xoa. O(R + C) space."""
        R, C = len(matrix), len(matrix[0])
        rows = {r for r in range(R) for c in range(C) if matrix[r][c] == 0}
        cols = {c for r in range(R) for c in range(C) if matrix[r][c] == 0}
        for r in range(R):
            for c in range(C):
                if r in rows or c in cols:
                    matrix[r][c] = 0

for case in ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],
             [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],
             [[1, 2], [3, 4]],
             [[0]]):
    m = [row[:] for row in case]
    SolutionNaive().setZeroes(m)
    print(case, "->", m)
```

In ra ví dụ `[[1, 1, 1], [1, 0, 1], [1, 1, 1]] -> [[1, 0, 1], [0, 0, 0], [1, 0, 1]]`.

`O(R·C)` time, `O(R + C)` space. Không "chậm" — nó cùng bậc thời gian với bản tối ưu. Điểm yếu duy nhất là bộ nhớ, và đó là thứ đề bài nhắm tới. `r in rows` là `O(1)` vì `rows` là `set` chứ không phải `list` (§03).

#### Optimized

```python
class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        R, C = len(matrix), len(matrix[0])
        # Giai doan 0: ghi nho trang thai GOC cua hang 0 va cot 0
        first_row_zero = any(matrix[0][c] == 0 for c in range(C))
        first_col_zero = any(matrix[r][0] == 0 for r in range(R))

        # Giai doan 1: dung hang 0 / cot 0 lam co cho vung trong
        for r in range(1, R):
            for c in range(1, C):
                if matrix[r][c] == 0:
                    matrix[r][0] = 0
                    matrix[0][c] = 0

        # Giai doan 2: ap co cho vung trong (chi DOC co)
        for r in range(1, R):
            for c in range(1, C):
                if matrix[r][0] == 0 or matrix[0][c] == 0:
                    matrix[r][c] = 0

        # Giai doan 3: xu ly hang 0 / cot 0 SAU CUNG
        if first_row_zero:
            for c in range(C):
                matrix[0][c] = 0
        if first_col_zero:
            for r in range(R):
                matrix[r][0] = 0

import random

def naive(matrix: list[list[int]]) -> list[list[int]]:
    m = [row[:] for row in matrix]
    R, C = len(m), len(m[0])
    rows = {r for r in range(R) for c in range(C) if m[r][c] == 0}
    cols = {c for r in range(R) for c in range(C) if m[r][c] == 0}
    for r in range(R):
        for c in range(C):
            if r in rows or c in cols:
                m[r][c] = 0
    return m

random.seed(0)
sol = Solution()
for _ in range(5000):
    R, C = random.randint(1, 5), random.randint(1, 5)
    # nhieu so 0 hon binh thuong -> ep cac truong hop bien lo ra
    case = [[random.choice([0, 1, 1, 2, 3]) for _ in range(C)] for _ in range(R)]
    got = [row[:] for row in case]
    sol.setZeroes(got)
    if got != naive(case):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop tren 5000 ma tran ngau nhien")

for case in ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],
             [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],
             [[1, 2], [3, 4]], [[0]]):
    m = [row[:] for row in case]
    sol.setZeroes(m)
    print(case, "->", m)
```

In ra `khop tren 5000 ma tran ngau nhien` rồi bốn dòng biến đổi.

**Đánh đổi**: `O(R + C)` → `O(1)` bộ nhớ, cùng `O(R·C)` thời gian (thực ra quét hai lượt thay vì một, nên hằng số cao hơn một chút). Cái ta trả là **rất nhiều**: bốn giai đoạn phải đúng thứ tự, hai biến boolean phải đọc trước khi ghi bất cứ thứ gì, và ma trận trở thành "vừa là dữ liệu vừa là metadata" — kiểu code mà sáu tháng sau bạn đọc lại sẽ không hiểu nếu không có comment.

Đây là ví dụ tốt để hỏi ngược: `O(R + C)` với `R, C ≤ 200` là **400 số nguyên**, khoảng 11 KB. Tiết kiệm 11 KB có đáng với chừng đó rủi ro không? Ngoài đời: không. Trong phỏng vấn: đáng, vì câu hỏi thật là "bạn có nghĩ ra được không". Biết phân biệt hai bối cảnh đó cũng là một kỹ năng.

Chú ý bộ sinh ngẫu nhiên dùng `random.choice([0, 1, 1, 2, 3])` — xác suất số 0 là 20%, cao hơn nhiều so với thực tế. Đó là cố ý: bug của bài này nằm ở hàng 0 / cột 0, và với ma trận ít số 0 thì các case đó gần như không bao giờ xuất hiện. Đây đúng là nguyên tắc "miền giá trị hẹp" của §05.

## Bài luyện thêm

- **59. Spiral Matrix II** — đảo chiều bài 54: thay vì *đọc* theo xoắn ốc, *ghi* các số `1..n²` theo xoắn ốc vào ma trận `n × n`. Cùng khung bốn biên; vì ma trận vuông nên hai điều kiện `if` bớt hiểm hơn, nhưng vẫn nên giữ.
- **240. Search a 2D Matrix II** — mỗi hàng tăng dần, mỗi cột tăng dần. Bắt đầu từ **góc trên-phải**: lớn hơn target thì đi trái (loại cả cột), nhỏ hơn thì đi xuống (loại cả hàng). `O(R + C)`, cùng invariant "mỗi bước loại vĩnh viễn một chiều" với two pointers ở §06.

## Bài toán áp dụng

Xoay và lật một game board (Tetris, sudoku, game xếp hình), cùng phép kiểm tra tính đối xứng:

```python
def rotate_cw(g: list[list[int]]) -> list[list[int]]:
    """Xoay 90 do thuan kim dong ho, khong in-place. Chay cho ca ma tran khong vuong."""
    return [list(r) for r in zip(*g[::-1])]

def rotate_ccw(g: list[list[int]]) -> list[list[int]]:
    """Nguoc kim dong ho: transpose truoc, roi dao thu tu HANG."""
    return [list(r) for r in zip(*g)][::-1]

# Manh Tetris hinh chu S, 2x3
piece = [[0, 1, 1],
         [1, 1, 0]]

g = piece
for step in range(1, 5):
    g = rotate_cw(g)
    print(f"xoay {step * 90:3d} do: {g}")
print("xoay 4 lan ve dung ban dau:", g == piece)
print("rotate_ccw dung nghich dao cua rotate_cw:", rotate_ccw(rotate_cw(piece)) == piece)

# Kiem tra ma tran co doi xung qua phep xoay 180 do khong
def is_180_symmetric(g: list[list[int]]) -> bool:
    return rotate_cw(rotate_cw(g)) == g

print("[[1,0],[0,1]] doi xung 180:", is_180_symmetric([[1, 0], [0, 1]]))
print("[[1,0],[0,0]] doi xung 180:", is_180_symmetric([[1, 0], [0, 0]]))
```

In ra bốn bước xoay, `xoay 4 lan ve dung ban dau: True`, `rotate_ccw dung nghich dao cua rotate_cw: True`, rồi `True` và `False`.

Ba điều đáng chú ý: `zip(*g[::-1])` chạy cho cả ma trận **không vuông** (`2×3` thành `3×2`) trong khi bản in-place transpose+reverse **chỉ chạy cho ma trận vuông** — đó là hạn chế thật của bài 48, không phải chi tiết vụn. `rotate_ccw` khác `rotate_cw` ở chỗ đảo hàng **sau** thay vì **trước**. Và "xoay bốn lần về chính nó" là một **property test** miễn phí — dạng bất biến toán học mà `hypothesis` (§05) được sinh ra để kiểm.

## Use case thực tế

- **Xử lý ảnh.** Xoay một image buffer là đúng bài 48, chỉ khác mỗi "phần tử" là 3–4 byte RGBA. Thư viện đồ hoạ trước thời GPU cài chính xác transpose + reverse, và tối ưu thêm bằng cách xoay theo **tile** (khối 8×8 hoặc 16×16) để vừa cache — một chi tiết mà `list[list[int]]` của Python không cho bạn kiểm soát.
- **JPEG encoding** duyệt ma trận hệ số DCT `8×8` theo thứ tự **zig-zag** — biến thể đường chéo của spiral. Mục đích: gom các hệ số tần số cao (thường bằng 0) về cuối dãy, để run-length encoding nén được tốt.
- **EXIF orientation.** Ảnh chụp từ điện thoại thường lưu nguyên bản buffer kèm một cờ orientation; viewer phải xoay lúc hiển thị. Đó là lý do ảnh "bị xoay" khi mở bằng phần mềm không đọc EXIF.
- **Game 2D**: xoay mảnh Tetris, xoay bàn cờ để tái dùng một hàm đánh giá cho cả bốn hướng, sinh các biến thể của một puzzle.
- **Convolution / kernel** trong CNN và trong filter ảnh cổ điển là duyệt cửa sổ trên ma trận — cùng họ chỉ số 2D, nhưng ở đó câu trả lời đúng gần như luôn là thư viện.
- **Khi nào dùng thư viện có sẵn**: `numpy.rot90`, `numpy.transpose`, `PIL.Image.rotate` cho ảnh thật. Chúng thao tác trên buffer liền khối, hỗ trợ view không copy (`numpy` transpose chỉ đổi stride, `O(1)`!), và nhanh hơn `list[list]` hàng trăm lần. Cài tay chỉ để hiểu, hoặc khi ở trên judge không có numpy.

## Bẫy thường gặp trong Python

- **`[[0] * C] * R`** tạo `R` tham chiếu tới **cùng một** list. `grid[0][0] = 1` sẽ đổi mọi hàng. Dùng `[[0] * C for _ in range(R)]`. Đây là bug ma trận số một trong Python (§04).
- **Transpose với `c` chạy từ `0`.** Mỗi cặp bị hoán đổi hai lần ⇒ ma trận không đổi. `for c in range(r + 1, n)`.
- **Quên hai `if` ở bước 3 và 4 của spiral.** Chỉ sai với ma trận `1 × C` và `R × 1` — nhớ đưa hai hình dạng đó vào bộ sinh stress test.
- **`m[r] = new_row` vs `m[r][:] = new_row`.** Cái đầu thay con trỏ hàng trong list ngoài; cái sau ghi đè nội dung hàng. Nếu ai đó đang giữ tham chiếu tới hàng cũ, hai cách cho kết quả khác nhau.
- **`zip(*m)` trả về iterator của `tuple`, không phải `list`.** `list(zip(*m))` cho `[(1, 4), (2, 5)]` — nếu bạn cần gán được thì phải `[list(r) for r in zip(*m)]`.
- **`zip(*m)` cắt theo hàng ngắn nhất.** Với ma trận "răng cưa" (các hàng khác độ dài), nó âm thầm bỏ phần thừa thay vì báo lỗi. Dùng `strict=True` nếu muốn nổ (§04).
- **`row.reverse()` trả về `None`.** `m = [row.reverse() for row in m]` biến ma trận thành list toàn `None`. `reverse()` sửa tại chỗ; `reversed(row)` trả iterator; `row[::-1]` trả list mới.
- **Copy nông của ma trận.** `new = matrix[:]` copy list ngoài nhưng **dùng chung các hàng** — sửa `new[0][0]` là sửa luôn `matrix[0][0]`. Dùng `[row[:] for row in matrix]`.
- **Nhầm `matrix[r][c]` với `matrix[c][r]`.** Không có gì trong Python ngăn bạn; với ma trận vuông thì không crash, chỉ ra sai. Đặt tên biến `r`/`c` (không phải `i`/`j`) giúp giảm hẳn loại lỗi này.
- **Ma trận không vuông trong bài xoay in-place.** Transpose tại chỗ chỉ định nghĩa được cho ma trận vuông — với `R != C` bạn buộc phải cấp phát mới. Đề bài 48 nói "n × n" là có lý do.
