# 06. Two pointers

Two pointers là kỹ thuật biến một vòng lặp kép `O(n²)` thành một lần quét `O(n)`, bằng cách để hai chỉ số di chuyển có kiểm soát trên dữ liệu **có tính đơn điệu** — thường là mảng đã sắp xếp. Điều khiến nó đúng không phải là "hai con trỏ đi tới", mà là một **invariant** cho phép loại bỏ vĩnh viễn cả một vùng không gian tìm kiếm ở mỗi bước. Section này tập trung vào chính lập luận loại bỏ đó.

## Lý thuyết

### Hai hình dạng

**1. Đối chiều (opposite direction).** `left = 0`, `right = n-1`, tiến vào giữa. Điều kiện dừng `left < right`. Mỗi bước dịch **đúng một** con trỏ, nên tổng số bước là `n`.

**2. Cùng chiều (same direction).** `slow` và `fast` cùng đi từ trái sang; `fast` quét, `slow` đánh dấu ranh giới của phần kết quả. Đây là dạng dùng cho `remove duplicates`, `move zeroes`, và là hình dạng gốc của sliding window (§07).

Trong cả hai, độ phức tạp là `O(n)` vì **mỗi con trỏ chỉ đi một chiều và không quay lại** — tổng số lần dịch bị chặn bởi `n` (đối chiều) hoặc `2n` (cùng chiều).

| Dạng | Điều kiện áp dụng | Time | Auxiliary space |
| --- | --- | --- | --- |
| Đối chiều | dữ liệu sorted, hoặc hàm mục tiêu đơn điệu theo mỗi đầu | `O(n)` sau sort | `O(1)` |
| Cùng chiều | cần lọc/nén tại chỗ, hoặc window | `O(n)` | `O(1)` |
| Fix 1 + two pointers | bài k-sum | `O(n^(k-1))` | `O(1)` ngoài sort |

### Invariant tổng quát của dạng đối chiều

Đây là khuôn lập luận dùng lại được cho mọi bài đối chiều:

> **Invariant**: mọi cặp `(i, j)` nằm *ngoài* khoảng `[left, right]` hiện tại đều đã được chứng minh là **không thể tốt hơn** đáp án tốt nhất đã ghi nhận.

Chứng minh tính đúng gồm ba mảnh:
1. **Khởi tạo**: lúc `left = 0, right = n-1`, tập bị loại là rỗng — invariant đúng tầm thường.
2. **Bảo toàn**: khi dịch một con trỏ, phải chứng minh *mọi* cặp chứa vị trí vừa bị bỏ đều không thể tốt hơn. Đây là bước duy nhất khó, và khác nhau ở từng bài.
3. **Kết thúc**: khi `left >= right`, không còn cặp nào chưa xét mà chưa bị loại. Kết hợp với invariant ⇒ đáp án đã ghi nhận là tối ưu.

Nếu bạn không chứng minh được bước 2 cho một bài cụ thể thì two pointers **không** áp dụng được cho bài đó, dù code có nhìn hợp lý.

### Tại sao bắt buộc phải sorted (ở dạng đối chiều)

Với bài "tìm cặp có tổng = target": nếu `nums[l] + nums[r] < target`, ta muốn tăng tổng. Trên mảng sorted, mọi phần tử ở bên trái `r` đều ≤ `nums[r]`, nên **mọi cặp `(l, j)` với `j < r` đều có tổng ≤ tổng hiện tại < target** ⇒ toàn bộ hàng `l` bị loại, an toàn tăng `l`. Chính tính đơn điệu này là thứ cho phép loại `O(n)` cặp trong `O(1)` thời gian. Trên mảng không sorted, câu "mọi phần tử bên trái `r` đều nhỏ hơn" là sai, và lập luận sụp đổ.

### Xử lý trùng lặp trong k-sum

Bài 15. 3Sum yêu cầu **các bộ ba phân biệt**. Có hai chỗ phải bỏ qua giá trị trùng, và quên chỗ nào cũng ra kết quả trùng (§05 đã bắt được đúng bug này bằng stress test):

- Ở vòng ngoài: `if i > 0 and nums[i] == nums[i-1]: continue`.
- Sau khi *tìm được* một bộ ba: dịch `l` qua hết các `nums[l]` bằng nhau **và** `r` qua hết các `nums[r]` bằng nhau.

## Bài tập chi tiết

