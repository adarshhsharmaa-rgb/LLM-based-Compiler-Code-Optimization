// category: loops  (real program 005)
// Codeforces submission 3825578, problem 306/A, GNU C++, 2013-06-05
// https://codeforces.com/contest/306/submission/3825578
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <algorithm>
#include <cstdio>
using namespace std;
int main() {
    int n,m;
    scanf("%d%d",&n,&m);
    for(int i=0;i<m;i++) printf("%d ",n/m+(i<n%m));
}
