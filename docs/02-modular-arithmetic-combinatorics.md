# Số học modulo + tổ hợp

Kiến thức cần khi đề yêu cầu "trả kết quả modulo 10^9 + 7": đếm hoán vị có lặp, lấy mod khi tính, nghịch đảo modulo, định lý Fermat nhỏ và lũy thừa nhanh. Ví dụ xuyên suốt: [2514. Count Anagrams](../practices/leetcode/problems/2514.count-anagrams.py).

## Tóm tắt nhanh

| Cần làm | Cách làm | Ghi chú |
| --- | --- | --- |
| Số cách xếp n phần tử khác nhau | `n!` | |
| Số cách xếp có phần tử lặp | `n! / (c1! · c2! · ... · ck!)` | `ci` là số lần xuất hiện của từng loại |
| Cộng / trừ / nhân dưới mod | Lấy `% MOD` sau **mỗi** phép tính | Số luôn nhỏ hơn MOD |
| Chia `a / b` dưới mod | `a * pow(b, MOD - 2, MOD) % MOD` | Chỉ đúng khi MOD nguyên tố và `b % MOD != 0` |
| Lũy thừa `b^e % m` | `pow(b, e, m)` | O(log e) |
| Nghịch đảo (Python 3.8+) | `pow(b, -1, m)` | Đúng cả khi m không nguyên tố, miễn là `gcd(b, m) = 1` |
| Hằng MOD | `MOD = 10**9 + 7` | **Không** viết `1e9 + 7` vì đó là float |

## 1. Hoán vị có lặp

Từ `"too"` có 3 ký tự.

- Nếu 3 ký tự đều khác nhau thì có `3! = 6` cách xếp.
- Hai chữ `o` giống nhau. Đổi chỗ chúng thì vẫn ra cùng chuỗi, nên mỗi chuỗi bị đếm `2!` lần.
- Kết quả: `3! / 2! = 3` (`too`, `oto`, `oot`).

Tổng quát, với một từ có độ dài `n` và các ký tự xuất hiện `c1, c2, ..., ck` lần:

```
anagram(word) = n! / (c1! × c2! × ... × ck!)
```

| Từ | Đếm ký tự | Số anagram |
| --- | --- | --- |
| `abc` | a:1, b:1, c:1 | 3! = 6 |
| `aabb` | a:2, b:2 | 4! / (2!·2!) = 6 |
| `cccbhbq` | c:3, b:2, h:1, q:1 | 7! / (3!·2!) = 420 |

**Sai lầm hay gặp:** chia cho `(số ký tự khác nhau)!`. Với `"abc"` cách này cho `3!/3! = 1` thay vì 6.

### Nhiều từ độc lập: quy tắc nhân

Nếu mỗi từ được hoán vị riêng và các từ giữ nguyên vị trí, thì:

```
đáp án = anagram(từ 1) × anagram(từ 2) × ...
```

Ví dụ `"too hot"`: `3 × 6 = 18`. Chuỗi chỉ có **một từ** vẫn có thể có nhiều anagram, nên không được `return 1` sớm.

## 2. Vì sao phải lấy mod sau mỗi bước

Giai thừa tăng rất nhanh: `20!` đã vượt `10^18`, còn `100000!` có khoảng 456.000 chữ số. Python có số nguyên lớn nên tính thẳng không bị tràn, nhưng chậm. Dùng float thì mất độ chính xác ngay.

Các tính chất được phép dùng:

```
(a + b) % M = ((a % M) + (b % M)) % M
(a - b) % M = ((a % M) - (b % M)) % M      # trong Python, % luôn trả về số không âm
(a × b) % M = ((a % M) × (b % M)) % M
```

**Phép chia thì không làm được như vậy.** Ví dụ với `M = 7`, cần tính `12 / 4 = 3`:

```
12 % 7 = 5,   4 % 7 = 4,   5 / 4 = 1.25    ← sai
```

Sau khi lấy mod, tử số không còn chia hết cho mẫu nữa. Vì vậy cần nghịch đảo modulo.

## 3. Nghịch đảo modulo