### Bài 1 — 167. Two Sum II - Input Array Is Sorted

#### Requirements

Cho `numbers` là mảng số nguyên **đã sắp xếp tăng dần** và một số `target`. Tìm hai chỉ số khác nhau sao cho tổng hai phần tử đúng bằng `target`. Trả về **chỉ số đánh từ 1**, dạng `[index1, index2]` với `index1 < index2`.

Đề bảo đảm **tồn tại đúng một lời giải**, và yêu cầu dùng **`O(1)` bộ nhớ phụ** — điều này loại thẳng lời giải hash map (dù hash map là lời giải chuẩn cho bài 1. Two Sum không sorted).

Ràng buộc: `2 ≤ n ≤ 3·10^4`, `-1000 ≤ numbers[i] ≤ 1000`, `-1000 ≤ target ≤ 1000`.

Edge cases: `n = 2` (đáp án luôn là `[1, 2]`); phần tử trùng nhau (`[3, 3]`, target `6`); giá trị âm; hai phần tử của đáp án nằm cạnh nhau ở đầu hoặc cuối mảng.

#### Complexity mục tiêu

`n ≤ 3·10^4` thì `O(n²)` là `9·10^8` phép tính — với CPython (~10^7 thao tác/giây, §03) là khoảng 90 giây. TLE chắc chắn. Cần `O(n)` hoặc `O(n log n)`.

Ràng buộc `O(1)` bộ nhớ phụ trong đề còn loại nốt cả hash map `O(n)` space. Còn lại: `O(n)` time, `O(1)` space — chính là chữ ký của two pointers đối chiều. Đề đã tự nói ra lời giải.

#### Idea

Đặt `l = 0`, `r = n-1`, và duy trì:

> **Invariant**: nếu cặp đáp án tồn tại, chỉ số của nó nằm hoàn toàn trong `[l, r]`.

Bảo toàn invariant qua mỗi bước:
- `numbers[l] + numbers[r] < target`: vì mảng tăng dần, với **mọi** `j` thoả `l < j ≤ r` ta có `numbers[j] ≤ numbers[r]`, do đó `numbers[l] + numbers[j] ≤ numbers[l] + numbers[r] < target`. Không cặp nào chứa `l` đạt được `target` ⇒ bỏ `l` an toàn, `l += 1`.
- `> target`: đối xứng, mọi cặp chứa `r` đều có tổng ≥ tổng hiện tại > target ⇒ `r -= 1`.
- `== target`: tìm thấy.

Khởi tạo đúng (chưa loại gì). Kết thúc: mỗi bước `r - l` giảm đúng 1 nên vòng lặp dừng sau ≤ `n` bước. Vì đề bảo đảm đáp án tồn tại và invariant nói nó luôn trong `[l, r]`, ta phải chạm vào nó trước khi `l ≥ r`.

#### Naive

```python
class SolutionNaive:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        n = len(numbers)
        for i in range(n):                       # O(n^2): thu moi cap
            for j in range(i + 1, n):
                if numbers[i] + numbers[j] == target:
                    return [i + 1, j + 1]
        return []

print(SolutionNaive().twoSum([2, 7, 11, 15], 9))
print(SolutionNaive().twoSum([2, 3, 4], 6))
print(SolutionNaive().twoSum([-1, 0], -1))
```

In ra `[1, 2]`, `[1, 3]`, `[1, 2]`.

`O(n²)` time, `O(1)` space. Chậm vì nó **không dùng chút nào** thông tin "mảng đã sorted" — chạy y hệt trên mảng ngẫu nhiên. Bất cứ khi nào lời giải của bạn không dùng tới một tính chất mà đề cho, đó là dấu hiệu còn tối ưu được.

#### Optimized

```python
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        l, r = 0, len(numbers) - 1
        while l < r:
            s = numbers[l] + numbers[r]
            if s == target:
                return [l + 1, r + 1]           # de bao dam co dung 1 dap an
            if s < target:
                l += 1                          # moi cap (l, j<=r) deu < target
            else:
                r -= 1                          # moi cap (i>=l, r) deu > target
        return []

print(Solution().twoSum([2, 7, 11, 15], 9))
print(Solution().twoSum([2, 3, 4], 6))
print(Solution().twoSum([-1, 0], -1))
print(Solution().twoSum([3, 3], 6))
```

In ra `[1, 2]`, `[1, 3]`, `[1, 2]`, `[1, 2]`.

