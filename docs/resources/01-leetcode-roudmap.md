# Lộ trình LeetCode 16 tuần

16 tuần, mỗi ngày 45–60 phút, chạy song song với lộ trình AI Engineer: ôn nền DSA, rồi medium, rồi hard, mỗi tuần một pattern nối tiếp pattern tuần trước.

## Vì sao giải rời rạc không đọng lại

Giải bài ngẫu nhiên khiến mỗi bài là một mẹo riêng; khi gặp bài mới, bạn không nhận ra nó cùng họ với bài cũ. Cách sửa là học theo **chuỗi pattern**: mỗi kỹ thuật được xây trên kỹ thuật trước và được dùng lại trong bài hard sau đó.

1. **Một tuần = một pattern**, đi từ bài warm-up (easy) → medium → hard cùng pattern. Không nhảy chủ đề giữa tuần.
2. **Bài hard cuối tuần ghép 2 pattern**: pattern tuần này + một pattern đã học (ví dụ Word Search II = Trie + Backtracking; Merge k Sorted Lists = Linked List + Heap). Đây là chỗ tạo ra “diện tích liên kết”.
3. **Mỗi bài ghi 3 dòng vào sổ pattern:** dấu hiệu nhận diện (“mảng đã sort + tìm cặp → two pointers”), template code, bài đã gặp cùng pattern.
4. **Ôn lặp lại theo khoảng cách** (D+1, D+3, D+7, D+21): làm lại từ đầu, không nhìn code cũ. Chủ nhật là ngày ôn.
5. **Nối với công việc AI:** mỗi tuần có một dòng “Ứng dụng AI” (top-k retrieval = heap, LRU cache cho LLM = hash map + linked list, đồ thị agent LangGraph = topo sort, WER/CER khi đánh giá speech = edit distance) để thuật toán có tính thực tiễn.
6. **Quy tắc 25 phút:** bí quá 25 phút thì đọc hint/pattern, không đọc lời giải; bí quá 45 phút thì đọc lời giải, rồi đưa bài vào danh sách ôn D+1.

## Bản đồ pattern

&#91;embedded content: Bản đồ pattern · 16 tuần, 4 nhánh\]

Ví dụ đọc sơ đồ: Dijkstra (tuần 12) = BFS của tuần 10 + heap của tuần 7; DP (tuần 13) = backtracking của tuần 8 + nhớ kết quả. Mỗi tuần bên dưới có dòng “Nối từ” ghi rõ các liên kết còn lại.

## Nhịp học mỗi tuần

Khoảng 7 giờ/tuần cho LeetCode; cộng 6–8 giờ lộ trình AI là 13–15 giờ/tuần. Nên làm LeetCode buổi sáng (đầu óc tỉnh), học khoá AI buổi tối.

| Ngày | Việc | Thời gian |
| --- | --- | --- |
| Thứ 2 | Học pattern mới: ý tưởng + viết template từ đầu, 1–2 bài warm-up \[E\] | 60 phút |
| Thứ 3 | 1–2 bài \[M\] cốt lõi của pattern | 45–60 phút |
| Thứ 4 | 1 bài \[M\] + làm lại bài hôm qua (D+1) | 60 phút |
| Thứ 5 | 1–2 bài \[M\] biến thể | 45–60 phút |
| Thứ 6 | 1 bài \[M\] khó hoặc nối với pattern cũ | 60 phút |
| Thứ 7 | 1 bài \[H\] ghép 2 pattern, viết phân tích độ phức tạp | 90 phút |
| Chủ nhật | Ôn: làm lại 3 bài cũ (D+7, D+21) không nhìn code, cập nhật sổ pattern | 60 phút |

Trong danh sách tuần bên dưới: \[E\] = easy warm-up, \[M\] = medium, \[H\] = hard. Bài nào không kịp thì dời sang Chủ nhật, không bỏ ngày ôn.

## Giai đoạn 1 — Nền tảng (tuần 1–4)

Mục tiêu: ôn lại Big-O và 4 pattern trên mảng dùng nhiều nhất; cuối giai đoạn giải được medium trong 30 phút.

### Tuần 1 — Arrays, Hashing, Prefix Sum

