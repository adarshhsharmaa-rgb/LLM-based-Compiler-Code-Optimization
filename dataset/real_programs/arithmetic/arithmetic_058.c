// category: arithmetic  (real program 058)
// Codeforces submission 818826, problem 125/A, GNU C++, 2011-10-30
// https://codeforces.com/contest/125/submission/818826
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
    int n;
    scanf("%d",&n);
    n=n/3+(n%3==2);
    printf("%d %d\n",n/12,n%12);
    return 0;
}