**Đánh đổi**: ở đây gần như không đánh đổi gì — đây là trường hợp hiếm khi bản tối ưu vừa nhanh hơn (`O(n)` vs `O(n²)`) vừa không tốn thêm bộ nhớ. Cái "giá" thực sự là **tiền đề**: nó chỉ chạy đúng khi mảng đã sorted. Nếu mảng chưa sorted, bạn phải trả `O(n log n)` để sort, và khi đó chỉ số gốc bị xáo — đó chính là lý do bài 1. Two Sum (không sorted, cần chỉ số gốc) dùng hash map chứ không dùng two pointers.

### Bài 2 — 11. Container With Most Water

#### Requirements

Cho mảng `height` với `height[i]` là chiều cao của đường thẳng đứng tại toạ độ `i`. Chọn hai đường tạo thành một thùng chứa nước; lượng nước chứa được là `min(height[i], height[j]) × (j - i)`. Trả về lượng nước lớn nhất.

Chú ý: đây **không phải** bài trapping rain water — thùng chỉ do hai đường tạo thành, mọi đường ở giữa bị bỏ qua hoàn toàn (coi như thùng không có đáy răng cưa).

Ràng buộc: `2 ≤ n ≤ 10^5`, `0 ≤ height[i] ≤ 10^4`.

Edge cases: `n = 2` (chỉ một lựa chọn); mọi chiều cao bằng nhau (đáp án là hai đầu mút); có chiều cao `0`; dãy tăng dần hoặc giảm dần hoàn toàn.

#### Complexity mục tiêu

`n ≤ 10^5` ⇒ `O(n²)` là `10^10` phép — vô vọng ngay cả với C++. Bảng §02 nói `10^5` là vùng của `O(n log n)` hoặc `O(n)`.

Ở đây thậm chí không có gì để sort (thứ tự chỉ số **là** khoảng cách, sort sẽ phá mất nó), nên `O(n log n)` cũng không có hình dạng rõ ràng. Còn lại: một lần quét `O(n)`.

#### Idea

`l = 0`, `r = n-1`. Ghi nhận diện tích hiện tại, rồi **dịch con trỏ đứng ở cạnh thấp hơn**.

> **Invariant**: mọi cặp `(i, j)` mà `i < l` hoặc `j > r` đều có diện tích ≤ `best` đã ghi nhận.

Bảo toàn — đây là bước đáng suy nghĩ. Giả sử `height[l] < height[r]` và ta bỏ `l`. Xét bất kỳ cặp `(l, j)` với `l < j < r`:

- Chiều rộng: `j - l < r - l`, **hẹp hơn**.
- Chiều cao: `min(height[l], height[j]) ≤ height[l] = min(height[l], height[r])`, **không cao hơn**.

Cả hai thừa số đều không lớn hơn, nên `area(l, j) ≤ area(l, r) ≤ best`. Vậy **mọi** cặp còn lại chứa `l` đều vô dụng ⇒ bỏ `l` an toàn. (Trường hợp `height[l] ≥ height[r]` đối xứng.)

Điểm tinh tế: lập luận này chỉ đi qua được vì ta dịch **cạnh thấp hơn**. Nếu dịch cạnh cao hơn, chiều cao có thể *tăng* ở bước sau và bù lại phần rộng bị mất — lập luận sụp, và thuật toán sai.

Kết thúc: `r - l` giảm 1 mỗi bước ⇒ dừng sau `n-1` bước; lúc đó mọi cặp đều đã bị loại hoặc đã được xét ⇒ `best` là tối ưu.

#### Naive

```python
class SolutionNaive:
    def maxArea(self, height: list[int]) -> int:
        best, n = 0, len(height)
        for i in range(n):                       # O(n^2)
            for j in range(i + 1, n):
                best = max(best, min(height[i], height[j]) * (j - i))
        return best

print(SolutionNaive().maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]))
print(SolutionNaive().maxArea([1, 1]))
```

In ra `49` và `1`.

`O(n²)` time, `O(1)` space. Với `n = 10^5` là `5·10^9` cặp — hàng giờ trong Python.

#### Optimized