Với số thực, chia cho `b` chính là nhân với `1/b`, số thỏa `b × (1/b) = 1`. Trong mod không có phân số, nhưng có thể có một **số nguyên** `x` đóng vai trò đó:

```
b × x ≡ 1  (mod M)      →  x gọi là inv(b)
a / b ≡ a × inv(b)  (mod M)
```

Ví dụ với `M = 7`: `inv(4) = 2` vì `4 × 2 = 8 ≡ 1`. Khi đó `12 / 4 → 5 × 2 = 10 ≡ 3` ✓.

### Khi nào nghịch đảo tồn tại

**`inv(b)` tồn tại khi và chỉ khi `gcd(b, M) = 1`.**

Phản ví dụ: với `M = 6`, số `2` không có nghịch đảo. `2x` luôn chẵn và 6 cũng chẵn, nên `2x mod 6` luôn chẵn, không bao giờ bằng 1.

Khi `M` là **số nguyên tố**, mọi `b` không chia hết cho `M` đều có nghịch đảo. Đó là lý do đề hay chọn `10^9 + 7` (một số nguyên tố). Trong bài Count Anagrams, `cnt ≤ 10^5 < MOD` nên `cnt!` không chứa thừa số MOD và luôn có nghịch đảo.

## 4. Định lý Fermat nhỏ

> Nếu `p` là số nguyên tố và `b` không chia hết cho `p` thì `b^(p-1) ≡ 1 (mod p)`.

Tách `b^(p-1) = b × b^(p-2)`, ta có `b × b^(p-2) ≡ 1`, do đó:

```
inv(b) = b^(p-2) mod p
```

Kiểm tra với `p = 7`, khi đó `p - 2 = 5`:

| b | b^5 mod 7 | Thử lại |
| --- | --- | --- |
| 2 | 32 ≡ 4 | 2 × 4 = 8 ≡ 1 ✓ |
| 3 | 243 ≡ 5 | 3 × 5 = 15 ≡ 1 ✓ |

### Trực giác vì sao định lý đúng

Lấy `p = 7`, `b = 3`. Nhân 3 với từng số từ 1 đến 6 rồi lấy mod 7:

```
3×1=3  3×2=6  3×3≡2  3×4≡5  3×5≡1  3×6≡4   →  {3, 6, 2, 5, 1, 4}
```

Kết quả đúng là tập `{1..6}`, chỉ đổi thứ tự. Hai tập giống nhau nên tích của chúng bằng nhau:

```
3^6 × 6! ≡ 6!   →   3^6 ≡ 1   (giản ước 6!, được phép vì 6! có nghịch đảo mod 7)
```

Kiểm tra: `3^6 = 729 = 7 × 104 + 1` ✓. Lập luận này đúng với mọi số nguyên tố `p`.

## 5. Lũy thừa nhanh

Số mũ `MOD - 2 = 1.000.000.005`, nên không thể nhân lặp từng lần. Lũy thừa nhanh (bình phương liên tiếp) dựa trên biểu diễn nhị phân của số mũ:

```
3^13:  13 = 8 + 4 + 1   (nhị phân 1101)
3^1 → 3^2 → 3^4 → 3^8   (bình phương liên tiếp)
3^13 = 3^8 × 3^4 × 3^1
```

Số bước khoảng `log2(e)`, tức khoảng 30 bước khi `e ≈ 10^9`. Python có sẵn `pow(b, e, m)`. Nếu cần tự viết:

```python
def mod_pow(b, e, m):
    res = 1
    b %= m
    while e:
        if e & 1:
            res = res * b % m
        b = b * b % m
        e >>= 1
    return res
```

## 6. Áp dụng: 2514. Count Anagrams

```python
from collections import Counter

class Solution:
    def countAnagrams(self, s: str) -> int:
        MOD = 10**9 + 7
        n = len(s)

        fact = [1] * (n + 1)                      # fact[i] = i! % MOD
        for i in range(1, n + 1):
            fact[i] = fact[i - 1] * i % MOD

        ans = 1
        for word in s.split(" "):
            ans = ans * fact[len(word)] % MOD     # nhân tử số: len(word)!
            for cnt in Counter(word).values():    # chia cho cnt! = nhân nghịch đảo
                ans = ans * pow(fact[cnt], MOD - 2, MOD) % MOD
        return ans
```