Nền cho mọi pattern sau. Ứng dụng AI: đếm token, dedup dữ liệu, báo cáo metric theo cửa sổ.

- [ ] &#91;E\] [1. Two Sum](https://leetcode.com/problems/two-sum/) — hash map tra cứu O(1)
- [ ] &#91;E\] [217. Contains Duplicate](https://leetcode.com/problems/contains-duplicate/)
- [ ] &#91;M\] [49. Group Anagrams](https://leetcode.com/problems/group-anagrams/) — khoá hash là chữ đã sort / đếm ký tự
- [ ] &#91;M\] [347. Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) — bucket sort; sẽ làm lại bằng heap ở tuần 7
- [ ] &#91;M\] [238. Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) — prefix/suffix
- [ ] &#91;M\] [560. Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — prefix sum + hash map
- [ ] &#91;M\] [128. Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/)
- [ ] &#91;H\] [41. First Missing Positive](https://leetcode.com/problems/first-missing-positive/) — dùng chính mảng làm hash

### Tuần 2 — Two Pointers, Sliding Window

Nối từ tuần 1: hash map giờ đếm tần suất trong cửa sổ. Ứng dụng AI: chunking văn bản có overlap cho RAG.

- [ ] &#91;E\] [125. Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)
- [ ] &#91;M\] [167. Two Sum II](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) — so với bài 1: mảng đã sort → hai con trỏ
- [ ] &#91;M\] [15. 3Sum](https://leetcode.com/problems/3sum/)
- [ ] &#91;M\] [11. Container With Most Water](https://leetcode.com/problems/container-with-most-water/)
- [ ] &#91;M\] [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) — template cửa sổ co giãn
- [ ] &#91;M\] [424. Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)
- [ ] &#91;M\] [567. Permutation in String](https://leetcode.com/problems/permutation-in-string/) — cửa sổ cố định
- [ ] &#91;H\] [76. Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) — cửa sổ + đếm tần suất (tuần 1)
- [ ] &#91;H\] [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) — làm bằng two pointers; tuần 3 làm lại bằng stack

### Tuần 3 — Stack, Monotonic Stack

Nối từ tuần 2: cùng bài toán “phần tử lớn hơn gần nhất” nhưng giữ ứng viên trong stack. Ứng dụng AI: parse JSON/biểu thức từ output LLM.

- [ ] &#91;E\] [20. Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)
- [ ] &#91;M\] [155. Min Stack](https://leetcode.com/problems/min-stack/)
- [ ] &#91;M\] [150. Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/)
- [ ] &#91;M\] [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) — nhá trước backtracking (tuần 8)
- [ ] &#91;M\] [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) — template monotonic stack
- [ ] &#91;M\] [853. Car Fleet](https://leetcode.com/problems/car-fleet/)
- [ ] &#91;H\] [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) — tuần 16 mở rộng thành bài 85
- [ ] &#91;H\] Làm lại [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) bằng monotonic stack, so sánh với cách two pointers

### Tuần 4 — Binary Search (kể cả tìm trên đáp án)

Ý chính: binary search không chỉ trên mảng mà trên không gian đáp án có tính đơn điệu. Ứng dụng AI: tìm batch size/ngưỡng confidence lớn nhất vẫn đạt điều kiện.

- [ ] &#91;E\] [704. Binary Search](https://leetcode.com/problems/binary-search/) — viết template lo/hi không lỗi biên
- [ ] &#91;M\] [74. Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/)
- [ ] &#91;M\] [875. Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) — binary search trên đáp án
- [ ] &#91;M\] [153. Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)
- [ ] &#91;M\] [33. Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)
- [ ] &#91;M\] [981. Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/) — hash map (tuần 1) + binary search
- [ ] &#91;H\] [410. Split Array Largest Sum](https://leetcode.com/problems/split-array-largest-sum/) — cùng khuôn với bài 875
- [ ] &#91;H\] [4. Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/)

## Giai đoạn 2 — Cấu trúc dữ liệu (tuần 5–9)

Mục tiêu: thành thạo linked list, tree, heap, backtracking, trie; bắt đầu giải hard ghép 2 pattern.

### Tuần 5 — Linked List & thiết kế cấu trúc