```python
class Solution:
    def maxArea(self, height: list[int]) -> int:
        l, r = 0, len(height) - 1
        best = 0
        while l < r:
            best = max(best, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1                           # canh thap hon khong the tot hon nua
            else:
                r -= 1
        return best

# Doi chieu voi naive tren input ngau nhien nho (ky luat cua §05)
import random

def naive_area(height: list[int]) -> int:
    best = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            best = max(best, min(height[i], height[j]) * (j - i))
    return best

random.seed(0)
sol = Solution()
for _ in range(5000):
    case = [random.randint(0, 6) for _ in range(random.randint(2, 9))]
    if naive_area(case) != sol.maxArea(case):
        print("COUNTEREXAMPLE:", case)
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]), sol.maxArea([1, 1]))
```

In ra `khop tren 5000 case ngau nhien` rồi `49 1`.

**Đánh đổi**: không tốn thêm bộ nhớ, không cần tiền xử lý — thứ ta "trả" là **một lập luận chứng minh khó hơn**. Đây là dạng tối ưu hoá bằng *insight* thay vì bằng cấu trúc dữ liệu, và cũng vì thế nó dễ viết sai một cách thầm lặng: đổi `<` thành `>` ở dòng so sánh vẫn chạy, vẫn trả về số, chỉ là sai. Stress test là thứ duy nhất bắt được.

### Bài 3 — 42. Trapping Rain Water

#### Requirements

Mảng `height` mô tả một bản đồ độ cao rộng 1 đơn vị mỗi cột. Tính tổng lượng nước đọng lại sau mưa.

Lượng nước trên cột `i` là `min(max(height[0..i]), max(height[i..n-1])) - height[i]`, và không bao giờ âm vì cả hai max đều ≥ `height[i]`.

Ràng buộc: `1 ≤ n ≤ 2·10^4`, `0 ≤ height[i] ≤ 10^5`.

Edge cases: `n = 1` (luôn 0); dãy tăng đơn điệu hoặc giảm đơn điệu (đều 0); toàn số 0; có nhiều "bồn" tách rời nhau; đỉnh cao nhất xuất hiện nhiều lần.

#### Complexity mục tiêu

`n ≤ 2·10^4` ⇒ `O(n²)` là `4·10^8`, biên giới TLE với Python — có thể qua ở C++ nhưng đừng đánh cược. Nhắm `O(n)`.

Ở đây có một mốc trung gian đáng nói: lời giải `O(n)` time / `O(n)` space (dựng sẵn hai mảng `leftMax`, `rightMax`) là hoàn toàn hợp lệ và dễ hơn nhiều. Two pointers chỉ thêm một cải tiến: `O(1)` space. Trong phỏng vấn, hãy nói ra mốc `O(n)` space trước — đó đã là lời giải đúng, bản `O(1)` là phần thưởng.

#### Idea

`l = 0`, `r = n-1`, cùng hai biến `left_max`, `right_max` là max đã thấy từ mỗi phía. Mỗi bước **dịch con trỏ đứng ở cột thấp hơn**, và cộng nước cho đúng cột vừa xử lý.

> **Invariant**: `left_max = max(height[0..l])`, `right_max = max(height[r..n-1])`, và nước ở mọi cột hai con trỏ đã đi qua đều đã được cộng đúng và **cuối cùng** — không phải chỉnh lại sau.

Tính đúng nằm ở bổ đề:

> **Bổ đề.** Khi `height[l] < height[r]`, lượng nước tại cột `l` đúng bằng `left_max - height[l]` (với `left_max` đã cập nhật để bao gồm `height[l]`).

Chứng minh. Lượng nước thật tại `l` là `min(left_max, R) - height[l]`, với `R = max(height[l+1..n-1])` là đỉnh cao nhất bên phải. Ta chỉ cần chỉ ra `left_max ≤ R`.

- Nếu `left_max = height[l]` (cột hiện tại là đỉnh mới bên trái): `R ≥ height[r] > height[l] = left_max`. Xong.
- Nếu `left_max > height[l]`: đỉnh tạo ra `left_max` nằm ở một vị trí `p < l`. Con trỏ trái chỉ **rời khỏi `p`** ở nhánh `height[p] < height[r_p]`, với `r_p` là vị trí con trỏ phải lúc đó — tức tồn tại `q_1 = r_p > p` với `height[q_1] > height[p] = left_max`.

  Nếu `q_1 > l` thì xong: `R ≥ height[q_1] ≥ left_max`. Nếu `q_1 ≤ l`, thì `height[q_1] > left_max = max(height[0..l])` là mâu thuẫn — nên trường hợp `q_1 ≤ l` **không thể xảy ra**, và ta luôn ở nhánh thứ nhất. Vậy `R ≥ left_max`. ∎

