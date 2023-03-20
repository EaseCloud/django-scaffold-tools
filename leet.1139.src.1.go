// https://leetcode.cn/problems/largest-1-bordered-square/
// 1139. 最大的以 1 为边界的正方形
// O(n^3) 暴力算了，其实如果做预处理是可以做到 n^2 的

func largest1BorderedSquare(grid [][]int) int {
    n := len(grid)
    m := len(grid[0])
    k := m
    if n < k { k = n }
    for ; k > 0; k-- {
        for i:=0; i+k<=n; i++ {
            for j:=0; j+k<=m; j++ {
                flag := true
                for ii:=0; ii<k; ii++ {
                    if grid[i][j+ii] == 0 ||
                        grid[i+k-1][j+ii] == 0 ||
                        grid[i+ii][j] == 0 ||
                        grid[i+ii][j+k-1] == 0 {
                        flag = false
                        break
                    }
                }
                if flag { return k*k }
            }
        }
    }
    return 0
}