Trace với `"too hot"`:

| Bước | Thao tác | `ans` |
| --- | --- | --- |
| khởi tạo | | 1 |
| `"too"` tử số | × 3! = 6 | 6 |
| `'t'`: cnt = 1 | × inv(1!) = 1 | 6 |
| `'o'`: cnt = 2 | × inv(2!) = 500000004 | **3** |
| `"hot"` tử số | × 3! = 6 | 18 |
| `'h'`, `'o'`, `'t'`: cnt = 1 | × 1 | **18** |

Số `500000004` là `inv(2)` vì `2 × 500000004 = 10^9 + 8 ≡ 1`. Nhân 6 với nó cho 3, đúng bằng `6 / 2`.

**Độ phức tạp:** thời gian O(n + k·log MOD), với k là tổng số ký tự khác nhau của các từ (k ≤ n). Bộ nhớ O(n).

### Tối ưu: tính sẵn bảng nghịch đảo giai thừa

Khi phải chia cho nhiều giai thừa (bài tổ hợp `C(n, k)`, nhiều truy vấn), tính sẵn `inv_fact` theo chiều ngược. Cả bài chỉ cần gọi `pow` một lần.

```python
fact = [1] * (n + 1)
for i in range(1, n + 1):
    fact[i] = fact[i - 1] * i % MOD

inv_fact = [1] * (n + 1)
inv_fact[n] = pow(fact[n], MOD - 2, MOD)
for i in range(n, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD   # 1/(i-1)! = i × 1/i!

def comb(n, k):                               # C(n, k) % MOD
    if k < 0 or k > n:
        return 0
    return fact[n] * inv_fact[k] % MOD * inv_fact[n - k] % MOD
```

## 7. Lỗi hay gặp

| Lỗi | Hậu quả | Sửa |
| --- | --- | --- |
| `MOD = 1e9 + 7` | MOD là float, kết quả mất chính xác | `MOD = 10**9 + 7` |
| Chia bằng `/` sau khi đã lấy mod | Ra số thực, sai kết quả | Nhân với `pow(b, MOD - 2, MOD)` |
| Chỉ lấy mod ở cuối | Số khổng lồ, chậm hoặc TLE | `% MOD` sau mỗi phép nhân |
| Bảng giai thừa kích thước cố định, ví dụ `[1] * 100` | `IndexError` khi chuỗi dài | Kích thước `n + 1` theo input |
| Chia cho `(số ký tự khác nhau)!` | Sai công thức | Chia cho tích `ci!` |
| Dùng Fermat khi MOD không nguyên tố | Nghịch đảo sai | Dùng `pow(b, -1, m)` (extended Euclid) |
| `k[c].append` thiếu `()` | Không append gì (chỉ lấy method ra) | `k[c].append(x)`, hoặc đếm bằng `Counter` |

## Phụ lục: `defaultdict`

`defaultdict(factory)` giống `dict`, nhưng khi truy cập một key chưa có, nó tự tạo key đó với giá trị `factory()`.

| Khai báo | Giá trị mặc định | Dùng cho |
| --- | --- | --- |
| `defaultdict(list)` | `[]` | Nhóm phần tử, danh sách kề của graph |
| `defaultdict(int)` | `0` | Đếm tần suất |
| `defaultdict(set)` | `set()` | Nhóm phần tử không trùng |

```python
from collections import defaultdict

groups = defaultdict(list)
for w in ["eat", "tea", "tan"]:
    groups["".join(sorted(w))].append(w)   # không cần kiểm tra key đã có chưa
# {'aet': ['eat', 'tea'], 'ant': ['tan']}
```

Chỉ truy cập `d[key]` mới tạo key. `key in d` và `d.get(key)` thì **không** tạo key. Nếu chỉ cần đếm, dùng `Counter(iterable)` cho gọn.