Trường hợp `height[l] ≥ height[r]` đối xứng hoàn toàn.

Cảnh báo quan trọng: bổ đề dựa vào việc so **`height[l]` với `height[r]`** — chiều cao *tại hai con trỏ*. Một biến thể trông rất hợp lý là so `left_max` với `right_max` rồi mới cập nhật; biến thể đó **sai**, và chính stress test ở phần Optimized bên dưới đã bắt được nó trong lúc viết chương này: với `[2, 4, 1, 4, 1, 2, 1, 0]` đáp án đúng là `4`, biến thể sai cho `1`.

Kết thúc: mỗi bước một con trỏ dịch vào trong, `r - l` giảm ⇒ vòng lặp dừng; mọi cột được xử lý đúng một lần.

#### Naive

```python
class SolutionNaive:
    def trap(self, height: list[int]) -> int:
        """O(n^2): moi cot tinh lai max hai phia bang max() tren slice."""
        total = 0
        for i in range(len(height)):
            left = max(height[:i + 1])
            right = max(height[i:])
            total += min(left, right) - height[i]
        return total

print(SolutionNaive().trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))
print(SolutionNaive().trap([4, 2, 0, 3, 2, 5]))
print(SolutionNaive().trap([5]))
```

In ra `6`, `9`, `0`.

`O(n²)` time, `O(n)` space (mỗi `height[:i+1]` là một slice mới — §04). Thực tế còn tệ hơn `O(n²)` thuần vì slicing cấp phát bộ nhớ ở mỗi vòng.

#### Optimized

```python
class Solution:
    def trap(self, height: list[int]) -> int:
        if not height:
            return 0
        l, r = 0, len(height) - 1
        left_max = right_max = 0
        total = 0
        while l < r:
            if height[l] < height[r]:            # dich con tro o COT thap hon
                left_max = max(left_max, height[l])
                total += left_max - height[l]    # bo de: min(left_max, R) == left_max
                l += 1
            else:
                right_max = max(right_max, height[r])
                total += right_max - height[r]
                r -= 1
        return total

import random

def naive_trap(height: list[int]) -> int:
    return sum(min(max(height[:i + 1]), max(height[i:])) - h
               for i, h in enumerate(height))

random.seed(0)
sol = Solution()
for _ in range(5000):
    case = [random.randint(0, 5) for _ in range(random.randint(1, 9))]
    if naive_trap(case) != sol.trap(case):
        print("COUNTEREXAMPLE:", case, naive_trap(case), sol.trap(case))
        break
else:
    print("khop tren 5000 case ngau nhien")

print(sol.trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]),
      sol.trap([4, 2, 0, 3, 2, 5]), sol.trap([5]), sol.trap([]))
```

In ra `khop tren 5000 case ngau nhien` rồi `6 9 0 0`.

**Đánh đổi**: so với bản trung gian dùng hai mảng `leftMax`/`rightMax` (`O(n)` time, `O(n)` space), bản này đổi **hai mảng phụ lấy hai biến vô hướng** — `O(1)` space. Cái giá là mất đi tính "nhìn là hiểu": hai mảng tường minh thì đọc phát biết ngay đúng, còn bản hai con trỏ đòi hỏi bổ đề ở trên và có một biến thể sai rất giống bản đúng.

## Bài luyện thêm

- **15. 3Sum** — sort, cố định `nums[i]`, chạy two pointers đối chiều trên phần đuôi để tìm cặp có tổng `-nums[i]`; hai chỗ phải bỏ qua giá trị trùng (vòng ngoài, và sau khi tìm được bộ ba) — xem counterexample ở §05.
- **26. Remove Duplicates from Sorted Array** — two pointers cùng chiều: `k` là số phần tử đã giữ, chỉ ghi `nums[k]` khi gặp giá trị khác `nums[k-1]`.
- **76. Minimum Window Substring** — biến thể co giãn cửa sổ; đây thực chất là bài sliding window, giải chi tiết ở §07.

## Bài toán áp dụng

Merge hai danh sách đã sắp xếp — nền tảng của merge sort và của "merge k sorted lists":