Nối từ tuần 2: kỹ thuật con trỏ nhanh/chậm. Ứng dụng AI: LRU cache cho kết quả LLM/embedding.

- [ ] &#91;E\] [206. Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/)
- [ ] &#91;E\] [141. Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) — fast/slow pointer
- [ ] &#91;M\] [143. Reorder List](https://leetcode.com/problems/reorder-list/) — tìm giữa + đảo + trộn
- [ ] &#91;M\] [19. Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
- [ ] &#91;M\] [138. Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) — hash map node cũ → mới
- [ ] &#91;M\] [287. Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) — Floyd trên mảng
- [ ] &#91;M\] [146. LRU Cache](https://leetcode.com/problems/lru-cache/) — hash map + doubly linked list
- [ ] &#91;H\] [25. Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/)

### Tuần 6 — Trees: DFS, BFS, BST

Nền cho graph (tuần 10) và DP trên cây. Ứng dụng AI: cây quyết định, cây tài liệu phân cấp trong RAG (RAPTOR, tree index).

- [ ] &#91;E\] [104. Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/)
- [ ] &#91;E\] [226. Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/)
- [ ] &#91;M\] [102. Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) — template BFS
- [ ] &#91;M\] [199. Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/)
- [ ] &#91;M\] [98. Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/)
- [ ] &#91;M\] [230. Kth Smallest Element in a BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) — inorder + stack (tuần 3)
- [ ] &#91;M\] [105. Construct Binary Tree from Preorder and Inorder](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)
- [ ] &#91;M\] [236. Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)
- [ ] &#91;H\] [124. Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) — DFS trả về giá trị, nhá trước DP
- [ ] &#91;H\] [297. Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

### Tuần 7 — Heap / Priority Queue

Nối từ tuần 1 (bài 347) và tuần 5 (linked list). Ứng dụng AI: top-k trong vector search, beam search, hàng đợi request theo ưu tiên.

- [ ] &#91;E\] [703. Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/)
- [ ] &#91;M\] [215. Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) — heap k phần tử vs quickselect
- [ ] &#91;M\] [973. K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) — chính là kNN
- [ ] &#91;M\] Làm lại [347. Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) bằng heap
- [ ] &#91;M\] [621. Task Scheduler](https://leetcode.com/problems/task-scheduler/)
- [ ] &#91;M\] [355. Design Twitter](https://leetcode.com/problems/design-twitter/) — hash map + heap
- [ ] &#91;H\] [23. Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) — linked list (tuần 5) + heap
- [ ] &#91;H\] [295. Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) — hai heap

### Tuần 8 — Backtracking

Nối từ tuần 3 (bài 22) và tuần 6 (DFS). Đây là gốc của DP: backtracking + nhớ kết quả = memoization. Ứng dụng AI: tìm kiếm kế hoạch của agent, Tree-of-Thoughts.

- [ ] &#91;M\] [78. Subsets](https://leetcode.com/problems/subsets/) — template chọn/không chọn
- [ ] &#91;M\] [90. Subsets II](https://leetcode.com/problems/subsets-ii/) — xử lý trùng
- [ ] &#91;M\] [39. Combination Sum](https://leetcode.com/problems/combination-sum/)
- [ ] &#91;M\] [46. Permutations](https://leetcode.com/problems/permutations/)
- [ ] &#91;M\] [79. Word Search](https://leetcode.com/problems/word-search/) — backtracking trên lưới
- [ ] &#91;M\] [131. Palindrome Partitioning](https://leetcode.com/problems/palindrome-partitioning/)
- [ ] &#91;H\] [51. N-Queens](https://leetcode.com/problems/n-queens/)

### Tuần 9 — Trie & Intervals

Nối từ tuần 6 (cây) và tuần 8 (backtracking). Ứng dụng AI: tokenizer, autocomplete, constrained decoding; gộp khoảng thời gian/đoạn văn bản trùng.

