// category: loops  (real program 065)
// Codeforces submission 2020020, problem 49/C, GNU C++, 2012-08-16
// https://codeforces.com/contest/49/submission/2020020
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
    int n;
    scanf("%d",&n);
    printf("%d",n);
    for (int i=2;i<=n;++i) printf(" %d",i-1);
    printf("\n");
    return 0;
}