```python
def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """Two pointers cung chieu tren HAI mang. O(len(a) + len(b))."""
    i = j = 0
    out: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:          # <= giu tinh STABLE: a di truoc khi bang nhau
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])             # dung 1 lan, ngoai vong lap -> khong sao
    out.extend(b[j:])
    return out

import random
random.seed(0)
for _ in range(3000):
    a = sorted(random.randint(-5, 5) for _ in range(random.randint(0, 6)))
    b = sorted(random.randint(-5, 5) for _ in range(random.randint(0, 6)))
    if merge_sorted(a, b) != sorted(a + b):
        print("COUNTEREXAMPLE:", a, b)
        break
else:
    print("merge_sorted khop voi sorted(a+b) tren 3000 case")

print(merge_sorted([1, 3, 5], [2, 3, 6]))
```

In ra `merge_sorted khop voi sorted(a+b) tren 3000 case` rồi `[1, 2, 3, 3, 5, 6]`.

Chi tiết đáng chú ý: `a[i] <= b[j]` (không phải `<`) là thứ giữ cho merge **stable**. Đổi thành `<` thì kết quả sắp xếp vẫn đúng, nhưng merge sort xây trên nó sẽ mất tính stable — một tính chất mà §04 đã cho thấy có giá trị thực sự.

## Use case thực tế

- **External merge sort.** Khi dữ liệu không vừa RAM, ta sort từng khối, ghi ra các file tạm đã sorted, rồi **merge** chúng bằng đúng vòng lặp hai con trỏ ở trên — chỉ khác là "đọc phần tử tiếp theo" là đọc từ file chứ không phải từ mảng. Đây là merge-phase trong `ORDER BY` của một CSDL trên bảng lớn hơn bộ nhớ, và trong shuffle phase của MapReduce/Spark.
- **Merge join trong CSDL.** Khi hai bảng đã có index sorted trên khoá join, engine dùng merge join `O(n + m)` thay vì hash join. Hai con trỏ, đúng nguyên lý này.
- **Merge k danh sách** tổng quát hoá bằng cách thay "so hai đầu" bằng một min-heap trên k đầu.
- **Khi nào dùng thư viện có sẵn**: `heapq.merge(*iterables)` để merge nhiều dãy đã sorted — nó lazy (trả iterator, không dựng cả kết quả trong RAM) và chạy bằng C. `sorted(a + b)` khi dữ liệu nhỏ và bạn không quan tâm `O((n+m) log(n+m))` vs `O(n+m)`. Tự viết merge chỉ khi cần kiểm soát bộ nhớ hoặc nhét logic riêng vào giữa vòng lặp.

## Bẫy thường gặp trong Python

- **`while l <= r` thay vì `l < r`** ở dạng đối chiều. Với `l == r` bạn đang ghép một phần tử với chính nó — sai cho Two Sum II (đề đòi hai chỉ số khác nhau) và cho Container (diện tích 0, vô hại nhưng thừa). Chọn có ý thức, đừng theo quán tính.
- **Quên rằng `nums.sort()` phá chỉ số gốc.** Bài 1. Two Sum đòi chỉ số của mảng ban đầu; sort xong two pointers sẽ cho chỉ số của mảng đã sort. Hoặc dùng hash map, hoặc sort các cặp `(giá trị, chỉ số gốc)`.
- **`nums.sort()` trả về `None`.** `nums = nums.sort()` là bug im lặng. Dùng `nums.sort()` (in-place) hoặc `nums = sorted(nums)`.
- **Slicing trong vòng lặp.** Bản naive của bài 42 dùng `max(height[:i+1])` — `O(n)` cấp phát mỗi vòng, tạo `O(n)` bộ nhớ rác. Chấp nhận được cho oracle, không chấp nhận được cho lời giải.
- **Sửa mảng trong lúc duyệt nó.** `for x in nums: nums.remove(x)` cho kết quả không đoán trước được. Two pointers cùng chiều tồn tại chính là để tránh việc này: ghi đè tại chỗ theo `slow`, không xoá.
- **Quên copy input khi stress test.** Nhiều lời giải two pointers bắt đầu bằng `nums.sort()` — chạy naive rồi optimized trên **cùng một list** nghĩa là bản chạy sau nhận mảng đã bị sort. Luôn `list(case)`.
- **`max()` trên dãy rỗng ném `ValueError`.** `max(height[i:])` với `i == len(height)` là lỗi. Trong bài 42 vòng lặp không chạm tới, nhưng khi copy pattern sang bài khác thì phải kiểm — hoặc dùng `max(seq, default=0)`.