- [ ] &#91;M\] [208. Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/)
- [ ] &#91;M\] [211. Design Add and Search Words](https://leetcode.com/problems/design-add-and-search-words-data-structure/) — trie + DFS
- [ ] &#91;M\] [56. Merge Intervals](https://leetcode.com/problems/merge-intervals/) — sort rồi quét
- [ ] &#91;M\] [57. Insert Interval](https://leetcode.com/problems/insert-interval/)
- [ ] &#91;M\] [435. Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) — greedy theo điểm kết thúc
- [ ] &#91;H\] [212. Word Search II](https://leetcode.com/problems/word-search-ii/) — trie + backtracking (bài 79)

## Giai đoạn 3 — Graph & Dynamic Programming (tuần 10–15)

Mục tiêu: giải được hard về graph và DP, hai mảng hay gặp nhất ở vòng phỏng vấn senior.

### Tuần 10 — Graph: BFS / DFS trên lưới và đồ thị

Nối từ tuần 6 (BFS/DFS trên cây) và tuần 8 (duyệt lưới). Ứng dụng AI: knowledge graph, GraphRAG, duyệt HNSW.

- [ ] &#91;M\] [200. Number of Islands](https://leetcode.com/problems/number-of-islands/) — template DFS lưới
- [ ] &#91;M\] [695. Max Area of Island](https://leetcode.com/problems/max-area-of-island/)
- [ ] &#91;M\] [133. Clone Graph](https://leetcode.com/problems/clone-graph/) — cùng ý với bài 138
- [ ] &#91;M\] [994. Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) — BFS nhiều nguồn
- [ ] &#91;M\] [417. Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) — duyệt ngược từ biên
- [ ] &#91;M\] [130. Surrounded Regions](https://leetcode.com/problems/surrounded-regions/)
- [ ] &#91;H\] [127. Word Ladder](https://leetcode.com/problems/word-ladder/) — BFS đường ngắn nhất

### Tuần 11 — Topological Sort & Union-Find

Nối từ tuần 10. Ứng dụng AI: thứ tự chạy node trong LangGraph/DAG pipeline, gộp thực thể trùng (entity resolution).

- [ ] &#91;M\] [207. Course Schedule](https://leetcode.com/problems/course-schedule/) — phát hiện chu trình
- [ ] &#91;M\] [210. Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) — Kahn’s algorithm
- [ ] &#91;M\] [547. Number of Provinces](https://leetcode.com/problems/number-of-provinces/) — template Union-Find
- [ ] &#91;M\] [684. Redundant Connection](https://leetcode.com/problems/redundant-connection/)
- [ ] &#91;M\] [721. Accounts Merge](https://leetcode.com/problems/accounts-merge/) — hash map + Union-Find
- [ ] &#91;H\] [329. Longest Increasing Path in a Matrix](https://leetcode.com/problems/longest-increasing-path-in-a-matrix/) — DFS + memo, cầu nối sang DP

### Tuần 12 — Đường đi ngắn nhất & cây khung

Nối từ tuần 7 (heap) + tuần 10 (BFS): Dijkstra = BFS dùng heap. Ứng dụng AI: routing giữa các model/agent theo chi phí.

- [ ] &#91;M\] [743. Network Delay Time](https://leetcode.com/problems/network-delay-time/) — template Dijkstra
- [ ] &#91;M\] [1631. Path With Minimum Effort](https://leetcode.com/problems/path-with-minimum-effort/)
- [ ] &#91;M\] [1584. Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/) — Prim/Kruskal (Union-Find tuần 11)
- [ ] &#91;M\] [787. Cheapest Flights Within K Stops](https://leetcode.com/problems/cheapest-flights-within-k-stops/) — Bellman-Ford
- [ ] &#91;H\] [778. Swim in Rising Water](https://leetcode.com/problems/swim-in-rising-water/) — Dijkstra hoặc binary search (tuần 4)
- [ ] &#91;H\] [332. Reconstruct Itinerary](https://leetcode.com/problems/reconstruct-itinerary/)

### Tuần 13 — DP 1 chiều

Nối từ tuần 8: viết backtracking trước → thêm memo → chuyển thành bảng. Ứng dụng AI: Viterbi, tách từ (word segmentation) tiếng Việt.

- [ ] &#91;E\] [70. Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) — viết cả 3 cách: đệ quy, memo, bảng
- [ ] &#91;M\] [198. House Robber](https://leetcode.com/problems/house-robber/)
- [ ] &#91;M\] [213. House Robber II](https://leetcode.com/problems/house-robber-ii/)
- [ ] &#91;M\] [91. Decode Ways](https://leetcode.com/problems/decode-ways/)
- [ ] &#91;M\] [322. Coin Change](https://leetcode.com/problems/coin-change/)
- [ ] &#91;M\] [152. Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/)
- [ ] &#91;M\] [300. Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) — O(n log n) dùng binary search (tuần 4)
- [ ] &#91;M\] [139. Word Break](https://leetcode.com/problems/word-break/) — có thể kết hợp trie (tuần 9)
- [ ] &#91;H\] [32. Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) — DP hoặc stack (tuần 3)

### Tuần 14 — DP 2 chiều & DP trên chuỗi

Nối từ tuần 13. Ứng dụng AI trực tiếp: edit distance là nền của WER/CER khi đánh giá speech/OCR; LCS là nền của ROUGE-L.

- [ ] &#91;M\] [62. Unique Paths](https://leetcode.com/problems/unique-paths/)
- [ ] &#91;M\] [1143. Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) — template DP 2 chuỗi
- [ ] &#91;M\] [518. Coin Change II](https://leetcode.com/problems/coin-change-ii/) — so với bài 322
- [ ] &#91;M\] [494. Target Sum](https://leetcode.com/problems/target-sum/)
- [ ] &#91;M\] [309. Best Time to Buy and Sell Stock with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) — DP trạng thái
- [ ] &#91;M\] [97. Interleaving String](https://leetcode.com/problems/interleaving-string/)
- [ ] &#91;H\] [72. Edit Distance](https://leetcode.com/problems/edit-distance/) — tự viết hàm tính WER sau khi giải
- [ ] &#91;H\] [115. Distinct Subsequences](https://leetcode.com/problems/distinct-subsequences/)
- [ ] &#91;H\] [10. Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/)

### Tuần 15 — Greedy & Interval DP

Nối từ tuần 9 (intervals) và tuần 13–14. Bài học chính: khi nào greedy đúng, khi nào phải DP.

- [ ] &#91;M\] [53. Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) — Kadane
- [ ] &#91;M\] [55. Jump Game](https://leetcode.com/problems/jump-game/)
- [ ] &#91;M\] [45. Jump Game II](https://leetcode.com/problems/jump-game-ii/) — BFS theo tầng trên mảng
- [ ] &#91;M\] [134. Gas Station](https://leetcode.com/problems/gas-station/)
- [ ] &#91;M\] [763. Partition Labels](https://leetcode.com/problems/partition-labels/)
- [ ] &#91;H\] [312. Burst Balloons](https://leetcode.com/problems/burst-balloons/) — interval DP
- [ ] &#91;H\] [1235. Maximum Profit in Job Scheduling](https://leetcode.com/problems/maximum-profit-in-job-scheduling/) — sort + DP + binary search (tuần 4)

## Tuần 16 — Tổng ôn & mock interview

Không học pattern mới; luyện nhận diện pattern khi không biết trước bài thuộc chủ đề nào.

- [ ] &#91;H\] [239. Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) — sliding window (tuần 2) + monotonic deque (tuần 3)
- [ ] &#91;H\] [85. Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) — gọi lại bài 84 cho từng hàng
- [ ] Làm lại 6 bài hard đại diện, không nhìn code: 76, 84, 23, 212, 72, 4
- [ ] Mock 1: 2 medium + 1 hard ngẫu nhiên trong 75 phút, nói to cách nghĩ như phỏng vấn thật
- [ ] Mock 2: như trên, chọn từ các bài đã đánh dấu “cần ôn”
- [ ] Mock 3: tham gia một LeetCode Weekly Contest

**Theo dõi tiến độ:** tick từng bài trong tab này. Cuối mỗi tuần tự chấm 3 chỉ số: số bài xong, số bài làm lại được không nhìn code, thời gian trung bình mỗi medium (mục tiêu dưới 30 phút từ tuần 8, hard dưới 45 phút từ tuần 14). Tổng cộng khoảng 120 bài, chủ yếu lấy từ danh sách NeetCode 150 và xếp lại theo chuỗi liên kết.
